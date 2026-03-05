---
inclusion: fileMatch
fileMatchPattern: "**/*.sql"
---

# SQL 脚本安全与性能审查 Skill

当打开 SQL 脚本文件时自动加载，对 DDL/DML/DQL 语句进行全面的安全性、性能、规范性审查。
同时结合项目中其他 SQL 脚本（建表语句、索引定义）进行交叉审查。

---

## 审查前准备

在审查当前 SQL 文件时，请主动搜索项目中的相关 SQL 文件以获取上下文：
1. 搜索项目中的建表语句（CREATE TABLE），了解表结构和已有索引
2. 搜索项目中的其他 SQL 脚本，了解已有的查询模式
3. 搜索 MyBatis XML 文件中的 SQL，了解应用层的查询方式
4. 结合以上信息进行综合审查

---

## 一、DDL 语句审查（CREATE/ALTER/DROP）

### 1.1 建表规范

**命名规范**
- 表名：小写 + 下划线，业务前缀，如 `t_order`、`t_user_account`
- 字段名：小写 + 下划线，语义清晰，如 `create_time`、`order_status`
- 索引名：`idx_表名_字段名`（普通索引）、`uk_表名_字段名`（唯一索引）
- 主键名：`pk_表名`
- 禁止使用 MySQL 保留字作为表名或字段名
- 禁止使用拼音命名

**字段类型选择**
- 整数：根据范围选择 TINYINT/SMALLINT/INT/BIGINT，不要一律用 BIGINT
- 金额：必须用 DECIMAL(M,N)，禁止 FLOAT/DOUBLE
- 字符串：定长用 CHAR，变长用 VARCHAR，长度按实际需要设定
- 时间：用 DATETIME 或 TIMESTAMP，禁止用字符串存时间
- 布尔：用 TINYINT(1)，0/1 表示
- 枚举/状态：用 TINYINT 或 SMALLINT + 注释说明含义，不要用 ENUM 类型
- IP 地址：用 INT UNSIGNED（INET_ATON/INET_NTOA）或 VARCHAR(45)（兼容 IPv6）
- JSON 数据：MySQL 5.7+ 可用 JSON 类型，但不要滥用

**必备字段**
- 主键：每张表必须有主键，推荐自增 BIGINT 或 Snowflake ID
- create_time：记录创建时间，DEFAULT CURRENT_TIMESTAMP
- update_time：记录更新时间，ON UPDATE CURRENT_TIMESTAMP
- 逻辑删除：is_deleted TINYINT(1) DEFAULT 0（如果使用逻辑删除）
- 乐观锁：version INT DEFAULT 0（如果需要并发控制）

**表属性**
- 引擎：InnoDB（支持事务和行锁）
- 字符集：utf8mb4（支持 emoji 和完整 Unicode）
- 排序规则：utf8mb4_general_ci 或 utf8mb4_unicode_ci
- 注释：表和每个字段都必须有 COMMENT
- ROW_FORMAT：DYNAMIC（支持大字段索引）

### 1.2 索引设计审查

**索引创建规范**
- 单表索引数量不超过 5-6 个（过多影响写入性能）
- 单个索引字段数不超过 5 个
- 索引字段总长度不超过 767 字节（InnoDB 限制）
- 区分度低的字段不要单独建索引（如 gender、status 只有几个值）
- 频繁更新的字段谨慎建索引（每次更新都要维护索引）

**索引类型选择**
- 等值查询：普通 B-Tree 索引
- 范围查询：B-Tree 索引（注意范围条件后的字段无法使用索引）
- 前缀匹配：前缀索引 `INDEX idx_name(name(20))`
- 全文搜索：FULLTEXT 索引或使用 Elasticsearch
- 覆盖索引：查询字段全部在索引中，避免回表

**联合索引设计（最左前缀原则）**
```sql
-- 联合索引 (a, b, c) 可以支持以下查询：
WHERE a = ?                    -- ✅ 使用索引
WHERE a = ? AND b = ?          -- ✅ 使用索引
WHERE a = ? AND b = ? AND c = ? -- ✅ 使用索引
WHERE b = ?                    -- ❌ 不使用索引（缺少最左列）
WHERE a = ? AND c = ?          -- ⚠️ 只使用 a 列索引，c 列不走索引
WHERE a > ? AND b = ?          -- ⚠️ 只使用 a 列索引（范围查询后的列不走索引）

-- 联合索引字段顺序原则：
-- 1. 等值查询的字段放前面
-- 2. 范围查询的字段放后面
-- 3. 区分度高的字段放前面
-- 4. 排序字段考虑放入索引（避免 filesort）
```

**必须有索引的场景**
- WHERE 条件中的高频查询字段
- JOIN 关联字段
- ORDER BY / GROUP BY 字段
- 唯一性约束字段（唯一索引）
- 外键字段（如果使用外键）

**索引失效场景检查**
```sql
-- 以下写法会导致索引失效，必须检查：
WHERE YEAR(create_time) = 2024       -- ❌ 函数操作导致索引失效
WHERE amount + 100 > 500             -- ❌ 表达式计算导致索引失效
WHERE name LIKE '%keyword%'          -- ❌ 左模糊导致索引失效
WHERE status != 1                    -- ⚠️ 不等于可能不走索引
WHERE status IS NULL                 -- ⚠️ 取决于数据分布
WHERE CAST(id AS CHAR) = '123'       -- ❌ 隐式类型转换导致索引失效
WHERE name = 123                     -- ❌ 字符串字段用数字比较，隐式转换

-- 正确写法：
WHERE create_time >= '2024-01-01' AND create_time < '2025-01-01'  -- ✅
WHERE amount > 400                                                 -- ✅
WHERE name LIKE 'keyword%'                                         -- ✅ 右模糊可以用索引
```

### 1.3 ALTER 语句审查

**高风险操作检查**
- ALTER TABLE 大表加字段/加索引：是否会锁表？建议使用 pt-online-schema-change 或 gh-ost
- 修改字段类型：是否兼容现有数据？是否会导致数据截断？
- 删除字段/索引：是否有代码依赖？是否已确认无引用？
- 修改字符集：是否影响已有数据和索引？

**安全操作建议**
```sql
-- 大表加字段（推荐 Online DDL）
ALTER TABLE t_order ADD COLUMN remark VARCHAR(500) DEFAULT '' COMMENT '备注',
  ALGORITHM=INPLACE, LOCK=NONE;

-- 大表加索引（推荐 Online DDL）
ALTER TABLE t_order ADD INDEX idx_create_time(create_time),
  ALGORITHM=INPLACE, LOCK=NONE;

-- 如果 Online DDL 不支持，使用工具：
-- pt-online-schema-change --alter "ADD COLUMN remark VARCHAR(500)" D=db,t=t_order
```

### 1.4 DROP 语句审查

- DROP TABLE：是否有备份？是否确认无业务依赖？建议先 RENAME 观察
- DROP INDEX：是否有查询依赖该索引？先用慢查询日志确认
- TRUNCATE TABLE：数据是否已备份？TRUNCATE 不可回滚
- 生产环境禁止直接 DROP，必须走变更审批流程


---

## 二、DQL 查询语句审查（SELECT）

### 2.1 查询性能审查

**禁止的查询模式**
```sql
-- ❌ 禁止 SELECT *
SELECT * FROM t_order WHERE user_id = 1;
-- ✅ 明确指定需要的字段
SELECT order_id, user_id, amount, status FROM t_order WHERE user_id = 1;

-- ❌ 禁止无 WHERE 条件的全表查询
SELECT COUNT(*) FROM t_order;
-- ✅ 加条件或使用近似值
SELECT COUNT(*) FROM t_order WHERE create_time >= '2024-01-01';

-- ❌ 禁止大表无限制查询
SELECT * FROM t_order WHERE status = 1;
-- ✅ 必须有 LIMIT
SELECT order_id, amount FROM t_order WHERE status = 1 LIMIT 100;

-- ❌ 禁止深分页
SELECT * FROM t_order ORDER BY id LIMIT 1000000, 20;
-- ✅ 使用游标分页
SELECT * FROM t_order WHERE id > #{lastId} ORDER BY id LIMIT 20;
-- ✅ 或使用延迟关联
SELECT t.* FROM t_order t
INNER JOIN (SELECT id FROM t_order ORDER BY id LIMIT 1000000, 20) tmp
ON t.id = tmp.id;
```

**JOIN 查询审查**
```sql
-- 检查项：
-- 1. JOIN 字段是否有索引
-- 2. 驱动表选择是否合理（小表驱动大表）
-- 3. JOIN 数量不超过 3 张表（超过考虑拆分或冗余）
-- 4. ON 条件字段类型是否一致（避免隐式转换）
-- 5. 是否可以用子查询替代（有时更优）

-- ⚠️ 注意 LEFT JOIN 的 WHERE 条件位置
-- 错误：WHERE 条件放在 ON 后面会变成 INNER JOIN 效果
SELECT * FROM t_order o
LEFT JOIN t_user u ON o.user_id = u.id
WHERE u.status = 1;  -- ⚠️ 这会过滤掉 u 为 NULL 的行

-- 正确：条件放在 ON 中
SELECT * FROM t_order o
LEFT JOIN t_user u ON o.user_id = u.id AND u.status = 1;
```

**子查询审查**
```sql
-- ❌ 避免相关子查询（每行都执行一次子查询）
SELECT *, (SELECT name FROM t_user WHERE id = t_order.user_id) AS user_name
FROM t_order;

-- ✅ 改用 JOIN
SELECT o.*, u.name AS user_name
FROM t_order o LEFT JOIN t_user u ON o.user_id = u.id;

-- ❌ IN 子查询数据量过大
SELECT * FROM t_order WHERE user_id IN (SELECT id FROM t_user WHERE status = 1);
-- ✅ 改用 EXISTS 或 JOIN（取决于数据量）
SELECT * FROM t_order o WHERE EXISTS (
  SELECT 1 FROM t_user u WHERE u.id = o.user_id AND u.status = 1
);
```

**排序与分组审查**
```sql
-- ORDER BY 字段是否有索引（避免 filesort）
-- GROUP BY 字段是否有索引（避免临时表）
-- HAVING 条件能否移到 WHERE 中（WHERE 先过滤效率更高）
-- DISTINCT 是否可以用 GROUP BY 替代
-- ORDER BY 多字段时方向是否一致（混合 ASC/DESC 无法使用索引）

-- ⚠️ 检查 ORDER BY 与索引方向
-- 索引 (a ASC, b ASC) 支持：ORDER BY a ASC, b ASC 或 ORDER BY a DESC, b DESC
-- 不支持：ORDER BY a ASC, b DESC（MySQL 8.0+ 支持降序索引）
```

### 2.2 查询安全审查

**SQL 注入防护**
```sql
-- ❌ 字符串拼接（SQL 注入风险）
"SELECT * FROM t_user WHERE name = '" + userName + "'"

-- ✅ 参数化查询
"SELECT * FROM t_user WHERE name = ?"

-- ❌ MyBatis 中使用 ${}（直接拼接）
SELECT * FROM t_user WHERE name = '${name}'

-- ✅ MyBatis 中使用 #{}（参数化）
SELECT * FROM t_user WHERE name = #{name}

-- ⚠️ 必须使用 ${} 的场景（表名/列名动态化）需要额外校验
-- 白名单校验：只允许预定义的表名/列名
ORDER BY ${orderColumn}  -- 必须校验 orderColumn 在白名单中
```

**数据泄露防护**
```sql
-- 检查是否查询了敏感字段
-- 手机号、身份证号、银行卡号、密码等不应出现在普通查询中
-- 如需查询，必须脱敏处理

-- ❌ 直接返回敏感信息
SELECT phone, id_card, bank_card FROM t_user WHERE id = 1;

-- ✅ 脱敏处理
SELECT
  CONCAT(LEFT(phone, 3), '****', RIGHT(phone, 4)) AS phone,
  CONCAT(LEFT(id_card, 4), '**********', RIGHT(id_card, 4)) AS id_card
FROM t_user WHERE id = 1;
```

**权限与范围控制**
```sql
-- 检查是否有数据权限控制（防止越权查询）
-- 多租户场景必须带 tenant_id 条件
-- 用户数据查询必须带 user_id 条件

-- ❌ 缺少权限过滤
SELECT * FROM t_order WHERE order_id = #{orderId};

-- ✅ 加上用户维度过滤
SELECT * FROM t_order WHERE order_id = #{orderId} AND user_id = #{userId};
```

---

## 三、DML 语句审查（INSERT/UPDATE/DELETE）

### 3.1 INSERT 审查

```sql
-- ❌ 禁止不指定字段的 INSERT
INSERT INTO t_user VALUES (1, 'name', 'phone');
-- ✅ 明确指定字段
INSERT INTO t_user (id, name, phone) VALUES (1, 'name', 'phone');

-- 批量插入优化
-- ❌ 循环单条插入
INSERT INTO t_order (user_id, amount) VALUES (1, 100);
INSERT INTO t_order (user_id, amount) VALUES (2, 200);
-- ✅ 批量插入（每批 500-1000 条）
INSERT INTO t_order (user_id, amount) VALUES (1, 100), (2, 200), ...;

-- INSERT ... ON DUPLICATE KEY UPDATE（幂等写入）
INSERT INTO t_config (config_key, config_value)
VALUES ('key1', 'value1')
ON DUPLICATE KEY UPDATE config_value = VALUES(config_value), update_time = NOW();
```

### 3.2 UPDATE 审查

```sql
-- ❌ 禁止无 WHERE 条件的 UPDATE（全表更新）
UPDATE t_user SET status = 0;

-- ❌ 禁止更新大量数据的单条 UPDATE
UPDATE t_order SET status = 2 WHERE status = 1;  -- 可能影响百万行
-- ✅ 分批更新
UPDATE t_order SET status = 2 WHERE status = 1 AND id BETWEEN 1 AND 10000;

-- ✅ 使用乐观锁防止并发覆盖
UPDATE t_account SET balance = balance - 100, version = version + 1
WHERE account_id = 1 AND version = #{currentVersion};

-- 检查 UPDATE 是否会导致索引失效或锁升级
-- UPDATE 的 WHERE 条件必须走索引，否则可能锁全表
```

### 3.3 DELETE 审查

```sql
-- ❌ 禁止无 WHERE 条件的 DELETE
DELETE FROM t_log;
-- ✅ 使用 TRUNCATE（如果确实要清空且不需要回滚）
TRUNCATE TABLE t_log;

-- ❌ 禁止大批量 DELETE（长事务 + 大量 undo log）
DELETE FROM t_order WHERE create_time < '2023-01-01';
-- ✅ 分批删除
DELETE FROM t_order WHERE create_time < '2023-01-01' LIMIT 5000;
-- 循环执行直到影响行数为 0

-- 推荐逻辑删除替代物理删除
UPDATE t_order SET is_deleted = 1 WHERE id = #{id};
```

---

## 四、事务与锁审查

### 4.1 事务审查
```sql
-- 检查事务范围是否合理（不要太大）
-- ❌ 大事务（包含耗时操作）
BEGIN;
  INSERT INTO t_order ...;
  -- 调用外部接口（耗时操作不应在事务中）
  UPDATE t_account ...;
COMMIT;

-- 事务隔离级别检查
-- 默认 REPEATABLE READ，大多数场景够用
-- 需要 READ COMMITTED 的场景：高并发写入，减少锁冲突
```

### 4.2 锁审查
```sql
-- SELECT ... FOR UPDATE 检查
-- 1. 必须在事务中使用
-- 2. WHERE 条件必须走索引（否则锁全表）
-- 3. 锁持有时间要短
-- 4. 注意死锁风险（多表加锁顺序要一致）

-- ❌ 可能锁全表
SELECT * FROM t_account WHERE status = 1 FOR UPDATE;  -- status 无索引
-- ✅ 走主键或唯一索引
SELECT * FROM t_account WHERE account_id = 1 FOR UPDATE;

-- 间隙锁（Gap Lock）注意
-- REPEATABLE READ 下，范围查询会加间隙锁
SELECT * FROM t_order WHERE amount > 100 FOR UPDATE;
-- 这会锁住 amount > 100 的范围，阻塞其他插入
```

---

## 五、数据安全审查

### 5.1 敏感数据
- 密码字段：必须存储 BCrypt/SCrypt 哈希值，禁止明文或 MD5
- 手机号/身份证/银行卡：存储时加密（AES-256），查询时脱敏
- 日志表中禁止记录敏感数据明文
- 测试环境数据必须脱敏

### 5.2 数据完整性
- 关键字段设置 NOT NULL + DEFAULT 值
- 金额字段设置 CHECK 约束（>= 0）或应用层校验
- 唯一性约束：业务唯一键必须建唯一索引
- 外键：互联网项目通常不用数据库外键，在应用层保证

### 5.3 数据备份与恢复
- 重要表的 DDL 变更前是否有备份
- 是否有 binlog 开启（用于数据恢复）
- 大批量数据操作前是否有回滚方案

---

## 六、审查输出格式

```
【问题类型】DDL规范 / 索引设计 / 查询性能 / SQL安全 / 数据安全 / 事务锁
【严重程度】🔴 严重（必须修复，如 SQL 注入、全表扫描、无 WHERE 更新）
           🟡 警告（建议修复，如缺少索引、SELECT *）
           🔵 建议（可优化，如命名不规范、缺少注释）
【问题位置】文件名:行号 或 SQL 片段
【问题描述】具体问题
【性能影响】预估影响（全表扫描/锁表/慢查询等）
【修复建议】具体的修复 SQL
【关联检查】是否需要检查项目中其他 SQL 文件或代码
```

审查完成后给出：
1. SQL 质量评分（1-10）
2. 索引覆盖率评估（查询是否都有合适的索引）
3. 安全风险评估
4. Top 5 优先修复项
5. 建议补充的索引列表
