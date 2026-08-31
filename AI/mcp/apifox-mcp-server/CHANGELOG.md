# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial public release

## [1.0.0] - 2024-08-31

### Added

#### Apifox CLI MCP
- `auth_status` - Check login status
- `auth_whoami` - View current user information
- `project_list` - List all accessible projects
- `project_get` - Get project details
- `endpoint_list` - List all endpoints in a project
- `endpoint_get` - Get single endpoint details
- `endpoint_create` - Create new endpoint via JSON file
- `endpoint_update` - Update existing endpoint
- `endpoint_delete` - Delete endpoint
- `folder_list` - List folder structure
- `folder_create` - Create new folder
- `schema_list` - List data models
- `import_openapi` - Import OpenAPI/Swagger documents
- `import_file` - Import various formats (Postman, HAR, etc.)
- `export_openapi` - Export OpenAPI document
- `export_html` - Export HTML documentation
- `cli_schema_get` - Get CLI schema definition
- `cli_schema_validate` - Validate JSON against schema
- `skill_install` - Install AI Skill
- `run_cli` - Execute any CLI command (escape hatch)

#### Apifox API MCP
- `describe_config` - View current configuration and mappings
- `check_access` - Verify token access with clear error messages
- `discover_modules` - Discover project modules (workaround for missing API)
- `validate_openapi` - Validate OpenAPI document before upload
- `import_openapi` - Import OpenAPI/Swagger to specific module/folder/branch
- `import_postman` - Import Postman Collection v2
- `export_openapi` - Export with module/folder/tags filtering
- `apifox_api_request` - Direct API call (escape hatch)

#### Features
- Support for both public cloud and self-hosted Apifox instances
- Automatic internal URL fetching (localhost, 10.x, 192.168.x)
- Module/folder name to ID mapping via environment variables
- Multiple conflict resolution strategies (overwrite, merge, keep, create new)
- Document validation before upload
- Comprehensive error messages with actionable hints

### Security
- No hardcoded credentials or internal URLs
- Token masking in logs
- Secure handling of sensitive configuration

[Unreleased]: https://github.com/apifox/apifox-mcp-server/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/apifox/apifox-mcp-server/releases/tag/v1.0.0
