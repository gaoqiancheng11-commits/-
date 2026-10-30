# -*- coding: utf-8 -*-
"""
电工刷题 - 校验脚本
核对 APK 内嵌的题库与 data/questions.json 完全一致（数量、题干、选项、答案、题型、顺序）。
用法： python tools/verify_apk.py [APK路径]
"""
import sys, io, os, json, zipfile, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS_DIR)
apk = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dist", "电工刷题.apk")
bank = os.path.join(ROOT, "data", "questions.json")

assert os.path.exists(apk), "APK 不存在: " + apk
assert os.path.exists(bank), "题库数据不存在: " + bank

with open(bank, encoding="utf-8") as f:
    src = json.load(f)

z = zipfile.ZipFile(apk)
html = z.read("assets/index.html").decode("utf-8")
m = re.search(r"const RAW_DATA = (\[)", html)
assert m, "APK 内未找到 RAW_DATA"
dec = json.JSONDecoder()
data, _ = dec.raw_decode(html[m.start() + 17:])

bad = 0
if len(src) != len(data):
    print("!! 数量不一致: 源 %d vs APK %d" % (len(src), len(data)))
    bad += 1
for i in range(min(len(src), len(data))):
    s, a = src[i], data[i]
    if not (a["q"] == s["q"] and a["o"] == s["o"] and a["a"] == s["a"] and a["t"] == s["t"]):
        print("!! 第 %d 题不一致: %s" % (i + 1, s["q"][:30]))
        bad += 1

print("源题库题数:", len(src), "| APK内嵌题数:", len(data))
if bad == 0:
    print("\nAPK 内嵌题库与 data/questions.json：数量、题干、选项、答案、题型、顺序 100% 一致 ✓")
else:
    print("\n存在 %d 处不一致" % bad)
    sys.exit(1)
