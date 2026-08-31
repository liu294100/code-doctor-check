# Apifox MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)

[Apifox](https://apifox.com/) API 管理平台的 MCP (Model Context Protocol) 服务。让 AI 助手能够与 Apifox 交互，管理 API 文档。

[English](README.md) | 中文

## 功能特性

本仓库包含两个 MCP 服务：

### 1. Apifox CLI MCP (`apifox_cli_mcp`)

基于 `apifox-cli` 命令行工具，提供：

- **认证管理**：查看登录状态、账号信息
- **项目管理**：列出项目、获取项目详情
- **接口管理**：接口的增删改查
- **目录管理**：创建和列出目录
- **数据模型**：列出数据模型
- **导入导出**：导入 OpenAPI/Swagger/Postman，导出为多种格式
- **Schema 校验**：操作前校验 JSON 文件

### 2. Apifox API MCP (`apifox_api_mcp`)

基于 [Apifox 开放 API](https://apifox-openapi.apifox.cn/)，补充**写入能力**：

- **导入 OpenAPI/Swagger**：上传到指定模块/目录/分支
- **导入 Postman Collection**：支持 Postman v2 格式
- **导出 OpenAPI**：按模块/目录/标签筛选
- **自动拉取内网地址**：自动拉取 localhost/内网地址的文档后上传
- **文档校验**：上传前校验，避免无效数据

## 安装

### 前置条件

- Python 3.10+
- CLI MCP 需要：Node.js 和全局安装的 `apifox-cli`

### 从 PyPI 安装

```bash
pip install apifox-mcp-server
```

### 从源码安装

```bash
git clone https://github.com/apifox/apifox-mcp-server.git
cd apifox-mcp-server
pip install -e .
```

### CLI MCP 前置条件

```bash
# 全局安装 apifox-cli
npm install -g apifox-cli@latest

# 登录 Apifox
npx apifox-cli auth login --api-base-url <YOUR_API_BASE_URL> --with-token <TOKEN>

# (可选) 安装 AI Skill
npx apifox-cli skill install
```

## 配置

### 环境变量

#### CLI MCP

| 变量 | 必填 | 说明 |
|------|------|------|
| `APIFOX_PROJECT_ID` | 建议 | 默认项目 ID |
| `APIFOX_CLI_CMD` | 否 | CLI 命令前缀，默认 `apifox` |
| `APIFOX_CLI_TIMEOUT` | 否 | 命令超时秒数，默认 `120` |

#### API MCP

| 变量 | 必填 | 说明 |
|------|------|------|
| `APIFOX_ACCESS_TOKEN` | 是 | API 访问令牌（Apifox 头像 → 账号设置 → API 访问令牌） |
| `APIFOX_PROJECT_ID` | 建议 | 默认项目 ID |
| `APIFOX_API_BASE_URL` | 否 | API 基础 URL，默认 `https://api.apifox.com` |
| `APIFOX_MODULE_MAP` | 否 | 模块名到 ID 映射，JSON 格式 `{"模块名": 123}` |
| `APIFOX_FOLDER_MAP` | 否 | 目录名到 ID 映射，JSON 格式 `{"目录名": 456}` |
| `APIFOX_PROJECT_MAP` | 否 | 项目别名到 ID 映射，JSON 格式 `{"别名": "789"}` |
| `APIFOX_API_VERSION` | 否 | API 版本，默认 `2024-03-28` |
| `APIFOX_AUTH_SCHEME` | 否 | 认证方式：`auto`（默认）/ `bearer` / `raw` |
| `APIFOX_LOCALE` | 否 | 语言，默认 `en-US` |
| `APIFOX_TIMEOUT` | 否 | 请求超时秒数，默认 `120` |

### MCP 客户端配置

添加到你的 MCP 客户端配置（如 Claude Desktop、Kiro CLI）：

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
        "APIFOX_ACCESS_TOKEN": "你的访问令牌",
        "APIFOX_PROJECT_ID": "你的项目ID",
        "APIFOX_MODULE_MAP": "{\"A\": 101, \"B\": 102}",
        "APIFOX_FOLDER_MAP": "{\"A1\": 8901}"
      }
    }
  }
}
```

## 使用示例

### 与 AI 助手对话

```
# 列出所有项目
"列出我所有的 Apifox 项目"

# 导入 OpenAPI 文档
"把 doc/openapi/trader.json 导入到 Apifox 的交易模块，冲突时自动合并"

# 导出 API 文档
"把交易模块的 OpenAPI 文档导出到 doc/export.json"

# 上传前校验
"校验 doc/api.yaml 这个 OpenAPI 文档是否有效"

# 发现模块
"查找项目 345091 中的所有模块"
```

### CLI MCP 工具

| 工具 | 说明 |
|------|------|
| `auth_status` | 查看登录状态 |
| `auth_whoami` | 当前用户信息 |
| `project_list` | 列出所有项目 |
| `project_get` | 获取项目详情 |
| `endpoint_list` | 列出接口 |
| `endpoint_get` | 获取接口详情 |
| `endpoint_create` | 创建接口 |
| `endpoint_update` | 更新接口 |
| `endpoint_delete` | 删除接口 |
| `folder_list` | 列出目录 |
| `folder_create` | 创建目录 |
| `schema_list` | 列出数据模型 |
| `import_openapi` | 导入 OpenAPI 文档 |
| `import_file` | 导入多种格式 |
| `export_openapi` | 导出 OpenAPI 文档 |
| `export_html` | 导出 HTML 文档 |
| `cli_schema_get` | 获取 CLI Schema 定义 |
| `cli_schema_validate` | 校验 JSON 文件 |
| `skill_install` | 安装 AI Skill |
| `run_cli` | 执行任意 CLI 命令 |

### API MCP 工具

| 工具 | 说明 |
|------|------|
| `describe_config` | 查看当前配置 |
| `check_access` | 验证令牌访问权限 |
| `discover_modules` | 发现项目模块 |
| `validate_openapi` | 校验 OpenAPI 文档 |
| `import_openapi` | 导入 OpenAPI/Swagger |
| `import_postman` | 导入 Postman Collection |
| `export_openapi` | 导出 OpenAPI 文档 |
| `apifox_api_request` | 直接调用 API（逃生通道） |

## 查找 moduleId / folderId

打开 Apifox Web 端，切到目标模块/目录，查看浏览器地址栏：

```
https://app.apifox.com/project/1234567/apis/folder-8901?module=234
                              ^projectId          ^folderId      ^moduleId
```

## 私有化部署

对于私有化部署的 Apifox 实例：

1. 设置 `APIFOX_API_BASE_URL` 为你的实例地址
2. Authorization 使用 `Bearer <token>` 格式（auto 模式会自动处理）
3. 确保你的令牌有项目维护者权限

## 贡献

欢迎贡献！请阅读我们的[贡献指南](CONTRIBUTING.md)了解详情。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 相关链接

- [Apifox](https://apifox.com/)
- [Apifox 开放 API 文档](https://apifox-openapi.apifox.cn/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [apifox-cli 文档](https://docs.apifox.com/)
