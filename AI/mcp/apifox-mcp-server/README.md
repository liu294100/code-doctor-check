# Apifox MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)

MCP (Model Context Protocol) servers for [Apifox](https://apifox.com/) API management platform. Enables AI assistants to interact with Apifox for API documentation management.

## Features

This repository contains two MCP servers:

### 1. Apifox CLI MCP (`apifox_cli_mcp`)

Based on the `apifox-cli` command-line tool, providing:

- **Authentication**: Check login status, view account info
- **Project Management**: List projects, get project details
- **Endpoint Management**: CRUD operations for API endpoints
- **Folder Management**: Create and list folders
- **Schema Management**: List data models
- **Import/Export**: Import OpenAPI/Swagger/Postman, export to various formats
- **CLI Schema Validation**: Validate JSON files before operations

### 2. Apifox API MCP (`apifox_api_mcp`)

Based on [Apifox Open API](https://apifox-openapi.apifox.cn/), adding **write capabilities**:

- **Import OpenAPI/Swagger**: Upload to specific module/folder/branch
- **Import Postman Collection**: Support Postman v2 format
- **Export OpenAPI**: Filter by module/folder/tags
- **Auto-fetch Internal URLs**: Automatically fetch and upload documents from localhost/internal networks
- **Document Validation**: Validate before upload to prevent invalid data

## Installation

### Prerequisites

- Python 3.10+
- For CLI MCP: Node.js and `apifox-cli` installed globally

### Install from PyPI

```bash
pip install apifox-mcp-server
```

### Install from Source

```bash
git clone https://github.com/liu294100/code-doctor-skills.git
cd AI/mcp/apifox-mcp-server/
pip install -e .
```

### CLI MCP Prerequisites

```bash
# Install apifox-cli globally
npm install -g apifox-cli@latest

# Login to Apifox
npx apifox-cli auth login --api-base-url <YOUR_API_BASE_URL> --with-token <TOKEN>

# (Optional) Install AI Skill
npx apifox-cli skill install
```

## Configuration

### Environment Variables

#### CLI MCP

| Variable | Required | Description |
|----------|----------|-------------|
| `APIFOX_PROJECT_ID` | Recommended | Default project ID |
| `APIFOX_CLI_CMD` | No | CLI command prefix, default `apifox` |
| `APIFOX_CLI_TIMEOUT` | No | Command timeout in seconds, default `120` |

#### API MCP

| Variable | Required | Description |
|----------|----------|-------------|
| `APIFOX_ACCESS_TOKEN` | Yes | API access token (Apifox avatar → Account Settings → API Access Token) |
| `APIFOX_PROJECT_ID` | Recommended | Default project ID |
| `APIFOX_API_BASE_URL` | No | API base URL, default `https://api.apifox.com` |
| `APIFOX_MODULE_MAP` | No | Module name to ID mapping, JSON format `{"ModuleName": 123}` |
| `APIFOX_FOLDER_MAP` | No | Folder name to ID mapping, JSON format `{"FolderName": 456}` |
| `APIFOX_PROJECT_MAP` | No | Project alias to ID mapping, JSON format `{"alias": "789"}` |
| `APIFOX_API_VERSION` | No | API version, default `2024-03-28` |
| `APIFOX_AUTH_SCHEME` | No | Auth scheme: `auto` (default) / `bearer` / `raw` |
| `APIFOX_LOCALE` | No | Locale, default `en-US` |
| `APIFOX_TIMEOUT` | No | Request timeout in seconds, default `120` |

### MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop, Kiro CLI):

#### CLI MCP

```json
{
  "mcpServers": {
    "apifox-cli": {
      "command": "python",
      "args": ["-m", "apifox_cli_mcp.server"],
      "env": {
				"APIFOX_CLI_CMD": "yourproject",
				"APIFOX_PROJECT_ID": "xxx",
				 "NO_PROXY": "*",
				"HTTP_PROXY": "",
				"HTTPS_PROXY": "",
				"no_proxy": "*",
				"http_proxy": "",
				"https_proxy": ""
			 },
        "disabled": false,
			"autoApprove": [
				"auth_status", "auth_whoami", "project_list", "project_get",
				"endpoint_list", "endpoint_get", "folder_list", "schema_list",
				"export_openapi", "export_html", "cli_schema_get", "cli_schema_validate",
				"run_cli"
			]
    }
  }
}
```

#### API MCP

```json
{
  "mcpServers": {
    "apifox-api": {
      "command": "python",
      "args": ["-m", "apifox_api_mcp.server"],
      "env": {
        "APIFOX_ACCESS_TOKEN": "your-access-token",
        "APIFOX_PROJECT_ID": "your-project-id",
        "APIFOX_MODULE_MAP": "{\"A\": 101, \"B\": 102}",
        "APIFOX_FOLDER_MAP": "{\"A1\": 8901}"
      }
    }
  }
}
```

## Usage Examples

### With AI Assistant

```
# List all projects
"List all my Apifox projects"

# Import OpenAPI document
"Import doc/openapi/trader.json to Apifox Trading module with auto-merge"

# Export API documentation
"Export OpenAPI document from Trading module to doc/export.json"

# Validate before upload
"Validate the OpenAPI spec at doc/api.yaml before uploading"

# Discover modules
"Find all modules in project 345091"
```

### CLI MCP Tools

| Tool | Description |
|------|-------------|
| `auth_status` | Check login status |
| `auth_whoami` | Current user info |
| `project_list` | List all projects |
| `project_get` | Get project details |
| `endpoint_list` | List endpoints |
| `endpoint_get` | Get endpoint details |
| `endpoint_create` | Create endpoint |
| `endpoint_update` | Update endpoint |
| `endpoint_delete` | Delete endpoint |
| `folder_list` | List folders |
| `folder_create` | Create folder |
| `schema_list` | List data models |
| `import_openapi` | Import OpenAPI document |
| `import_file` | Import various formats |
| `export_openapi` | Export OpenAPI document |
| `export_html` | Export HTML documentation |
| `cli_schema_get` | Get CLI schema definition |
| `cli_schema_validate` | Validate JSON against schema |
| `skill_install` | Install AI Skill |
| `run_cli` | Execute any CLI command |

### API MCP Tools

| Tool | Description |
|------|-------------|
| `describe_config` | View current configuration |
| `check_access` | Verify token access |
| `discover_modules` | Discover project modules |
| `validate_openapi` | Validate OpenAPI document |
| `import_openapi` | Import OpenAPI/Swagger |
| `import_postman` | Import Postman Collection |
| `export_openapi` | Export OpenAPI document |
| `apifox_api_request` | Direct API call (escape hatch) |

## Finding moduleId / folderId

Open Apifox Web, navigate to target module/folder, check browser URL:

```
https://app.apifox.com/project/1234567/apis/folder-8901?module=234
                              ^projectId          ^folderId      ^moduleId
```

## Self-Hosted Deployment

For self-hosted Apifox instances:

1. Set `APIFOX_API_BASE_URL` to your instance URL
2. Use `Bearer <token>` format for Authorization (auto mode handles this)
3. Ensure your token has project maintainer permissions

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Links

- [Apifox](https://apifox.com/)
- [Apifox Open API Documentation](https://apifox-openapi.apifox.cn/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [apifox-cli Documentation](https://docs.apifox.com/)
