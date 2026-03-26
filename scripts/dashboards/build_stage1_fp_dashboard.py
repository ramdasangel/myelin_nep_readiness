#!/usr/bin/env python3
"""
Stage-1 Intent FP Distribution Dashboard
Teacher (1234 + 103) and Leader (7890 + 104) orientation data.
Shows FP1-FP5 distribution per branch and overall.
"""

import csv
import json
import os
import sys
from collections import defaultdict
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INTENT_DIR = os.path.join(BASE, "data", "extracted", "intent")
OUT_PATH = os.path.join(BASE, "output", "dashboards", "12_stage1_fp_distribution.html")

FP_NAMES = {
    "FP1": "Each Child is Unique",
    "FP2": "Holistic & Experiential Learning",
    "FP3": "Reflective Practitioner",
    "FP4": "Assessment for Learning",
    "FP5": "Collaboration & Community",
}
FPS = ["FP1", "FP2", "FP3", "FP4", "FP5"]
FP_COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"]

# Goal → FP mappings
TEACHER_GOAL_FP = {
    "Each Child is Unique": "FP1", "Competency-Based Learning": "FP2",
    "Teacher Upskilling": "FP3", "Diagnosing Learning Levels": "FP4",
    "Parent–Teacher Collaboration": "FP5", "Parent-Teacher Collaboration": "FP5",
    "प्रत्येक मूल वेगळे आहे": "FP1", "क्षमताधिष्ठित अध्ययन": "FP2", "क्षमताधिष्टित अध्ययन": "FP2",
    "शिक्षक कौशल्यवृद्धी": "FP3", "शिक्षक कौशल्यवृध्दी": "FP3",
    "अध्ययन स्तरांचे निदान": "FP4",
    "पालक - शिक्षक सहयोग": "FP5", "पालक -शिक्षक सहयोग": "FP5", "पालक - शिक्षक सहभागीता": "FP5",
}
LEADER_GOAL_FP = {
    "Learning Progress Monitoring": "FP1", "Student Engagement": "FP1", "Understanding Learners": "FP1",
    "Classroom Observation": "FP2", "Activity Design": "FP2", "Lesson Planning": "FP2", "Task Rigor": "FP2",
    "Teacher Support": "FP3", "Teacher Coaching": "FP3", "Innovation in Teaching": "FP3",
    "Teacher Development": "FP3", "Team Leadership": "FP3", "School Improvement": "FP3",
    "Data Analysis": "FP4", "Instructional Review": "FP4", "Learning Data Analysis": "FP4",
    "Parent Engagement": "FP5", "Parent Communication": "FP5", "School Communication": "FP5",
    # Marathi leader goals map to same FPs via teacher mapping
    **TEACHER_GOAL_FP,
}

# Note: role is taken from the CSV 'role' column, NOT the filename.
# Some leaders answered the teacher instrument (1234/103) — their role
# is correctly recorded as "Leader" in the CSV data.
FILES = [
    ("intent_teacher_english_responses.csv", "English", TEACHER_GOAL_FP),
    ("intent_teacher_marathi_responses.csv", "Marathi", TEACHER_GOAL_FP),
    ("intent_leader_english_responses.csv", "English", LEADER_GOAL_FP),
    ("intent_leader_marathi_responses.csv", "Marathi", LEADER_GOAL_FP),
]

# Branch name lookup
def load_branch_names():
    path = os.path.join(BASE, "output", "reports", "sri_unified.json")
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        return {bc: b.get("branchName", "") for bc, b in data.get("branches", {}).items()}
    return {}


def load_data():
    """Load per-user FP vote data from intent CSVs."""
    # {userId: {bc, role, lang, fp_votes: {FP: count}, responses: count}}
    users = {}

    for fname, lang, goal_map in FILES:
        fpath = os.path.join(INTENT_DIR, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath) as f:
            for row in csv.DictReader(f):
                bc = row.get("branchCode", "").strip()
                uid = row.get("userId", "")
                goal = row.get("goal", "").strip()
                # Use role from CSV data — leaders who took teacher survey
                # are correctly identified as "Leader" in the role column
                csv_role = row.get("role", "").strip()
                if not bc or bc.startswith("m") or not uid:
                    continue
                fp = goal_map.get(goal)
                if not fp:
                    continue

                if uid not in users:
                    users[uid] = {"bc": bc, "role": csv_role, "lang": lang, "fp_votes": defaultdict(int), "responses": 0}
                users[uid]["fp_votes"][fp] += 1
                users[uid]["responses"] += 1

    return users


def build_html(users, branch_names):
    # Separate teachers and leaders
    teachers = {uid: u for uid, u in users.items() if u["role"] == "Teacher"}
    leaders = {uid: u for uid, u in users.items() if u["role"] == "Leader"}

    all_bcs = sorted(set(u["bc"] for u in users.values()))

    def get_dominant_fp(u):
        if not u["fp_votes"]:
            return "FP1"
        return max(u["fp_votes"], key=u["fp_votes"].get)

    # ── Overall FP distribution ──
    def fp_dist(user_set):
        dist = {fp: 0 for fp in FPS}
        for u in user_set.values():
            dist[get_dominant_fp(u)] += 1
        return dist

    t_dist = fp_dist(teachers)
    l_dist = fp_dist(leaders)

    # ── Per-branch FP distribution ──
    def branch_fp_data(user_set):
        bd = defaultdict(lambda: {fp: 0 for fp in FPS})
        bc_counts = defaultdict(int)
        for u in user_set.values():
            bc = u["bc"]
            bd[bc][get_dominant_fp(u)] += 1
            bc_counts[bc] += 1
        return bd, bc_counts

    t_branch, t_bc_counts = branch_fp_data(teachers)
    l_branch, l_bc_counts = branch_fp_data(leaders)

    # ── Per-branch per-FP mean ADV (Aspirational Depth Vector) ──
    def branch_adv(user_set):
        # branch → fp → [adv scores]
        adv = defaultdict(lambda: defaultdict(list))
        for u in user_set.values():
            for fp in FPS:
                vals = []
                # ADV = mean(selectedOption) / 3 → but we only have fp_votes count
                # Use proportion of votes going to this FP as a proxy
                total = sum(u["fp_votes"].values())
                adv[u["bc"]][fp].append(u["fp_votes"].get(fp, 0) / total if total > 0 else 0)
        result = {}
        for bc in adv:
            result[bc] = {fp: round(sum(adv[bc][fp]) / len(adv[bc][fp]), 4) if adv[bc][fp] else 0 for fp in FPS}
        return result

    t_adv = branch_adv(teachers)
    l_adv = branch_adv(leaders)

    # ── Language split ──
    t_en = sum(1 for u in teachers.values() if u["lang"] == "English")
    t_mr = sum(1 for u in teachers.values() if u["lang"] == "Marathi")
    l_en = sum(1 for u in leaders.values() if u["lang"] == "English")
    l_mr = sum(1 for u in leaders.values() if u["lang"] == "Marathi")

    # ── Branch table rows ──
    def branch_table_rows(branch_data, bc_counts, adv_data, role):
        rows = ""
        for bc in all_bcs:
            n = bc_counts.get(bc, 0)
            if n == 0:
                continue
            bname = branch_names.get(bc, "")[:35]
            fp_cells = ""
            dominant = ""
            max_pct = 0
            for i, fp in enumerate(FPS):
                count = branch_data.get(bc, {}).get(fp, 0)
                pct = count / n * 100 if n > 0 else 0
                adv_val = adv_data.get(bc, {}).get(fp, 0)
                bg = f"background:rgba({int(FP_COLORS[i][1:3],16)},{int(FP_COLORS[i][3:5],16)},{int(FP_COLORS[i][5:7],16)},{min(pct/60,0.3):.2f})"
                fp_cells += f'<td style="text-align:center;{bg}"><strong>{count}</strong><br><span style="font-size:9px;color:var(--muted)">{pct:.0f}%</span></td>'
                if pct > max_pct:
                    max_pct = pct
                    dominant = fp

            dom_color = FP_COLORS[FPS.index(dominant)] if dominant else "#6b7280"
            rows += f'<tr><td><strong>{bc}</strong></td><td style="font-size:11px">{bname}</td><td style="text-align:center">{n}</td>{fp_cells}<td style="text-align:center;color:{dom_color};font-weight:700">{dominant}</td></tr>'
        return rows

    t_rows = branch_table_rows(t_branch, t_bc_counts, t_adv, "Teacher")
    l_rows = branch_table_rows(l_branch, l_bc_counts, l_adv, "Leader")

    # ── Chart data ──
    j = json.dumps

    # Overall doughnut data
    t_dist_vals = j([t_dist[fp] for fp in FPS])
    l_dist_vals = j([l_dist[fp] for fp in FPS])

    # Per-branch stacked bar (teacher)
    t_chart_bcs = [bc for bc in all_bcs if t_bc_counts.get(bc, 0) > 0]
    l_chart_bcs = [bc for bc in all_bcs if l_bc_counts.get(bc, 0) > 0]

    def stacked_datasets(branch_data, chart_bcs):
        datasets = []
        for i, fp in enumerate(FPS):
            datasets.append({
                "label": f"{fp}: {FP_NAMES[fp]}",
                "data": [branch_data.get(bc, {}).get(fp, 0) for bc in chart_bcs],
                "backgroundColor": FP_COLORS[i],
            })
        return j(datasets)

    t_stacked = stacked_datasets(t_branch, t_chart_bcs)
    l_stacked = stacked_datasets(l_branch, l_chart_bcs)

    # Percentage stacked bar
    def pct_datasets(branch_data, bc_counts, chart_bcs):
        datasets = []
        for i, fp in enumerate(FPS):
            datasets.append({
                "label": fp,
                "data": [round(branch_data.get(bc, {}).get(fp, 0) / bc_counts.get(bc, 1) * 100, 1) for bc in chart_bcs],
                "backgroundColor": FP_COLORS[i],
            })
        return j(datasets)

    t_pct = pct_datasets(t_branch, t_bc_counts, t_chart_bcs)
    l_pct = pct_datasets(l_branch, l_bc_counts, l_chart_bcs)

    # Comparison: teacher vs leader per FP (overall %)
    t_total = sum(t_dist.values()) or 1
    l_total = sum(l_dist.values()) or 1
    comparison_t = j([round(t_dist[fp] / t_total * 100, 1) for fp in FPS])
    comparison_l = j([round(l_dist[fp] / l_total * 100, 1) for fp in FPS])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stage-1 Intent — FP Distribution Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
:root{{--bg:#f5f6fa;--card:#fff;--border:#e0e3ea;--text:#1a1a2e;--muted:#6b7280;
--blue:#2563eb;--green:#16a34a;--amber:#d97706;--red:#dc2626;--purple:#7c3aed;--teal:#0d9488;
--radius:8px;--shadow:0 1px 3px rgba(0,0,0,.08)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.5}}
.header{{background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);color:#fff;padding:20px 32px;display:flex;align-items:center;justify-content:space-between}}
.header h1{{font-size:22px;font-weight:700}}.header .sub{{font-size:13px;opacity:.8}}
.tabs{{display:flex;background:#fff;border-bottom:2px solid var(--border);padding:0 24px;overflow-x:auto;gap:2px;position:sticky;top:0;z-index:100}}
.tab{{padding:12px 18px;cursor:pointer;font-weight:600;font-size:13px;border-bottom:3px solid transparent;color:var(--muted);white-space:nowrap;transition:.15s}}
.tab:hover{{color:var(--text);background:#f8f9fb}}.tab.active{{color:var(--blue);border-bottom-color:var(--blue)}}
.content{{display:none;padding:24px 32px;max-width:1800px;margin:0 auto}}.content.active{{display:block}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:24px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow)}}
.card .label{{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);margin-bottom:4px}}
.card .value{{font-size:28px;font-weight:700}}.card .sub{{font-size:12px;color:var(--muted);margin-top:2px}}
table{{width:100%;border-collapse:collapse;background:var(--card);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);font-size:12px}}
th{{background:#f1f3f8;font-weight:600;text-align:left;padding:8px 10px;border-bottom:2px solid var(--border);position:sticky;top:44px;white-space:nowrap}}
td{{padding:6px 10px;border-bottom:1px solid var(--border)}}tr:hover td{{background:#f8f9fc}}
.tbl-wrap{{overflow-x:auto;border-radius:var(--radius);margin-bottom:24px}}
.chart-box{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;box-shadow:var(--shadow);margin-bottom:24px}}
.chart-box h3{{font-size:15px;margin-bottom:12px;color:var(--text)}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.grid-3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px}}
.section-title{{font-size:17px;font-weight:700;margin:24px 0 12px;padding-bottom:8px;border-bottom:2px solid var(--border)}}
.info-box{{background:#eff6ff;border:1px solid #bfdbfe;border-radius:var(--radius);padding:14px 18px;margin-bottom:20px;font-size:13px;color:#1e40af}}
.fp-legend{{display:flex;gap:16px;flex-wrap:wrap;margin:12px 0}}
.fp-dot{{width:12px;height:12px;border-radius:50%;display:inline-block;margin-right:4px;vertical-align:middle}}
@media(max-width:900px){{.grid-2,.grid-3{{grid-template-columns:1fr}}.content{{padding:16px}}}}
@media print{{.tabs{{display:none}}.content{{display:block!important;padding:10px}}canvas{{max-height:300px}}.chart-box{{page-break-inside:avoid}}}}
</style>
</head>
<body>

<div class="header">
<div><h1>Stage-1 Intent — FP1 to FP5 Distribution</h1>
<div class="sub">Teacher Orientation (1234 + 103) & Leader Orientation (7890 + 104)</div></div>
<div style="text-align:right"><div style="font-size:12px;opacity:.7">Deccan Education Society</div>
<div style="font-size:11px;opacity:.5">Generated: {date.today()}</div></div></div>

<div class="tabs">
<div class="tab active" onclick="showTab('overview')">Overview</div>
<div class="tab" onclick="showTab('teacher')">Teacher Detail</div>
<div class="tab" onclick="showTab('leader')">Leader Detail</div>
<div class="tab" onclick="showTab('compare')">Teacher vs Leader</div>
</div>

<!-- ═══ OVERVIEW ═══ -->
<div id="overview" class="content active">

<div class="cards">
<div class="card"><div class="label">Total Teachers</div><div class="value" style="color:var(--blue)">{len(teachers)}</div>
<div class="sub">{t_en} English + {t_mr} Marathi</div></div>
<div class="card"><div class="label">Total Leaders</div><div class="value" style="color:var(--purple)">{len(leaders)}</div>
<div class="sub">{l_en} English + {l_mr} Marathi</div></div>
<div class="card"><div class="label">Branches</div><div class="value" style="color:var(--teal)">{len(all_bcs)}</div>
<div class="sub">M001–M038</div></div>
<div class="card"><div class="label">Total Responses</div><div class="value">{sum(u['responses'] for u in users.values()):,}</div>
<div class="sub">across all instruments</div></div>
{"".join(f'<div class="card" style="border-left:4px solid {FP_COLORS[i]}"><div class="label">{fp}</div><div class="value" style="color:{FP_COLORS[i]}">{t_dist[fp]+l_dist[fp]}</div><div class="sub">{FP_NAMES[fp]}<br>T:{t_dist[fp]} L:{l_dist[fp]}</div></div>' for i, fp in enumerate(FPS))}
</div>

<div class="info-box">
<strong>FP Distribution</strong> shows which Foundational Philosophy each respondent naturally gravitates towards, based on their dominant response pattern.
Each user's answers are tagged with FP1-FP5. The FP with the most votes = their dominant orientation.
EN and MR responses are combined — they measure the same construct.
</div>

<div class="fp-legend">
{"".join(f'<span><span class="fp-dot" style="background:{FP_COLORS[i]}"></span>{fp}: {FP_NAMES[fp]}</span>' for i, fp in enumerate(FPS))}
</div>

<div class="grid-2">
<div class="chart-box"><h3>Teacher FP Distribution ({len(teachers)} respondents)</h3><canvas id="tDoughnut" height="250"></canvas></div>
<div class="chart-box"><h3>Leader FP Distribution ({len(leaders)} respondents)</h3><canvas id="lDoughnut" height="250"></canvas></div>
</div>

<div class="chart-box"><h3>Teacher vs Leader — FP Comparison (%)</h3><canvas id="compareBar" height="200"></canvas></div>
</div>

<!-- ═══ TEACHER DETAIL ═══ -->
<div id="teacher" class="content">
<h2 class="section-title">Teacher FP Distribution by Branch ({len(teachers)} teachers across {len(t_chart_bcs)} branches)</h2>

<div class="grid-2">
<div class="chart-box"><h3>FP Count per Branch (Stacked)</h3><canvas id="tStacked" height="450"></canvas></div>
<div class="chart-box"><h3>FP Percentage per Branch (%)</h3><canvas id="tPct" height="450"></canvas></div>
</div>

<h3 class="section-title" style="font-size:15px">Branch Detail Table</h3>
<div class="tbl-wrap"><table>
<thead><tr>
<th>Branch</th><th>Name</th><th style="text-align:center">N</th>
{"".join(f'<th style="text-align:center;color:{FP_COLORS[i]}">{fp}</th>' for i, fp in enumerate(FPS))}
<th style="text-align:center">Dominant</th>
</tr></thead>
<tbody>{t_rows}</tbody>
</table></div>
</div>

<!-- ═══ LEADER DETAIL ═══ -->
<div id="leader" class="content">
<h2 class="section-title">Leader FP Distribution by Branch ({len(leaders)} leaders across {len(l_chart_bcs)} branches)</h2>

<div class="grid-2">
<div class="chart-box"><h3>FP Count per Branch (Stacked)</h3><canvas id="lStacked" height="450"></canvas></div>
<div class="chart-box"><h3>FP Percentage per Branch (%)</h3><canvas id="lPct" height="450"></canvas></div>
</div>

<h3 class="section-title" style="font-size:15px">Branch Detail Table</h3>
<div class="tbl-wrap"><table>
<thead><tr>
<th>Branch</th><th>Name</th><th style="text-align:center">N</th>
{"".join(f'<th style="text-align:center;color:{FP_COLORS[i]}">{fp}</th>' for i, fp in enumerate(FPS))}
<th style="text-align:center">Dominant</th>
</tr></thead>
<tbody>{l_rows}</tbody>
</table></div>
</div>

<!-- ═══ COMPARE ═══ -->
<div id="compare" class="content">
<h2 class="section-title">Teacher vs Leader FP Alignment</h2>

<div class="info-box">
Where teacher and leader dominant FPs <strong>diverge</strong>, it signals a potential alignment gap.
SET1 uses this to identify WHERE translation gaps exist.
</div>

<div class="chart-box"><h3>FP Distribution Comparison (% of respondents)</h3><canvas id="compareRadar" height="300"></canvas></div>

<h3 class="section-title" style="font-size:15px">Per-Branch Alignment</h3>
<div class="tbl-wrap"><table>
<thead><tr><th>Branch</th><th>Name</th><th style="text-align:center">Teachers</th><th style="text-align:center">Teacher FP</th><th style="text-align:center">Leaders</th><th style="text-align:center">Leader FP</th><th style="text-align:center">Aligned?</th></tr></thead>
<tbody>
{"".join(f'''<tr>
<td><strong>{bc}</strong></td>
<td style="font-size:11px">{branch_names.get(bc,"")[:35]}</td>
<td style="text-align:center">{t_bc_counts.get(bc,0)}</td>
<td style="text-align:center;color:{FP_COLORS[FPS.index(max(t_branch.get(bc,{fp:0 for fp in FPS}), key=t_branch.get(bc,{fp:0 for fp in FPS}).get))] if t_bc_counts.get(bc,0) > 0 else "#999"};font-weight:700">{max(t_branch.get(bc,{fp:0 for fp in FPS}), key=t_branch.get(bc,{fp:0 for fp in FPS}).get) if t_bc_counts.get(bc,0) > 0 else "—"}</td>
<td style="text-align:center">{l_bc_counts.get(bc,0)}</td>
<td style="text-align:center;color:{FP_COLORS[FPS.index(max(l_branch.get(bc,{fp:0 for fp in FPS}), key=l_branch.get(bc,{fp:0 for fp in FPS}).get))] if l_bc_counts.get(bc,0) > 0 else "#999"};font-weight:700">{max(l_branch.get(bc,{fp:0 for fp in FPS}), key=l_branch.get(bc,{fp:0 for fp in FPS}).get) if l_bc_counts.get(bc,0) > 0 else "—"}</td>
<td style="text-align:center">{('<span style="color:#16a34a;font-weight:700">YES</span>' if (t_bc_counts.get(bc,0) > 0 and l_bc_counts.get(bc,0) > 0 and max(t_branch.get(bc,{fp:0 for fp in FPS}), key=t_branch.get(bc,{fp:0 for fp in FPS}).get) == max(l_branch.get(bc,{fp:0 for fp in FPS}), key=l_branch.get(bc,{fp:0 for fp in FPS}).get)) else ('<span style="color:#dc2626;font-weight:700">NO</span>' if t_bc_counts.get(bc,0) > 0 and l_bc_counts.get(bc,0) > 0 else '<span style="color:#d1d5db">—</span>'))}</td>
</tr>''' for bc in all_bcs if t_bc_counts.get(bc,0) > 0 or l_bc_counts.get(bc,0) > 0)}
</tbody>
</table></div>
</div>

<div style="text-align:center;padding:20px;color:var(--muted);font-size:11px">Project Kshitij | Myelin | Generated {date.today()}</div>

<script>
function showTab(id){{
  document.querySelectorAll('.tab').forEach(function(t){{t.classList.remove('active')}});
  document.querySelectorAll('.content').forEach(function(c){{c.classList.remove('active')}});
  event.target.classList.add('active');
  document.getElementById(id).classList.add('active');
}}

var FP_LABELS = {j(FPS)};
var FP_FULL = {j([f"{fp}: {FP_NAMES[fp]}" for fp in FPS])};
var FP_COLORS = {j(FP_COLORS)};

// Doughnuts
new Chart(document.getElementById('tDoughnut'),{{type:'doughnut',data:{{labels:FP_FULL,datasets:[{{data:{t_dist_vals},backgroundColor:FP_COLORS}}]}},options:{{plugins:{{legend:{{position:'right'}}}}}}}});
new Chart(document.getElementById('lDoughnut'),{{type:'doughnut',data:{{labels:FP_FULL,datasets:[{{data:{l_dist_vals},backgroundColor:FP_COLORS}}]}},options:{{plugins:{{legend:{{position:'right'}}}}}}}});

// Comparison bar
new Chart(document.getElementById('compareBar'),{{type:'bar',data:{{labels:FP_FULL,datasets:[
  {{label:'Teacher %',data:{comparison_t},backgroundColor:'rgba(59,130,246,0.7)'}},
  {{label:'Leader %',data:{comparison_l},backgroundColor:'rgba(124,58,237,0.7)'}}
]}},options:{{scales:{{y:{{max:100}}}},plugins:{{legend:{{position:'top'}}}}}}}});

// Teacher stacked
new Chart(document.getElementById('tStacked'),{{type:'bar',data:{{labels:{j(t_chart_bcs)},datasets:{t_stacked}}},options:{{indexAxis:'y',scales:{{x:{{stacked:true}},y:{{stacked:true}}}},plugins:{{legend:{{position:'top'}}}}}}}});
new Chart(document.getElementById('tPct'),{{type:'bar',data:{{labels:{j(t_chart_bcs)},datasets:{t_pct}}},options:{{indexAxis:'y',scales:{{x:{{stacked:true,max:100}},y:{{stacked:true}}}},plugins:{{legend:{{position:'top'}}}}}}}});

// Leader stacked
new Chart(document.getElementById('lStacked'),{{type:'bar',data:{{labels:{j(l_chart_bcs)},datasets:{l_stacked}}},options:{{indexAxis:'y',scales:{{x:{{stacked:true}},y:{{stacked:true}}}},plugins:{{legend:{{position:'top'}}}}}}}});
new Chart(document.getElementById('lPct'),{{type:'bar',data:{{labels:{j(l_chart_bcs)},datasets:{l_pct}}},options:{{indexAxis:'y',scales:{{x:{{stacked:true,max:100}},y:{{stacked:true}}}},plugins:{{legend:{{position:'top'}}}}}}}});

// Comparison radar
new Chart(document.getElementById('compareRadar'),{{type:'radar',data:{{labels:FP_LABELS,datasets:[
  {{label:'Teacher %',data:{comparison_t},backgroundColor:'rgba(59,130,246,0.15)',borderColor:'#3b82f6',borderWidth:2,pointRadius:5}},
  {{label:'Leader %',data:{comparison_l},backgroundColor:'rgba(124,58,237,0.15)',borderColor:'#7c3aed',borderWidth:2,pointRadius:5}}
]}},options:{{scales:{{r:{{min:0,max:80}}}},plugins:{{legend:{{position:'top'}}}}}}}});
</script>
</body></html>"""

    return html


def main():
    print("Loading Stage-1 intent data...")
    users = load_data()
    branch_names = load_branch_names()
    teachers = sum(1 for u in users.values() if u["role"] == "Teacher")
    leaders = sum(1 for u in users.values() if u["role"] == "Leader")
    print(f"  {len(users)} users ({teachers} teachers, {leaders} leaders)")

    html = build_html(users, branch_names)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(html)
    print(f"  Written: {OUT_PATH} ({os.path.getsize(OUT_PATH) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
