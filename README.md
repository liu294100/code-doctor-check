# Code Doctor Check — Kiro Skills 套件集合

面向开发的 Kiro AI Skills 集合，覆盖 Java 和 Python 两大技术栈，提供代码审查、开发指导、架构设计、打包部署等全方位 AI 辅助能力。

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
└── python-doctor-check/        # Python 技术栈 Skills
    └── .kiro/skills/
        ├── 01-python-sdk/      # Python SDK（开发/审查/打包）
        ├── 02-flask/           # Flask Web 应用（开发/审查/部署）
        └── 03-gui-toolkit/     # GUI 桌面小工具（开发/审查/打包）
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

## 快速开始

1. 将对应技术栈的文件夹复制到你的项目根目录
2. 确保 `.kiro/skills/` 目录结构完整
3. 在 Kiro 中打开项目，自动触发的 Skills 会在打开对应文件时生效
4. 手动触发的 Skills 在聊天中使用 `#skill-name` 引用即可

## 许可证

MIT License
