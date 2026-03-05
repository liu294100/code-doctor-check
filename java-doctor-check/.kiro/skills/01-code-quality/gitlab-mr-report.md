---
inclusion: manual
---

# GitLab Merge Request 审查报告生成 Skill

在完成代码审查后，生成可直接粘贴到 GitLab MR 评论区的标准化审查报告。
使用方式：先用 `#merge-review #Git Diff` 完成审查，再用 `#gitlab-mr-report` 生成 GitLab 格式报告。
也可以直接使用：`#gitlab-mr-report #Git Diff` 一步完成审查 + 报告生成。

---

## 报告生成规则

### 1. 先执行完整审查（参考 merge-review 的审查维度）
### 2. 将审查结果转换为以下 GitLab Markdown 格式输出
### 3. 用户可以直接复制报告内容粘贴到 GitLab MR 评论区

---

## 输出模板

审查完成后，严格按照以下模板格式输出报告。根据实际审查结果填充内容，没有问题的分类可以省略。

````markdown
## 🔍 Code Review Report

> **审查人**：AI Code Reviewer
> **审查时间**：YYYY-MM-DD HH:mm
> **审查结论**：✅ Approved / ⚠️ Request Changes / ❌ Rejected

---

### 📊 变动概览

| 指标 | 数值 |
|------|------|
| 变动文件数 | X 个（新增 X / 修改 X / 删除 X） |
| 代码行数 | +XXX / -XXX |
| 影响模块 | module-a, module-b |
| 发现问题 | 🔴 X 严重 · 🟡 X 警告 · 🔵 X 建议 |

<details>
<summary>📁 变动文件清单（点击展开）</summary>

| 状态 | 文件路径 | 变动行数 |
|------|---------|---------|
| ✏️ 修改 | `src/main/java/.../OrderService.java` | +30 / -10 |
| ➕ 新增 | `src/main/java/.../PaymentHandler.java` | +120 |
| ✏️ 修改 | `src/main/resources/mapper/OrderMapper.xml` | +25 / -5 |
| ✏️ 修改 | `src/main/resources/db/V2__alter_order.sql` | +15 |
| ❌ 删除 | `src/main/java/.../OldService.java` | -80 |

</details>

---

### 🔴 严重问题（必须修复）

#### 1. [SQL注入] MyBatis 使用 ${} 拼接用户输入

**文件**：`src/main/resources/mapper/OrderMapper.xml` **L25**

```xml
<!-- 当前代码 -->
<select id="findByName">
  SELECT * FROM t_order WHERE name = '${name}'
</select>
```

**风险**：用户输入未参数化，存在 SQL 注入漏洞，攻击者可获取或篡改数据库数据。

**建议修复**：
```xml
<select id="findByName">
  SELECT * FROM t_order WHERE name = #{name}
</select>
```

---

#### 2. [事务失效] 同类内部调用导致 @Transactional 不生效

**文件**：`src/main/java/.../OrderService.java` **L45**

```java
// 当前代码
public void createOrder(Order order) {
    this.saveOrder(order);  // 内部调用，事务不生效
}

@Transactional(rollbackFor = Exception.class)
public void saveOrder(Order order) { ... }
```

**风险**：saveOrder 的事务注解不会生效，异常时数据不会回滚，可能导致数据不一致。

**建议修复**：
```java
// 方案1：将事务注解移到外层方法
@Transactional(rollbackFor = Exception.class)
public void createOrder(Order order) {
    this.saveOrder(order);
}

// 方案2：注入自身代理
@Autowired @Lazy
private OrderService self;
public void createOrder(Order order) {
    self.saveOrder(order);  // 通过代理调用，事务生效
}
```

---

### 🟡 警告问题（建议修复）

#### 3. [N+1查询] 循环中查询数据库

**文件**：`src/main/java/.../OrderService.java` **L60-L65**

```java
// 当前代码
for (Order order : orders) {
    User user = userMapper.findById(order.getUserId());
    order.setUserName(user.getName());
}
```

**影响**：100 条订单产生 100 次 DB 查询，接口 RT 随数据量线性增长。

**建议修复**：
```java
List<Long> userIds = orders.stream()
    .map(Order::getUserId).distinct().collect(toList());
Map<Long, User> userMap = userMapper.findByIds(userIds).stream()
    .collect(toMap(User::getId, Function.identity()));
orders.forEach(o -> o.setUserName(
    Optional.ofNullable(userMap.get(o.getUserId()))
        .map(User::getName).orElse("")));
```

---

#### 4. [缺少索引] 查询字段无索引覆盖

**文件**：`src/main/resources/mapper/OrderMapper.xml` **L40**

```sql
SELECT * FROM t_order WHERE user_id = #{userId} AND status = #{status}
ORDER BY create_time DESC
```

**当前索引**：`idx_user_id(user_id)`
**影响**：status 和 create_time 未被索引覆盖，可能产生 filesort。

**建议补充索引**：
```sql
ALTER TABLE t_order ADD INDEX idx_user_status_time(user_id, status, create_time);
-- 可删除被覆盖的旧索引
ALTER TABLE t_order DROP INDEX idx_user_id;
```

---

#### 5. [设计问题] 大量 if-else 分支，建议使用策略模式

**文件**：`src/main/java/.../PaymentHandler.java` **L30-L55**

```java
if ("ALIPAY".equals(channel)) {
    return handleAlipay(request);
} else if ("WECHAT".equals(channel)) {
    return handleWechat(request);
} else if ("BANK".equals(channel)) {
    return handleBank(request);
} // ... 更多分支
```

**影响**：新增支付渠道需要修改此方法，违反开闭原则，且可读性差。

**建议重构**：
```java
// 策略接口
public interface PaymentStrategy {
    String channel();
    PaymentResult handle(PaymentRequest request);
}

// 策略注册（利用 Spring 自动注入）
@Component
public class PaymentRouter {
    private final Map<String, PaymentStrategy> strategyMap;

    public PaymentRouter(List<PaymentStrategy> strategies) {
        this.strategyMap = strategies.stream()
            .collect(toMap(PaymentStrategy::channel, Function.identity()));
    }

    public PaymentResult route(String channel, PaymentRequest request) {
        return Optional.ofNullable(strategyMap.get(channel))
            .orElseThrow(() -> new BizException("不支持的支付渠道: " + channel))
            .handle(request);
    }
}
```

---

### 🔵 优化建议

#### 6. [代码风格] 可使用 Stream 简化集合操作

**文件**：`src/main/java/.../OrderService.java` **L80-L85**

```java
// 当前
List<String> names = new ArrayList<>();
for (User u : users) {
    if (u.getStatus() == 1) {
        names.add(u.getName());
    }
}

// 建议
List<String> names = users.stream()
    .filter(u -> u.getStatus() == 1)
    .map(User::getName)
    .collect(Collectors.toList());
```

---

#### 7. [注释] 新增 public 方法缺少 Javadoc

**文件**：`src/main/java/.../OrderService.java` **L90**

以下方法缺少 Javadoc 注释：
- `processRefund(Long orderId, BigDecimal amount)`
- `batchUpdateStatus(List<Long> orderIds, Integer status)`

---

### 📈 综合评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 代码规范 | ⭐⭐⭐⭐ 8/10 | 命名规范，少量注释缺失 |
| 代码健壮性 | ⭐⭐⭐ 7/10 | 存在事务失效风险 |
| 设计合理性 | ⭐⭐⭐ 6/10 | if-else 分支建议重构为策略模式 |
| SQL 性能 | ⭐⭐⭐ 7/10 | 缺少联合索引，存在 N+1 |
| 安全性 | ⭐⭐ 5/10 | 存在 SQL 注入风险 |
| 测试覆盖 | ⭐⭐⭐ 6/10 | 新增方法缺少单元测试 |

---

### 📌 修复优先级

| 优先级 | 问题 | 预计耗时 |
|--------|------|---------|
| P0 🔴 | #1 SQL 注入修复 | 5 min |
| P0 🔴 | #2 事务失效修复 | 10 min |
| P1 🟡 | #3 N+1 查询优化 | 15 min |
| P1 🟡 | #4 补充索引 | 5 min |
| P2 🟡 | #5 策略模式重构 | 30 min |
| P3 🔵 | #6 #7 代码风格优化 | 10 min |

---

### 💬 总结

本次 MR 实现了 [功能描述]，整体代码质量良好。主要需要关注 **SQL 注入漏洞**和**事务失效**两个严重问题，修复后可以合并。N+1 查询和索引优化建议在本次一并处理，策略模式重构可以作为后续优化项。

/label ~"code-review" ~"needs-fix"
````

---

## 报告生成规则补充

### 严重程度判定标准

**🔴 严重（必须修复，阻塞合并）**
- SQL 注入漏洞
- 事务失效导致数据不一致风险
- 资金计算使用 float/double
- 无 WHERE 条件的 UPDATE/DELETE
- 敏感信息明文硬编码
- 并发安全问题（共享可变状态无同步）
- 空指针必现场景（外部输入未校验直接使用）
- 资源泄漏（连接/流未关闭）

**🟡 警告（建议修复，不阻塞但强烈建议）**
- N+1 查询问题
- 缺少数据库索引
- 深分页未优化
- 大事务（事务中包含 RPC 调用）
- SELECT * 查询
- 大量 if-else 可用设计模式优化
- 异常被吞（空 catch 块）
- 缺少参数校验

**🔵 建议（可优化，不阻塞）**
- 代码风格可用 Stream/Optional 简化
- 缺少 Javadoc 注释
- 魔法数字未提取为常量
- 命名不够语义化
- 可提取公共方法减少重复
- 缺少单元测试

### 审查结论判定

```
✅ Approved（批准合并）：
  - 无 🔴 严重问题
  - 🟡 警告问题 <= 3 个且不涉及数据安全

⚠️ Request Changes（需要修改）：
  - 存在 🔴 严重问题
  - 或 🟡 警告问题 > 3 个
  - 修复后需要重新审查

❌ Rejected（拒绝合并）：
  - 存在多个 🔴 严重问题
  - 或存在重大架构设计缺陷
  - 建议重新设计方案
```

### 输出注意事项

1. 报告使用 GitLab 支持的 Markdown 语法（表格、折叠块、代码块、emoji）
2. 代码示例使用对应语言的语法高亮（java/xml/sql/yaml）
3. 文件路径使用反引号包裹，便于在 GitLab 中点击跳转
4. 末尾的 `/label` 是 GitLab 快速操作命令，可自动添加标签
5. 问题描述要具体，包含文件名和行号，方便开发者定位
6. 修复建议要给出可直接使用的代码示例，降低修复成本
7. 总结部分简洁明了，一段话说清楚核心问题和合并建议
8. 如果项目使用中文沟通，报告用中文；如果用英文，报告用英文
