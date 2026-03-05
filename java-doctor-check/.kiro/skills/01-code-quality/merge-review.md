---
inclusion: manual
---

# Git 合并/PR 全面审查 Skill

在代码合并（Merge/PR/MR）前，对所有变动文件及其依赖文件进行全方位审查。
使用方式：在聊天中输入 `#merge-review #Git Diff` 触发审查。

---

## 审查执行流程

### 第一步：变动文件统计与分析

读取 Git Diff 信息，生成变动统计报告：

```
📊 本次合并变动统计
═══════════════════════════════════════════
提交数量：X 个提交
变动文件：X 个文件（新增 X / 修改 X / 删除 X）
代码行数：+XXX / -XXX（净增 XXX 行）

📁 变动文件清单
───────────────────────────────────────────
[新增] src/main/java/com/example/service/OrderService.java        (+120)
[修改] src/main/java/com/example/controller/OrderController.java  (+30 / -10)
[修改] src/main/resources/mapper/OrderMapper.xml                  (+25 / -5)
[修改] src/main/resources/db/migration/V2__add_order_table.sql    (+40)
[删除] src/main/java/com/example/service/OldOrderService.java     (-80)

📈 变动分布
───────────────────────────────────────────
Java 文件：X 个（Service: X, Controller: X, Mapper: X, Entity: X, Config: X）
SQL 文件：X 个
XML 文件：X 个（MyBatis Mapper）
配置文件：X 个（yml/properties）
测试文件：X 个
其他文件：X 个
```

### 第二步：依赖文件发现

对每个变动文件，自动搜索其依赖和被依赖的文件：

```
分析维度：
1. 上游依赖（当前文件引用了谁）
   - import 的类
   - 注入的 Bean（@Autowired / 构造器注入）
   - MyBatis XML 引用的 Mapper 接口和实体类
   - SQL 涉及的表 → 对应的建表脚本

2. 下游依赖（谁引用了当前文件）
   - 哪些类调用了变动的方法
   - 哪些 Controller 暴露了变动的 Service
   - 哪些测试覆盖了变动的代码

3. 关联文件
   - 同一业务域的其他文件
   - 配置文件中相关的配置项
   - 数据库迁移脚本中相关的表结构
```

### 第三步：逐文件深度审查

对每个变动文件，按文件类型执行对应的审查规则。

### 第四步：跨文件综合审查

从全局视角审查变动的整体合理性。

### 第五步：生成审查报告

汇总所有问题，按优先级排序输出。

---

## 一、Java 文件审查（变动的 .java 文件）

### 1.1 代码规范与整洁度

**变动代码检查**
- 新增代码是否符合项目现有的命名风格（与周围代码一致）
- 新增方法是否有 Javadoc 注释
- 是否引入了未使用的 import
- 是否存在魔法数字/字符串未提取为常量
- 方法长度是否合理（新增方法不超过 50 行）
- 参数数量是否合理（不超过 4 个，否则封装为对象）
- 嵌套层级是否过深（不超过 3 层，使用卫语句提前返回）

**代码优雅性检查**
```java
// ❌ 不优雅：大量 if-else
if (type.equals("A")) {
    handleA();
} else if (type.equals("B")) {
    handleB();
} else if (type.equals("C")) {
    handleC();
}
// ✅ 优雅：策略模式 + Map
Map<String, Handler> handlers = Map.of("A", new AHandler(), "B", new BHandler());
handlers.getOrDefault(type, defaultHandler).handle();

// ❌ 不优雅：手动空判断嵌套
if (user != null) {
    if (user.getAddress() != null) {
        if (user.getAddress().getCity() != null) {
            return user.getAddress().getCity();
        }
    }
}
return "unknown";
// ✅ 优雅：Optional 链式调用
return Optional.ofNullable(user)
    .map(User::getAddress)
    .map(Address::getCity)
    .orElse("unknown");

// ❌ 不优雅：循环中拼接字符串
String result = "";
for (String s : list) { result += s + ","; }
// ✅ 优雅：Stream + Collectors
String result = list.stream().collect(Collectors.joining(","));

// ❌ 不优雅：手动遍历转换
List<String> names = new ArrayList<>();
for (User u : users) { names.add(u.getName()); }
// ✅ 优雅：Stream map
List<String> names = users.stream().map(User::getName).collect(Collectors.toList());
```

### 1.2 设计原则检查

**SOLID 原则逐项检查**

单一职责（SRP）：
- 新增/修改的类是否只负责一个业务领域
- 一个 Service 是否混合了多个不相关的业务逻辑
- Controller 是否包含了业务逻辑（应该只做参数校验和结果封装）

开闭原则（OCP）：
- 新增功能是通过扩展实现还是修改已有代码
- 是否可以通过接口/抽象类/策略模式来支持扩展
- 是否有大量 if-else/switch 可以用多态替代

里氏替换（LSP）：
- 子类是否改变了父类方法的语义
- 子类是否抛出了父类未声明的异常

接口隔离（ISP）：
- 新增的接口是否过于庞大（方法过多）
- 实现类是否被迫实现了不需要的方法

依赖倒置（DIP）：
- 是否依赖了具体实现而非接口
- Service 层是否直接 new 了依赖对象而非注入

**设计模式应用检查**
```
检查变动代码中是否存在以下可以用设计模式优化的场景：

场景 → 建议模式：
  多个 if-else/switch 分支处理不同类型 → 策略模式（Strategy）
  对象创建逻辑复杂，多个可选参数 → 建造者模式（Builder）
  需要在不修改原有代码的情况下增加功能 → 装饰器模式（Decorator）
  多个对象需要响应同一事件 → 观察者模式（Observer）/ Spring Event
  需要将请求沿链传递处理 → 责任链模式（Chain of Responsibility）
  复杂对象的状态流转 → 状态模式（State）
  需要统一接口适配不同实现 → 适配器模式（Adapter）
  创建对象的逻辑需要封装 → 工厂模式（Factory）
  全局唯一实例 → 单例模式（Spring Bean 默认单例）
  需要缓存已创建的对象 → 享元模式（Flyweight）

注意：不要过度设计，简单场景不需要强行套模式。
判断标准：模式引入后代码是否更易读、更易扩展、更易测试。
```

### 1.3 性能检查

```java
// 检查新增代码中的性能问题：

// ❌ 循环中查询数据库（N+1 问题）
for (Order order : orders) {
    User user = userMapper.findById(order.getUserId());  // N 次查询
}
// ✅ 批量查询 + Map 关联
List<Long> userIds = orders.stream().map(Order::getUserId).collect(Collectors.toList());
Map<Long, User> userMap = userMapper.findByIds(userIds).stream()
    .collect(Collectors.toMap(User::getId, Function.identity()));
orders.forEach(o -> o.setUser(userMap.get(o.getUserId())));

// ❌ 循环中调用远程服务
for (Order order : orders) {
    PaymentResult result = paymentClient.query(order.getPaymentId());
}
// ✅ 批量调用或并行调用
List<CompletableFuture<PaymentResult>> futures = orders.stream()
    .map(o -> CompletableFuture.supplyAsync(() -> paymentClient.query(o.getPaymentId())))
    .collect(Collectors.toList());

// ❌ 大集合全量加载到内存
List<Order> allOrders = orderMapper.findAll();  // 可能百万条
// ✅ 流式查询或分页查询
try (Cursor<Order> cursor = orderMapper.findAllWithCursor()) {
    cursor.forEach(this::process);
}

// ❌ 字符串拼接在循环中
String sql = "";
for (...) { sql += "UNION ALL SELECT ..."; }
// ✅ StringBuilder
StringBuilder sb = new StringBuilder();
for (...) { sb.append("UNION ALL SELECT ..."); }

// ❌ 不必要的对象创建
for (int i = 0; i < 10000; i++) {
    SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");  // 每次创建
}
// ✅ 复用或使用线程安全的替代
private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd");

// ❌ 未设置合理的超时
restTemplate.getForObject(url, String.class);  // 无超时，可能永久阻塞
// ✅ 设置超时
restTemplate.setRequestFactory(new SimpleClientHttpRequestFactory() {{
    setConnectTimeout(3000);
    setReadTimeout(5000);
}});
```

### 1.4 健壮性检查

```java
// 检查新增代码的防御性编程：

// 空指针防护
// - 外部输入（请求参数、RPC 返回、DB 查询结果）是否做了空判断
// - Optional 是否正确使用（不要 optional.get() 不判断）
// - 集合操作前是否检查 null/empty

// 异常处理
// - 是否有空 catch 块
// - 异常信息是否包含上下文（关键参数值）
// - 是否区分了业务异常和系统异常
// - 资源是否在 finally 或 try-with-resources 中关闭

// 并发安全
// - 新增的共享变量是否有同步机制
// - Spring Bean（单例）中是否有可变成员变量
// - 是否使用了线程不安全的类（SimpleDateFormat/HashMap 等）

// 边界条件
// - 数值计算是否考虑溢出
// - 金额是否使用 BigDecimal
// - 分页查询是否限制了最大页大小
// - 集合操作是否考虑了空集合和大数据量
```


---

## 二、SQL 文件审查（变动的 .sql 和 MyBatis XML）

### 2.1 SQL 脚本变动审查

**DDL 变更检查**
- 新增表：是否有主键、必备字段（create_time/update_time）、注释、合适的索引
- 修改表：ALTER 是否会锁表？大表是否用 Online DDL 或 pt-osc？
- 删除表/字段：是否确认无代码依赖？是否有备份？
- 索引变更：新增索引是否合理？删除索引是否影响查询？

**DML 变更检查**
- INSERT/UPDATE/DELETE 是否有 WHERE 条件
- 批量操作是否分批执行
- 是否有回滚方案

### 2.2 MyBatis XML 变动审查

**新增/修改的 SQL 语句**
- 是否使用 #{} 而非 ${}（SQL 注入）
- WHERE 条件字段是否有索引（结合建表脚本检查）
- 动态 SQL 是否可能退化为全表查询（所有条件都为 null）
- JOIN 是否合理（不超过 3 张表，关联字段有索引）
- 是否有 N+1 问题（嵌套查询 vs 嵌套结果）
- 分页是否有深分页风险
- IN 列表是否有大小限制
- 是否有 SELECT *

### 2.3 索引交叉审查

```
对变动 SQL 中涉及的每张表：
1. 查找项目中的建表脚本，获取当前索引列表
2. 分析所有查询的 WHERE/JOIN/ORDER BY 字段
3. 检查是否有缺失的索引
4. 检查是否有冗余的索引
5. 检查联合索引字段顺序是否最优
6. 输出索引建议（具体 DDL）
```

---

## 三、配置文件审查（变动的 yml/properties）

```yaml
# 检查项：
# 1. 是否有敏感信息明文（密码、密钥、token）
# 2. 数据源配置是否合理（连接池参数）
# 3. 超时配置是否合理（不要太长也不要太短）
# 4. 日志级别是否合适（生产环境要不要 DEBUG）
# 5. 新增配置是否有默认值（防止缺失配置导致启动失败）
# 6. 配置是否区分环境（dev/test/prod）
```

---

## 四、跨文件综合审查

### 4.1 架构合理性

```
检查变动是否符合分层架构：
  Controller → Service → Repository/Mapper

违规检查：
  ❌ Controller 直接调用 Mapper/DAO
  ❌ Controller 包含业务逻辑
  ❌ Service 层直接操作 HttpServletRequest/Response
  ❌ 循环依赖（A 依赖 B，B 依赖 A）
  ❌ 跨业务域直接调用（OrderService 直接调用 UserMapper）
     → 应该通过 UserService 调用
```

### 4.2 接口设计合理性

```
新增/修改的 API 接口检查：
  - RESTful 规范：资源名用名词复数，HTTP 方法语义正确
  - 统一响应格式：是否使用项目统一的 Result/Response 包装
  - 参数校验：是否使用 @Valid/@Validated
  - 权限控制：是否有 @PreAuthorize 或自定义权限注解
  - 幂等性：POST 接口是否考虑重复提交
  - 版本兼容：接口变更是否向后兼容（不破坏已有调用方）
```

### 4.3 事务一致性

```
检查变动中的事务使用：
  - @Transactional 范围是否合理（不要太大）
  - 事务中是否有 RPC/HTTP 调用（应该移到事务外）
  - 同类内部调用是否导致事务失效
  - rollbackFor 是否正确配置
  - 多表操作是否在同一事务中
  - 分布式场景是否有最终一致性保障
```

### 4.4 安全性

```
检查变动中的安全问题：
  - SQL 注入：所有 SQL 参数是否参数化
  - XSS：用户输入是否有过滤/编码
  - 越权：数据查询是否带用户维度过滤
  - 敏感数据：日志中是否打印了敏感信息
  - 硬编码：是否有密码/密钥/token 硬编码
  - 文件操作：文件路径是否可被用户控制
```

### 4.5 测试覆盖

```
检查变动代码的测试情况：
  - 新增的 public 方法是否有对应的单元测试
  - 核心业务逻辑是否有测试覆盖
  - 边界条件是否有测试（空值、极值、异常）
  - 如果没有测试文件变动，提醒补充测试
```

---

## 五、依赖影响分析

### 5.1 变动影响范围评估

```
对每个变动的文件，分析影响范围：

直接影响：
  - 修改了 Service 方法签名 → 所有调用方需要适配
  - 修改了数据库表结构 → 所有查询该表的 SQL 需要检查
  - 修改了 API 接口 → 所有调用方（前端/其他服务）需要适配
  - 修改了配置项 → 所有引用该配置的代码需要检查

间接影响：
  - 修改了公共工具类 → 所有使用该工具类的模块
  - 修改了基类/接口 → 所有子类/实现类
  - 修改了 MQ 消息格式 → 所有消费者
  - 修改了缓存 Key 规则 → 可能导致缓存失效
```

### 5.2 兼容性检查

```
向后兼容性：
  - API 接口是否删除了字段（破坏性变更）
  - 数据库是否删除了字段（需要先确认无引用）
  - MQ 消息格式是否变更（消费者是否已适配）
  - 配置项是否重命名（旧配置是否兼容）

发布兼容性：
  - 数据库变更是否可以先于代码发布（加字段可以，删字段不行）
  - 是否需要灰度发布（新旧版本并存时是否兼容）
  - 回滚时数据是否兼容（新版本写入的数据旧版本能否处理）
```

---

## 六、审查报告输出格式

### 6.1 变动统计摘要

```
📊 合并审查报告
═══════════════════════════════════════════
分支：feature/xxx → develop
变动文件：X 个 | 代码行数：+XXX / -XXX
影响范围：X 个直接依赖文件 | X 个间接依赖文件
审查发现：🔴 X 个严重 | 🟡 X 个警告 | 🔵 X 个建议
整体评估：✅ 可合并 / ⚠️ 需修复后合并 / ❌ 不建议合并
```

### 6.2 问题清单

对每个问题按以下格式输出：

```
🔴/🟡/🔵 [问题编号] [问题类型]
  文件：src/main/java/com/example/service/OrderService.java
  行号：L45-L60
  问题：循环中查询数据库，存在 N+1 性能问题
  影响：订单量大时接口响应时间线性增长，100 条订单约 100 次 DB 查询
  建议：改为批量查询 + Map 关联
  修复示例：
    List<Long> userIds = orders.stream().map(Order::getUserId).collect(toList());
    Map<Long, User> userMap = userMapper.findByIds(userIds)...;
```

问题类型标签：
```
[SQL注入]    [N+1查询]    [全表扫描]    [缺少索引]
[事务问题]   [空指针风险]  [并发安全]    [资源泄漏]
[设计违规]   [命名不规范]  [代码重复]    [过度复杂]
[性能问题]   [安全风险]    [配置问题]    [兼容性]
[缺少校验]   [缺少注释]    [缺少测试]    [硬编码]
```

### 6.3 综合评估

```
📋 综合评估
═══════════════════════════════════════════

代码质量评分：X/10
  规范性：X/10（命名/格式/注释）
  健壮性：X/10（空判断/异常处理/边界条件）
  优雅度：X/10（设计模式/代码简洁度/可读性）

设计评分：X/10
  架构合理性：X/10（分层/职责划分）
  设计原则：X/10（SOLID/DRY/KISS）
  扩展性：X/10（是否易于扩展新功能）

性能评分：X/10
  SQL 性能：X/10（索引覆盖/查询效率）
  代码性能：X/10（算法/数据结构/IO）
  并发性能：X/10（锁/线程安全/资源竞争）

安全评分：X/10
  注入防护：X/10
  权限控制：X/10
  数据安全：X/10

🔝 优先修复 Top 5
  1. [🔴 严重] ...
  2. [🔴 严重] ...
  3. [🟡 警告] ...
  4. [🟡 警告] ...
  5. [🟡 警告] ...

💡 优化建议
  - 建议补充的索引：ALTER TABLE ... ADD INDEX ...
  - 建议引入的设计模式：...
  - 建议补充的测试：...

📌 合并建议
  ✅ 可合并：无严重问题，建议项可后续优化
  ⚠️ 需修复后合并：存在 X 个严重问题必须修复
  ❌ 不建议合并：存在重大设计缺陷或安全风险
```
