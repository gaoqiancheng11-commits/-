# -*- coding: utf-8 -*-
"""
电工刷题 - 一键构建 APK 脚本（无需 Android Studio / Gradle）

原理（标准 Android 构建管线的手工实现）：
  aapt2 compile/link（打包资源+assets+manifest，生成 R.java）
  -> javac（编译 Java 源码）
  -> d8（DEX 化）
  -> zipalign（对齐）
  -> apksigner（签名）

依赖（脚本会自动定位，无需手动安装）：
  - JDK 17+（含 keytool/javac）
  - Android build-tools 34.x（aapt2/d8/zipalign/apksigner）
  - Android platform android-33（android.jar）

定位顺序（依次尝试，找到即用）：
  1. 环境变量 DSH_JDK / DSH_SDK（推荐，例如构建机 CI 上设置）
  2. 环境变量 JAVA_HOME / ANDROID_HOME（标准开发机）
  3. 项目内 jdk/ 与 sdk/ 目录（首次可手动放进去）

用法：
  python tools/build_apk.py
  产物输出到 dist/电工刷题.apk
"""
import os, shutil, subprocess, sys, glob, zipfile

# ---------- 项目路径 ----------
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS_DIR)                 # 项目根目录
SRC = os.path.join(ROOT, "app", "src", "main")
ASSETS = os.path.join(SRC, "assets")
RES = os.path.join(SRC, "res")
JAVA_SRC = os.path.join(SRC, "java")
MANIFEST = os.path.join(SRC, "AndroidManifest.xml")
HTML_SRC = os.path.join(ASSETS, "index.html")

DIST = os.path.join(ROOT, "dist")
GEN = os.path.join(ROOT, "build", "gen")
CLASSES = os.path.join(ROOT, "build", "classes")
KEY_DIR = os.path.join(ROOT, "keystore")
KEYSTORE = os.path.join(KEY_DIR, "dsh-quiz.keystore")
STORE_PASS = os.environ.get("DSH_KEYSTORE_PASS", "dshquiz2026")
OUT_APK = os.path.join(DIST, "电工刷题.apk")

# ---------- JDK / SDK 定位 ----------
def first_existing(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None

JDK = first_existing([
    os.environ.get("DSH_JDK"),
    os.environ.get("JAVA_HOME"),
    *glob.glob(os.path.join(ROOT, "jdk", "jdk-*")),
    os.path.join(ROOT, "jdk"),
])
BT = first_existing([
    os.path.join(os.environ.get("DSH_SDK", ""), "build-tools") if os.environ.get("DSH_SDK") else "",
    os.path.join(os.environ.get("ANDROID_HOME", ""), "build-tools") if os.environ.get("ANDROID_HOME") else "",
    *glob.glob(os.path.join(ROOT, "sdk", "build-tools", "3*")),
])
PLATFORM = first_existing([
    os.path.join(os.environ.get("DSH_SDK", ""), "platforms", "android-33") if os.environ.get("DSH_SDK") else "",
    os.path.join(os.environ.get("ANDROID_HOME", ""), "platforms", "android-33") if os.environ.get("ANDROID_HOME") else "",
    os.path.join(ROOT, "sdk", "platforms", "android-33"),
])

def find_bt(tool):
    if not BT:
        return None
    for v in sorted(os.listdir(BT), reverse=True):
        p = os.path.join(BT, v, tool)
        if os.path.exists(p):
            return p
    return None

def check(cond, msg):
    if not cond:
        print("缺少: " + msg)
        sys.exit(1)

check(os.path.exists(HTML_SRC), "题库页面 assets/index.html")
check(JDK and os.path.exists(os.path.join(JDK, "bin", "javac.exe")), "JDK（设置 DSH_JDK 或 JAVA_HOME，或在项目根放 jdk/）")
check(BT and os.path.exists(BT), "Android build-tools（设置 DSH_SDK 或 ANDROID_HOME，或在项目根放 sdk/build-tools/）")
check(PLATFORM and os.path.exists(os.path.join(PLATFORM, "android.jar")), "android-33 platform")

javac = os.path.join(JDK, "bin", "javac.exe")
keytool = os.path.join(JDK, "bin", "keytool.exe")
aapt2 = find_bt("aapt2.exe")
d8 = find_bt("d8.bat")
zipalign = find_bt("zipalign.exe")
apksigner = find_bt("apksigner.bat")
check(all([aapt2, d8, zipalign, apksigner]), "build-tools 34.x 组件不全（aapt2/d8/zipalign/apksigner）")

os.environ["JAVA_HOME"] = JDK
os.environ["PATH"] = os.path.join(JDK, "bin") + os.pathsep + os.environ.get("PATH", "")

# ---------- 工具函数 ----------
def run(cmd):
    print(">>", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stdout[-3000:])
        print(r.stderr[-3000:])
        sys.exit(1)
    return r

# ---------- 1. 签名密钥（不存在则自动生成；生产发布请替换为自己的密钥） ----------
if not os.path.exists(KEYSTORE):
    os.makedirs(KEY_DIR, exist_ok=True)
    run([keytool, "-genkeypair", "-keystore", KEYSTORE, "-alias", "dsh-quiz",
         "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000",
         "-storepass", STORE_PASS, "-keypass", STORE_PASS,
         "-dname", "CN=Electrician Quiz, OU=Quiz, O=OpenSource, L=Beijing, ST=Beijing, C=CN"])
    print("已生成签名密钥:", KEYSTORE)

# ---------- 2. 编译资源 ----------
compiled = os.path.join(ROOT, "build", "compiled.zip")
os.makedirs(os.path.dirname(compiled), exist_ok=True)
if os.path.exists(compiled):
    os.remove(compiled)
res_files = [os.path.join(dp, f) for dp, _, fs in os.walk(RES) for f in fs]
run([aapt2, "compile"] + res_files + ["-o", compiled])

# ---------- 3. 链接资源+manifest+assets ----------
# 注意：aapt2 对含中文等非 ASCII 的目录路径处理有缺陷，
# 这里把 assets 复制到系统临时目录（纯 ASCII 路径）再链接。
import tempfile
tmp_assets = os.path.join(tempfile.mkdtemp(prefix="dsh_assets_"), "assets")
shutil.copytree(ASSETS, tmp_assets)
base_apk = os.path.join(ROOT, "build", "base.apk")
os.makedirs(GEN, exist_ok=True)
if os.path.exists(base_apk):
    os.remove(base_apk)
run([aapt2, "link", "-o", base_apk,
     "-I", os.path.join(PLATFORM, "android.jar"),
     "--manifest", MANIFEST,
     "--java", GEN,
     "-A", tmp_assets,
     compiled])

# ---------- 4. 编译 Java ----------
if os.path.exists(CLASSES):
    shutil.rmtree(CLASSES)
os.makedirs(CLASSES, exist_ok=True)
java_files = [os.path.join(dp, f) for dp, _, fs in os.walk(JAVA_SRC) for f in fs if f.endswith(".java")]
gen_files = [os.path.join(dp, f) for dp, _, fs in os.walk(GEN) for f in fs if f.endswith(".java")]
run([javac, "-source", "1.8", "-target", "1.8",
     "-bootclasspath", os.path.join(PLATFORM, "android.jar"),
     "-d", CLASSES] + gen_files + java_files)

# ---------- 5. DEX ----------
dex_out = os.path.join(ROOT, "build", "classes.dex")
if os.path.exists(dex_out):
    os.remove(dex_out)
class_files = [os.path.join(dp, f) for dp, _, fs in os.walk(CLASSES) for f in fs if f.endswith(".class")]
run([d8, "--lib", os.path.join(PLATFORM, "android.jar"),
     "--output", os.path.dirname(dex_out)] + class_files)

# ---------- 6. 合并 dex 进 apk ----------
with zipfile.ZipFile(base_apk, "a", zipfile.ZIP_DEFLATED) as z:
    z.write(dex_out, "classes.dex")

# ---------- 7. 对齐 ----------
aligned = os.path.join(ROOT, "build", "aligned.apk")
if os.path.exists(aligned):
    os.remove(aligned)
run([zipalign, "-f", "4", base_apk, aligned])

# ---------- 8. 签名 ----------
os.makedirs(DIST, exist_ok=True)
if os.path.exists(OUT_APK):
    os.remove(OUT_APK)
run([apksigner, "sign", "--ks", KEYSTORE,
     "--ks-pass", "pass:" + STORE_PASS, "--key-pass", "pass:" + STORE_PASS,
     "--out", OUT_APK, aligned])

# ---------- 9. 校验 ----------
run([apksigner, "verify", OUT_APK])

print("\n=== 构建成功 ===")
print("APK:", OUT_APK)
print("大小: %.2f MB" % (os.path.getsize(OUT_APK) / 1048576))
