# 电工刷题（Electrician Quiz）

科目一风格的**电工中级理论题库刷题 App**（Android），像考驾照科目一一样逐题刷题、即时判分、错题自动收录。

- 内置 **1240 道题**（2026 年新增 240 道 + 2025 题库 1000 道，判断 248 + 单选 992）
- 题目与原始 Excel 题库**逐题 100% 一致**（有校验脚本可复现验证）
- 纯本地运行：题目全部内嵌在 App 里，**无需联网**

## 功能

| 功能 | 说明 |
| --- | --- |
| 练习范围 | 全部题库 / 2025 题库 / 2026 年新增 |
| 练习模式 | 顺序练习、随机练习 |
| 模拟考试 | 随机抽题、计分、未答统计、错题回顾 |
| 错题本 | 答错的题自动收录，可重刷 |
| 收藏 | 收藏重点题目 |
| 进度统计 | 累计做题、正确率，本地保存（localStorage） |

## 界面

首页选择练习范围与练习模式，答题页逐题判分并高亮正确答案，模拟考试后展示得分与错题回顾。移动端优先设计，也支持电脑浏览器打开 `app/src/main/assets/index.html` 直接体验。

## 目录结构

```
电工刷题/
├── app/
│   └── src/main/
│       ├── AndroidManifest.xml          # App 清单
│       ├── java/com/dgpower/quiz/
│       │   └── MainActivity.java        # WebView 壳（唯一 Java 代码）
│       ├── assets/
│       │   └── index.html               # 刷题程序本体（科目一风格，内置全部题目）
│       └── res/drawable/ic_launcher.png # 应用图标
├── data/
│   └── questions.json                   # 1240 道题的结构化数据（可读、可复用）
├── tools/
│   ├── parse_banks.py                   # Excel 题库 -> questions.json
│   ├── build_apk.py                     # 一键构建 APK（无需 Android Studio）
│   └── verify_apk.py                    # 校验 APK 内题目与 questions.json 一致
├── docs/
│   └── BUILD_CN.md                      # 详细构建说明
├── dist/                                # 构建产物（APK 输出到这里）
└── keystore/                            # 签名密钥（自动生成，已 gitignore）
```

## 快速开始

环境要求：**Python 3.8+**（Windows / macOS / Linux 均可）。

```bash
# 1. 构建 APK（脚本自动定位 JDK 与 Android SDK；找不到时见 docs/BUILD_CN.md）
python tools/build_apk.py

# 2. 校验 APK 内嵌题库与 data/questions.json 完全一致
python tools/verify_apk.py

# 产物：dist/电工刷题.apk，直接安装到手机即可
```

### 从 Excel 重新生成题库数据（可选）

需要 `python -m pip install xlrd openpyxl`：

```bash
python tools/parse_banks.py "电工中级理论题库2026年新增.xls" "电工中级理论题库2025年6.6 (1).xlsx"
```

会重新生成 `data/questions.json`，再跑 `build_apk.py` 即得到新版 App。

## 构建原理（无 Android Studio）

本项目用**最简依赖**实现了完整 Android 构建管线，方便学习与审计：

```
aapt2 compile/link  ->  javac  ->  d8  ->  zipalign  ->  apksigner
（资源+manifest+assets打包、生成R.java）   （DEX）     （对齐）      （签名）
```

- App 本体是 `assets/index.html`（单文件网页），Android 端只是一个加载它的 WebView 壳，任何网页开发经验都能直接上手改。
- 需要 JDK 17+ 与 Android build-tools 34.x / platform-33，脚本支持通过环境变量 `DSH_JDK`、`DSH_SDK` 指定位置。

## 数据来源与版权提示

- `data/questions.json` 由用户提供的两份 Excel 题库提取而来，属于用户资料，公开分发前请注意确认题库内容的使用与传播权限。
- 代码部分采用 MIT 协议（见 LICENSE）。

## 许可证

MIT License © 2026 电工刷题 contributors

## 致谢

- 题目数据：用户提供
- App 代码由 Doubao（豆包）协助开发并开源
