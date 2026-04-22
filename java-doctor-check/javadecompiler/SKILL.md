
---
inclusion: manual
---

# JAR 反编译 Skill（CFR）

使用 CFR 反编译器查看 JAR 包中 `.class` 文件的完整 Java 源码。
使用方式：在聊天中输入 `#jar-decompile` 并提供 JAR 文件路径和要查看的类名。

---

## 使用示例

```
#jar-decompile
帮我反编译 D:/lib/some-sdk-1.0.jar 中的 com.example.SomeClass

#jar-decompile
列出 order-server/target/order-server.jar 里所有的类

#jar-decompile
查看 ~/.m2/repository/com/chief/trader/common/1.0.0/common-1.0.0.jar 中 com.chief.trader.common.util.DateUtils 的源码
```

---

## 工具环境

- 统一启动脚本：`D:/dev/tools/decompile.bat`
  - 自动检测系统上的 Java 版本（支持 8/11/17/21）
  - 优先使用高版本 Java，自动适配 JVM 参数
- CFR 反编译器：`D:/dev/tools/cfr.jar`（v0.152）
  - 输出完整 Java 源码，对 Java 8+ 特性支持最好
- 备选工具：javap（JDK 自带，只能看方法签名和字节码）

查看环境信息：
```bash
D:/dev/tools/decompile.bat info
```

### 工具下载（如未安装）

```bash
# 1. 下载统一启动脚本 decompile.bat
curl -L -o D:/dev/tools/decompile.bat https://raw.githubusercontent.com/liu294100/code-doctor-check/refs/heads/main/java-doctor-check/decompile.bat

# 2. 下载 CFR 反编译器
curl -L -o D:/dev/tools/cfr.jar https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar

# 3.（可选）下载 JADX（Java 8 用 1.4.7，Java 11+ 用 1.5.5）
# Java 8:
curl -L -o D:/dev/tools/jadx.zip https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip
# Java 11+:
curl -L -o D:/dev/tools/jadx.zip https://github.com/skylot/jadx/releases/download/v1.5.5/jadx-1.5.5.zip
# 解压到 D:/dev/tools/jadx/
```

> 注意：JADX 1.4.7 的 `jadx.bat` 中 `-XX:MaxRAMPercentage=70.0` 参数不兼容 Java 8，需手动删除该参数。

---

## 执行流程

### 第一步：确认输入参数

从用户消息中提取：
- **JAR 文件路径**（必须）：绝对路径或相对路径
- **目标类名**（可选）：全限定类名，如 `com.example.MyClass`
- **操作类型**（可选）：
  - `list` - 列出 JAR 中所有类
  - `decompile` - 反编译指定类（默认）
  - `search` - 搜索包含关键字的类名

如果用户没有提供目标类名，先执行 `list` 操作让用户选择。

### 第二步：验证 JAR 文件

```bash
ls -la "<JAR路径>"
jar tf "<JAR路径>" 2>&1 | head -5
```

### 第三步：列出 JAR 内容（list 操作）

```bash
# 列出所有 .class 文件（不含内部类）
jar tf "<JAR路径>" | grep "\.class$" | grep -v '\$' | sort

# 按包名过滤
jar tf "<JAR路径>" | grep "\.class$" | grep "com/example" | sort
```

输出格式示例：
```
📦 JAR 包内容：some-sdk-1.0.jar
═══════════════════════════════════════════
共包含 X 个类（不含内部类）

📁 com/example/
  ├── SomeClass.class
  ├── AnotherClass.class
  └── util/
      └── DateUtils.class
```

### 第四步：搜索类名（search 操作）

```bash
jar tf "<JAR路径>" | grep -i "<关键字>" | grep "\.class$" | sort
```

### 第五步：反编译（decompile 操作）

#### 使用 CFR（推荐）

```bash
# 反编译单个类，输出到控制台
D:/dev/tools/decompile.bat cfr "<JAR路径>" "com.example.MyClass"

# 反编译并输出到目录
D:/dev/tools/decompile.bat cfr "<JAR路径>" "com.example.MyClass" --outputdir /tmp/cfr-output

# 反编译整个包
D:/dev/tools/decompile.bat cfr "<JAR路径>" --jarfilter "com.example.service.*" --outputdir /tmp/decompiled/
```

#### 使用 javap（备选，只看结构）

```bash
# 先提取 class 文件
mkdir -p /tmp/jar-decompile && cd /tmp/jar-decompile
jar xf "<JAR路径>" "com/example/MyClass.class"

# 查看类结构（含 private 成员）
D:/dev/tools/decompile.bat javap -p -cp /tmp/jar-decompile "com.example.MyClass"

# 查看字节码
D:/dev/tools/decompile.bat javap -p -c -cp /tmp/jar-decompile "com.example.MyClass"
```

### 第六步：格式化输出

```
🔍 反编译结果：com.example.MyClass
═══════════════════════════════════════════
来源：some-sdk-1.0.jar
工具：CFR 0.152
═══════════════════════════════════════════
```

然后用 java 代码块展示反编译的源码。

### 第七步：查看内部类（如需要）

```bash
# 列出内部类
jar tf "<JAR路径>" | grep "com/example/MyClass\$"

# 反编译内部类
D:/dev/tools/decompile.bat cfr "<JAR路径>" "com.example.MyClass$InnerClass"
```

---

## 常见场景

### 查看 Maven 依赖源码
```bash
D:/dev/tools/decompile.bat cfr ~/.m2/repository/org/springframework/spring-core/5.3.20/spring-core-5.3.20.jar "org.springframework.core.annotation.AnnotationUtils"
```

### 查看项目构建产物
```bash
mvn package -DskipTests
D:/dev/tools/decompile.bat cfr target/my-app-1.0.jar "com.example.MyService"
```

### 对比两个版本
```bash
D:/dev/tools/decompile.bat cfr old.jar "com.example.MyClass" > /tmp/old.java
D:/dev/tools/decompile.bat cfr new.jar "com.example.MyClass" > /tmp/new.java
diff /tmp/old.java /tmp/new.java
```

---

## 注意事项

- 反编译结果仅供参考，变量名和注释会丢失
- 混淆过的代码可读性较差
- CFR 对 Lambda、Stream 等 Java 8+ 特性反编译效果最好
- 如果 JAR 包很大，建议先 search 再反编译具体类
