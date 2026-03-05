# 互联网券商 Java 开发 Kiro Skills 套件

面向互联网券商（参考富途牛牛/moomoo）的 Kiro AI Skills 集合，覆盖代码审查、架构设计、业务系统和技术方案文档生成。

## 目录结构

```
.kiro/skills/
├── 01-code-quality/            # 代码质量审查
│   ├── java-code-review.md     # Java 代码全面审查（自动触发）
│   ├── sql-script-review.md    # SQL 脚本安全与性能审查（自动触发）
│   ├── springboot-sql-review.md # Spring Boot 项目 SQL 审查（自动触发）
│   ├── merge-review.md         # Git 合并/PR 全面审查（手动触发）
│   └── gitlab-mr-report.md    # GitLab MR 审查报告生成（手动触发）
├── 02-architecture/            # 架构设计审查
│   ├── fintech-architecture.md # 互联网金融通用架构（CAP/性能/高可用）
│   └── brokerage-architecture.md # 互联网券商整体架构
├── 03-brokerage-business/      # 券商业务系统专项
│   ├── brokerage-trading.md    # 交易系统（港股/美股/A股/期货/期权）
│   └── brokerage-capital.md    # 资金系统（保证金/融资/多币种/清算）
└── 04-techspec-templates/      # 技术方案文档生成模板
    ├── techspec-hkus-stock.md  # 港美股交易方案模板
    ├── techspec-derivatives.md # 期货/期权/牛熊证/窝轮方案模板
    └── techspec-fund-ipo.md    # 基金/月供股票/IPO/债券方案模板
```

## Skills 说明

### 01 - 代码质量审查

| Skill | 触发方式 | 说明 |
|-------|---------|------|
| java-code-review | 自动（打开 .java 文件） | 代码规范、健壮性、设计原则、高并发、安全、Spring 专项，共 8 大维度审查 |
| sql-script-review | 自动（打开 .sql 文件） | DDL 规范、索引设计、查询性能、SQL 注入、事务锁、数据安全，结合项目建表脚本交叉审查 |
| springboot-sql-review | 自动（打开 Mapper/Repository/DAO） | MyBatis ${}注入检测、N+1 问题、JPA 事务陷阱、连接池配置、索引覆盖分析，结合项目 SQL 脚本交叉审查 |
| merge-review | 手动 `#merge-review #Git Diff` | 合并前全面审查：变动统计、依赖分析、代码/SQL/设计/性能/安全多维度检查，输出综合评分和合并建议 |
| gitlab-mr-report | 手动 `#gitlab-mr-report #Git Diff` | 生成 GitLab MR 标准化审查报告，可直接粘贴到 MR 评论区，含评分/问题清单/修复建议/合并结论 |

### 02 - 架构设计审查

| Skill | 触发方式 | 说明 |
|-------|---------|------|
| fintech-architecture | 手动 `#fintech-architecture` | CAP 选型（CP/AP 场景分析）、极致性能优化、金融级架构、资金安全、风控、合规 |
| brokerage-architecture | 手动 `#brokerage-architecture` | 券商全景架构、行情/交易/清算/账户/风控/合规、多市场技术选型矩阵 |

### 03 - 券商业务系统专项

| Skill | 触发方式 | 说明 |
|-------|---------|------|
| brokerage-trading | 手动 `#brokerage-trading` | 统一委托模型、港股（IPO/牛熊证/窝轮）、美股（PDT/期权/SOR）、北向A股、条件单/智能订单 |
| brokerage-capital | 手动 `#brokerage-capital` | 现金/保证金/融资账户模型、保证金计算引擎、强平机制、多币种、出入金、IPO融资、清算对账 |

### 04 - 技术方案文档生成

| Skill | 触发方式 | 说明 |
|-------|---------|------|
| techspec-hkus-stock | 手动 `#techspec-hkus-stock` | 港美股交易规则库 + 技术方案模板（含港股通北向规则） |
| techspec-derivatives | 手动 `#techspec-derivatives` | 期货/期权/牛熊证/窝轮规则库 + 定价模型 + 技术方案模板 |
| techspec-fund-ipo | 手动 `#techspec-fund-ipo` | 基金申赎/月供股票/IPO认购/债券/暗盘/供股 + 技术方案模板 |

## 使用方式

### 自动触发
`java-code-review` 配置为 `fileMatch` 模式，打开任何 `.java` 文件时自动加载，在聊天中请求审查代码即可。

### 手动引用
其他 Skills 配置为 `manual` 模式，在聊天输入框中使用 `#` 引用对应的 Skill 名称即可激活：

```
# 审查架构设计
输入：#fintech-architecture 帮我审查这个支付系统的架构设计

# 审查交易代码
输入：#brokerage-trading 审查这个委托下单的实现

# 生成技术方案
输入：#techspec-hkus-stock 帮我写一个港股暗盘交易的技术方案

# 组合使用
输入：#brokerage-trading #brokerage-capital 审查这个融资买入的完整链路
```

## 覆盖的产品/市场

| 市场/产品 | 交易 | 资金 | 技术方案模板 |
|-----------|------|------|-------------|
| 港股（正股/ETF） | ✅ | ✅ | ✅ |
| 港股 IPO（现金/融资） | ✅ | ✅ | ✅ |
| 港股暗盘 | ✅ | ✅ | ✅ |
| 牛熊证（CBBC） | ✅ | — | ✅ |
| 窝轮（Warrants） | ✅ | — | ✅ |
| 美股（正股/ETF） | ✅ | ✅ | ✅ |
| 美股期权 | ✅ | ✅ | ✅ |
| 美股碎股 | ✅ | ✅ | ✅ |
| A 股北向（沪深港通） | ✅ | ✅ | ✅ |
| 期货（港/美） | ✅ | ✅ | ✅ |
| 基金（场内/场外） | — | — | ✅ |
| 月供股票 | — | — | ✅ |
| 债券 | — | — | ✅ |
| 保证金融资 | — | ✅ | — |
| 多币种换汇 | — | ✅ | — |
