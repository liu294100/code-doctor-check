# -*- coding: utf-8 -*-
"""
Apifox API MCP Server

MCP server for Apifox Open API - enables AI to upload/import API documents to Apifox.

The official apifox-mcp-server only supports reading API documents.
This server adds write capabilities based on Apifox Open API:

    POST /v1/projects/{projectId}/import-openapi   Import OpenAPI/Swagger
    POST /v1/projects/{projectId}/import-postman   Import Postman Collection
    POST /v1/projects/{projectId}/export-openapi   Export OpenAPI

Key features:
- Upload to specific module/folder/branch
- Auto-fetch internal URLs (localhost/10.x/192.168.x) locally before upload
- Validate documents before upload

Dependencies: pip install mcp httpx pyyaml
Usage: python server.py

Repository: https://github.com/apifox/apifox-mcp-server
"""
import asyncio
import ipaddress
import json
import os
import re
from pathlib import Path
from typing import Any, Optional

import httpx
from mcp.server.fastmcp import FastMCP

try:
    import yaml
except ImportError:  # pyyaml optional, only affects YAML parsing
    yaml = None

# ---------------------------------------------------------------- Configuration

BASE_URL = os.environ.get("APIFOX_API_BASE_URL", "https://api.apifox.com").rstrip("/")
ACCESS_TOKEN = os.environ.get("APIFOX_ACCESS_TOKEN", "")
DEFAULT_PROJECT_ID = os.environ.get("APIFOX_PROJECT_ID", "")
API_VERSION = os.environ.get("APIFOX_API_VERSION", "2024-03-28")
LOCALE = os.environ.get("APIFOX_LOCALE", "en-US")
TIMEOUT = float(os.environ.get("APIFOX_TIMEOUT", "120"))
# auto | bearer | raw
AUTH_SCHEME = os.environ.get("APIFOX_AUTH_SCHEME", "auto").lower()


def _load_map(env_key: str) -> dict:
    """Load JSON mapping config like {"Trading":123,"Market":456}."""
    raw = os.environ.get(env_key, "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return {str(k): v for k, v in data.items()} if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


MODULE_MAP = _load_map("APIFOX_MODULE_MAP")      # Module name -> moduleId
FOLDER_MAP = _load_map("APIFOX_FOLDER_MAP")      # Folder name -> folderId
PROJECT_MAP = _load_map("APIFOX_PROJECT_MAP")    # Project alias -> projectId

mcp = FastMCP("apifox-api")

OVERWRITE_CHOICES = ("OVERWRITE_EXISTING", "AUTO_MERGE", "KEEP_EXISTING", "CREATE_NEW")

# ---------------------------------------------------------------- Utilities


def _err(msg: str, **extra) -> str:
    return json.dumps({"ok": False, "error": msg, **extra}, ensure_ascii=False, indent=2)


def _ok(payload: Any) -> str:
    return json.dumps({"ok": True, **payload}, ensure_ascii=False, indent=2)


def _resolve_project(project: Optional[str]) -> Optional[str]:
    if project:
        key = str(project)
        return str(PROJECT_MAP.get(key, key))
    return str(DEFAULT_PROJECT_ID) if DEFAULT_PROJECT_ID else None


def _resolve_id(name: Optional[str], explicit_id: Optional[int], mapping: dict) -> tuple[Optional[int], Optional[str]]:
    """Resolve name to ID via mapping, or use explicit_id directly. Returns (id, error)."""
    if explicit_id is not None:
        return int(explicit_id), None
    if not name:
        return None, None
    if name in mapping:
        return int(mapping[name]), None
    if str(name).isdigit():
        return int(name), None
    return None, f"Name `{name}` not found in mapping. Available: {sorted(mapping.keys()) or '(not configured)'}"


def _is_internal_url(url: str) -> bool:
    """Check if URL points to internal/local network (Apifox cloud can't reach)."""
    m = re.match(r"^https?://([^/:]+)", url, re.IGNORECASE)
    if not m:
        return False
    host = m.group(1).lower()
    if host in ("localhost", "host.docker.internal") or host.endswith(".local") or host.endswith(".internal"):
        return True
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback
    except ValueError:
        return False


def _read_spec_file(path: str) -> tuple[Optional[str], Optional[str]]:
    p = Path(path).expanduser()
    if not p.is_file():
        return None, f"File not found: {p}"
    try:
        return p.read_text(encoding="utf-8"), None
    except Exception as exc:
        return None, f"Failed to read file: {exc}"


def _parse_spec(text: str) -> tuple[Optional[dict], Optional[str]]:
    text = text.strip()
    if text.startswith("{"):
        try:
            return json.loads(text), None
        except json.JSONDecodeError as exc:
            return None, f"JSON parse error: {exc}"
    if yaml is None:
        return None, "Content is not JSON and pyyaml is not installed (pip install pyyaml)"
    try:
        data = yaml.safe_load(text)
        return (data, None) if isinstance(data, dict) else (None, "YAML root is not an object")
    except Exception as exc:
        return None, f"YAML parse error: {exc}"


def _auth_candidates() -> list[str]:
    """Authorization header value candidates.

    Tested: `Bearer <token>` is the correct format. Raw token may cause
    403012 "No project maintainer privilege" on self-hosted instances.
    So auto mode tries Bearer first, then falls back to raw on 401/403.
    """
    token = ACCESS_TOKEN.strip()
    if token.lower().startswith("bearer "):
        return [token]
    if AUTH_SCHEME == "bearer":
        return [f"Bearer {token}"]
    if AUTH_SCHEME == "raw":
        return [token]
    return [f"Bearer {token}", token]


_HINTS = {
    "403012": "Two possibilities: (1) Authorization format wrong - self-hosted instances require `Bearer <token>`, "
              "raw token also causes this error; (2) Token account is not project admin/maintainer. "
              "Check APIFOX_AUTH_SCHEME is not forced to raw, then check account role.",
    "401000": "Token invalid, or wrong instance: self-hosted deployment must set APIFOX_API_BASE_URL to your domain, "
              "tokens from self-hosted instance will return 401 on api.apifox.com.",
}


def _extract_counters(data: Any) -> dict:
    """Handle two response structures.

    New (public cloud docs): data.counters.{endpointCreated,...}
    Old (some self-hosted): data.apiCollection.{item,folder}.{createCount,...}
    """
    if not isinstance(data, dict):
        return {}
    if isinstance(data.get("counters"), dict):
        return data["counters"]
    legacy = {}
    for group in ("apiCollection", "customEndpointCollection", "schemaCollection"):
        node = data.get(group)
        if not isinstance(node, dict):
            continue
        for part, counts in node.items():
            if isinstance(counts, dict):
                for k, v in counts.items():
                    if v:
                        legacy[f"{group}.{part}.{k}"] = v
    return legacy


def _hint_for(payload: Any) -> Optional[str]:
    if isinstance(payload, dict):
        code = str(payload.get("errorCode") or "")
        if code in _HINTS:
            return _HINTS[code]
    return None


async def _request(method: str, path: str, *, params: Optional[dict] = None,
                   body: Optional[dict] = None) -> tuple[Optional[Any], Optional[str], int]:
    if not ACCESS_TOKEN:
        return None, "APIFOX_ACCESS_TOKEN not configured (Apifox avatar -> Account Settings -> API Access Token)", 0
    query = {"locale": LOCALE}
    if params:
        query.update(params)

    payload: Any = None
    resp = None
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for auth in _auth_candidates():
            resp = await client.request(
                method.upper(), f"{BASE_URL}{path}",
                headers={
                    "Authorization": auth,
                    "X-Apifox-Api-Version": API_VERSION,
                    "Content-Type": "application/json",
                },
                params=query, json=body,
            )
            try:
                payload = resp.json()
            except Exception:
                payload = {"raw": resp.text}
            # 401/403 may just be Authorization format issue, worth retrying with different format
            if resp.status_code not in (401, 403):
                break

    if resp is not None and resp.status_code >= 400:
        msg = f"HTTP {resp.status_code}: {json.dumps(payload, ensure_ascii=False)[:800]}"
        hint = _hint_for(payload)
        if hint:
            msg = f"{msg}\nHint: {hint}"
        return payload, msg, resp.status_code
    return payload, None, resp.status_code if resp is not None else 0


# ---------------------------------------------------------------- Tools


@mcp.tool()
async def describe_config() -> str:
    """View current Apifox MCP configuration: default project, registered module/folder/project mappings.

    Call this before uploading to confirm module/folder names can be resolved.
    If mappings are empty, you haven't configured APIFOX_MODULE_MAP / APIFOX_FOLDER_MAP / APIFOX_PROJECT_MAP in env.

    How to find moduleId/folderId? Open Apifox Web, switch to target module/folder,
    check browser URL like:
    https://app.apifox.com/project/1234567/apis/folder-8901?module=234
    where module= is moduleId, folder- is folderId.
    """
    return _ok({
        "baseUrl": BASE_URL,
        "apiVersion": API_VERSION,
        "locale": LOCALE,
        "tokenConfigured": bool(ACCESS_TOKEN),
        "defaultProjectId": DEFAULT_PROJECT_ID or None,
        "projectMap": PROJECT_MAP,
        "moduleMap": MODULE_MAP,
        "folderMap": FOLDER_MAP,
        "overwriteBehaviors": list(OVERWRITE_CHOICES),
    })


@mcp.tool()
async def check_access(project: str = "") -> str:
    """Self-check: verify if access token can call Open API, with clear failure reasons and fixes.

    Does a minimal export-openapi probe (doesn't modify any data), distinguishing:
    - 200: Token works, can upload
    - 401: Token invalid or Authorization format wrong
    - 403 / errorCode 403012: Token valid but missing "project maintainer" permission

    Recommended to run before uploading.
    """
    project_id = _resolve_project(project)
    if not project_id:
        return _err("Project not specified: pass project parameter or configure APIFOX_PROJECT_ID")
    if not ACCESS_TOKEN:
        return _err("APIFOX_ACCESS_TOKEN not configured")

    payload, err, status = await _request(
        "POST", f"/v1/projects/{project_id}/export-openapi",
        body={"scope": {"type": "ALL"}, "oasVersion": "3.1", "exportFormat": "JSON"},
    )
    masked = f"{ACCESS_TOKEN[:9]}...{ACCESS_TOKEN[-4:]}" if len(ACCESS_TOKEN) > 14 else "***"
    base = {
        "projectId": project_id,
        "token": masked,
        "authScheme": AUTH_SCHEME,
        "httpStatus": status,
    }
    if err:
        return json.dumps({"ok": False, **base, "error": err,
                           "hint": _hint_for(payload)}, ensure_ascii=False, indent=2)
    doc = payload if isinstance(payload, dict) else {}
    return _ok({**base,
                "writable": True,
                "projectTitle": (doc.get("info") or {}).get("title"),
                "endpointCount": len(doc.get("paths") or {})})


@mcp.tool()
async def discover_modules(project: str = "", start: int = 1, end: int = 120,
                           concurrency: int = 5) -> str:
    """Discover real module IDs and names in project, for filling APIFOX_MODULE_MAP.

    Open API has no "list modules" endpoint. This tool uses export-openapi response to detect:
    Response `info.title` is the module name; non-existent moduleId silently falls back to project name.
    So first get baseline title with a definitely non-existent ID, then compare each,
    different titles indicate real modules.

    Read-only detection, doesn't modify any data. Don't scan too large a range.

    Args:
        start / end: moduleId range to scan (inclusive)
        concurrency: Concurrent requests, default 5
    """
    project_id = _resolve_project(project)
    if not project_id:
        return _err("Project not specified: pass project parameter or configure APIFOX_PROJECT_ID")
    if end < start or end - start > 500:
        return _err("Invalid or too large range (max 500 IDs)")

    path = f"/v1/projects/{project_id}/export-openapi"

    def _body(mid: Optional[int]) -> dict:
        b: dict = {"scope": {"type": "ALL"}, "oasVersion": "2.0", "exportFormat": "JSON"}
        if mid is not None:
            b["moduleId"] = mid
        return b

    async def _title(mid: Optional[int]) -> tuple[Optional[str], int]:
        payload, err, _ = await _request("POST", path, body=_body(mid))
        if err or not isinstance(payload, dict):
            return None, 0
        return (payload.get("info") or {}).get("title"), len(payload.get("paths") or {})

    baseline, _ = await _title(999_999_999)      # Invalid ID fallback title (usually = project name)
    default_title, default_paths = await _title(None)  # Default module

    sem = asyncio.Semaphore(max(1, min(concurrency, 10)))

    async def _one(mid: int):
        async with sem:
            title, paths = await _title(mid)
            return mid, title, paths

    results = await asyncio.gather(*[_one(m) for m in range(start, end + 1)])
    modules = [{"moduleId": m, "name": t, "endpointCount": n}
               for m, t, n in results
               if t and t != baseline]

    return _ok({
        "projectId": project_id,
        "projectName": baseline,
        "defaultModule": {"name": default_title, "endpointCount": default_paths},
        "scanned": f"{start}-{end}",
        "modules": modules,
        "moduleMapSnippet": json.dumps({m["name"]: m["moduleId"] for m in modules},
                                       ensure_ascii=False) if modules else None,
        "note": "Empty modules means no real modules in this range; try different range, "
                "or get moduleId directly from Apifox URL's ?module= parameter.",
    })


@mcp.tool()
async def validate_openapi(spec_file: str = "", spec: str = "") -> str:
    """Locally validate OpenAPI/Swagger document. Validate before upload to avoid invalid uploads.

    Returns version, endpoint count, path list, schema count, and obvious structural issues.

    Args:
        spec_file: Local file path (.json / .yaml / .yml)
        spec: Document string (choose either spec_file or spec)
    """
    if spec_file:
        text, err = _read_spec_file(spec_file)
        if err:
            return _err(err)
    elif spec:
        text = spec
    else:
        return _err("Either spec_file or spec must be provided")

    doc, err = _parse_spec(text)
    if err:
        return _err(err)

    paths = doc.get("paths") or {}
    endpoints = []
    for p, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            if method.lower() in ("get", "post", "put", "delete", "patch", "head", "options"):
                endpoints.append({
                    "method": method.upper(),
                    "path": p,
                    "summary": (op or {}).get("summary", "") if isinstance(op, dict) else "",
                    "tags": (op or {}).get("tags", []) if isinstance(op, dict) else [],
                })
    problems = []
    version = doc.get("openapi") or doc.get("swagger")
    if not version:
        problems.append("Missing openapi/swagger version field, Apifox will reject import")
    if not paths:
        problems.append("paths is empty, no endpoints will be created after import")
    schemas = (doc.get("components") or {}).get("schemas") or doc.get("definitions") or {}

    return _ok({
        "version": version,
        "title": (doc.get("info") or {}).get("title"),
        "endpointCount": len(endpoints),
        "schemaCount": len(schemas),
        "tags": sorted({t for e in endpoints for t in e["tags"]}),
        "endpoints": endpoints[:200],
        "problems": problems,
        "sizeBytes": len(text.encode("utf-8")),
    })


@mcp.tool()
async def import_openapi(
    spec_file: str = "",
    spec: str = "",
    spec_url: str = "",
    module: str = "",
    module_id: Optional[int] = None,
    folder: str = "",
    endpoint_folder_id: Optional[int] = None,
    schema_folder_id: Optional[int] = None,
    project: str = "",
    branch_id: Optional[int] = None,
    endpoint_overwrite_behavior: str = "OVERWRITE_EXISTING",
    schema_overwrite_behavior: str = "OVERWRITE_EXISTING",
    update_folder_of_changed_endpoint: bool = False,
    prepend_base_path: bool = False,
    delete_unmatched_resources: bool = False,
    url_username: str = "",
    url_password: str = "",
    dry_run: bool = False,
) -> str:
    """Upload (import) OpenAPI/Swagger document to specified Apifox module and folder.

    Three data sources, choose one:
    - spec_file: Local file path, e.g., doc/openapi/trader.json
    - spec: Document string (JSON / YAML)
    - spec_url: Remote URL, e.g., http://localhost:8080/v3/api-docs
      If URL is internal (localhost, 10.x, 172.16-31.x, 192.168.x),
      auto-fetches locally then uploads as string, since Apifox cloud can't reach internal network.

    Target location (module/folder support names, resolved via APIFOX_MODULE_MAP / APIFOX_FOLDER_MAP):
    - module / module_id: Target module, defaults to main module if not provided
    - folder / endpoint_folder_id: Endpoint folder, defaults to root if not provided
    - schema_folder_id: Schema folder
    - branch_id: Target branch, defaults to main branch if not provided

    Args:
        endpoint_overwrite_behavior: Endpoint conflict strategy OVERWRITE_EXISTING(overwrite) /
            AUTO_MERGE(auto merge) / KEEP_EXISTING(keep existing) / CREATE_NEW(create new)
        schema_overwrite_behavior: Schema conflict strategy, same options
        update_folder_of_changed_endpoint: Whether to update folder when matching existing endpoint
        prepend_base_path: Whether to prepend basePath to each endpoint path, recommend false
        delete_unmatched_resources: DANGEROUS. true deletes endpoints/schemas not in this document
        url_username / url_password: Basic Auth for spec_url if needed
        dry_run: true only validates locally and echoes parameters without calling Apifox
    """
    project_id = _resolve_project(project)
    if not project_id:
        return _err("Project not specified: pass project parameter or configure APIFOX_PROJECT_ID")

    if endpoint_overwrite_behavior not in OVERWRITE_CHOICES:
        return _err(f"Invalid endpoint_overwrite_behavior, options: {list(OVERWRITE_CHOICES)}")
    if schema_overwrite_behavior not in OVERWRITE_CHOICES:
        return _err(f"Invalid schema_overwrite_behavior, options: {list(OVERWRITE_CHOICES)}")

    mid, err = _resolve_id(module, module_id, MODULE_MAP)
    if err:
        return _err(err)
    fid, err = _resolve_id(folder, endpoint_folder_id, FOLDER_MAP)
    if err:
        return _err(err)

    # ---- Build input
    fetched_from = None
    if spec_file:
        text, err = _read_spec_file(spec_file)
        if err:
            return _err(err)
        input_payload: Any = text
    elif spec:
        input_payload = spec
    elif spec_url:
        if _is_internal_url(spec_url):
            try:
                async with httpx.AsyncClient(timeout=TIMEOUT, verify=False) as client:
                    r = await client.get(spec_url)
                    r.raise_for_status()
                    input_payload = r.text
                fetched_from = f"Locally fetched internal URL {spec_url}"
            except Exception as exc:
                return _err(f"Failed to fetch {spec_url} locally: {exc}")
        else:
            input_payload = {"url": spec_url}
            if url_username and url_password:
                input_payload["basicAuth"] = {"username": url_username, "password": url_password}
    else:
        return _err("One of spec_file / spec / spec_url must be provided")

    # Validate string sources locally to avoid pushing garbage
    preview = None
    if isinstance(input_payload, str):
        doc, perr = _parse_spec(input_payload)
        if perr:
            return _err(f"Document validation failed, upload aborted: {perr}")
        preview = {
            "version": doc.get("openapi") or doc.get("swagger"),
            "title": (doc.get("info") or {}).get("title"),
            "pathCount": len(doc.get("paths") or {}),
        }

    options: dict = {
        "endpointOverwriteBehavior": endpoint_overwrite_behavior,
        "schemaOverwriteBehavior": schema_overwrite_behavior,
        "updateFolderOfChangedEndpoint": update_folder_of_changed_endpoint,
        "prependBasePath": prepend_base_path,
        "deleteUnmatchedResources": delete_unmatched_resources,
    }
    if mid is not None:
        options["moduleId"] = mid
    if fid is not None:
        options["targetEndpointFolderId"] = fid
    if schema_folder_id is not None:
        options["targetSchemaFolderId"] = int(schema_folder_id)
    if branch_id is not None:
        options["targetBranchId"] = int(branch_id)

    target = {"projectId": project_id, "options": options, "specPreview": preview,
              "fetchedFrom": fetched_from}
    if dry_run:
        return _ok({"dryRun": True, "willSend": target})

    payload, err, status = await _request(
        "POST", f"/v1/projects/{project_id}/import-openapi",
        body={"input": input_payload, "options": options},
    )
    if err:
        return _err(err, target=target, httpStatus=status)

    data = (payload or {}).get("data") or {}
    errors = data.get("errors") or []
    counters = _extract_counters(data)
    # Only return non-zero counts for cleaner output
    changed = {k: v for k, v in counters.items() if v}
    return json.dumps({
        "ok": not errors,
        "target": target,
        "counters": changed or "All zero (possibly empty document or all ignored)",
        "errors": errors,
        "hint": "Error code 403 usually means 'another user is importing', retry shortly" if any(
            str(e.get("code")) == "403" for e in errors) else None,
    }, ensure_ascii=False, indent=2)


@mcp.tool()
async def import_postman(
    collection_file: str = "",
    collection: str = "",
    module: str = "",
    module_id: Optional[int] = None,
    folder: str = "",
    endpoint_folder_id: Optional[int] = None,
    project: str = "",
    endpoint_overwrite_behavior: str = "OVERWRITE_EXISTING",
    dry_run: bool = False,
) -> str:
    """Import Postman Collection v2 format data to Apifox specified module/folder.

    Args:
        collection_file: Local Postman export file path
        collection: Postman Collection JSON string (choose either collection_file or collection)
        module / module_id: Target module
        folder / endpoint_folder_id: Target endpoint folder
        endpoint_overwrite_behavior: Conflict strategy, same as import_openapi
        dry_run: Only echo parameters without actual upload
    """
    project_id = _resolve_project(project)
    if not project_id:
        return _err("Project not specified: pass project parameter or configure APIFOX_PROJECT_ID")
    if endpoint_overwrite_behavior not in OVERWRITE_CHOICES:
        return _err(f"Invalid endpoint_overwrite_behavior, options: {list(OVERWRITE_CHOICES)}")

    if collection_file:
        text, err = _read_spec_file(collection_file)
        if err:
            return _err(err)
    elif collection:
        text = collection
    else:
        return _err("Either collection_file or collection must be provided")

    try:
        json.loads(text)
    except json.JSONDecodeError as exc:
        return _err(f"Postman Collection must be valid JSON: {exc}")

    mid, err = _resolve_id(module, module_id, MODULE_MAP)
    if err:
        return _err(err)
    fid, err = _resolve_id(folder, endpoint_folder_id, FOLDER_MAP)
    if err:
        return _err(err)

    options: dict = {"endpointOverwriteBehavior": endpoint_overwrite_behavior}
    if mid is not None:
        options["moduleId"] = mid
    if fid is not None:
        options["targetEndpointFolderId"] = fid

    if dry_run:
        return _ok({"dryRun": True, "willSend": {"projectId": project_id, "options": options}})

    payload, err, status = await _request(
        "POST", f"/v1/projects/{project_id}/import-postman",
        body={"input": text, "options": options},
    )
    if err:
        return _err(err, httpStatus=status)
    return _ok({"projectId": project_id, "options": options, "data": (payload or {}).get("data")})


@mcp.tool()
async def export_openapi(
    project: str = "",
    module: str = "",
    module_id: Optional[int] = None,
    scope_type: str = "ALL",
    folder_ids: str = "",
    endpoint_ids: str = "",
    tags: str = "",
    excluded_tags: str = "",
    oas_version: str = "3.1",
    export_format: str = "JSON",
    branch_id: Optional[int] = None,
    include_apifox_extensions: bool = False,
    add_folders_to_tags: bool = True,
    save_to: str = "",
    summary_only: bool = True,
) -> str:
    """Export OpenAPI document from Apifox, filterable by module/folder/tags/endpoints.

    Typical usage: Export current online document for comparison before upload,
    or export to local file for code generation.

    Args:
        scope_type: ALL / SELECTED_ENDPOINTS / SELECTED_FOLDERS / SELECTED_TAGS
        folder_ids: Comma-separated folder IDs, required when scope_type=SELECTED_FOLDERS
        endpoint_ids: Comma-separated endpoint IDs, required when scope_type=SELECTED_ENDPOINTS
        tags: Comma-separated tags, required when scope_type=SELECTED_TAGS
        excluded_tags: Comma-separated tags to exclude
        oas_version: 3.1 / 3.0 / 2.0
        export_format: JSON / YAML
        save_to: If provided, writes complete document to this local path
        summary_only: true returns only endpoint list summary (saves tokens); false returns full document
    """
    project_id = _resolve_project(project)
    if not project_id:
        return _err("Project not specified: pass project parameter or configure APIFOX_PROJECT_ID")

    def _nums(raw: str) -> list[int]:
        return [int(x) for x in re.split(r"[,\s]+", raw.strip()) if x.strip().isdigit()]

    def _strs(raw: str) -> list[str]:
        return [x for x in re.split(r"[,\s]+", raw.strip()) if x]

    scope: dict = {"type": scope_type}
    if scope_type == "SELECTED_FOLDERS":
        ids = _nums(folder_ids)
        if not ids:
            return _err("scope_type=SELECTED_FOLDERS requires folder_ids")
        scope["selectedFolderIds"] = ids
    elif scope_type == "SELECTED_ENDPOINTS":
        ids = _nums(endpoint_ids)
        if not ids:
            return _err("scope_type=SELECTED_ENDPOINTS requires endpoint_ids")
        scope["selectedEndpointIds"] = ids
    elif scope_type == "SELECTED_TAGS":
        ts = _strs(tags)
        if not ts:
            return _err("scope_type=SELECTED_TAGS requires tags")
        scope["selectedTags"] = ts
    elif scope_type != "ALL":
        return _err("scope_type options: ALL / SELECTED_ENDPOINTS / SELECTED_FOLDERS / SELECTED_TAGS")
    if excluded_tags:
        scope["excludedByTags"] = _strs(excluded_tags)

    mid, err = _resolve_id(module, module_id, MODULE_MAP)
    if err:
        return _err(err)

    body: dict = {
        "scope": scope,
        "options": {
            "includeApifoxExtensionProperties": include_apifox_extensions,
            "addFoldersToTags": add_folders_to_tags,
        },
        "oasVersion": oas_version,
        "exportFormat": export_format,
    }
    if mid is not None:
        body["moduleId"] = mid
    if branch_id is not None:
        body["branchId"] = int(branch_id)

    payload, err, status = await _request(
        "POST", f"/v1/projects/{project_id}/export-openapi", body=body)
    if err:
        return _err(err, httpStatus=status)

    saved = None
    if save_to:
        try:
            p = Path(save_to).expanduser()
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(payload, str):
                p.write_text(payload, encoding="utf-8")
            else:
                p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            saved = str(p)
        except Exception as exc:
            return _err(f"Failed to write to {save_to}: {exc}")

    if not summary_only:
        return json.dumps({"ok": True, "savedTo": saved, "document": payload},
                          ensure_ascii=False, indent=2)

    doc = payload if isinstance(payload, dict) else {}
    endpoints = []
    for path_, item in (doc.get("paths") or {}).items():
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            if method.lower() in ("get", "post", "put", "delete", "patch"):
                op = op or {}
                endpoints.append(f"{method.upper()} {path_}  {op.get('summary', '')}".rstrip())
    return _ok({
        "savedTo": saved,
        "projectId": project_id,
        "moduleId": mid,
        "title": (doc.get("info") or {}).get("title"),
        "endpointCount": len(endpoints),
        "tags": [t.get("name") for t in (doc.get("tags") or []) if isinstance(t, dict)],
        "endpoints": endpoints[:300],
        "note": "summary_only=true, full document not returned; set summary_only=false or use save_to for full file",
    })


@mcp.tool()
async def apifox_api_request(method: str, path: str, params: str = "", body: str = "") -> str:
    """General escape hatch: directly call any Apifox Open API.

    Auto-adds Authorization, X-Apifox-Api-Version, locale.
    Use for APIs not wrapped by this service or newly added by Apifox.

    Args:
        method: GET / POST / PUT / DELETE
        path: Path starting with /, e.g., /v1/projects/123456/import-openapi
        params: Query parameters, JSON string
        body: Request body, JSON string
    """
    try:
        q = json.loads(params) if params else None
        b = json.loads(body) if body else None
    except json.JSONDecodeError as exc:
        return _err(f"params/body is not valid JSON: {exc}")
    payload, err, status = await _request(method, path, params=q, body=b)
    if err:
        return _err(err, httpStatus=status)
    return json.dumps({"ok": True, "httpStatus": status, "data": payload},
                      ensure_ascii=False, indent=2)


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
