# 电工刷题（Electrician Quiz）

科目一风格的**电工中级理论题库刷题 App**——像考驾照科目一一样逐题刷题、即时判分、答错出解析和记忆口诀、错题自动收录。内置 **1240 道真题**，题目与原始 Excel 题库**逐题 100% 一致**（附校验脚本可复现验证）。

- **Android 真机 App**：直接安装 APK，纯本地运行、无需联网
- **在线网页版**：iPhone / Android 通用，浏览器打开即用，Safari 可"添加到主屏幕"变全屏 App
- 代码极简、可审计：无 Android Studio、无 Gradle、无网络依赖，一条命令构建 APK

---

## 在线体验（发给朋友最快的方式）

无需安装，手机浏览器直接打开：

```
https://4m8exj11z7wph.doubaoapps.com/app/app_17fxfw50h8n
```

**iPhone 用户**（iOS 无法安装第三方 APK，用这个方式体验与 App 无异）：

1. 用 iPhone 自带 **Safari** 打开上面的链接（不要在微信/QQ 内置浏览器里打开）
2. 点底部中间的**分享按钮** → 下滑&#x70B9;**"添加到主屏幕"**
3. 桌面出现"电工刷题"图标，点开即全屏运行，带专属图标

**Android 用户**：浏览器打开即可直接用，同样可"添加到主屏幕"；或直接安装 `dist/` 里的 APK。

---

## 功能

| 功能   | 说明                                       |
| ---- | ---------------------------------------- |
| 练习范围 | 全部题库（1240）/ 2025 题库（1000）/ 2026 年新增（240） |
| 练习模式 | 顺序练习、随机练习                                |
| 模拟考试 | 随机抽 100 题、45 分钟计时、**60 分及格线**、得分环 + 错题回顾 |
| 逐题解析 | 1240 题每题一段真实解析，**答错时展示**                 |
| 记忆要点 | 1240 题每题一句记忆口诀（对比/联想/数值锚点），答错时和解析一起出现    |
| 答题音效 | 答对=上行三连音，答错=下滑警示音（Web Audio 合成，无音频文件）    |
| 游戏化  | 等级/经验、连击、每日打卡、同题连错 3 次弹"易错复习卡"、答题粒子特效    |
| 错题本  | 答错自动收录，可重练，做对自动移出                        |
| 收藏   | 收藏重点题目专项复习                               |
| 进度统计 | 累计做题、正确率、易错点，localStorage 本地保存           |
| 断点续刷 | 顺序练习中途退出，下次从原位置继续并保留答题记录                 |
| 答题节奏 | 答对后 1 秒自动进入下一题（间隔内禁止跳过），答错停留看解析          |
| 退出修复 | 自绘确认弹层，做题中退出不卡顿、计时不中断                    |

## 数据与格式

题库统一存放在 `data/questions.json`（单行压缩、UTF-8），每条结构：

| 字段  | 说明                                   |
| --- | ------------------------------------ |
| `t` | 题型：`judge`（判断）/ `single`（单选）         |
| `q` | 题干                                   |
| `o` | 选项数组（判断题恒为 `["正确","错误"]`，单选 4 项）     |
| `a` | 答案索引（判断：0 正确 / 1 错误；单选：0~~3 对应 A~~D） |
| `x` | 解析（1240 条全覆盖）                        |
| `s` | 来源：`2026新增`（240 题）/ `2025题库`（1000 题） |
| `m` | 记忆要点（1240 条全覆盖）                      |

题库统计：**1240 题 = 判断 248 + 单选 992**，来自 2026 年新增题库（240 题）与 2025 年理论题库（1000 题）。

## 目录结构

```
电工刷题/
├── app/
│   └── src/main/
│       ├── AndroidManifest.xml          # App 清单
│       ├── java/com/dgpower/quiz/
│       │   └── MainActivity.java        # WebView 壳（唯一 Java 代码）
│       ├── assets/
│       │   └── index.html               # 刷题程序本体（科目一风格，内置全部题目+解析+记忆要点）
│       └── res/drawable/ic_launcher.png # 应用图标
├── data/
│   └── questions.json                   # 1240 道题结构化数据（可读、可复用）
├── tools/
│   ├── parse_banks.py                   # Excel 题库 -> questions.json
│   ├── build_apk.py                     # 一键构建 APK（无需 Android Studio）
│   └── verify_apk.py                    # 校验 APK 内题目与 questions.json 100% 一致
├── docs/
│   └── BUILD_CN.md                      # 详细构建说明与常见问题
├── publish/                             # 在线网页版发布目录（index.html + manifest + 图标）
├── dist/                                # APK 构建产物（只保留最新版）
└── keystore/                            # 签名密钥（自动生成，已 gitignore，绝不上传）
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
- 需要 JDK 17+ 与 Android build-tools 34.x / platform-33，脚本支持通过环境变量 `DSH_JDK`、`DSH_SDK` 指定位置（详见 `docs/BUILD_CN.md`）。

## 在线网页版发布（可选）

`publish/` 目录是发布用的单文件网页（`index.html` + PWA `manifest.json` + 图标）。用 lark-cli 发布：

```bash
cd publish
lark-cli apps +deploy --file-path ./index.html
```

发布成功后会返回一个公开链接，iPhone（Safari 添加到主屏幕）和 Android 均可直接使用。

## 数据来源与版权提示

- `data/questions.json` 由用户提供的两份 Excel 题库提取而来，属于用户资料，公开分发前请注意确认题库内容的使用与传播权限。
- 逐题**解析与记忆要点**由 AI 辅助生成，供学习参考；判断题以题库标准答案为准。
- 代码部分采用 MIT 协议（见 LICENSE）。

## 许可证

MIT License © 2026 电工刷题 contributors

## 致谢



