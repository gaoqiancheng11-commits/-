# 构建说明

## 方式一：一键脚本（推荐，无需 Android Studio）

```bash
python tools/build_apk.py
```

脚本会自动定位 JDK 与 Android SDK，找不到时按下表准备：

| 组件 | 版本 | 如何提供 |
| --- | --- | --- |
| JDK | 17+（21 已验证） | 设置环境变量 `DSH_JDK`（或 `JAVA_HOME`）指向 JDK 根目录 |
| Android build-tools | 34.x | 设置 `DSH_SDK`（或 `ANDROID_HOME`）指向 SDK 根目录（内含 build-tools/ 与 platforms/） |

也可直接把 JDK 解压放到项目根目录的 `jdk/`、SDK 放到 `sdk/`。

### 首次运行会自动做的事

1. 在 `keystore/` 生成签名密钥 `dsh-quiz.keystore`（密码默认 `dshquiz2026`，可用环境变量 `DSH_KEYSTORE_PASS` 覆盖）
2. 执行完整构建管线，输出 `dist/电工刷题.apk`

### 重要安全提示

- `keystore/` 已加入 `.gitignore`，**绝对不要**把密钥提交到 GitHub。别人拿到你的签名密钥，就能冒充你的应用发布恶意版本。
- 发布到应用商店前，建议自己用 `keytool` 生成正式密钥（保持密码私密、妥善备份），并在 `build_apk.py` 中替换。

## 方式二：校验构建产物

```bash
python tools/verify_apk.py
```

逐题比对 `dist/电工刷题.apk` 内嵌题库与 `data/questions.json`（数量、题干、选项、答案、题型、顺序），输出 100% 一致才通过。

## 方式三：标准 Android Studio（可选）

本项目结构（`app/src/main/...`）与标准 Gradle 工程一致，如需使用 Android Studio：

1. 新建 Empty Activity 工程，包名 `com.dgpower.quiz`
2. 把 `app/src/main/` 下的 `AndroidManifest.xml`、`java/`、`res/`、`assets/` 覆盖进工程
3. 直接 Build 即可

## 更换题目

1. 修改题库后重新生成数据：`python tools/parse_banks.py <2026新增.xls> <2025题库.xlsx>`
2. 重新构建：`python tools/build_apk.py`
3. 校验：`python tools/verify_apk.py`

也可以直接编辑 `data/questions.json` 后，将内容替换进 `app/src/main/assets/index.html` 的 `const RAW_DATA = [...]`（建议用脚本做，避免 JSON 语法错误）。

## 常见问题

| 问题 | 解决 |
| --- | --- |
| `缺少: JDK` | 安装 JDK 21 并设置 `DSH_JDK` / `JAVA_HOME` |
| `缺少: Android build-tools` | 下载 build-tools 34.x + platform-33，设置 `DSH_SDK` |
| 手机上安装提示"未知来源" | 系统设置允许该来源安装应用（所有非应用商店 App 都需此授权） |
