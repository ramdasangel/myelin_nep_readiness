#!/usr/bin/env python3
"""
Stage-1 Leader Intent — FP Orientation Dashboard
Leader instrument setCodes: 7890 (English) + 104 (Marathi)
Also includes leaders who answered teacher instrument (1234 + 103).
FP Orientation Score = mean(selectedOption) / 3 per FP section.
Range: 0-1.  Higher = deeper orientation within that FP section.
"""

import csv
import json
import os
from collections import defaultdict
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INTENT_DIR = os.path.join(BASE, "data", "extracted", "intent")
OUT_PATH = os.path.join(BASE, "output", "dashboards", "12b_stage1_leader_fp.html")

FP_NAMES = {
    "FP1": "Each Child is Unique",
    "FP2": "Holistic & Experiential Learning",
    "FP3": "Reflective Practitioner",
    "FP4": "Assessment for Learning",
    "FP5": "Collaboration & Community",
}
FPS = ["FP1", "FP2", "FP3", "FP4", "FP5"]
FP_COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"]

# Leader instrument question counts per FP section
LEADER_FP_Q = {"FP1": 3, "FP2": 5, "FP3": 6, "FP4": 3, "FP5": 3}
# Teacher instrument question counts per FP section
TEACHER_FP_Q = {"FP1": 4, "FP2": 4, "FP3": 5, "FP4": 5, "FP5": 4}

GOAL_FP = {
    # Teacher instrument goals (leaders also answered these)
    "Each Child is Unique": "FP1", "Competency-Based Learning": "FP2",
    "Teacher Upskilling": "FP3", "Diagnosing Learning Levels": "FP4",
    "Parent\u2013Teacher Collaboration": "FP5", "Parent-Teacher Collaboration": "FP5",
    "\u092a\u094d\u0930\u0924\u094d\u092f\u0947\u0915 \u092e\u0942\u0932 \u0935\u0947\u0917\u0933\u0947 \u0906\u0939\u0947": "FP1",
    "\u0915\u094d\u0937\u092e\u0924\u093e\u0927\u093f\u0937\u094d\u0920\u093f\u0924 \u0905\u0927\u094d\u092f\u092f\u0928": "FP2",
    "\u0915\u094d\u0937\u092e\u0924\u093e\u0927\u093f\u0937\u094d\u091f\u093f\u0924 \u0905\u0927\u094d\u092f\u092f\u0928": "FP2",
    "\u0936\u093f\u0915\u094d\u0937\u0915 \u0915\u094c\u0936\u0932\u094d\u092f\u0935\u0943\u0926\u094d\u0927\u0940": "FP3",
    "\u0936\u093f\u0915\u094d\u0937\u0915 \u0915\u094c\u0936\u0932\u094d\u092f\u0935\u0943\u0927\u094d\u0926\u0940": "FP3",
    "\u0905\u0927\u094d\u092f\u092f\u0928 \u0938\u094d\u0924\u0930\u093e\u0902\u091a\u0947 \u0928\u093f\u0926\u093e\u0928": "FP4",
    "\u092a\u093e\u0932\u0915 - \u0936\u093f\u0915\u094d\u0937\u0915 \u0938\u0939\u092f\u094b\u0917": "FP5",
    "\u092a\u093e\u0932\u0915 -\u0936\u093f\u0915\u094d\u0937\u0915 \u0938\u0939\u092f\u094b\u0917": "FP5",
    "\u092a\u093e\u0932\u0915 - \u0936\u093f\u0915\u094d\u0937\u0915 \u0938\u0939\u092d\u093e\u0917\u0940\u0924\u093e": "FP5",
    # Leader instrument goals
    "Learning Progress Monitoring": "FP1", "Student Engagement": "FP1", "Understanding Learners": "FP1",
    "Classroom Observation": "FP2", "Activity Design": "FP2", "Lesson Planning": "FP2", "Task Rigor": "FP2",
    "Teacher Support": "FP3", "Teacher Coaching": "FP3", "Innovation in Teaching": "FP3",
    "Teacher Development": "FP3", "Team Leadership": "FP3", "School Improvement": "FP3",
    "Data Analysis": "FP4", "Instructional Review": "FP4", "Learning Data Analysis": "FP4",
    "Parent Engagement": "FP5", "Parent Communication": "FP5", "School Communication": "FP5",
}

# All 4 intent files -- filter by role=Leader from CSV
FILES = [
    ("intent_teacher_english_responses.csv", "English"),
    ("intent_teacher_marathi_responses.csv", "Marathi"),
    ("intent_leader_english_responses.csv", "English"),
    ("intent_leader_marathi_responses.csv", "Marathi"),
]


def load_branch_names():
    path = os.path.join(BASE, "output", "reports", "sri_unified.json")
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        return {bc: b.get("branchName", "") for bc, b in data.get("branches", {}).items()}
    return {}


def load_data():
    # Per user: {uid: {bc, lang, source, fp_opts: {fp: [opts]}}}
    users = {}
    # Raw counts for reference tab
    branch_fp_raw = defaultdict(lambda: {fp: 0 for fp in FPS})
    overall_fp_raw = {fp: 0 for fp in FPS}
    total_raw = 0

    for fname, lang in FILES:
        fpath = os.path.join(INTENT_DIR, fname)
        if not os.path.exists(fpath):
            continue
        is_leader_file = "leader" in fname
        with open(fpath) as f:
            for row in csv.DictReader(f):
                bc = row.get("branchCode", "").strip()
                uid = row.get("userId", "")
                goal = row.get("goal", "").strip()
                role = row.get("role", "").strip()
                if not bc or bc.startswith("m") or not uid:
                    continue
                if role != "Leader":
                    continue
                fp = GOAL_FP.get(goal)
                if not fp:
                    continue

                try:
                    opt = int(row.get("selectedOption", ""))
                except (ValueError, TypeError):
                    continue

                if uid not in users:
                    source = "L" if is_leader_file else "T"
                    users[uid] = {"bc": bc, "lang": lang, "source": source, "fp_opts": defaultdict(list)}
                users[uid]["fp_opts"][fp].append(opt)

                branch_fp_raw[bc][fp] += 1
                overall_fp_raw[fp] += 1
                total_raw += 1

    # Compute orientation score per branch per FP
    branch_users = defaultdict(set)
    branch_lang = defaultdict(lambda: {"English": set(), "Marathi": set()})
    branch_source = defaultdict(lambda: {"L": set(), "T": set()})
    user_fp_scores = {}

    for uid, u in users.items():
        bc = u["bc"]
        branch_users[bc].add(uid)
        branch_lang[bc][u["lang"]].add(uid)
        branch_source[bc][u["source"]].add(uid)
        user_fp_scores[uid] = {}
        for fp in FPS:
            opts = u["fp_opts"].get(fp, [])
            if opts:
                user_fp_scores[uid][fp] = sum(opts) / len(opts) / 3.0
            else:
                user_fp_scores[uid][fp] = None

    # Branch FP scores: mean of per-user scores
    branch_fp_scores = {}
    for bc in branch_users:
        branch_fp_scores[bc] = {}
        for fp in FPS:
            vals = [user_fp_scores[uid][fp] for uid in branch_users[bc] if user_fp_scores[uid][fp] is not None]
            branch_fp_scores[bc][fp] = sum(vals) / len(vals) if vals else 0.0

    # Overall FP scores
    overall_fp_scores = {}
    for fp in FPS:
        vals = [user_fp_scores[uid][fp] for uid in user_fp_scores if user_fp_scores[uid][fp] is not None]
        overall_fp_scores[fp] = sum(vals) / len(vals) if vals else 0.0

    return (branch_fp_scores, branch_users, branch_lang, branch_source, overall_fp_scores,
            branch_fp_raw, overall_fp_raw, total_raw, users, user_fp_scores)


def build_html(branch_fp_scores, branch_users, branch_lang, branch_source, overall_fp_scores,
               branch_fp_raw, overall_fp_raw, total_raw, users, user_fp_scores, branch_names):
    j = json.dumps
    all_bcs = sorted(branch_fp_scores.keys())
    total_users = sum(len(v) for v in branch_users.values())
    total_en = sum(len(v["English"]) for v in branch_lang.values())
    total_mr = sum(len(v["Marathi"]) for v in branch_lang.values())
    from_leader = sum(len(v["L"]) for v in branch_source.values())
    from_teacher = sum(len(v["T"]) for v in branch_source.values())

    best_fp = max(FPS, key=lambda fp: overall_fp_scores[fp])

    # ---- Overview FP cards ----
    fp_cards = ""
    for i, fp in enumerate(FPS):
        score = overall_fp_scores[fp]
        fp_cards += (
            '<div class="card" style="border-left:4px solid %s">'
            '<div class="label">%s: %s</div>'
            '<div class="value" style="color:%s">%.3f</div>'
            '<div class="sub">Orientation Score (0-1)</div></div>'
        ) % (FP_COLORS[i], fp, FP_NAMES[fp], FP_COLORS[i], score)

    # ---- Branch FP Profile table ----
    profile_rows = ""
    for bc in all_bcs:
        bname = branch_names.get(bc, "")[:35]
        n_users = len(branch_users[bc])
        en = len(branch_lang[bc]["English"])
        mr = len(branch_lang[bc]["Marathi"])
        nl = len(branch_source[bc]["L"])
        nt = len(branch_source[bc]["T"])
        scores = [branch_fp_scores[bc][fp] for fp in FPS]
        hi_fp = FPS[scores.index(max(scores))] if max(scores) > 0 else "-"
        hi_idx = FPS.index(hi_fp) if hi_fp != "-" else 0

        cells = '<td><strong>%s</strong></td><td style="font-size:11px">%s</td>' % (bc, bname)
        cells += '<td style="text-align:center">%d</td>' % n_users
        cells += '<td style="text-align:center;font-size:10px">%dE/%dM</td>' % (en, mr)
        cells += '<td style="text-align:center;font-size:10px">%dL/%dT</td>' % (nl, nt)

        for idx, fp in enumerate(FPS):
            fp_val = branch_fp_scores[bc][fp]
            intensity = min(fp_val * 0.4, 0.4)
            r, g, b_val = int(FP_COLORS[idx][1:3], 16), int(FP_COLORS[idx][3:5], 16), int(FP_COLORS[idx][5:7], 16)
            bg = "background:rgba(%d,%d,%d,%.2f)" % (r, g, b_val, intensity)
            cells += '<td style="text-align:center;%s"><strong>%.3f</strong></td>' % (bg, fp_val)

        hi_color = FP_COLORS[hi_idx]
        cells += '<td style="text-align:center;font-weight:700;color:%s">%s</td>' % (hi_color, hi_fp)

        profile_rows += "<tr>%s</tr>" % cells

    # ---- Raw counts table ----
    raw_rows = ""
    for bc in all_bcs:
        bname = branch_names.get(bc, "")[:35]
        n_users = len(branch_users[bc])
        total_v = sum(branch_fp_raw[bc].values())
        cells = '<td><strong>%s</strong></td><td style="font-size:11px">%s</td>' % (bc, bname)
        cells += '<td style="text-align:center">%d</td>' % n_users
        cells += '<td style="text-align:center">%d</td>' % total_v

        for idx, fp in enumerate(FPS):
            count = branch_fp_raw[bc][fp]
            pct = count / total_v * 100 if total_v > 0 else 0
            cells += '<td style="text-align:center">%d <span style="font-size:9px;color:#6b7280">(%.1f%%)</span></td>' % (count, pct)

        raw_rows += "<tr>%s</tr>" % cells

    # ---- Chart data ----
    grouped_datasets = j([{
        "label": "%s: %s" % (fp, FP_NAMES[fp]),
        "data": [round(branch_fp_scores[bc][fp], 3) for bc in all_bcs],
        "backgroundColor": FP_COLORS[i],
    } for i, fp in enumerate(FPS)])

    fp_highest_counts = {fp: 0 for fp in FPS}
    for bc in all_bcs:
        scores = [branch_fp_scores[bc][fp] for fp in FPS]
        hi = FPS[scores.index(max(scores))] if max(scores) > 0 else None
        if hi:
            fp_highest_counts[hi] += 1

    branch_radar = {}
    for bc in all_bcs:
        branch_radar[bc] = [round(branch_fp_scores[bc][fp], 3) for fp in FPS]

    # Build table headers
    fp_th_profile = "".join(
        '<th style="text-align:center;color:%s" onclick="sortTbl(%d,&quot;n&quot;,&quot;profileTable&quot;)">%s</th>' % (FP_COLORS[i], 5 + i, fp)
        for i, fp in enumerate(FPS)
    )

    fp_th_raw = "".join(
        '<th style="text-align:center;color:%s">%s</th>' % (FP_COLORS[i], fp)
        for i, fp in enumerate(FPS)
    )

    branch_opts = "".join('<option value="%s">%s</option>' % (bc, bc) for bc in all_bcs)

    today = date.today()

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stage-1 Leader Intent — FP Orientation Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
:root{--bg:#f5f6fa;--card:#fff;--border:#e0e3ea;--text:#1a1a2e;--muted:#6b7280;--blue:#2563eb;--green:#16a34a;--amber:#d97706;--red:#dc2626;--purple:#7c3aed;--teal:#0d9488;--radius:8px;--shadow:0 1px 3px rgba(0,0,0,.08)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.5}
.header{background:linear-gradient(135deg,#4c1d95 0%%,#7c3aed 100%%);color:#fff;padding:20px 32px;display:flex;align-items:center;justify-content:space-between}
.header h1{font-size:22px;font-weight:700}.header .sub{font-size:13px;opacity:.8}
.tabs{display:flex;background:#fff;border-bottom:2px solid var(--border);padding:0 24px;overflow-x:auto;gap:2px;position:sticky;top:0;z-index:100}
.tab{padding:12px 18px;cursor:pointer;font-weight:600;font-size:13px;border-bottom:3px solid transparent;color:var(--muted);white-space:nowrap;transition:.15s}
.tab:hover{color:var(--text);background:#f8f9fb}.tab.active{color:var(--purple);border-bottom-color:var(--purple)}
.content{display:none;padding:24px 32px;max-width:1800px;margin:0 auto}.content.active{display:block}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:24px}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow)}
.card .label{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);margin-bottom:4px}
.card .value{font-size:28px;font-weight:700}.card .sub{font-size:12px;color:var(--muted);margin-top:2px}
table{width:100%%;border-collapse:collapse;background:var(--card);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);font-size:12px}
th{background:#f1f3f8;font-weight:600;text-align:left;padding:8px 10px;border-bottom:2px solid var(--border);position:sticky;top:44px;white-space:nowrap;cursor:pointer}
th:hover{background:#e2e5eb}
td{padding:6px 10px;border-bottom:1px solid var(--border)}tr:hover td{background:#f8f9fc}
.tbl-wrap{overflow-x:auto;border-radius:var(--radius);margin-bottom:24px}
.chart-box{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;box-shadow:var(--shadow);margin-bottom:24px}
.chart-box h3{font-size:15px;margin-bottom:12px}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.section-title{font-size:17px;font-weight:700;margin:24px 0 12px;padding-bottom:8px;border-bottom:2px solid var(--border)}
.info-box{background:#f5f3ff;border:1px solid #c4b5fd;border-radius:var(--radius);padding:14px 18px;margin-bottom:20px;font-size:13px;color:#5b21b6}
.warn-box{background:#fef3c7;border:1px solid #fcd34d;border-radius:var(--radius);padding:14px 18px;margin-bottom:20px;font-size:13px;color:#92400e}
select{padding:6px 10px;border-radius:6px;border:1px solid var(--border);font-size:12px;background:#fff}
@media(max-width:900px){.grid-2{grid-template-columns:1fr}.content{padding:16px}}
@media print{.tabs{display:none}.content{display:block!important;padding:10px}canvas{max-height:300px}}
</style>
</head>
<body>

<div class="header">
<div><h1>Stage-1 Leader Intent — FP Orientation</h1>
<div class="sub">Orientation Score = mean(selectedOption) / 3 per FP section | Leader instrument (7890/104) + Leaders from teacher instrument (1234/103)</div></div>
<div style="text-align:right"><div style="font-size:12px;opacity:.7">Deccan Education Society</div>
<div style="font-size:11px;opacity:.5">Generated: %(today)s</div></div></div>

<div class="tabs">
<div class="tab active" onclick="showTab('overview')">Overview</div>
<div class="tab" onclick="showTab('profile')">Branch FP Profile</div>
<div class="tab" onclick="showTab('radar')">Branch Radar</div>
<div class="tab" onclick="showTab('rawcounts')">Raw Counts</div>
</div>

<!-- OVERVIEW -->
<div id="overview" class="content active">
<div class="cards">
<div class="card"><div class="label">Leaders</div><div class="value" style="color:var(--purple)">%(total_users)d</div><div class="sub">%(total_en)d English + %(total_mr)d Marathi</div></div>
<div class="card"><div class="label">From Leader Survey</div><div class="value" style="color:var(--teal)">%(from_leader)d</div><div class="sub">setCodes 7890 + 104</div></div>
<div class="card"><div class="label">From Teacher Survey</div><div class="value" style="color:var(--amber)">%(from_teacher)d</div><div class="sub">leaders who answered 1234 + 103</div></div>
<div class="card"><div class="label">Branches</div><div class="value">%(n_branches)d</div><div class="sub">with leader intent data</div></div>
<div class="card"><div class="label">Dominant FP</div><div class="value" style="color:var(--green)">%(best_fp)s</div><div class="sub">%(best_fp_score).3f across all leaders</div></div>
%(fp_cards)s
</div>

<div class="info-box">
<strong>FP Orientation Score</strong> = mean(selectedOption) / 3 per FP section. Higher = deeper orientation within that FP.
This ranges from 0 to 1. The Source column shows L (from leader instrument 7890/104) or T (leaders who took teacher survey 1234/103).
Leader instrument has different question counts: FP1=3, FP2=5, FP3=6, FP4=3, FP5=3.
<a href="./12a_stage1_teacher_fp.html" style="font-weight:600">View Teacher Dashboard &rarr;</a>
</div>

<div class="grid-2">
<div class="chart-box"><h3>Overall Orientation Score per FP Section</h3><canvas id="overallBar" height="250"></canvas></div>
<div class="chart-box"><h3>Branches by Dominant FP</h3><canvas id="overallDoughnut" height="250"></canvas></div>
</div>
</div>

<!-- BRANCH FP PROFILE -->
<div id="profile" class="content">
<h2 class="section-title">Branch FP Profile — Orientation Scores (0-1 scale)</h2>
<div class="chart-box"><h3>Orientation Score by Branch (grouped bar)</h3><canvas id="groupedBar" height="500"></canvas></div>
<div class="tbl-wrap"><table id="profileTable">
<thead><tr>
<th onclick="sortTbl(0,'s','profileTable')">Branch</th><th>Name</th>
<th style="text-align:center" onclick="sortTbl(2,'n','profileTable')">Leaders</th>
<th style="text-align:center">Lang</th>
<th style="text-align:center">Source</th>
%(fp_th_profile)s
<th style="text-align:center" onclick="sortTbl(10,'s','profileTable')">Highest</th>
</tr></thead>
<tbody>%(profile_rows)s</tbody>
</table></div>
</div>

<!-- RADAR -->
<div id="radar" class="content">
<h2 class="section-title">Branch FP Radar — Select up to 3 branches</h2>
<div style="margin-bottom:16px">
<select id="r1" onchange="updateRadar()"><option value="">-- Branch 1 --</option>%(branch_opts)s</select>
<select id="r2" onchange="updateRadar()"><option value="">-- Branch 2 --</option>%(branch_opts)s</select>
<select id="r3" onchange="updateRadar()"><option value="">-- Branch 3 --</option>%(branch_opts)s</select>
</div>
<div class="chart-box"><canvas id="radarChart" height="350"></canvas></div>
</div>

<!-- RAW COUNTS -->
<div id="rawcounts" class="content">
<h2 class="section-title">Raw FP Response Counts (Reference Only)</h2>
<div class="warn-box">
<strong>Note:</strong> Raw counts reflect the question structure, not leader orientation.
The leader instrument has FP1=3, FP2=5, FP3=6, FP4=3, FP5=3 questions. Leaders who took the teacher instrument have FP1=4, FP2=4, FP3=5, FP4=5, FP5=4 questions.
These proportions are fixed per user. Use the Orientation Score (Overview / Branch Profile tabs) for meaningful comparisons.
</div>
<div class="tbl-wrap"><table id="rawTable">
<thead><tr>
<th>Branch</th><th>Name</th><th style="text-align:center">Leaders</th><th style="text-align:center">Total</th>
%(fp_th_raw)s
</tr></thead>
<tbody>%(raw_rows)s</tbody>
</table></div>
</div>

<div style="text-align:center;padding:20px;color:var(--muted);font-size:11px">Stage-1 Leader Intent (FP Orientation) | Project Kshitij | Myelin | %(today)s</div>

<script>
function showTab(id){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.content').forEach(c=>c.classList.remove('active'));event.target.classList.add('active');document.getElementById(id).classList.add('active')}
function sortTbl(col,type,tblId){var t=document.getElementById(tblId),b=t.querySelector('tbody'),rows=Array.from(b.querySelectorAll('tr')),dir=t.dataset.d==='a'?'d':'a';t.dataset.d=dir;rows.sort(function(a,b_){var av=a.cells[col].textContent.trim(),bv=b_.cells[col].textContent.trim();if(type==='n'){av=parseFloat(av)||0;bv=parseFloat(bv)||0}return dir==='a'?av>bv?1:-1:av<bv?1:-1});rows.forEach(r=>b.appendChild(r))}

var FPS=%(fps_json)s, FP_NAMES=%(fp_names_json)s, FP_COLORS=%(fp_colors_json)s;

new Chart(document.getElementById('overallBar'),{type:'bar',data:{labels:FP_NAMES,datasets:[{data:%(overall_fp_vals)s,backgroundColor:FP_COLORS}]},options:{plugins:{legend:{display:false}},scales:{y:{min:0,max:1,title:{display:true,text:'Orientation Score (0-1)'}}}}});

new Chart(document.getElementById('overallDoughnut'),{type:'doughnut',data:{labels:FP_NAMES,datasets:[{data:%(doughnut_vals)s,backgroundColor:FP_COLORS}]},options:{plugins:{legend:{position:'right'},title:{display:true,text:'# branches where this FP is dominant'}}}});

new Chart(document.getElementById('groupedBar'),{type:'bar',data:{labels:%(all_bcs_json)s,datasets:%(grouped_datasets)s},options:{indexAxis:'y',scales:{x:{min:0,max:1,title:{display:true,text:'Orientation Score (0-1)'}}},plugins:{legend:{position:'top'}}}});

var BRANCH_RADAR=%(branch_radar_json)s;
var radarChart=new Chart(document.getElementById('radarChart'),{type:'radar',data:{labels:FPS,datasets:[]},options:{scales:{r:{min:0,max:1,ticks:{stepSize:0.2}}}}});
var RC=['#7c3aed','#dc2626','#16a34a'];
function updateRadar(){
  var ds=[];
  ['r1','r2','r3'].forEach(function(id,i){
    var bc=document.getElementById(id).value;
    if(bc&&BRANCH_RADAR[bc])ds.push({label:bc,data:BRANCH_RADAR[bc],backgroundColor:'transparent',borderColor:RC[i],borderWidth:2,pointRadius:4});
  });
  radarChart.data.datasets=ds;radarChart.update();
}
</script>
</body></html>"""

    return html % {
        "today": today,
        "total_users": total_users,
        "total_en": total_en,
        "total_mr": total_mr,
        "from_leader": from_leader,
        "from_teacher": from_teacher,
        "n_branches": len(all_bcs),
        "best_fp": best_fp,
        "best_fp_score": overall_fp_scores[best_fp],
        "fp_cards": fp_cards,
        "fp_th_profile": fp_th_profile,
        "fp_th_raw": fp_th_raw,
        "profile_rows": profile_rows,
        "raw_rows": raw_rows,
        "branch_opts": branch_opts,
        "fps_json": j(FPS),
        "fp_names_json": j(["%s: %s" % (fp, FP_NAMES[fp]) for fp in FPS]),
        "fp_colors_json": j(FP_COLORS),
        "overall_fp_vals": j([round(overall_fp_scores[fp], 3) for fp in FPS]),
        "doughnut_vals": j([fp_highest_counts[fp] for fp in FPS]),
        "all_bcs_json": j(all_bcs),
        "grouped_datasets": grouped_datasets,
        "branch_radar_json": j(branch_radar),
    }


def main():
    print("Loading Stage-1 Leader intent data (FP Orientation)...")
    (branch_fp_scores, branch_users, branch_lang, branch_source, overall_fp_scores,
     branch_fp_raw, overall_fp_raw, total_raw, users, user_fp_scores) = load_data()
    branch_names = load_branch_names()
    total_users = sum(len(v) for v in branch_users.values())
    from_l = sum(len(v["L"]) for v in branch_source.values())
    from_t = sum(len(v["T"]) for v in branch_source.values())
    print("  %d leaders (%d from leader survey + %d from teacher survey)" % (total_users, from_l, from_t))
    print("  %d branches" % len(branch_fp_scores))
    for fp in FPS:
        print("  %s Orientation = %.3f" % (fp, overall_fp_scores[fp]))
    html = build_html(branch_fp_scores, branch_users, branch_lang, branch_source, overall_fp_scores,
                      branch_fp_raw, overall_fp_raw, total_raw, users, user_fp_scores, branch_names)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(html)
    print("  Written: %s (%d KB)" % (OUT_PATH, os.path.getsize(OUT_PATH) // 1024))


if __name__ == "__main__":
    main()
