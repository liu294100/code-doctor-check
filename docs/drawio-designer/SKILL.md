---
name: drawio-designer
description: 生成和编辑 draw.io（diagrams.net）XML 格式的架构图、流程图、时序图、ER 图、类图等，支持创建新图、修改现有图、添加/删除元素，输出可直接在 draw.io 中打开的 .drawio 文件。
---

# Draw.io 图表设计 Skill

生成和编辑 draw.io XML 格式的各类技术图表，输出 `.drawio` 文件可直接在 draw.io 桌面版或 VS Code Draw.io 插件中打开编辑。

使用方式：在聊天中输入 `#drawio-designer` 并描述你需要的图表内容。

---

## 使用示例

```
#drawio-designer
帮我画一个订单系统的架构图，包含 Controller、Service、Repository、数据库 四层

#drawio-designer
根据 order-server 的代码结构，生成一个类图

#drawio-designer
画一个订单创建的流程图：用户下单 → 参数校验 → 费用计算 → 创建订单 → 推送消息

#drawio-designer
帮我画一个 ER 图，包含 tb_order、tb_order_fees_record、tb_order_fill_detail 三张表的关系

#drawio-designer
修改 doc/design/order-flow.drawio，在"费用计算"节点后面增加一个"风控检查"节点

#drawio-designer
画一个订单消息处理的时序图：OrderController → OrderService → FeeCalculationService → KafkaProducer
```

---

## 支持的图表类型

| 图表类型 | 说明 | 适用场景 |
|---------|------|---------|
| 架构图 | 系统分层、模块关系 | 系统设计、技术方案 |
| 流程图 | 业务流程、审批流程 | 需求分析、流程梳理 |
| 时序图 | 模块间调用时序 | 接口设计、问题排查 |
| ER 图 | 数据库表关系 | 数据库设计 |
| 类图 | 类继承、依赖关系 | 代码设计、重构 |
| 部署图 | 服务部署拓扑 | 运维部署 |
| 思维导图 | 知识梳理、方案对比 | 头脑风暴、文档整理 |

---

## 生成规则

### 1. XML 结构规范

生成的 draw.io XML 必须遵循以下结构：

```xml
<mxfile host="app.diagrams.net" modified="2026-04-27T00:00:00.000Z" agent="Kiro" version="24.0.0" type="device">
  <diagram id="diagram-id" name="图表名称">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- 图表元素从这里开始 -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 2. 元素 ID 规范

- 每个 `mxCell` 必须有唯一的 `id`
- ID 使用有意义的命名：`node-controller`、`edge-ctrl-to-svc`
- 根节点 ID 固定为 `0`，第一层 parent 固定为 `1`

### 3. 样式规范

#### 矩形节点（类/模块/服务）
```xml
<mxCell id="node-1" value="OrderController" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="200" height="60" as="geometry" />
</mxCell>
```

#### 数据库节点
```xml
<mxCell id="node-db" value="MySQL" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;" vertex="1" parent="1">
  <mxGeometry x="100" y="400" width="120" height="80" as="geometry" />
</mxCell>
```

#### 连接线（箭头）
```xml
<mxCell id="edge-1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" source="node-1" target="node-2" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

#### 带标签的连接线
```xml
<mxCell id="edge-2" value="调用" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;" edge="1" source="node-1" target="node-2" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### 4. 颜色规范

| 层级/类型 | 填充色 | 边框色 | 用途 |
|----------|--------|--------|------|
| Controller | `#dae8fc` | `#6c8ebf` | 蓝色系，接入层 |
| Service | `#d5e8d4` | `#82b366` | 绿色系，业务层 |
| Repository/DAO | `#fff2cc` | `#d6b656` | 黄色系，数据层 |
| Database | `#f5f5f5` | `#666666` | 灰色系，存储 |
| External/RPC | `#e1d5e7` | `#9673a6` | 紫色系，外部依赖 |
| MQ/Kafka | `#f8cecc` | `#b85450` | 红色系，消息队列 |
| Config/Job | `#fff2cc` | `#d6b656` | 黄色系，配置/任务 |
| 决策/判断 | `#fff2cc` | `#d6b656` | 菱形，流程分支 |
| 开始/结束 | `#d5e8d4` | `#82b366` | 圆角，流程起止 |

### 5. 布局规范

- 节点间距：水平 ≥ 80px，垂直 ≥ 60px
- 节点默认尺寸：宽 200px，高 60px
- 从上到下或从左到右排列
- 同层级节点水平对齐
- 连接线使用正交路由（`edgeStyle=orthogonalEdgeStyle`）

### 6. 流程图特殊元素

#### 开始/结束节点（圆角矩形）
```xml
<mxCell id="start" value="开始" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;arcSize=50;" vertex="1" parent="1">
  <mxGeometry x="200" y="20" width="120" height="40" as="geometry" />
</mxCell>
```

#### 判断节点（菱形）
```xml
<mxCell id="decision-1" value="参数校验通过？" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
  <mxGeometry x="175" y="160" width="170" height="80" as="geometry" />
</mxCell>
```

### 7. 时序图规范

- 参与者使用矩形节点，水平排列在顶部
- 生命线使用虚线垂直向下延伸
- 消息使用带箭头的水平连接线
- 同步消息用实线箭头，异步消息用虚线箭头
- 返回消息用虚线箭头

### 8. ER 图规范

- 表名使用粗体，放在节点顶部
- 字段列表放在节点内部，每行一个字段
- 主键字段前加 🔑 或 PK 标记
- 外键关系使用连接线，标注 1:N 或 N:M

---

## 编辑现有图表

当用户提供现有 `.drawio` 文件路径时：

1. 读取文件内容，解析 XML 结构
2. 理解现有图表的元素和布局
3. 按用户要求添加、修改或删除元素
4. 保持现有元素的位置和样式不变（除非用户要求修改）
5. 新增元素的 ID 不与现有 ID 冲突
6. 输出修改后的完整 XML

---

## 输出规范

- 文件扩展名：`.drawio`（不是 `.xml`）
- 默认输出路径：`doc/design/` 目录下
- 文件名使用英文小写 + 连字符：如 `order-flow.drawio`、`system-architecture.drawio`
- 生成后提示用户可以用 draw.io 桌面版或 VS Code Draw.io Integration 插件打开
