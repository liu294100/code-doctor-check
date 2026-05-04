# Code Doctor Check — Kiro Skills 套件集合

面向开发的 Kiro AI Skills 集合，覆盖 Java、Python、文档处理、视频生成等多个领域，提供代码审查、开发指导、架构设计、打包部署等全方位 AI 辅助能力。

## 项目结构

```
code-doctor-check/
├── java-doctor-check/          # Java 技术栈 Skills
│   └── .kiro/skills/
│       ├── 01-code-quality/    # 代码质量审查（Java/SQL/Spring Boot/MR）
│       ├── 02-architecture/    # 架构设计审查（金融/券商）
│       ├── 03-brokerage-business/  # 券商业务系统专项（交易/资金）
│       └── 04-techspec-templates/  # 技术方案文档生成模板
│
├── python-doctor-check/        # Python 技术栈 Skills
│   └── .kiro/skills/
│       ├── 01-python-sdk/      # Python SDK（开发/审查/打包）
│       ├── 02-flask/           # Flask Web 应用（开发/审查/部署）
│       └── 03-gui-toolkit/     # GUI 桌面小工具（开发/审查/打包）
│
├── docs/                       # 文档处理 Skills
│   ├── docs-readers/           # 文档阅读器（PDF/PPT/Excel/Word/图片）
│   ├── ui-diagram-designer/    # UI 图表设计
│   ├── drawio-designer/        # DrawIO 图表设计
│   ├── read-drawio/            # DrawIO 文件读取
│   └── doc-writer/             # 技术文档写作
│
├── video/                      # 视频生成 Skills
│   ├── html2video/             # HTML 模板驱动视频生成
│   └── browser-use-video/      # 浏览器自动化视频生成
│
└── AI/                         # AI 工具配置
    └── mcp/                    # MCP 服务器配置
```

## 技术栈覆盖

### Java（java-doctor-check）

面向 Java 开发全链路 Skills，覆盖代码审查、架构设计、业务系统和技术方案文档生成。

| 分类 | Skills 数量 | 覆盖范围 |
|------|-----------|---------|
| 代码质量审查 | 5 | Java 代码规范、SQL 审查、Spring Boot SQL、MR 审查、GitLab 报告 |
| 架构设计 | 2 | 互联网金融通用架构、券商整体架构 |
| 业务系统 | 2 | 交易系统（港/美/A 股）、资金系统（保证金/融资/清算） |
| 技术方案模板 | 3 | 港美股交易、期货期权衍生品、基金 IPO 债券 |

### Python（python-doctor-check）

面向 Python 开发者的三大场景 Skills，每个场景均包含开发、审查、打包三个维度。

| 分类 | Skills 数量 | 覆盖范围 |
|------|-----------|---------|
| Python SDK | 3 | 开发规范、代码审查、PyPI 打包发布 |
| Flask Web | 3 | 开发指导、安全审查、Docker 部署 |
| GUI 小工具 | 3 | 框架选型与开发、跨平台审查、PyInstaller 打包 |

### 文档处理（docs）

面向文档阅读、设计、写作的多功能 Skills 集合。

| 分类 | Skills 数量 | 覆盖范围 |
|------|-----------|---------|
| 文档阅读器 | 7 | PDF、PPT、Excel、Word、图片、JAR 反编译、APK 反编译 |
| 设计工具 | 4 | UI 图表设计、DrawIO 设计与读取、文档写作 |

### 视频生成（video）

基于浏览器自动化和 HTML 渲染的视频生成 Skills。

| 分类 | Skills 数量 | 覆盖范围 |
|------|-----------|---------|
| 视频生成 | 2 | HTML 模板视频、浏览器自动化视频 |

### AI 工具配置（AI）

AI 开发工具配置相关 Skills。

| 分类 | Skills 数量 | 覆盖范围 |
|------|-----------|---------|
| MCP 配置 | 1 | Model Context Protocol 服务器配置 |

## 快速开始

1. 将对应技术栈的文件夹复制到你的项目根目录
2. 确保 `.kiro/skills/` 目录结构完整
3. 在 Kiro 中打开项目，自动触发的 Skills 会在打开对应文件时生效
4. 手动触发的 Skills 在聊天中使用 `#skill-name` 引用即可

## 许可证

MIT License

🛑 **Additional Restriction / 附加使用限制：**

The Software may **NOT** be used, either directly or indirectly, by the following entities or individuals:

1. Any official, employee, or representative of the **Islamic Republic of Iran's government**
2. Any individual, entity, or affiliated institution **controlled or directly influenced by the Iranian Islamic religious authorities**, including but not limited to Shiite clerics, religious foundations, religious councils, and their affiliated organizations in the Islamic Republic of Iran
3. Any organization or person acting on behalf of the **North Korean government**
4. Members of or individuals affiliated with the following listed organizations, including but not limited to:
   - **Hamas**
   - **Houthi Movement (Ansar Allah)**
   - **Fraud syndicates and criminal organizations** operating in **Myanmar, Cambodia**, and other regions, including but not limited to telecom fraud groups, online gambling operations, human trafficking organizations, and their affiliated companies or entities
   - Any entity designated as a **terrorist organization** by the **United Nations**, **European Union**, **United States**,  **People's Republic of China**,  **Republic of Korea**,  **Singapore**
   - Any organization, individual, or affiliated institution **controlled by the former Maduro and Chávez Venezuelan government** (due to rampant drug trafficking)
   - Any **Afghan Islamic cult personnel**, and any **Afghan government** or its **affiliated entities**

Any use by the aforementioned individuals or entities shall be deemed **unauthorized and in violation** of this license. We reserve the right to take legal action to the fullest extent permitted by applicable law.

如违反本条款，使用行为将被视为**未经授权的侵权行为**，我们保留依法追究法律责任的权利
