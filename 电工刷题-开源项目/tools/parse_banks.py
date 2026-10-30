# -*- coding: utf-8 -*-
"""
电工刷题 - 题库提取脚本
把两个 Excel 题库（2026新增.xls / 2025题库.xlsx）解析为 data/questions.json。

用法：
  python tools/parse_banks.py <2026新增.xls> <2025题库.xlsx>

说明：
  - 2026 新增表头在第 1 行；2025 题库表头在第 2 行（脚本已按各自结构处理）
  - 判断题答案常见写法（正确/对/√/是/T、错误/错/×/否/F/X）统一映射为 0/1
  - 单选题答案为 A/B/C/D，映射为 0/1/2/3
  - 全部题目保留（不去重），保证与原始题库逐题一致
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

if len(sys.argv) != 3:
    print(__doc__)
    sys.exit(1)

F1, F2 = sys.argv[1], sys.argv[2]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "questions.json")
OUT = os.path.normpath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)

questions = []

# ---------- 2026新增.xls（表头第1行） ----------
import xlrd
wb1 = xlrd.open_workbook(F1)
sh1 = wb1.sheet_by_name('电工理论测试-题库')
hdr1 = [str(sh1.cell_value(0, c)).strip() for c in range(sh1.ncols)]
col = {name: i for i, name in enumerate(hdr1)}

def cell(sh, r, name):
    if name not in col:
        return ""
    v = sh.cell_value(r, col[name])
    return str(v).strip() if v is not None else ""

for r in range(1, sh1.nrows):
    qstem = cell(sh1, r, '题干')
    if not qstem:
        continue
    qtype = cell(sh1, r, '题型')
    options = [o for o in [cell(sh1, r, c) for c in 'ABCD'] if o]
    if '判断' in qtype and len(options) < 2:
        options = ['正确', '错误']
    questions.append({
        "type": "judge" if '判断' in qtype else "single",
        "q": qstem,
        "opts": options,
        "ans_raw": cell(sh1, r, '正确答案'),
        "analysis": cell(sh1, r, '答案解析'),
        "src": "2026新增"
    })

# ---------- 2025题库.xlsx（表头第2行） ----------
import openpyxl
wb2 = openpyxl.load_workbook(F2, read_only=True, data_only=True)
ws2 = wb2['理论题库模板']
hdr2 = [str(c.value).strip() if c.value else "" for c in ws2[2]]
c2 = {name: i for i, name in enumerate(hdr2)}

def cell2(row, name):
    if name not in c2:
        return ""
    v = row[c2[name]]
    return str(v).strip() if v is not None else ""

for row in ws2.iter_rows(min_row=3, values_only=True):
    qstem = cell2(row, '题干')
    if not qstem:
        continue
    qtype = cell2(row, '题目类型')
    options = [o for o in [cell2(row, f'选项{c}') for c in 'ABCD'] if o]
    if '判断' in qtype and len(options) < 2:
        options = ['正确', '错误']
    questions.append({
        "type": "judge" if '判断' in qtype else "single",
        "q": qstem,
        "opts": options,
        "ans_raw": cell2(row, '正确答案'),
        "analysis": "",
        "src": "2025题库"
    })

# ---------- 答案映射 ----------
ANSWER_MAP = {
    "正确": 0, "对": 0, "√": 0, "是": 0, "T": 0,
    "错误": 1, "错": 1, "×": 1, "否": 1, "F": 1, "X": 1,
    "A": 0, "B": 1, "C": 2, "D": 3
}

def map_answer(q):
    raw = q["ans_raw"].strip().upper()
    if raw in ANSWER_MAP:
        return ANSWER_MAP[raw], "ok"
    for i, o in enumerate(q["opts"]):
        if o and raw == o.strip().upper():
            return i, "text-match"
    return None, "unknown"

clean, bad = [], []
for q in questions:
    opts = [o for o in q["opts"] if o]
    if not opts:
        bad.append(("无选项", q["q"][:25]))
        continue
    ans_idx, status = map_answer(q)
    if ans_idx is None or ans_idx >= len(opts):
        bad.append(("答案无法映射[%s] ans=%r n=%d" % (status, q["ans_raw"], len(opts)), q["q"][:25]))
        continue
    clean.append({"t": q["type"], "q": q["q"], "o": opts, "a": ans_idx,
                  "x": q.get("analysis", ""), "s": q["src"]})

from collections import Counter
print("原始合计:", len(questions), "有效:", len(clean), "异常:", len(bad))
print("题型分布:", dict(Counter(q["t"] for q in clean)))
print("来源分布:", dict(Counter(q["s"] for q in clean)))
for b in bad[:15]:
    print("  异常:", b)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(clean, f, ensure_ascii=False)
print("已写入:", OUT, "共", len(clean), "条")
