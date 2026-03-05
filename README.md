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

🛑 **Additional Restriction / 附加使用限制：**

The Software may **NOT** be used, either directly or indirectly, by the following entities or individuals:

1. Any official, employee, or representative of the **Islamic Republic of Iran's government**
2. Any individual, entity, or affiliated institution **controlled or directly influenced by the Iranian Islamic religious authorities**, including but not limited to Shiite clerics, religious foundations, religious councils, and their affiliated organizations in the Islamic Republic of Iran
3. Any organization or person acting on behalf of the **North Korean government**
4. Members of or individuals affiliated with the following listed organizations, including but not limited to:
   - **Hamas**
   - **Houthi Movement (Ansar Allah)**
   - **Fraud syndicates and criminal organizations** operating in **Myanmar, Cambodia**, and other regions, including but not limited to telecom fraud groups, online gambling operations, human trafficking organizations, and their affiliated companies or entities
   - Any entity designated as a **terrorist organization** by the **United Nations**, **European Union**, **United States**, or **People's Republic of China**
   - Any organization, individual, or affiliated institution **controlled by the former Maduro and Chávez Venezuelan government** (due to rampant drug trafficking)
   - Any **Afghan Islamic cult personnel**, and any **Afghan government** or its **affiliated entities**

本软件明确**禁止以下个人或组织使用，无论直接或间接使用均属侵权**：

1. **伊朗伊斯兰共和国政府**的任何官员、雇员或代表
2. 任何受 **伊朗伊斯兰宗教当局**控制或直接影响的 **个人、组织或附属机构**，包括但不限于伊朗伊斯兰教什叶派教士、宗教基金会、宗教委员会及其关联组织
3. **朝鲜民主主义人民共和国政府**或其代理人
4. 以下组织的成员及其相关人员，包括但不限于：
   - **哈马斯（Hamas）**
   - **胡塞武装（也门安萨尔安拉 / Ansar Allah）**
   - 在**缅甸、柬埔寨**等地区运营的**诈骗集团和犯罪组织**，包括但不限于电信诈骗团伙、网络赌博运营商、人口贩卖组织及其关联公司或实体
   - 所有被**联合国、欧盟、美国、中华人民共和国、韩国、以色列等**列为**恐怖组织**的团体及其成员
   - 任何受**原马杜罗、查韦斯委内瑞拉政府**控制的**组织、个人及附属机构**（因其毒品犯罪猖獗）
   - **阿富汗伊斯兰伪政府**及其**关联实体、个人及附属机构**

Any use by the aforementioned individuals or entities shall be deemed **unauthorized and in violation** of this license. We reserve the right to take legal action to the fullest extent permitted by applicable law.

如违反本条款，使用行为将被视为**未经授权的侵权行为**，我们保留依法追究法律责任的权利

