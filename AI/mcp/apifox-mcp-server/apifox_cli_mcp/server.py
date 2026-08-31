# -*- coding: utf-8 -*-
"""
Apifox CLI MCP Server

MCP server based on apifox-cli command line tool.
Provides API management capabilities through CLI commands.

Prerequisites:
  npm install -g apifox-cli@latest
  npx apifox-cli auth login --api-base-url <YOUR_API_BASE_URL> --with-token <TOKEN>
  npx apifox-cli skill install

Usage: python server.py

Repository: https://github.com/apifox/apifox-mcp-server
"""
import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------- Configuration

DEFAULT_PROJECT_ID = os.environ.get("APIFOX_PROJECT_ID", "")
CLI_CMD = os.environ.get("APIFOX_CLI_CMD", "apifox")
TIMEOUT = int(os.environ.get("APIFOX_CLI_TIMEOUT", "120"))

mcp = FastMCP("apifox-cli")


# ---------------------------------------------------------------- Internal Utilities


async def _run(args: str, *, stdin_data: str = "", timeout: int = 0) -> dict:
    """Execute apifox-cli command and return structured result."""
    cmd = f"{CLI_CMD} {args}"
    t = timeout or TIMEOUT
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdin=asyncio.subprocess.PIPE if stdin_data else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=stdin_data.encode() if stdin_data else None),
            timeout=t,
        )
        out = stdout.decode("utf-8", errors="replace").strip()
        err = stderr.decode("utf-8", errors="replace").strip()
        # Try to parse JSON output
        data = None
        if out:
            try:
                data = json.loads(out)
            except json.JSONDecodeError:
                pass
        return {
            "ok": proc.returncode == 0,
            "exitCode": proc.returncode,
            "stdout": out if not data else None,
            "data": data,
            "stderr": err if err else None,
            "command": cmd,
        }
    except asyncio.TimeoutError:
        return {"ok": False, "error": f"Command timeout ({t}s)", "command": cmd}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "command": cmd}


def _project_flag(project: str = "") -> str:
    pid = project or DEFAULT_PROJECT_ID
    if not pid:
        return ""
    return f"--project {pid}"


def _json_result(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- Tools: Authentication


@mcp.tool()
async def auth_status() -> str:
    """Check apifox-cli current login status and account information.

    Prerequisites: Run `npx apifox-cli auth login --api-base-url <url> --with-token <token>` first.
    """
    return _json_result(await _run("auth status"))


@mcp.tool()
async def auth_whoami() -> str:
    """Display current logged-in user information (username, email, team, etc.)."""
    return _json_result(await _run("auth whoami"))


# ---------------------------------------------------------------- Tools: Project


@mcp.tool()
async def project_list() -> str:
    """List all projects accessible by the current account (returns projectId, name, etc.)."""
    return _json_result(await _run("project list"))


@mcp.tool()
async def project_get(project: str = "") -> str:
    """Get project details (name, description, creation time, etc.).

    Args:
        project: Project ID. If not provided, uses APIFOX_PROJECT_ID environment variable.
    """
    pid = project or DEFAULT_PROJECT_ID
    if not pid:
        return _json_result({"ok": False, "error": "Project ID not specified"})
    return _json_result(await _run(f"project get {pid}"))


# ---------------------------------------------------------------- Tools: Import/Export


@mcp.tool()
async def import_openapi(
    file: str = "",
    spec: str = "",
    project: str = "",
    branch: str = "",
) -> str:
    """Import OpenAPI/Swagger document to Apifox project.

    Supports two input methods:
    - file: Local file path (.json/.yaml/.yml)
    - spec: Document string (will be written to temp file before import)

    Args:
        file: Local OpenAPI file path
        spec: OpenAPI document string (choose either file or spec)
        project: Project ID
        branch: Branch name (optional, defaults to main branch)
    """
    pf = _project_flag(project)
    if not pf:
        return _json_result({"ok": False, "error": "Project ID not specified"})

    if spec and not file:
        # Write to temp file
        tmp = Path(tempfile.mktemp(suffix=".json"))
        tmp.write_text(spec, encoding="utf-8")
        file = str(tmp)

    if not file:
        return _json_result({"ok": False, "error": "Either file or spec must be provided"})

    branch_flag = f"--branch {branch}" if branch else ""
    result = await _run(f"import {pf} --format openapi --file \"{file}\" {branch_flag}")

    # Clean up temp file
    if spec:
        try:
            Path(file).unlink(missing_ok=True)
        except Exception:
            pass

    return _json_result(result)


@mcp.tool()
async def import_file(
    file: str,
    format: str = "openapi",
    project: str = "",
    branch: str = "",
    module_map: str = "",
) -> str:
    """Import file to Apifox, supporting multiple formats.

    Args:
        file: Local file path
        format: Import format (openapi/postman/har/insomnia/jmeter/wsdl/yapi/rap2/apidoc/markdown/jsonschema/apifox)
        project: Project ID
        branch: Branch name (optional)
        module_map: Module mapping, format: "SourceModuleName=TargetModuleID" (optional, only for apifox format)
    """
    pf = _project_flag(project)
    if not pf:
        return _json_result({"ok": False, "error": "Project ID not specified"})

    branch_flag = f"--branch {branch}" if branch else ""
    module_flag = f'--module-map "{module_map}"' if module_map else ""
    return _json_result(await _run(
        f'import {pf} --format {format} --file "{file}" {branch_flag} {module_flag}'
    ))


@mcp.tool()
async def export_openapi(
    output: str = "",
    project: str = "",
    oas_version: str = "3.0",
    scope: str = "all",
    module_id: str = "",
    folder_ids: str = "",
    branch: str = "",
    add_folders_to_tags: bool = True,
) -> str:
    """Export OpenAPI document from Apifox to local file.

    Args:
        output: Output file path (required)
        project: Project ID
        oas_version: OAS version (2.0/3.0/3.1)
        scope: Export scope (all/apis/tags/folders)
        module_id: Module ID (optional)
        folder_ids: Folder IDs, comma-separated (used when scope=folders)
        branch: Branch name (optional)
        add_folders_to_tags: Whether to add folder names to tags
    """
    pf = _project_flag(project)
    if not pf:
        return _json_result({"ok": False, "error": "Project ID not specified"})
    if not output:
        return _json_result({"ok": False, "error": "output path is required"})

    parts = [f"export {pf} --format openapi", f'--output "{output}"',
             f"--oas-version {oas_version}", f"--scope {scope}"]
    if module_id:
        parts.append(f"--module-id {module_id}")
    if folder_ids:
        parts.append(f"--folder-ids {folder_ids}")
    if branch:
        parts.append(f"--branch {branch}")
    if add_folders_to_tags:
        parts.append("--add-folders-to-tags")

    return _json_result(await _run(" ".join(parts)))


@mcp.tool()
async def export_html(
    output: str = "",
    project: str = "",
    branch: str = "",
) -> str:
    """Export HTML format documentation from Apifox.

    Args:
        output: Output file path
        project: Project ID
        branch: Branch name (optional)
    """
    pf = _project_flag(project)
    if not pf:
        return _json_result({"ok": False, "error": "Project ID not specified"})
    if not output:
        return _json_result({"ok": False, "error": "output path is required"})
    branch_flag = f"--branch {branch}" if branch else ""
    return _json_result(await _run(f'export {pf} --format html --output "{output}" {branch_flag}'))


# ---------------------------------------------------------------- Tools: Endpoint Management


@mcp.tool()
async def endpoint_list(
    project: str = "",
    page: int = 1,
    page_size: int = 500,
    branch: str = "",
) -> str:
    """List all endpoints in the project.

    Args:
        project: Project ID
        page: Page number
        page_size: Items per page (max 500)
        branch: Branch name (optional)
    """
    pf = _project_flag(project)
    if not pf:
        return _json_result({"ok": False, "error": "Project ID not specified"})
    branch_flag = f"--branch {branch}" if branch else ""
    return _json_result(await _run(
        f"endpoint list {pf} --page {page} --page-size {page_size} {branch_flag}"
    ))


@mcp.tool()
async def endpoint_get(
    endpoint_id: str,
    project: str = "",
    branch: str = "",
) -> str:
    """Get single endpoint details.

    Args:
        endpoint_id: Endpoint ID
        project: Project ID
        branch: Branch name (optional)
    """
    pf = _project_flag(project)
    if not pf:
        return _json_result({"ok": False, "error": "Project ID not specified"})
    branch_flag = f"--branch {branch}" if branch else ""
    return _json_result(await _run(f"endpoint get {endpoint_id} {pf} {branch_flag}"))


@mcp.tool()
async def endpoint_create(
    file: str,
    project: str = "",
    branch: str = "",
) -> str:
    """Create endpoint via JSON file.

    Use `cli_schema_get schema_name="endpoint-create"` to see JSON structure requirements,
    then use `cli_schema_validate` to validate before creating.

    Args:
        file: Endpoint definition JSON file path
        project: Project ID
        branch: Branch name (optional)
    """
    pf = _project_flag(project)
    if not pf:
        return _json_result({"ok": False, "error": "Project ID not specified"})
    branch_flag = f"--branch {branch}" if branch else ""
    return _json_result(await _run(f'endpoint create {pf} --file "{file}" {branch_flag}'))


@mcp.tool()
async def endpoint_update(
    endpoint_id: str,
    file: str = "",
    status: str = "",
    project: str = "",
    branch: str = "",
) -> str:
    """Update endpoint (via JSON file or status field).

    Args:
        endpoint_id: Endpoint ID
        file: Endpoint definition JSON file path (optional)
        status: Endpoint status, e.g., released/developing/deprecated (optional)
        project: Project ID
        branch: Branch name (optional)
    """
    pf = _project_flag(project)
    if not pf:
        return _json_result({"ok": False, "error": "Project ID not specified"})
    parts = [f"endpoint update {endpoint_id} {pf}"]
    if file:
        parts.append(f'--file "{file}"')
    if status:
        parts.append(f"--status {status}")
    if branch:
        parts.append(f"--branch {branch}")
    return _json_result(await _run(" ".join(parts)))


@mcp.tool()
async def endpoint_delete(
    endpoint_id: str,
    project: str = "",
    branch: str = "",
) -> str:
    """Delete endpoint.

    Args:
        endpoint_id: Endpoint ID
        project: Project ID
        branch: Branch name (optional)
    """
    pf = _project_flag(project)
    if not pf:
        return _json_result({"ok": False, "error": "Project ID not specified"})
    branch_flag = f"--branch {branch}" if branch else ""
    return _json_result(await _run(f"endpoint delete {endpoint_id} {pf} {branch_flag}"))


# ---------------------------------------------------------------- Tools: Folder Management


@mcp.tool()
async def folder_list(
    type: str = "endpoint",
    project: str = "",
    branch: str = "",
) -> str:
    """List folder structure in the project.

    Args:
        type: Folder type (endpoint/schema/test-scenario/response-component/security-scheme/test-suite/test-data)
        project: Project ID
        branch: Branch name (optional)
    """
    pf = _project_flag(project)
    if not pf:
        return _json_result({"ok": False, "error": "Project ID not specified"})
    branch_flag = f"--branch {branch}" if branch else ""
    return _json_result(await _run(f"folder list {pf} --type {type} {branch_flag}"))


@mcp.tool()
async def folder_create(
    name: str,
    type: str = "endpoint",
    project: str = "",
    branch: str = "",
) -> str:
    """Create folder.

    Args:
        name: Folder name
        type: Folder type (endpoint/schema/test-scenario, etc.)
        project: Project ID
        branch: Branch name (optional)
    """
    pf = _project_flag(project)
    if not pf:
        return _json_result({"ok": False, "error": "Project ID not specified"})
    branch_flag = f"--branch {branch}" if branch else ""
    return _json_result(await _run(
        f'folder create {pf} --type {type} --name "{name}" {branch_flag}'
    ))


# ---------------------------------------------------------------- Tools: Schema Management


@mcp.tool()
async def schema_list(project: str = "", branch: str = "") -> str:
    """List data models in the project.

    Args:
        project: Project ID
        branch: Branch name (optional)
    """
    pf = _project_flag(project)
    if not pf:
        return _json_result({"ok": False, "error": "Project ID not specified"})
    branch_flag = f"--branch {branch}" if branch else ""
    return _json_result(await _run(f"schema list {pf} {branch_flag}"))


# ---------------------------------------------------------------- Tools: CLI Schema Validation


@mcp.tool()
async def cli_schema_get(schema_name: str) -> str:
    """Get JSON Schema structure definition required by CLI commands.

    Use this tool before executing write commands like endpoint create / folder create
    to see what the JSON file structure should be.

    Args:
        schema_name: Schema name, e.g., endpoint-create, folder-create, import-auto-import-create
    """
    return _json_result(await _run(f"cli-schema get {schema_name}"))


@mcp.tool()
async def cli_schema_validate(schema_name: str, file: str) -> str:
    """Validate if JSON file conforms to specified CLI Schema.

    Must pass validation before writing.

    Args:
        schema_name: Schema name
        file: JSON file path to validate
    """
    return _json_result(await _run(f'cli-schema validate {schema_name} --file "{file}"'))


# ---------------------------------------------------------------- Tools: Skill


@mcp.tool()
async def skill_install() -> str:
    """Install or update Apifox AI Skill (generates Skill file in current working directory).

    Equivalent to running `npx apifox-cli skill install`.
    """
    return _json_result(await _run("skill install", timeout=180))


# ---------------------------------------------------------------- Tools: General Command


@mcp.tool()
async def run_cli(command: str) -> str:
    """Execute any apifox-cli subcommand directly (escape hatch).

    Use this when other tools don't meet your needs.
    No need to add `apifox` prefix, just write the subcommand directly.

    Examples:
    - "endpoint list --project 345091 --page 1 --page-size 10"
    - "branch list --project 345091"
    - "environment list --project 345091"
    - "mock list --project 345091"

    Args:
        command: apifox-cli subcommand and arguments (without `apifox` prefix)
    """
    return _json_result(await _run(command))


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
