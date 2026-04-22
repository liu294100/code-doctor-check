---
inclusion: manual
---

# JADX 反编译 Skill

使用 JADX 反编译 JAR/APK/DEX/AAR 文件，查看 Java 源码。
JADX 特别擅长 Android 相关文件（APK/DEX），同时也支持普通 JAR 包。
使用方式：在聊天中输入 `#jadx-decompile` 并提供文件路径。

---

## 使用示例

```
#jadx-decompile
帮我反编译 D:/apk/some-app.apk 到 D:/output/

#jadx-decompile
用 JADX 查看 some-sdk.jar 中 com.example.SomeClass 的源码

#jadx-decompile
打开 JADX GUI 查看 D:/lib/some.aar

#jadx-decompile
反编译 classes.dex 文件
```

---

## 工具环境

- 统一启动脚本：`D:/dev/tools/decompile.bat`
  - 自动检测系统上的 Java 版本（支持 8/11/17/21）
  - 优先使用高版本 Java，自动适配 JVM 参数
- JADX CLI：`D:/dev/tools/jadx/bin/jadx.bat`（v1.4.7）
- JADX GUI：`D:/dev/tools/jadx/bin/jadx-gui.bat`

查看环境信息：
```bash
D:/dev/tools/decompile.bat info
```

### 工具下载（如未安装）

```bash
# 1. 下载统一启动脚本 decompile.bat
curl -L -o D:/dev/tools/decompile.bat https://raw.githubusercontent.com/liu294100/code-doctor-check/refs/heads/main/java-doctor-check/decompile.bat

# 2. 下载 JADX（Java 8 用 1.4.7，Java 11+ 用 1.5.5）
# Java 8:
curl -L -o D:/dev/tools/jadx.zip https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip
# Java 11+:
curl -L -o D:/dev/tools/jadx.zip https://github.com/skylot/jadx/releases/download/v1.5.5/jadx-1.5.5.zip
# 解压到 D:/dev/tools/jadx/

# 3.（可选）下载 CFR 反编译器
curl -L -o D:/dev/tools/cfr.jar https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar
```

> 注意：JADX 1.4.7 的 `jadx.bat` 中 `-XX:MaxRAMPercentage=70.0` 参数不兼容 Java 8，需手动删除该参数。

---

## JADX vs CFR 选择指南

| 场景 | 推荐工具 | 原因 |
|------|---------|------|
| 普通 Java JAR 反编译 | CFR（`#jar-decompile`） | 源码质量更高，Lambda/Stream 支持更好 |
| Android APK 反编译 | JADX（本 skill） | 专为 Android 设计，支持资源文件解析 |
| DEX 文件反编译 | JADX（本 skill） | 原生支持 DEX 格式 |
| AAR 库反编译 | JADX（本 skill） | 支持 Android Archive 格式 |
| 需要 GUI 浏览 | JADX GUI | 可视化浏览代码结构 |
| 批量反编译整个 JAR | 两者都行 | JADX 输出目录结构更清晰 |

---

## 支持的文件格式

- `.apk` - Android 应用包
- `.dex` - Dalvik 可执行文件
- `.jar` - Java Archive
- `.aar` - Android Archive
- `.class` - Java 字节码文件
- `.zip` - 包含上述文件的压缩包

---

## 执行流程

### 第一步：确认输入参数

从用户消息中提取：
- **输入文件路径**（必须）：APK/JAR/DEX/AAR 文件路径
- **输出目录**（可选）：反编译结果输出目录，默认 `/tmp/jadx-output`
- **目标类名**（可选）：如果只想看某个类
- **操作模式**：
  - `cli` - 命令行反编译到目录（默认）
  - `gui` - 打开 JADX GUI 可视化浏览
  - `single` - 反编译后只查看指定类

### 第二步：验证输入文件

```bash
ls -la "<文件路径>"
```

### 第三步：CLI 反编译（整体反编译到目录）

```bash
# 基本用法：反编译到指定目录
D:/dev/tools/decompile.bat jadx -d "<输出目录>" "<输入文件>"

# 常用参数组合
D:/dev/tools/decompile.bat jadx -d "<输出目录>" --deobf --show-bad-code "<输入文件>"
```

#### JADX CLI 常用参数

| 参数 | 说明 |
|------|------|
| `-d <dir>` | 输出目录（必须） |
| `--deobf` | 反混淆（对混淆过的代码有帮助） |
| `--show-bad-code` | 即使反编译失败也显示代码（带注释标记） |
| `--no-res` | 不反编译资源文件（加快速度） |
| `--no-src` | 不反编译源码（只提取资源） |
| `-e` | 导出为 Gradle 项目 |
| `--threads-count <N>` | 线程数（默认 4） |
| `-r` | 不解码资源（保持原始格式） |

#### 反编译示例

```bash
# 反编译 APK（完整，含资源）
D:/dev/tools/decompile.bat jadx -d /tmp/jadx-output/app --show-bad-code some-app.apk

# 反编译 JAR（只要源码，不要资源）
D:/dev/tools/decompile.bat jadx -d /tmp/jadx-output/lib --no-res some-lib.jar

# 反编译混淆过的 APK
D:/dev/tools/decompile.bat jadx -d /tmp/jadx-output/app --deobf --show-bad-code obfuscated.apk

# 快速反编译（跳过资源）
D:/dev/tools/decompile.bat jadx -d /tmp/jadx-output/quick --no-res --threads-count 8 large-app.apk
```

### 第四步：查看反编译结果

反编译完成后，输出目录结构：
```
<输出目录>/
├── sources/           # Java 源码
│   └── com/
│       └── example/
│           ├── MainActivity.java
│           └── utils/
│               └── Helper.java
└── resources/         # 资源文件（APK 才有）
    ├── AndroidManifest.xml
    ├── res/
    └── assets/
```

#### 查看指定类

```bash
# 反编译后，直接读取生成的 Java 文件
# 类名 com.example.MyClass 对应路径 sources/com/example/MyClass.java

cat "<输出目录>/sources/com/example/MyClass.java"
```

#### 搜索类

```bash
# 在反编译结果中搜索类
find "<输出目录>/sources" -name "*.java" | grep -i "keyword"

# 搜索代码内容
grep -r "someMethod" "<输出目录>/sources/" --include="*.java"
```

### 第五步：打开 JADX GUI（可视化浏览）

如果用户想用 GUI 浏览：

```bash
# 打开 JADX GUI（会在新窗口中启动）
D:/dev/tools/decompile.bat jadx-gui "<文件路径>"
```

JADX GUI 功能：
- 代码高亮和导航
- 类/方法/字段搜索
- 交叉引用查找
- 反混淆
- 导出为 Gradle 项目

提示用户：JADX GUI 已在新窗口中打开，可以在 GUI 中浏览代码。

### 第六步：格式化输出

对于 CLI 模式，读取反编译后的文件并展示：

```
🔍 JADX 反编译结果：com.example.MyClass
═══════════════════════════════════════════
来源：some-app.apk
工具：JADX 1.4.7
输出目录：/tmp/jadx-output/
═══════════════════════════════════════════
```

然后用 java 代码块展示源码内容。

---

## 常见场景

### 场景一：反编译 Android APK

```bash
# 完整反编译
D:/dev/tools/decompile.bat jadx -d /tmp/jadx-output/myapp --show-bad-code D:/apk/myapp.apk

# 查看 AndroidManifest.xml
cat /tmp/jadx-output/myapp/resources/AndroidManifest.xml

# 查看主 Activity
cat /tmp/jadx-output/myapp/sources/com/example/myapp/MainActivity.java
```

### 场景二：反编译 JAR 依赖

```bash
# 反编译 JAR（跳过资源处理，更快）
D:/dev/tools/decompile.bat jadx -d /tmp/jadx-output/lib --no-res ~/.m2/repository/com/example/sdk/1.0/sdk-1.0.jar

# 查看指定类
cat /tmp/jadx-output/lib/sources/com/example/sdk/SomeService.java
```

### 场景三：反编译混淆代码

```bash
# 使用反混淆选项
D:/dev/tools/decompile.bat jadx -d /tmp/jadx-output/deobf --deobf --show-bad-code obfuscated.apk

# 查看反混淆映射
ls /tmp/jadx-output/deobf/
```

### 场景四：导出为可导入的项目

```bash
# 导出为 Gradle 项目，可以直接用 Android Studio 打开
D:/dev/tools/decompile.bat jadx -e -d /tmp/jadx-project some-app.apk
```

### 场景五：只提取资源文件

```bash
# 只提取资源，不反编译代码
D:/dev/tools/decompile.bat jadx -d /tmp/jadx-res --no-src some-app.apk
```

---

## 与 CFR 配合使用

对于 JAR 文件，可以两个工具配合：
- 先用 JADX 整体反编译到目录，浏览项目结构
- 再用 CFR 精确反编译某个类，获得更高质量的源码

```bash
# 1. JADX 整体反编译，了解结构
D:/dev/tools/decompile.bat jadx -d /tmp/jadx-output --no-res some.jar

# 2. 找到感兴趣的类后，用 CFR 精确反编译
D:/dev/tools/decompile.bat cfr some.jar "com.example.InterestingClass"
```

---

## 注意事项

- JADX 反编译是整体操作，会反编译所有类到输出目录
- 大型 APK 反编译可能需要较长时间和较多内存
- 混淆过的代码即使反编译成功，可读性也较差，建议配合 `--deobf`
- JADX GUI 需要图形界面环境
- 当前安装的 JADX 1.4.7 兼容 Java 8+
- 如果后续升级 Java 到 11+，可以升级 JADX 到最新版 1.5.5 获得更好的反编译效果
