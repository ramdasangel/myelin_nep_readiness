#!/usr/bin/env python3
"""Generate a self-contained HTML dashboard for Mathangle Assessment with Exit Levels."""

import json
from collections import defaultdict
from pathlib import Path

INPUT = "/tmp/mathangle_raw.jsonl"
EXIT_INPUT = "/tmp/mathangle_exit_levels.jsonl"
INDECISION_INPUT = "/tmp/mathangle_indecision.jsonl"
OUT = Path("/Users/ramdasangel/MyelinMaster/myelin_nep_readiness/output/mathangle_dashboard.html")

CHAPTER_MAP = {
    "Addition": "Addition & Subtraction", "बेरीज": "Addition & Subtraction",
    "Multiplication": "Multiplication", "गुणाकार": "Multiplication",
    "Division": "Division", "भागाकार": "Division",
    "Factors & Multiples": "Factors & Multiples", "विभाज्य आणि विभाजक": "Factors & Multiples",
    "Geometry": "Geometry", "भूमिती": "Geometry",
    "Measurement": "Measurement", "मापन": "Measurement",
    "Money": "Money", "पैसे": "Money",
    "Time & Calendar": "Time & Calendar", "वेळ आणि दिनदर्शिका": "Time & Calendar",
}

# Map subtopic names from question bank → unified competency areas
SUBTOPIC_MAP = {
    "Multiplication": "Multiplication",
    "Currency, openarions on money": "Money",
    "LCM": "Factors & Multiples",
    "LCM, Time measurement": "Factors & Multiples",
    "Divisibility Tests": "Factors & Multiples",
    "Division": "Division",
    "Length measurement": "Measurement",
    "Length measurement, conversion": "Measurement",
    "Addition, Subtraction": "Addition & Subtraction",
    "Minutes, Hours, Seconds measurement": "Time & Calendar",
    "Types of angles and shapes": "Geometry",
    "Measuring angles": "Geometry",
}

# Question_Level → NEP exit stage
EXIT_LABELS = {1: "Foundational", 2: "Preparatory", 3: "Middle"}
EXIT_COLORS = {"Middle": "#10B981", "Preparatory": "#3B82F6", "Foundational": "#F59E0B",
               "Below Foundational": "#EF4444", "Not Assessed": "#CBD5E1"}

def mc(ch):
    for k, v in CHAPTER_MAP.items():
        if ch.startswith(k): return v
    return ch

def load():
    rows = []
    with open(INPUT) as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"): rows.append(json.loads(line))
    return rows

def load_exit():
    rows = []
    with open(EXIT_INPUT) as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"): rows.append(json.loads(line))
    return rows

def load_indecision():
    rows = []
    with open(INDECISION_INPUT) as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"): rows.append(json.loads(line))
    return rows

def compute_indecision(indecision_rows):
    """Compute indecision index per person.

    Indecision Score = weighted combination of:
      - changes_per_question: avg answer changes per question (0 = decisive)
      - flip_flop_rate: fraction of questions with flip-flops
      - change_time_ratio: fraction of total time spent deliberating between changes
      - changed_from_correct: times changed away from correct answer

    Final index: 0-100 scale, higher = more indecisive.
    """
    result = {}
    for ir in indecision_rows:
        sid = ir["studentId"]
        tq = ir["totalQs"] or 1
        tc = ir["totalChanges"]
        tff = ir["totalFlipFlops"]
        tt = max(ir["totalTime"], 1)
        ct = ir["changeTime"]

        changes_per_q = tc / tq
        flip_rate = tff / tq
        time_ratio = min(ct / tt, 1.0) if tt > 0 else 0
        changed_from_correct = sum(1 for pq in ir["perQuestion"] if pq.get("changedFromCorrect"))
        cfc_rate = changed_from_correct / tq

        # Weighted score (0-100)
        # Max changes_per_q is ~4, normalize to 0-1 by dividing by 4
        score = (
            min(changes_per_q / 4, 1.0) * 40 +   # 40% weight: raw changes
            flip_rate * 25 +                        # 25% weight: flip-flops
            time_ratio * 15 +                       # 15% weight: deliberation time
            cfc_rate * 20                           # 20% weight: changed from correct
        )
        score = round(min(score, 100), 1)

        result[sid] = {
            "score": score,
            "totalChanges": tc,
            "totalFlipFlops": tff,
            "changesPerQ": round(changes_per_q, 2),
            "changeTime": ct,
            "changedFromCorrect": changed_from_correct,
            "changedToCorrect": sum(1 for pq in ir["perQuestion"] if pq.get("changedToCorrect")),
            "totalQs": tq,
            "totalTime": ir["totalTime"],
        }
    return result

def enrich(rows):
    for r in rows:
        r["lang"] = "MR" if "मराठी" in r["testName"] else "EN"
        r["name"] = f'{r["firstName"]} {r["lastName"]}'.strip()
        areas = defaultdict(lambda: {"right": 0, "total": 0})
        for ch in r.get("chapterWise", []):
            a = mc(ch["chapter"])
            areas[a]["right"] += ch["right"]
            areas[a]["total"] += ch["total"]
        r["areas"] = {k: round(v["right"]/v["total"]*100, 1) if v["total"] else 0 for k, v in areas.items()}
        r["areas_raw"] = {k: dict(v) for k, v in areas.items()}
        cog = {}
        for c in r.get("cognitiveLevel", []):
            cog[c["level"]] = {"right": c["right"], "total": c["total"], "pct": c["pct"]}
        r["cog"] = cog
        diff = {}
        for q in r.get("questionLevel", []):
            diff[str(q["level"])] = {"right": q["right"], "total": q["total"],
                                      "pct": round(q["right"]/q["total"]*100,1) if q["total"] else 0}
        r["diff"] = diff
    return rows

def compute_exit_levels(exit_rows):
    """Compute per-person per-competency exit level from per-question data."""
    AREA_ORDER = ["Multiplication", "Money", "Factors & Multiples", "Division",
                  "Measurement", "Addition & Subtraction", "Time & Calendar", "Geometry"]
    result = {}
    for er in exit_rows:
        sid = er["studentId"]
        comp_levels = defaultdict(dict)  # competency -> {level: right}
        for subtopic, levels in er.get("topicLevels", {}).items():
            comp = SUBTOPIC_MAP.get(subtopic)
            if not comp: continue
            for lv_str, data in levels.items():
                lv = int(lv_str)
                # If multiple subtopics map to same competency, take best at each level
                if lv not in comp_levels[comp] or data["right"] > comp_levels[comp][lv]:
                    comp_levels[comp][lv] = data["right"]

        # Derive highest exit level per competency
        exit_map = {}
        for comp in AREA_ORDER:
            if comp not in comp_levels:
                exit_map[comp] = "Not Assessed"
                continue
            levels = comp_levels[comp]
            # Highest level where they got at least 1 right
            highest = None
            for lv in sorted(levels.keys(), reverse=True):
                if levels[lv] > 0:
                    highest = lv
                    break
            if highest:
                exit_map[comp] = EXIT_LABELS[highest]
            else:
                exit_map[comp] = "Below Foundational"
        result[sid] = exit_map
    return result

def build_js_data(rows, exit_levels, indecision):
    teachers = [r for r in rows if r["role"] == "Teacher"]
    leaders = [r for r in rows if r["role"] == "Leader"]
    all_pcts = [r["percentage"] for r in rows]
    t_pcts = [r["percentage"] for r in teachers]
    l_pcts = [r["percentage"] for r in leaders]

    area_order = ["Multiplication", "Money", "Factors & Multiples", "Division",
                  "Measurement", "Addition & Subtraction", "Time & Calendar", "Geometry"]

    def area_avg(group, area):
        right = sum(r["areas_raw"].get(area, {}).get("right", 0) for r in group)
        total = sum(r["areas_raw"].get(area, {}).get("total", 0) for r in group)
        return round(right / total * 100, 1) if total else 0

    def cog_avg(group, level):
        rs, ts = 0, 0
        for p in group:
            for c in p.get("cognitiveLevel", []):
                if c["level"] == level: rs += c["right"]; ts += c["total"]
        return round(rs / ts * 100, 1) if ts else 0

    def diff_avg(group, level):
        rs, ts = 0, 0
        for p in group:
            for q in p.get("questionLevel", []):
                if q["level"] == level: rs += q["right"]; ts += q["total"]
        return round(rs / ts * 100, 1) if ts else 0

    # Branch data
    branch_map = defaultdict(list)
    for r in rows: branch_map[r["branchName"]].append(r)
    branch_data = []
    for br, br_rows in sorted(branch_map.items(), key=lambda x: sum(r["percentage"] for r in x[1])/len(x[1]), reverse=True):
        avg = round(sum(r["percentage"] for r in br_rows) / len(br_rows), 1)
        areas_br = {}
        for a in area_order:
            right = sum(r["areas_raw"].get(a, {}).get("right", 0) for r in br_rows)
            total = sum(r["areas_raw"].get(a, {}).get("total", 0) for r in br_rows)
            areas_br[a] = round(right/total*100, 1) if total else 0
        branch_data.append({"name": br, "count": len(br_rows), "avg": avg,
                            "teachers": len([r for r in br_rows if r["role"]=="Teacher"]),
                            "leaders": len([r for r in br_rows if r["role"]=="Leader"]),
                            "areas": areas_br})

    # Person table with exit levels + indecision
    sorted_rows = sorted(rows, key=lambda x: x["percentage"], reverse=True)
    person_table = []
    for i, r in enumerate(sorted_rows, 1):
        sid = r.get("studentId", "")
        el = exit_levels.get(sid, {})
        ind = indecision.get(sid, {})
        person_table.append({
            "rank": i, "name": r["name"], "role": r["role"], "sid": sid,
            "branch": r["branchName"], "school": r["schoolName"],
            "lang": r["lang"], "obtained": r["totalObtained"],
            "total": r["totalMarks"], "pct": r["percentage"],
            "time": r["timeTaken"],
            "areas": {a: r["areas"].get(a, None) for a in area_order},
            "cog": {c: r["cog"].get(c, {}).get("pct", None) for c in ["Understand","Apply","Analyze","Evaluate"]},
            "exit": {a: el.get(a, "Not Assessed") for a in area_order},
            "ind": ind.get("score", 0),
            "indDetail": {
                "changes": ind.get("totalChanges", 0),
                "flipFlops": ind.get("totalFlipFlops", 0),
                "changesPerQ": ind.get("changesPerQ", 0),
                "fromCorrect": ind.get("changedFromCorrect", 0),
                "toCorrect": ind.get("changedToCorrect", 0),
            },
        })

    # Exit level summary stats
    exit_summary = {}
    for a in area_order:
        counts = defaultdict(int)
        for sid, el in exit_levels.items():
            counts[el.get(a, "Not Assessed")] += 1
        exit_summary[a] = dict(counts)

    # Indecision summary
    all_ind_scores = [indecision[sid]["score"] for sid in indecision]
    ind_with_changes = [s for s in all_ind_scores if s > 0]

    import numpy as np
    bins = list(range(0, 110, 10))
    t_hist = list(map(int, np.histogram(t_pcts, bins=bins)[0]))
    l_hist = list(map(int, np.histogram(l_pcts, bins=bins)[0]))
    bin_labels = [f"{b}-{b+10}" for b in bins[:-1]]

    return {
        "kpi": {
            "total": len(rows), "teachers": len(teachers), "leaders": len(leaders),
            "avg": round(sum(all_pcts)/len(all_pcts), 1),
            "tAvg": round(sum(t_pcts)/len(t_pcts), 1),
            "lAvg": round(sum(l_pcts)/len(l_pcts), 1),
            "max": round(max(all_pcts), 1), "min": round(min(all_pcts), 1),
            "median": round(float(sorted(all_pcts)[len(all_pcts)//2]), 1),
        },
        "histogram": {"bins": bin_labels, "teachers": t_hist, "leaders": l_hist},
        "areas": {
            "labels": area_order,
            "teachers": [area_avg(teachers, a) for a in area_order],
            "leaders": [area_avg(leaders, a) for a in area_order],
            "all": [area_avg(rows, a) for a in area_order],
        },
        "cognitive": {
            "labels": ["Understand", "Apply", "Analyze", "Evaluate"],
            "all": [cog_avg(rows, c) for c in ["Understand","Apply","Analyze","Evaluate"]],
            "teachers": [cog_avg(teachers, c) for c in ["Understand","Apply","Analyze","Evaluate"]],
            "leaders": [cog_avg(leaders, c) for c in ["Understand","Apply","Analyze","Evaluate"]],
        },
        "difficulty": {
            "labels": ["Level 1 (Easy)", "Level 2 (Medium)", "Level 3 (Hard)"],
            "all": [diff_avg(rows, d) for d in [1,2,3]],
            "teachers": [diff_avg(teachers, d) for d in [1,2,3]],
            "leaders": [diff_avg(leaders, d) for d in [1,2,3]],
        },
        "branches": branch_data,
        "persons": person_table,
        "exitSummary": exit_summary,
        "exitLabels": list(EXIT_LABELS.values()) + ["Below Foundational", "Not Assessed"],
        "exitColors": EXIT_COLORS,
        "indecision": {
            "total": len(indecision),
            "withChanges": len(ind_with_changes),
            "avgScore": round(np.mean(all_ind_scores), 1) if all_ind_scores else 0,
            "maxScore": round(max(all_ind_scores), 1) if all_ind_scores else 0,
            "totalChanges": sum(indecision[s]["totalChanges"] for s in indecision),
            "totalFlipFlops": sum(indecision[s]["totalFlipFlops"] for s in indecision),
            "totalFromCorrect": sum(indecision[s]["changedFromCorrect"] for s in indecision),
            "totalToCorrect": sum(indecision[s]["changedToCorrect"] for s in indecision),
        },
    }


def generate_html(data):
    js_data = json.dumps(data, ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mathangle Assessment Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
:root {{
  --blue:#2563EB;--purple:#7C3AED;--green:#10B981;--amber:#F59E0B;
  --red:#EF4444;--cyan:#06B6D4;--gray:#6B7280;--bg:#F1F5F9;
  --card:#FFFFFF;--border:#E2E8F0;--text:#1E293B;--muted:#94A3B8;
  --teacher:#3B82F6;--leader:#8B5CF6;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text)}}
.header{{background:linear-gradient(135deg,#1E3A5F 0%,#2563EB 100%);color:white;padding:24px 32px}}
.header h1{{font-size:24px;font-weight:700;letter-spacing:-0.5px}}
.header p{{opacity:.85;margin-top:4px;font-size:13px}}
.container{{max-width:1440px;margin:0 auto;padding:20px}}
.grid{{display:grid;gap:16px}}
.grid-6{{grid-template-columns:repeat(6,1fr)}}
.grid-4{{grid-template-columns:repeat(4,1fr)}}
.grid-3{{grid-template-columns:repeat(3,1fr)}}
.grid-2{{grid-template-columns:repeat(2,1fr)}}
.grid-12{{grid-template-columns:repeat(12,1fr)}}
.card{{background:var(--card);border-radius:10px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.06);border:1px solid var(--border)}}
.card h3{{font-size:12px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}}
.kpi{{text-align:center;padding:12px 8px}}
.kpi .value{{font-size:28px;font-weight:800}}
.kpi .label{{font-size:11px;color:var(--muted);margin-top:2px}}
.kpi.blue .value{{color:var(--blue)}} .kpi.teacher .value{{color:var(--teacher)}}
.kpi.leader .value{{color:var(--leader)}} .kpi.green .value{{color:var(--green)}}
.kpi.red .value{{color:var(--red)}} .kpi.amber .value{{color:var(--amber)}}
.chart-wrap{{position:relative;height:220px}}
.span-2{{grid-column:span 2}} .span-3{{grid-column:span 3}} .span-4{{grid-column:span 4}}
.span-5{{grid-column:span 5}} .span-6{{grid-column:span 6}} .span-7{{grid-column:span 7}} .span-8{{grid-column:span 8}}
.section{{margin-top:20px}}
.section-title{{font-size:16px;font-weight:700;color:var(--text);margin-bottom:12px;padding-left:10px;border-left:4px solid var(--blue)}}
.tbl-wrap{{overflow-x:auto;max-height:550px;overflow-y:auto}}
table{{width:100%;border-collapse:collapse;font-size:11px}}
th{{background:#F8FAFC;position:sticky;top:0;z-index:2;padding:8px 6px;text-align:left;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.3px;border-bottom:2px solid var(--border);font-size:10px;cursor:pointer}}
th:hover{{color:var(--blue)}}
td{{padding:6px;border-bottom:1px solid #F1F5F9;white-space:nowrap}}
tr:hover td{{background:#F8FAFC}}
.badge{{display:inline-block;padding:2px 6px;border-radius:8px;font-size:10px;font-weight:600}}
.badge-teacher{{background:#DBEAFE;color:#1D4ED8}} .badge-leader{{background:#EDE9FE;color:#6D28D9}}
.pct-bar{{display:inline-block;height:5px;border-radius:3px;vertical-align:middle}}
.score-cell{{font-weight:700}}
.heat-tbl td{{text-align:center;font-weight:700;font-size:11px;min-width:65px}}
.heat-tbl th{{font-size:9px;text-align:center}}
.heat-tbl td.br-name{{text-align:left;font-weight:600;white-space:nowrap;font-size:10px}}
.filters{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:12px}}
.filters label{{font-size:11px;color:var(--muted);font-weight:600}}
.filters select,.filters input{{padding:5px 8px;border:1px solid var(--border);border-radius:6px;font-size:11px;background:white}}
.filters input{{width:180px}}
.exit-pill{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;color:white}}
.exit-Middle{{background:#10B981}} .exit-Preparatory{{background:#3B82F6}}
.exit-Foundational{{background:#F59E0B;color:#1F2937}}
.exit-Below{{background:#EF4444}} .exit-NA{{background:#E2E8F0;color:#94A3B8}}
/* Tabs */
.tabs{{display:flex;gap:0;border-bottom:2px solid var(--border);margin-bottom:16px}}
.tab{{padding:8px 20px;font-size:13px;font-weight:600;color:var(--muted);cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-2px;transition:.15s}}
.tab:hover{{color:var(--text)}} .tab.active{{color:var(--blue);border-bottom-color:var(--blue)}}
.tab-panel{{display:none}} .tab-panel.active{{display:block}}
@media(max-width:1024px){{
  .grid-6{{grid-template-columns:repeat(3,1fr)}}
  .grid-4,.grid-3{{grid-template-columns:repeat(2,1fr)}}
  .grid-12{{grid-template-columns:1fr}}
  .span-2,.span-3,.span-4,.span-5,.span-6,.span-7,.span-8{{grid-column:span 1}}
}}
</style>
</head>
<body>
<div class="header">
  <h1>Mathangle Assessment Dashboard</h1>
  <p>Adaptive Maths Competency Assessment &bull; Deccan Education Society &bull; February 2026</p>
</div>
<div class="container">

  <!-- KPIs -->
  <div class="section"><div class="grid grid-6" id="kpi-row"></div></div>

  <!-- Charts Row 1 -->
  <div class="section">
    <div class="grid grid-12">
      <div class="card span-5"><h3>Score Distribution</h3><div class="chart-wrap"><canvas id="histChart"></canvas></div></div>
      <div class="card span-7"><h3>Competency Areas — Teachers vs Leaders</h3><div class="chart-wrap"><canvas id="areaChart"></canvas></div></div>
    </div>
  </div>

  <!-- Charts Row 2 -->
  <div class="section">
    <div class="grid grid-12">
      <div class="card span-3"><h3>Bloom's Cognitive Levels</h3><div class="chart-wrap"><canvas id="cogChart"></canvas></div></div>
      <div class="card span-3"><h3>Difficulty Levels</h3><div class="chart-wrap"><canvas id="diffChart"></canvas></div></div>
      <div class="card span-3"><h3>Competency Radar</h3><div class="chart-wrap"><canvas id="radarChart"></canvas></div></div>
      <div class="card span-3"><h3>NEP Exit Level Distribution</h3><div class="chart-wrap"><canvas id="exitOverviewChart"></canvas></div></div>
    </div>
  </div>

  <!-- Indecision Section -->
  <div class="section">
    <h2 class="section-title">Indecision Index</h2>
    <div class="grid grid-12">
      <div class="card span-4">
        <h3>Indecision Summary</h3>
        <div id="indecision-kpis" style="display:grid;grid-template-columns:1fr 1fr;gap:10px"></div>
        <p style="font-size:10px;color:var(--muted);margin-top:10px;line-height:1.5">
          <b>Indecision Index (0–100):</b> Weighted score based on answer changes per question (40%),
          flip-flops (25%), deliberation time ratio (15%), and changed-away-from-correct (20%).
          <span style="color:#10B981">■</span> 0 = Decisive &nbsp;
          <span style="color:#F59E0B">■</span> 1–10 = Mild &nbsp;
          <span style="color:#EF4444">■</span> &gt;10 = High indecision
        </p>
      </div>
      <div class="card span-4"><h3>Score vs Indecision</h3><div class="chart-wrap"><canvas id="scatterIndChart"></canvas></div></div>
      <div class="card span-4"><h3>Indecision Distribution</h3><div class="chart-wrap"><canvas id="indDistChart"></canvas></div></div>
    </div>
  </div>

  <!-- Exit Level Matrix -->
  <div class="section">
    <h2 class="section-title">NEP Exit Level — Competency Matrix</h2>
    <div class="card">
      <p style="font-size:12px;color:var(--muted);margin-bottom:12px">
        Based on adaptive question levels: <b>Level 1</b> → Foundational exit, <b>Level 2</b> → Preparatory exit, <b>Level 3</b> → Middle Stage exit.
        Shows the <b>highest level mastered</b> per competency for each respondent.
      </p>
      <div class="chart-wrap" style="height:260px"><canvas id="exitStackedChart"></canvas></div>
    </div>
  </div>

  <!-- Heatmap -->
  <div class="section">
    <h2 class="section-title">Branch-wise Competency Heatmap</h2>
    <div class="card"><div class="tbl-wrap" id="heatmap-wrap"></div></div>
  </div>

  <!-- Tabbed: Ranking + Exit Matrix -->
  <div class="section">
    <h2 class="section-title">Individual Data</h2>
    <div class="card">
      <div class="tabs">
        <div class="tab active" data-tab="tab-ranking">Ranking Table</div>
        <div class="tab" data-tab="tab-exit">Exit Level Matrix</div>
      </div>
      <div id="tab-ranking" class="tab-panel active">
        <div class="filters">
          <label>Role:</label><select id="fRole"><option value="">All</option><option value="Teacher">Teacher</option><option value="Leader">Leader</option></select>
          <label>Lang:</label><select id="fLang"><option value="">All</option><option value="EN">EN</option><option value="MR">MR</option></select>
          <label>Branch:</label><select id="fBranch"><option value="">All</option></select>
          <label>Search:</label><input id="fSearch" type="text" placeholder="Name...">
        </div>
        <div class="tbl-wrap" id="ranking-wrap"></div>
      </div>
      <div id="tab-exit" class="tab-panel">
        <div class="filters">
          <label>Role:</label><select id="fRole2"><option value="">All</option><option value="Teacher">Teacher</option><option value="Leader">Leader</option></select>
          <label>Branch:</label><select id="fBranch2"><option value="">All</option></select>
          <label>Search:</label><input id="fSearch2" type="text" placeholder="Name...">
        </div>
        <div class="tbl-wrap" id="exit-wrap"></div>
      </div>
    </div>
  </div>

</div>

<script>
const D = {js_data};
const AREAS = D.areas.labels;
const EXIT_STAGES = ['Middle','Preparatory','Foundational','Below Foundational','Not Assessed'];
const EXIT_CLR = {{'Middle':'#10B981','Preparatory':'#3B82F6','Foundational':'#F59E0B','Below Foundational':'#EF4444','Not Assessed':'#E2E8F0'}};
const EXIT_SHORT = {{'Middle':'M','Preparatory':'P','Foundational':'F','Below Foundational':'BF','Not Assessed':'—'}};

// ── Tabs ─────────────────────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(t => {{
  t.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    document.getElementById(t.dataset.tab).classList.add('active');
  }});
}});

// ── KPIs ─────────────────────────────────────────────────────────────
(function(){{
  const kpis=[
    {{l:'Total Responses',v:D.kpi.total,c:'blue',s:''}},
    {{l:'Overall Average',v:D.kpi.avg,c:'blue',s:'%'}},
    {{l:'Teacher Avg (n='+D.kpi.teachers+')',v:D.kpi.tAvg,c:'teacher',s:'%'}},
    {{l:'Leader Avg (n='+D.kpi.leaders+')',v:D.kpi.lAvg,c:'leader',s:'%'}},
    {{l:'Highest Score',v:D.kpi.max,c:'green',s:'%'}},
    {{l:'Lowest Score',v:D.kpi.min,c:'red',s:'%'}},
  ];
  const el=document.getElementById('kpi-row');
  kpis.forEach(k=>{{el.innerHTML+=`<div class="card kpi ${{k.c}}"><div class="value">${{k.v}}${{k.s}}</div><div class="label">${{k.l}}</div></div>`}});
}})();

// ── Chart defaults ───────────────────────────────────────────────────
Chart.defaults.font.family="'Segoe UI',system-ui,sans-serif";
Chart.defaults.font.size=11;
Chart.defaults.plugins.legend.labels.usePointStyle=true;
Chart.defaults.plugins.legend.labels.font={{size:10}};

// ── Histogram ────────────────────────────────────────────────────────
new Chart(document.getElementById('histChart'),{{
  type:'bar',data:{{labels:D.histogram.bins,datasets:[
    {{label:'Teachers',data:D.histogram.teachers,backgroundColor:'rgba(59,130,246,.7)',borderRadius:3}},
    {{label:'Leaders',data:D.histogram.leaders,backgroundColor:'rgba(139,92,246,.7)',borderRadius:3}}
  ]}},options:{{responsive:true,maintainAspectRatio:false,
    plugins:{{legend:{{position:'top'}}}},
    scales:{{x:{{title:{{display:true,text:'Score Range (%)'}}}},y:{{title:{{display:true,text:'Count'}},beginAtZero:true}}}}
  }}
}});

// ── Competency Area ──────────────────────────────────────────────────
new Chart(document.getElementById('areaChart'),{{
  type:'bar',data:{{labels:AREAS,datasets:[
    {{label:'Teachers',data:D.areas.teachers,backgroundColor:'rgba(59,130,246,.8)',borderRadius:3}},
    {{label:'Leaders',data:D.areas.leaders,backgroundColor:'rgba(139,92,246,.8)',borderRadius:3}}
  ]}},options:{{responsive:true,maintainAspectRatio:false,
    plugins:{{tooltip:{{callbacks:{{label:c=>c.dataset.label+': '+c.parsed.y+'%'}}}}}},
    scales:{{y:{{beginAtZero:true,max:100,title:{{display:true,text:'Accuracy (%)'}}}}}}
  }}
}});

// ── Cognitive ────────────────────────────────────────────────────────
new Chart(document.getElementById('cogChart'),{{
  type:'bar',data:{{labels:D.cognitive.labels,datasets:[
    {{label:'Teachers',data:D.cognitive.teachers,backgroundColor:'rgba(59,130,246,.8)',borderRadius:3}},
    {{label:'Leaders',data:D.cognitive.leaders,backgroundColor:'rgba(139,92,246,.8)',borderRadius:3}}
  ]}},options:{{responsive:true,maintainAspectRatio:false,
    scales:{{y:{{beginAtZero:true,max:100,title:{{display:true,text:'%'}}}}}}
  }}
}});

// ── Difficulty ───────────────────────────────────────────────────────
new Chart(document.getElementById('diffChart'),{{
  type:'bar',data:{{labels:D.difficulty.labels,datasets:[
    {{label:'Teachers',data:D.difficulty.teachers,backgroundColor:['rgba(16,185,129,.8)','rgba(245,158,11,.8)','rgba(239,68,68,.8)'],borderRadius:3}},
    {{label:'Leaders',data:D.difficulty.leaders,backgroundColor:['rgba(16,185,129,.5)','rgba(245,158,11,.5)','rgba(239,68,68,.5)'],borderRadius:3}}
  ]}},options:{{responsive:true,maintainAspectRatio:false,
    scales:{{y:{{beginAtZero:true,max:100,title:{{display:true,text:'%'}}}}}}
  }}
}});

// ── Radar ────────────────────────────────────────────────────────────
new Chart(document.getElementById('radarChart'),{{
  type:'radar',data:{{labels:AREAS,datasets:[
    {{label:'Teachers',data:D.areas.teachers,borderColor:'#3B82F6',backgroundColor:'rgba(59,130,246,.12)',pointBackgroundColor:'#3B82F6',borderWidth:2}},
    {{label:'Leaders',data:D.areas.leaders,borderColor:'#8B5CF6',backgroundColor:'rgba(139,92,246,.12)',pointBackgroundColor:'#8B5CF6',borderWidth:2}}
  ]}},options:{{responsive:true,maintainAspectRatio:false,
    scales:{{r:{{beginAtZero:true,max:100,ticks:{{stepSize:25,font:{{size:9}}}}}}}},
    plugins:{{legend:{{position:'bottom'}}}}
  }}
}});

// ── Exit Overview stacked bar ────────────────────────────────────────
(function(){{
  const es = D.exitSummary;
  const stages = ['Middle','Preparatory','Foundational','Below Foundational','Not Assessed'];
  const colors = ['#10B981','#3B82F6','#F59E0B','#EF4444','#E2E8F0'];
  const datasets = stages.map((s,i) => ({{
    label: s, data: AREAS.map(a => (es[a]||{{}})[s]||0),
    backgroundColor: colors[i], borderRadius: 2
  }}));
  new Chart(document.getElementById('exitOverviewChart'),{{
    type:'bar',data:{{labels:AREAS,datasets}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'bottom',labels:{{font:{{size:9}}}}}},
        tooltip:{{callbacks:{{label:c=>c.dataset.label+': '+c.parsed.y+' respondents'}}}}
      }},
      scales:{{x:{{stacked:true,ticks:{{font:{{size:9}}}}}},y:{{stacked:true,title:{{display:true,text:'Respondents'}}}}}}
    }}
  }});
}})();

// ── Exit Stacked % chart ─────────────────────────────────────────────
(function(){{
  const es = D.exitSummary;
  const stages = ['Middle','Preparatory','Foundational','Below Foundational','Not Assessed'];
  const colors = ['#10B981','#3B82F6','#F59E0B','#EF4444','#E2E8F0'];
  const totals = AREAS.map(a => stages.reduce((s,st) => s+((es[a]||{{}})[st]||0), 0));
  const datasets = stages.map((s,i) => ({{
    label: s,
    data: AREAS.map((a,j) => totals[j]? Math.round(((es[a]||{{}})[s]||0)/totals[j]*100) : 0),
    backgroundColor: colors[i], borderRadius: 2
  }}));
  new Chart(document.getElementById('exitStackedChart'),{{
    type:'bar',data:{{labels:AREAS,datasets}},
    options:{{responsive:true,maintainAspectRatio:false,indexAxis:'y',
      plugins:{{legend:{{position:'bottom',labels:{{font:{{size:9}}}}}},
        tooltip:{{callbacks:{{label:c=>c.dataset.label+': '+c.parsed.x+'%'}}}}
      }},
      scales:{{x:{{stacked:true,max:100,title:{{display:true,text:'% of Respondents'}}}},y:{{stacked:true,ticks:{{font:{{size:10}}}}}}}}
    }}
  }});
}})();

// ── Indecision KPIs ──────────────────────────────────────────────────
(function(){{
  const I = D.indecision;
  const el = document.getElementById('indecision-kpis');
  const kpis = [
    {{l:'Avg Index',v:I.avgScore,c:'var(--amber)'}},
    {{l:'Max Index',v:I.maxScore,c:'var(--red)'}},
    {{l:'Had Changes',v:I.withChanges+'/'+I.total,c:'var(--blue)'}},
    {{l:'Total Changes',v:I.totalChanges,c:'var(--purple)'}},
    {{l:'Flip-Flops',v:I.totalFlipFlops,c:'var(--red)'}},
    {{l:'Changed→Wrong',v:I.totalFromCorrect,c:'var(--red)'}},
    {{l:'Changed→Right',v:I.totalToCorrect,c:'var(--green)'}},
    {{l:'Net Harm',v:I.totalFromCorrect - I.totalToCorrect,c:I.totalFromCorrect>I.totalToCorrect?'var(--red)':'var(--green)'}},
  ];
  kpis.forEach(k=>{{el.innerHTML+=`<div style="text-align:center;padding:6px"><div style="font-size:20px;font-weight:800;color:${{k.c}}">${{k.v}}</div><div style="font-size:10px;color:var(--muted)">${{k.l}}</div></div>`}});
}})();

// ── Scatter: Score vs Indecision ─────────────────────────────────────
new Chart(document.getElementById('scatterIndChart'),{{
  type:'scatter',
  data:{{datasets:[
    {{label:'Teachers',data:D.persons.filter(p=>p.role==='Teacher').map(p=>({{x:p.pct,y:p.ind,name:p.name}})),
      backgroundColor:'rgba(59,130,246,.6)',pointRadius:4}},
    {{label:'Leaders',data:D.persons.filter(p=>p.role==='Leader').map(p=>({{x:p.pct,y:p.ind,name:p.name}})),
      backgroundColor:'rgba(139,92,246,.6)',pointRadius:4,pointStyle:'rect'}},
  ]}},
  options:{{responsive:true,maintainAspectRatio:false,
    plugins:{{tooltip:{{callbacks:{{label:c=>c.raw.name+': Score '+c.raw.x+'%, Indecision '+c.raw.y}}}}}},
    scales:{{x:{{title:{{display:true,text:'Score (%)'}},min:0,max:100}},y:{{title:{{display:true,text:'Indecision Index'}},min:0}}}}
  }}
}});

// ── Indecision Distribution ──────────────────────────────────────────
(function(){{
  const scores = D.persons.map(p=>p.ind);
  const bins = [0,1,2,5,10,20,50,100];
  const labels = [];
  const counts = [];
  for(let i=0;i<bins.length-1;i++){{
    const lo=bins[i],hi=bins[i+1];
    labels.push(lo===0&&hi===1?'0 (Decisive)':lo+'-'+hi);
    counts.push(scores.filter(s=>s>=lo&&s<hi).length);
  }}
  new Chart(document.getElementById('indDistChart'),{{
    type:'bar',data:{{labels,datasets:[{{data:counts,backgroundColor:labels.map((_,i)=>
      i===0?'#10B981':i<=2?'#F59E0B':i<=4?'#F97316':'#EF4444'),borderRadius:3}}]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},
      scales:{{y:{{beginAtZero:true,title:{{display:true,text:'Count'}}}},x:{{title:{{display:true,text:'Indecision Range'}}}}}}
    }}
  }});
}})();

// ── Heatmap ──────────────────────────────────────────────────────────
(function(){{
  let h='<table class="heat-tbl"><thead><tr><th>Branch</th><th>n</th><th>T</th><th>L</th><th>Avg%</th>';
  AREAS.forEach(a=>{{h+='<th>'+a+'</th>'}});
  h+='</tr></thead><tbody>';
  D.branches.forEach(b=>{{
    h+='<tr><td class="br-name">'+b.name+'</td><td>'+b.count+'</td><td>'+b.teachers+'</td><td>'+b.leaders+'</td>';
    h+='<td style="font-weight:700;color:'+(b.avg>=60?'#10B981':b.avg>=40?'#F59E0B':'#EF4444')+'">'+b.avg+'%</td>';
    AREAS.forEach(a=>{{
      const v=b.areas[a]||0;
      const bg=v>=75?'#BBF7D0':v>=60?'#D9F99D':v>=45?'#FEF08A':v>=30?'#FED7AA':'#FECACA';
      const fg=v<30?'#991B1B':'#1F2937';
      h+='<td style="background:'+bg+';color:'+fg+'">'+v+'%</td>';
    }});
    h+='</tr>';
  }});
  h+='</tbody></table>';
  document.getElementById('heatmap-wrap').innerHTML=h;
}})();

// ── Ranking Table ────────────────────────────────────────────────────
(function(){{
  const cogs=['Understand','Apply','Analyze','Evaluate'];
  const brSet=[...new Set(D.persons.map(p=>p.branch))].sort();
  const fBranch=document.getElementById('fBranch');
  brSet.forEach(b=>{{const o=document.createElement('option');o.value=b;o.text=b;fBranch.appendChild(o)}});
  let sortCol='rank',sortAsc=true;
  function pc(v){{if(v===null||v===undefined)return'#94A3B8';if(v>=75)return'#10B981';if(v>=50)return'#2563EB';if(v>=25)return'#F59E0B';return'#EF4444'}}
  function render(){{
    const fR=document.getElementById('fRole').value,fL=document.getElementById('fLang').value;
    const fB=document.getElementById('fBranch').value,fS=document.getElementById('fSearch').value.toLowerCase();
    let data=D.persons.filter(p=>{{
      if(fR&&p.role!==fR)return false;if(fL&&p.lang!==fL)return false;
      if(fB&&p.branch!==fB)return false;if(fS&&!p.name.toLowerCase().includes(fS))return false;return true;
    }});
    data.sort((a,b)=>{{
      let va=a[sortCol],vb=b[sortCol];
      if(sortCol.startsWith('area_')){{const k=sortCol.slice(5);va=a.areas[k];vb=b.areas[k]}}
      if(sortCol.startsWith('cog_')){{const k=sortCol.slice(4);va=a.cog[k];vb=b.cog[k]}}
      if(va===null||va===undefined)va=-1;if(vb===null||vb===undefined)vb=-1;
      if(typeof va==='string'){{va=va.toLowerCase();vb=(vb||'').toLowerCase()}}
      return sortAsc?(va<vb?-1:va>vb?1:0):(va>vb?-1:va<vb?1:0);
    }});
    let h='<table><thead><tr>';
    const cols=[['rank','#'],['name','Name'],['role','Role'],['branch','Branch'],['lang','L'],['pct','Score%'],['ind','Indecision'],['obtained','Marks'],['time','Time']];
    AREAS.forEach(a=>cols.push(['area_'+a,a]));
    cogs.forEach(c=>cols.push(['cog_'+c,c]));
    cols.forEach(([k,l])=>{{const ar=sortCol===k?(sortAsc?' ▲':' ▼'):'';h+=`<th data-col="${{k}}">${{l}}${{ar}}</th>`}});
    h+='</tr></thead><tbody>';
    data.forEach((p,i)=>{{
      h+='<tr>';
      h+=`<td>${{i+1}}</td><td style="font-weight:600">${{p.name}}</td>`;
      h+=`<td><span class="badge badge-${{p.role.toLowerCase()}}">${{p.role}}</span></td>`;
      h+=`<td style="max-width:180px;overflow:hidden;text-overflow:ellipsis" title="${{p.branch}}">${{p.branch}}</td>`;
      h+=`<td>${{p.lang}}</td>`;
      const c=pc(p.pct);
      h+=`<td class="score-cell" style="color:${{c}}">${{p.pct}}%<div class="pct-bar" style="width:${{p.pct}}%;background:${{c}}"></div></td>`;
      const ic=p.ind===0?'#10B981':p.ind<=5?'#84CC16':p.ind<=10?'#F59E0B':'#EF4444';
      const id=p.indDetail||{{}};
      const ititle=`Changes: ${{id.changes||0}}, Flip-flops: ${{id.flipFlops||0}}, Changed→Wrong: ${{id.fromCorrect||0}}, Changed→Right: ${{id.toCorrect||0}}`;
      h+=`<td title="${{ititle}}" style="font-weight:700;color:${{ic}};cursor:help">${{p.ind}}</td>`;
      h+=`<td>${{p.obtained}}/${{p.total}}</td><td>${{p.time}}</td>`;
      AREAS.forEach(a=>{{const v=p.areas[a];h+=v!==null&&v!==undefined?`<td style="color:${{pc(v)}};font-weight:600">${{v}}%</td>`:'<td style="color:#CBD5E1">—</td>'}});
      cogs.forEach(c=>{{const v=p.cog[c];h+=v!==null&&v!==undefined?`<td style="color:${{pc(v)}};font-weight:600">${{v}}%</td>`:'<td style="color:#CBD5E1">—</td>'}});
      h+='</tr>';
    }});
    h+='</tbody></table>';
    document.getElementById('ranking-wrap').innerHTML=h;
    document.querySelectorAll('#ranking-wrap th').forEach(th=>{{
      th.addEventListener('click',()=>{{const c=th.dataset.col;if(sortCol===c)sortAsc=!sortAsc;else{{sortCol=c;sortAsc=c==='name'||c==='branch'}};render()}});
    }});
  }}
  ['fRole','fLang','fBranch'].forEach(id=>document.getElementById(id).addEventListener('change',render));
  document.getElementById('fSearch').addEventListener('input',render);
  render();
}})();

// ── Exit Level Matrix Table ──────────────────────────────────────────
(function(){{
  const brSet=[...new Set(D.persons.map(p=>p.branch))].sort();
  const fB2=document.getElementById('fBranch2');
  brSet.forEach(b=>{{const o=document.createElement('option');o.value=b;o.text=b;fB2.appendChild(o)}});

  const exitOrder = {{'Middle':4,'Preparatory':3,'Foundational':2,'Below Foundational':1,'Not Assessed':0}};
  let sortCol='pct',sortAsc=false;

  function render(){{
    const fR=document.getElementById('fRole2').value;
    const fB=document.getElementById('fBranch2').value;
    const fS=document.getElementById('fSearch2').value.toLowerCase();
    let data=D.persons.filter(p=>{{
      if(fR&&p.role!==fR)return false;
      if(fB&&p.branch!==fB)return false;
      if(fS&&!p.name.toLowerCase().includes(fS))return false;return true;
    }});
    data.sort((a,b)=>{{
      if(sortCol==='pct')return sortAsc?a.pct-b.pct:b.pct-a.pct;
      if(sortCol==='name'){{const av=a.name.toLowerCase(),bv=b.name.toLowerCase();return sortAsc?(av<bv?-1:1):(av>bv?-1:1)}}
      if(sortCol.startsWith('exit_')){{const k=sortCol.slice(5);const av=exitOrder[a.exit[k]]||0,bv=exitOrder[b.exit[k]]||0;return sortAsc?av-bv:bv-av}}
      return 0;
    }});
    let h='<table><thead><tr>';
    const cols=[['rank','#'],['name','Name'],['role','Role'],['branch','Branch'],['pct','Score%']];
    AREAS.forEach(a=>cols.push(['exit_'+a,a]));
    cols.forEach(([k,l])=>{{const ar=sortCol===k?(sortAsc?' ▲':' ▼'):'';h+=`<th data-col="${{k}}">${{l}}${{ar}}</th>`}});
    h+='</tr></thead><tbody>';
    data.forEach((p,i)=>{{
      h+='<tr>';
      h+=`<td>${{i+1}}</td><td style="font-weight:600">${{p.name}}</td>`;
      h+=`<td><span class="badge badge-${{p.role.toLowerCase()}}">${{p.role}}</span></td>`;
      h+=`<td style="max-width:180px;overflow:hidden;text-overflow:ellipsis" title="${{p.branch}}">${{p.branch}}</td>`;
      const c=p.pct>=75?'#10B981':p.pct>=50?'#2563EB':p.pct>=25?'#F59E0B':'#EF4444';
      h+=`<td style="font-weight:700;color:${{c}}">${{p.pct}}%</td>`;
      AREAS.forEach(a=>{{
        const ex=p.exit[a]||'Not Assessed';
        const cls=ex==='Middle'?'exit-Middle':ex==='Preparatory'?'exit-Preparatory':ex==='Foundational'?'exit-Foundational':ex==='Below Foundational'?'exit-Below':'exit-NA';
        h+=`<td><span class="exit-pill ${{cls}}">${{EXIT_SHORT[ex]||ex}}</span> ${{ex}}</td>`;
      }});
      h+='</tr>';
    }});
    h+='</tbody></table>';
    document.getElementById('exit-wrap').innerHTML=h;
    document.querySelectorAll('#exit-wrap th').forEach(th=>{{
      th.addEventListener('click',()=>{{const c=th.dataset.col;if(sortCol===c)sortAsc=!sortAsc;else{{sortCol=c;sortAsc=false}};render()}});
    }});
  }}
  ['fRole2','fBranch2'].forEach(id=>document.getElementById(id).addEventListener('change',render));
  document.getElementById('fSearch2').addEventListener('input',render);
  render();
}})();
</script>
</body>
</html>"""
    return html


if __name__ == "__main__":
    rows = load()
    print(f"Loaded {len(rows)} analysis records")
    rows = enrich(rows)

    exit_rows = load_exit()
    print(f"Loaded {len(exit_rows)} exit-level records")
    exit_levels = compute_exit_levels(exit_rows)
    print(f"Exit levels computed for {len(exit_levels)} persons")

    indecision_rows = load_indecision()
    print(f"Loaded {len(indecision_rows)} indecision records")
    indecision = compute_indecision(indecision_rows)
    ind_with = sum(1 for s in indecision.values() if s["score"] > 0)
    print(f"Indecision computed: {ind_with}/{len(indecision)} had answer changes")

    data = build_js_data(rows, exit_levels, indecision)
    html = generate_html(data)
    OUT.write_text(html, encoding="utf-8")
    print(f"Dashboard → {OUT}  ({len(html)//1024} KB)")
