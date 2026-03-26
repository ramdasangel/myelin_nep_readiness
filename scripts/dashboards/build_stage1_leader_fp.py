#!/usr/bin/env python3
"""
Stage-1 Leader Intent — FP1 to FP5 Distribution Dashboard
setCodes: 7890 (English) + 104 (Marathi)
Also includes leaders who answered teacher instrument (1234 + 103).
Shows raw FP response counts per branch.
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

GOAL_FP = {
    # Teacher instrument goals (leaders also answered these)
    "Each Child is Unique": "FP1", "Competency-Based Learning": "FP2",
    "Teacher Upskilling": "FP3", "Diagnosing Learning Levels": "FP4",
    "Parent–Teacher Collaboration": "FP5", "Parent-Teacher Collaboration": "FP5",
    "प्रत्येक मूल वेगळे आहे": "FP1", "क्षमताधिष्ठित अध्ययन": "FP2", "क्षमताधिष्टित अध्ययन": "FP2",
    "शिक्षक कौशल्यवृद्धी": "FP3", "शिक्षक कौशल्यवृध्दी": "FP3",
    "अध्ययन स्तरांचे निदान": "FP4",
    "पालक - शिक्षक सहयोग": "FP5", "पालक -शिक्षक सहयोग": "FP5", "पालक - शिक्षक सहभागीता": "FP5",
    # Leader instrument goals
    "Learning Progress Monitoring": "FP1", "Student Engagement": "FP1", "Understanding Learners": "FP1",
    "Classroom Observation": "FP2", "Activity Design": "FP2", "Lesson Planning": "FP2", "Task Rigor": "FP2",
    "Teacher Support": "FP3", "Teacher Coaching": "FP3", "Innovation in Teaching": "FP3",
    "Teacher Development": "FP3", "Team Leadership": "FP3", "School Improvement": "FP3",
    "Data Analysis": "FP4", "Instructional Review": "FP4", "Learning Data Analysis": "FP4",
    "Parent Engagement": "FP5", "Parent Communication": "FP5", "School Communication": "FP5",
}

# All 4 intent files — we filter by role=Leader from CSV
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
    branch_fp_votes = defaultdict(lambda: {fp: 0 for fp in FPS})
    branch_users = defaultdict(set)
    branch_lang = defaultdict(lambda: {"English": set(), "Marathi": set()})
    # Track which instrument leaders came from
    branch_source = defaultdict(lambda: {"leader_instrument": set(), "teacher_instrument": set()})
    overall_fp = {fp: 0 for fp in FPS}
    total_responses = 0

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
                # Only include leaders (from CSV role column)
                if role != "Leader":
                    continue
                fp = GOAL_FP.get(goal)
                if not fp:
                    continue

                branch_fp_votes[bc][fp] += 1
                branch_users[bc].add(uid)
                branch_lang[bc][lang].add(uid)
                overall_fp[fp] += 1
                total_responses += 1

                if is_leader_file:
                    branch_source[bc]["leader_instrument"].add(uid)
                else:
                    branch_source[bc]["teacher_instrument"].add(uid)

    return branch_fp_votes, branch_users, branch_lang, branch_source, overall_fp, total_responses


def build_html(branch_fp_votes, branch_users, branch_lang, branch_source, overall_fp, total_responses, branch_names):
    j = json.dumps
    all_bcs = sorted(branch_fp_votes.keys())
    total_users = sum(len(v) for v in branch_users.values())
    total_en = sum(len(v["English"]) for v in branch_lang.values())
    total_mr = sum(len(v["Marathi"]) for v in branch_lang.values())
    from_teacher_inst = sum(len(v["teacher_instrument"]) for v in branch_source.values())
    from_leader_inst = sum(len(v["leader_instrument"]) for v in branch_source.values())

    # Table rows
    table_rows = ""
    for bc in all_bcs:
        bname = branch_names.get(bc, "")[:35]
        n = len(branch_users[bc])
        total_v = sum(branch_fp_votes[bc].values())
        en = len(branch_lang[bc]["English"])
        mr = len(branch_lang[bc]["Marathi"])
        from_t = len(branch_source[bc]["teacher_instrument"])
        from_l = len(branch_source[bc]["leader_instrument"])

        cells = f'<td><strong>{bc}</strong></td><td style="font-size:11px">{bname}</td>'
        cells += f'<td style="text-align:center">{n}</td>'
        cells += f'<td style="text-align:center;font-size:10px">{en}E/{mr}M</td>'
        cells += f'<td style="text-align:center;font-size:10px">{from_l}L/{from_t}T</td>'

        for i, fp in enumerate(FPS):
            count = branch_fp_votes[bc][fp]
            pct = count / total_v * 100 if total_v > 0 else 0
            intensity = min(pct / 30, 0.35)
            r, g, b_val = int(FP_COLORS[i][1:3], 16), int(FP_COLORS[i][3:5], 16), int(FP_COLORS[i][5:7], 16)
            bg = f"background:rgba({r},{g},{b_val},{intensity:.2f})"
            cells += f'<td style="text-align:center;{bg}"><strong>{count}</strong><br><span style="font-size:9px;color:#6b7280">{pct:.1f}%</span></td>'

        table_rows += f"<tr>{cells}</tr>"

    # Chart data
    overall_vals = j([overall_fp[fp] for fp in FPS])
    stacked = j([{
        "label": f"{fp}: {FP_NAMES[fp]}",
        "data": [branch_fp_votes[bc][fp] for bc in all_bcs],
        "backgroundColor": FP_COLORS[i],
    } for i, fp in enumerate(FPS)])
    pct_stacked = j([{
        "label": fp,
        "data": [round(branch_fp_votes[bc][fp] / max(sum(branch_fp_votes[bc].values()), 1) * 100, 1) for bc in all_bcs],
        "backgroundColor": FP_COLORS[i],
    } for i, fp in enumerate(FPS)])

    branch_radar = {}
    for bc in all_bcs:
        total = sum(branch_fp_votes[bc].values()) or 1
        branch_radar[bc] = [round(branch_fp_votes[bc][fp] / total * 100, 1) for fp in FPS]

    fp_th_branch = "".join(
        '<th style="text-align:center;color:%s" onclick="sortTbl(%d,&quot;n&quot;)">%s</th>' % (FP_COLORS[i], 5+i, fp)
        for i, fp in enumerate(FPS)
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stage-1 Leader Intent — FP Distribution</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
:root{{--bg:#f5f6fa;--card:#fff;--border:#e0e3ea;--text:#1a1a2e;--muted:#6b7280;--blue:#2563eb;--green:#16a34a;--amber:#d97706;--red:#dc2626;--purple:#7c3aed;--teal:#0d9488;--radius:8px;--shadow:0 1px 3px rgba(0,0,0,.08)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.5}}
.header{{background:linear-gradient(135deg,#4c1d95 0%,#7c3aed 100%);color:#fff;padding:20px 32px;display:flex;align-items:center;justify-content:space-between}}
.header h1{{font-size:22px;font-weight:700}}.header .sub{{font-size:13px;opacity:.8}}
.tabs{{display:flex;background:#fff;border-bottom:2px solid var(--border);padding:0 24px;overflow-x:auto;gap:2px;position:sticky;top:0;z-index:100}}
.tab{{padding:12px 18px;cursor:pointer;font-weight:600;font-size:13px;border-bottom:3px solid transparent;color:var(--muted);white-space:nowrap;transition:.15s}}
.tab:hover{{color:var(--text);background:#f8f9fb}}.tab.active{{color:var(--purple);border-bottom-color:var(--purple)}}
.content{{display:none;padding:24px 32px;max-width:1800px;margin:0 auto}}.content.active{{display:block}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:24px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow)}}
.card .label{{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);margin-bottom:4px}}
.card .value{{font-size:28px;font-weight:700}}.card .sub{{font-size:12px;color:var(--muted);margin-top:2px}}
table{{width:100%;border-collapse:collapse;background:var(--card);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);font-size:12px}}
th{{background:#f1f3f8;font-weight:600;text-align:left;padding:8px 10px;border-bottom:2px solid var(--border);position:sticky;top:44px;white-space:nowrap;cursor:pointer}}
th:hover{{background:#e2e5eb}}
td{{padding:6px 10px;border-bottom:1px solid var(--border)}}tr:hover td{{background:#f8f9fc}}
.tbl-wrap{{overflow-x:auto;border-radius:var(--radius);margin-bottom:24px}}
.chart-box{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;box-shadow:var(--shadow);margin-bottom:24px}}
.chart-box h3{{font-size:15px;margin-bottom:12px}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.section-title{{font-size:17px;font-weight:700;margin:24px 0 12px;padding-bottom:8px;border-bottom:2px solid var(--border)}}
.info-box{{background:#f5f3ff;border:1px solid #c4b5fd;border-radius:var(--radius);padding:14px 18px;margin-bottom:20px;font-size:13px;color:#5b21b6}}
select{{padding:6px 10px;border-radius:6px;border:1px solid var(--border);font-size:12px;background:#fff}}
@media(max-width:900px){{.grid-2{{grid-template-columns:1fr}}.content{{padding:16px}}}}
@media print{{.tabs{{display:none}}.content{{display:block!important;padding:10px}}canvas{{max-height:300px}}}}
</style>
</head>
<body>

<div class="header">
<div><h1>Stage-1 Leader Intent — FP1 to FP5</h1>
<div class="sub">Raw Response Counts | setCodes: 7890 + 104 (leader) + 1234 + 103 (leaders who took teacher survey)</div></div>
<div style="text-align:right"><div style="font-size:12px;opacity:.7">Deccan Education Society</div>
<div style="font-size:11px;opacity:.5">Generated: {date.today()}</div></div></div>

<div class="tabs">
<div class="tab active" onclick="showTab('overview')">Overview</div>
<div class="tab" onclick="showTab('branches')">Branch Detail</div>
<div class="tab" onclick="showTab('radar')">Branch Radar</div>
</div>

<!-- OVERVIEW -->
<div id="overview" class="content active">
<div class="cards">
<div class="card"><div class="label">Leaders</div><div class="value" style="color:var(--purple)">{total_users}</div><div class="sub">{total_en} English + {total_mr} Marathi</div></div>
<div class="card"><div class="label">From Leader Survey</div><div class="value" style="color:var(--teal)">{from_leader_inst}</div><div class="sub">setCodes 7890 + 104</div></div>
<div class="card"><div class="label">From Teacher Survey</div><div class="value" style="color:var(--amber)">{from_teacher_inst}</div><div class="sub">leaders who answered 1234 + 103</div></div>
<div class="card"><div class="label">Branches</div><div class="value">{len(all_bcs)}</div><div class="sub">with leader intent data</div></div>
<div class="card"><div class="label">Total Responses</div><div class="value">{total_responses:,}</div><div class="sub">FP-tagged answer selections</div></div>
{"".join(f'<div class="card" style="border-left:4px solid {FP_COLORS[i]}"><div class="label">{fp}: {FP_NAMES[fp]}</div><div class="value" style="color:{FP_COLORS[i]}">{overall_fp[fp]:,}</div><div class="sub">{overall_fp[fp]/total_responses*100:.1f}% of responses</div></div>' for i, fp in enumerate(FPS))}
</div>

<div class="info-box">
<strong>Raw FP counts</strong> for all leaders (role=Leader from CSV), including those who answered the teacher instrument.
The "Source" column in the branch table shows how many came from the Leader instrument (L) vs Teacher instrument (T).
<a href="./12a_stage1_teacher_fp.html" style="font-weight:600">View Teacher Dashboard →</a>
</div>

<div class="grid-2">
<div class="chart-box"><h3>Overall FP Distribution (raw counts)</h3><canvas id="overallBar" height="250"></canvas></div>
<div class="chart-box"><h3>FP Proportion (%)</h3><canvas id="overallDoughnut" height="250"></canvas></div>
</div>

<div class="chart-box"><h3>FP Distribution by Branch (stacked counts)</h3><canvas id="stackedChart" height="400"></canvas></div>
<div class="chart-box"><h3>FP Distribution by Branch (% of branch total)</h3><canvas id="pctChart" height="400"></canvas></div>
</div>

<!-- BRANCHES -->
<div id="branches" class="content">
<h2 class="section-title">Branch Detail — Raw FP Response Counts (Leaders)</h2>
<div class="tbl-wrap"><table id="branchTable">
<thead><tr>
<th onclick="sortTbl(0,'s')">Branch</th><th>Name</th><th style="text-align:center" onclick="sortTbl(2,'n')">Leaders</th><th style="text-align:center">Lang</th><th style="text-align:center">Source</th>
{fp_th_branch}
</tr></thead>
<tbody>{table_rows}</tbody>
</table></div>
</div>

<!-- RADAR -->
<div id="radar" class="content">
<h2 class="section-title">Branch FP Radar — Select up to 3 branches</h2>
<div style="margin-bottom:16px">
<select id="r1" onchange="updateRadar()"><option value="">— Branch 1 —</option>{"".join(f'<option value="{bc}">{bc}</option>' for bc in all_bcs)}</select>
<select id="r2" onchange="updateRadar()"><option value="">— Branch 2 —</option>{"".join(f'<option value="{bc}">{bc}</option>' for bc in all_bcs)}</select>
<select id="r3" onchange="updateRadar()"><option value="">— Branch 3 —</option>{"".join(f'<option value="{bc}">{bc}</option>' for bc in all_bcs)}</select>
</div>
<div class="chart-box"><canvas id="radarChart" height="350"></canvas></div>
</div>

<div style="text-align:center;padding:20px;color:var(--muted);font-size:11px">Stage-1 Leader Intent | Project Kshitij | Myelin | {date.today()}</div>

<script>
function showTab(id){{document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.content').forEach(c=>c.classList.remove('active'));event.target.classList.add('active');document.getElementById(id).classList.add('active')}}
function sortTbl(col,type){{var t=document.getElementById('branchTable'),b=t.querySelector('tbody'),rows=Array.from(b.querySelectorAll('tr')),dir=t.dataset.d==='a'?'d':'a';t.dataset.d=dir;rows.sort(function(a,b_){{var av=a.cells[col].textContent.trim(),bv=b_.cells[col].textContent.trim();if(type==='n'){{av=parseFloat(av)||0;bv=parseFloat(bv)||0}}return dir==='a'?av>bv?1:-1:av<bv?1:-1}});rows.forEach(r=>b.appendChild(r))}}

var FPS={j(FPS)},FP_NAMES={j([f"{fp}: {FP_NAMES[fp]}" for fp in FPS])},FP_COLORS={j(FP_COLORS)};

new Chart(document.getElementById('overallBar'),{{type:'bar',data:{{labels:FP_NAMES,datasets:[{{data:{overall_vals},backgroundColor:FP_COLORS}}]}},options:{{plugins:{{legend:{{display:false}}}}}}}});
new Chart(document.getElementById('overallDoughnut'),{{type:'doughnut',data:{{labels:FP_NAMES,datasets:[{{data:{overall_vals},backgroundColor:FP_COLORS}}]}},options:{{plugins:{{legend:{{position:'right'}}}}}}}});
new Chart(document.getElementById('stackedChart'),{{type:'bar',data:{{labels:{j(all_bcs)},datasets:{stacked}}},options:{{indexAxis:'y',scales:{{x:{{stacked:true}},y:{{stacked:true}}}},plugins:{{legend:{{position:'top'}}}}}}}});
new Chart(document.getElementById('pctChart'),{{type:'bar',data:{{labels:{j(all_bcs)},datasets:{pct_stacked}}},options:{{indexAxis:'y',scales:{{x:{{stacked:true,max:100}},y:{{stacked:true}}}},plugins:{{legend:{{position:'top'}}}}}}}});

var BRANCH_RADAR={j(branch_radar)};
var radarChart=new Chart(document.getElementById('radarChart'),{{type:'radar',data:{{labels:FPS,datasets:[]}},options:{{scales:{{r:{{min:0,max:40}}}}}}}});
var RC=['#7c3aed','#dc2626','#16a34a'];
function updateRadar(){{
  var ds=[];
  ['r1','r2','r3'].forEach(function(id,i){{
    var bc=document.getElementById(id).value;
    if(bc&&BRANCH_RADAR[bc])ds.push({{label:bc,data:BRANCH_RADAR[bc],backgroundColor:'transparent',borderColor:RC[i],borderWidth:2,pointRadius:4}});
  }});
  radarChart.data.datasets=ds;radarChart.update();
}}
</script>
</body></html>"""
    return html


def main():
    print("Loading Stage-1 Leader intent data...")
    branch_fp, branch_users, branch_lang, branch_source, overall_fp, total_resp = load_data()
    branch_names = load_branch_names()
    total_users = sum(len(v) for v in branch_users.values())
    from_t = sum(len(v["teacher_instrument"]) for v in branch_source.values())
    from_l = sum(len(v["leader_instrument"]) for v in branch_source.values())
    print(f"  {total_users} leaders ({from_l} from leader survey + {from_t} from teacher survey)")
    print(f"  {len(branch_fp)} branches, {total_resp:,} responses")
    html = build_html(branch_fp, branch_users, branch_lang, branch_source, overall_fp, total_resp, branch_names)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(html)
    print(f"  Written: {OUT_PATH} ({os.path.getsize(OUT_PATH) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
