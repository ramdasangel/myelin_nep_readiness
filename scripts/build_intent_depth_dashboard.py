#!/usr/bin/env python3
"""Build Stage 2 Intent Survey — Practice Depth Dashboard (D1–D4).

Reads:
  assets/myelin_stat_ro/intent_teacher_english_responses.csv
  assets/myelin_stat_ro/intent_teacher_marathi_responses.csv

Writes:
  output/intent_depth_dashboard.html

D1–D4 map to selectedOption 0–3:
  D1 (option 0) = surface / procedural
  D2 (option 1) = emerging awareness
  D3 (option 2) = applied understanding
  D4 (option 3) = deep / strategic
"""
import csv, json
from collections import defaultdict
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RESPONSE_CSVS = [
    BASE / "assets" / "myelin_stat_ro" / "intent_teacher_english_responses.csv",
    BASE / "assets" / "myelin_stat_ro" / "intent_teacher_marathi_responses.csv",
]
OUTPUT = BASE / "output" / "intent_depth_dashboard.html"
TODAY = date.today().isoformat()

# Goal name normalisation (Marathi → English)
GOAL_MAP = {
    'Each Child is Unique': 'Each Child is Unique',
    'Diagnosing Learning Levels': 'Diagnosing Learning Levels',
    'Competency-Based Learning': 'Competency-Based Learning',
    'Teacher Upskilling': 'Teacher Upskilling',
    'Parent–Teacher Collaboration': 'Parent-Teacher Collaboration',
    'Parent\u2013Teacher Collaboration': 'Parent-Teacher Collaboration',
    'अध्ययन स्तरांचे निदान': 'Diagnosing Learning Levels',
    'पालक - शिक्षक सहयोग': 'Parent-Teacher Collaboration',
    'पालक -शिक्षक सहयोग': 'Parent-Teacher Collaboration',
    'शिक्षक कौशल्यवृद्धी': 'Teacher Upskilling',
    'क्षमताधिष्टित अध्ययन': 'Competency-Based Learning',
    'प्रत्येक मूल वेगळे आहे': 'Each Child is Unique',
}
GOAL_ORDER = [
    'Each Child is Unique',
    'Diagnosing Learning Levels',
    'Competency-Based Learning',
    'Teacher Upskilling',
    'Parent-Teacher Collaboration',
]

# ── Load data ──
rows = []
for p in RESPONSE_CSVS:
    if not p.exists():
        print(f"WARN: {p.name} not found, skipping")
        continue
    with open(p, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r.get('schoolName', '').strip() == 'Deccan Education Society' and r.get('role', '').strip() == 'Teacher':
                rows.append(r)

# ── Per-teacher aggregation ──
users = {}
for r in rows:
    uid = r['userId']
    if uid not in users:
        users[uid] = {
            'name': f"{r['firstName']} {r['lastName']}".strip(),
            'branch': r.get('branchName', ''),
            'branchCode': r.get('branchCode', ''),
            'd': [0, 0, 0, 0],  # D1–D4 counts
            'total': 0,
            'goals': defaultdict(lambda: [0, 0, 0, 0]),
        }
    u = users[uid]
    opt = r.get('selectedOption', '')
    if opt in ('0', '1', '2', '3'):
        idx = int(opt)
        u['d'][idx] += 1
        u['total'] += 1
        goal = GOAL_MAP.get(r.get('goal', ''), r.get('goal', ''))
        u['goals'][goal][idx] += 1

# ── Per-branch aggregation ──
branches = defaultdict(lambda: {'d': [0, 0, 0, 0], 'total': 0, 'teachers': 0})
for uid, u in users.items():
    bk = u['branchCode'] or u['branch']
    b = branches[bk]
    b['name'] = u['branch']
    b['code'] = u['branchCode']
    for i in range(4):
        b['d'][i] += u['d'][i]
    b['total'] += u['total']
    b['teachers'] += 1

# ── Build JSON data for embedding ──
teacher_list = []
for uid, u in users.items():
    t = u['total'] or 1
    teacher_list.append({
        'uid': uid,
        'name': u['name'],
        'branch': u['branch'],
        'branchCode': u['branchCode'],
        'd': u['d'],
        'pct': [round(u['d'][i] / t * 100, 1) for i in range(4)],
        'avg': round(sum(i * u['d'][i] for i in range(4)) / t, 2),
        'total': t,
    })

branch_list = []
for bk, b in branches.items():
    t = b['total'] or 1
    branch_list.append({
        'name': b['name'],
        'code': b['code'],
        'd': b['d'],
        'pct': [round(b['d'][i] / t * 100, 1) for i in range(4)],
        'avg': round(sum(i * b['d'][i] for i in range(4)) / t, 2),
        'total': t,
        'teachers': b['teachers'],
    })

# ── Overall stats ──
total_teachers = len(users)
total_responses = sum(u['total'] for u in users.values())
overall_d = [sum(u['d'][i] for u in users.values()) for i in range(4)]
overall_avg = round(sum(i * overall_d[i] for i in range(4)) / total_responses, 2)

# ── Goal-level aggregation ──
goal_data = {}
for g in GOAL_ORDER:
    gd = [0, 0, 0, 0]
    for u in users.values():
        for i in range(4):
            gd[i] += u['goals'].get(g, [0, 0, 0, 0])[i]
    gt = sum(gd)
    goal_data[g] = {
        'd': gd,
        'pct': [round(gd[i] / gt * 100, 1) if gt > 0 else 0 for i in range(4)],
    }

# ── Write HTML ──
HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stage 2 — Intent Survey Practice Depth Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
:root {{
  --primary: #1a365d; --accent: #2b6cb0; --bg: #f7fafc; --card: #fff;
  --border: #e2e8f0; --text: #2d3748; --muted: #718096; --light: #ebf4ff;
  --d1: #e53e3e; --d2: #ed8936; --d3: #38a169; --d4: #3182ce;
  --d1bg: #fff5f5; --d2bg: #fffaf0; --d3bg: #f0fff4; --d4bg: #ebf8ff;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }}
.header {{ background: linear-gradient(135deg, var(--primary), var(--accent)); color: white; padding: 24px 32px; }}
.header h1 {{ font-size: 22px; margin-bottom: 4px; }}
.header p {{ font-size: 13px; opacity: 0.85; }}
.container {{ max-width: 1440px; margin: 0 auto; padding: 24px; }}

/* Tabs */
.tab-bar {{ display: flex; gap: 0; margin-bottom: 24px; border-bottom: 3px solid var(--border); }}
.tab-btn {{ padding: 12px 28px; font-size: 14px; font-weight: 700; cursor: pointer; border: none; background: none; color: var(--muted); border-bottom: 3px solid transparent; margin-bottom: -3px; transition: all 0.2s; }}
.tab-btn:hover {{ color: var(--primary); background: var(--light); }}
.tab-btn.active {{ color: var(--primary); border-bottom-color: var(--accent); }}
.tab-btn.d1.active {{ border-bottom-color: var(--d1); color: var(--d1); }}
.tab-btn.d2.active {{ border-bottom-color: var(--d2); color: var(--d2); }}
.tab-btn.d3.active {{ border-bottom-color: var(--d3); color: var(--d3); }}
.tab-btn.d4.active {{ border-bottom-color: var(--d4); color: var(--d4); }}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}

/* KPI */
.kpi-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 24px; }}
.kpi {{ background: white; border-radius: 12px; padding: 18px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.06); border-top: 4px solid var(--accent); }}
.kpi .value {{ font-size: 32px; font-weight: 800; color: var(--primary); }}
.kpi .label {{ font-size: 11px; color: var(--muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }}

/* Charts */
.chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }}
.chart-box {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
.chart-box h3 {{ font-size: 14px; color: var(--primary); margin-bottom: 12px; }}
.chart-box canvas {{ max-height: 340px; }}
.chart-box.full {{ grid-column: 1 / -1; }}

/* Tables */
.table-section {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 24px; overflow-x: auto; }}
.table-section h3 {{ font-size: 14px; color: var(--primary); margin-bottom: 12px; }}
table.data {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
table.data th {{ background: var(--primary); color: white; padding: 10px 12px; text-align: left; white-space: nowrap; cursor: pointer; user-select: none; position: sticky; top: 0; font-size: 11px; }}
table.data th:hover {{ background: var(--accent); }}
table.data td {{ padding: 8px 12px; border-bottom: 1px solid var(--border); }}
table.data tr:hover {{ background: var(--light); }}
table.data tr:nth-child(even) {{ background: #f8fafc; }}
table.data tr:nth-child(even):hover {{ background: var(--light); }}

/* Depth bars */
.depth-bar {{ display: flex; height: 16px; border-radius: 4px; overflow: hidden; min-width: 120px; }}
.depth-bar .seg {{ height: 100%; }}
.depth-bar .seg.d1 {{ background: var(--d1); }}
.depth-bar .seg.d2 {{ background: var(--d2); }}
.depth-bar .seg.d3 {{ background: var(--d3); }}
.depth-bar .seg.d4 {{ background: var(--d4); }}

/* Score badge */
.score-badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; }}
.score-badge.high {{ background: var(--d4bg); color: var(--d4); }}
.score-badge.med {{ background: var(--d3bg); color: var(--d3); }}
.score-badge.low {{ background: var(--d2bg); color: var(--d2); }}
.score-badge.vlow {{ background: var(--d1bg); color: var(--d1); }}

/* Filter */
.filter-bar {{ background: white; border: 1px solid var(--border); border-radius: 8px; padding: 12px 20px; margin-bottom: 20px; display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }}
.filter-bar label {{ font-weight: 600; font-size: 13px; color: var(--primary); }}
.filter-bar input {{ padding: 6px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; min-width: 200px; }}
.filter-bar .count {{ margin-left: auto; font-size: 12px; font-weight: 600; color: var(--accent); }}

/* Depth legend */
.depth-legend {{ display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }}
.depth-legend .item {{ display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; }}
.depth-legend .dot {{ width: 12px; height: 12px; border-radius: 3px; }}

/* Download buttons */
.btn-row {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
.btn-csv {{ display: inline-flex; align-items: center; gap: 6px; padding: 8px 18px; border: 2px solid var(--accent); background: white; color: var(--accent); border-radius: 8px; font-size: 13px; font-weight: 700; cursor: pointer; transition: all 0.2s; }}
.btn-csv:hover {{ background: var(--accent); color: white; }}
.btn-csv svg {{ width: 16px; height: 16px; fill: currentColor; }}

@media (max-width: 900px) {{ .chart-grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<div class="header">
  <h1>Stage 2 — Intent Survey: Practice Depth Dashboard</h1>
  <p>Teacher Intent Responses &nbsp;|&nbsp; Deccan Education Society &nbsp;|&nbsp; {total_teachers} Teachers &nbsp;|&nbsp; {total_responses} Responses &nbsp;|&nbsp; Data as of {TODAY}</p>
</div>
<div class="container">

<!-- Depth Legend -->
<div class="depth-legend">
  <div class="item"><div class="dot" style="background:var(--d1)"></div>D1 — Surface / Procedural</div>
  <div class="item"><div class="dot" style="background:var(--d2)"></div>D2 — Emerging Awareness</div>
  <div class="item"><div class="dot" style="background:var(--d3)"></div>D3 — Applied Understanding</div>
  <div class="item"><div class="dot" style="background:var(--d4)"></div>D4 — Deep / Strategic</div>
</div>

<!-- Tab Bar -->
<div class="tab-bar">
  <button class="tab-btn active" onclick="switchTab('overview')">Overview</button>
  <button class="tab-btn d1" onclick="switchTab('d1')">D1 — Surface</button>
  <button class="tab-btn d2" onclick="switchTab('d2')">D2 — Emerging</button>
  <button class="tab-btn d3" onclick="switchTab('d3')">D3 — Applied</button>
  <button class="tab-btn d4" onclick="switchTab('d4')">D4 — Deep</button>
</div>

<!-- TAB: Overview -->
<div class="tab-content active" id="tab-overview">
  <div class="btn-row">
    <button class="btn-csv" onclick="downloadCSV('overview-teachers')"><svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>Teacher Summary CSV</button>
    <button class="btn-csv" onclick="downloadCSV('overview-branches')"><svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>Branch Summary CSV</button>
  </div>
  <div class="kpi-row">
    <div class="kpi"><div class="value">{total_teachers}</div><div class="label">Teachers Surveyed</div></div>
    <div class="kpi" style="border-top-color:var(--d1)"><div class="value" style="color:var(--d1)">{round(overall_d[0]/total_responses*100, 1)}%</div><div class="label">D1 — Surface</div></div>
    <div class="kpi" style="border-top-color:var(--d2)"><div class="value" style="color:var(--d2)">{round(overall_d[1]/total_responses*100, 1)}%</div><div class="label">D2 — Emerging</div></div>
    <div class="kpi" style="border-top-color:var(--d3)"><div class="value" style="color:var(--d3)">{round(overall_d[2]/total_responses*100, 1)}%</div><div class="label">D3 — Applied</div></div>
    <div class="kpi" style="border-top-color:var(--d4)"><div class="value" style="color:var(--d4)">{round(overall_d[3]/total_responses*100, 1)}%</div><div class="label">D4 — Deep</div></div>
    <div class="kpi"><div class="value">{overall_avg}</div><div class="label">Avg Depth (0–3)</div></div>
  </div>
  <div class="chart-grid">
    <div class="chart-box"><h3>Overall D1–D4 Distribution</h3><canvas id="chartOverallDist"></canvas></div>
    <div class="chart-box"><h3>Depth Profile by Goal Area</h3><canvas id="chartGoalDepth"></canvas></div>
  </div>
  <div class="chart-grid">
    <div class="chart-box full"><h3>Avg Depth Score by Branch (highest → lowest)</h3><canvas id="chartBranchAvg"></canvas></div>
  </div>
</div>

<!-- TAB: D1 -->
<div class="tab-content" id="tab-d1">
  <div class="btn-row">
    <button class="btn-csv" onclick="downloadCSV('d1-teachers')"><svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>D1 Teacher Ranking CSV</button>
    <button class="btn-csv" onclick="downloadCSV('d1-branches')"><svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>D1 Branch Ranking CSV</button>
  </div>
  <div class="filter-bar"><label>Search:</label><input type="text" id="filterD1" placeholder="Name or branch..." oninput="filterTable('d1')"><span class="count" id="countD1"></span></div>
  <div class="chart-grid">
    <div class="chart-box full"><h3>D1 (Surface) % by School/Branch — Highest to Lowest</h3><canvas id="chartBranchD1"></canvas></div>
  </div>
  <div class="table-section"><h3>Teacher Ranking — D1 (Surface) Score: Highest to Lowest</h3>
    <table class="data"><thead><tr><th>#</th><th>Teacher</th><th>Branch</th><th>D1 Count</th><th>D1 %</th><th>Depth Profile</th><th>Avg Depth</th></tr></thead>
    <tbody id="tbodyD1"></tbody></table>
  </div>
</div>

<!-- TAB: D2 -->
<div class="tab-content" id="tab-d2">
  <div class="btn-row">
    <button class="btn-csv" onclick="downloadCSV('d2-teachers')"><svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>D2 Teacher Ranking CSV</button>
    <button class="btn-csv" onclick="downloadCSV('d2-branches')"><svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>D2 Branch Ranking CSV</button>
  </div>
  <div class="filter-bar"><label>Search:</label><input type="text" id="filterD2" placeholder="Name or branch..." oninput="filterTable('d2')"><span class="count" id="countD2"></span></div>
  <div class="chart-grid">
    <div class="chart-box full"><h3>D2 (Emerging) % by School/Branch — Highest to Lowest</h3><canvas id="chartBranchD2"></canvas></div>
  </div>
  <div class="table-section"><h3>Teacher Ranking — D2 (Emerging) Score: Highest to Lowest</h3>
    <table class="data"><thead><tr><th>#</th><th>Teacher</th><th>Branch</th><th>D2 Count</th><th>D2 %</th><th>Depth Profile</th><th>Avg Depth</th></tr></thead>
    <tbody id="tbodyD2"></tbody></table>
  </div>
</div>

<!-- TAB: D3 -->
<div class="tab-content" id="tab-d3">
  <div class="btn-row">
    <button class="btn-csv" onclick="downloadCSV('d3-teachers')"><svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>D3 Teacher Ranking CSV</button>
    <button class="btn-csv" onclick="downloadCSV('d3-branches')"><svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>D3 Branch Ranking CSV</button>
  </div>
  <div class="filter-bar"><label>Search:</label><input type="text" id="filterD3" placeholder="Name or branch..." oninput="filterTable('d3')"><span class="count" id="countD3"></span></div>
  <div class="chart-grid">
    <div class="chart-box full"><h3>D3 (Applied) % by School/Branch — Highest to Lowest</h3><canvas id="chartBranchD3"></canvas></div>
  </div>
  <div class="table-section"><h3>Teacher Ranking — D3 (Applied) Score: Highest to Lowest</h3>
    <table class="data"><thead><tr><th>#</th><th>Teacher</th><th>Branch</th><th>D3 Count</th><th>D3 %</th><th>Depth Profile</th><th>Avg Depth</th></tr></thead>
    <tbody id="tbodyD3"></tbody></table>
  </div>
</div>

<!-- TAB: D4 -->
<div class="tab-content" id="tab-d4">
  <div class="btn-row">
    <button class="btn-csv" onclick="downloadCSV('d4-teachers')"><svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>D4 Teacher Ranking CSV</button>
    <button class="btn-csv" onclick="downloadCSV('d4-branches')"><svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>D4 Branch Ranking CSV</button>
  </div>
  <div class="filter-bar"><label>Search:</label><input type="text" id="filterD4" placeholder="Name or branch..." oninput="filterTable('d4')"><span class="count" id="countD4"></span></div>
  <div class="chart-grid">
    <div class="chart-box full"><h3>D4 (Deep) % by School/Branch — Highest to Lowest</h3><canvas id="chartBranchD4"></canvas></div>
  </div>
  <div class="table-section"><h3>Teacher Ranking — D4 (Deep) Score: Highest to Lowest</h3>
    <table class="data"><thead><tr><th>#</th><th>Teacher</th><th>Branch</th><th>D4 Count</th><th>D4 %</th><th>Depth Profile</th><th>Avg Depth</th></tr></thead>
    <tbody id="tbodyD4"></tbody></table>
  </div>
</div>

</div><!-- /container -->

<script>
// ══════════════════════════════════════════════════════════════
// DATA
// ══════════════════════════════════════════════════════════════
const TEACHERS = {json.dumps(teacher_list)};
const BRANCHES = {json.dumps(branch_list)};
const GOAL_DATA = {json.dumps(goal_data)};
const GOAL_ORDER = {json.dumps(GOAL_ORDER)};
const D_COLORS = ['#e53e3e', '#ed8936', '#38a169', '#3182ce'];
const D_LABELS = ['D1 Surface', 'D2 Emerging', 'D3 Applied', 'D4 Deep'];

// ══════════════════════════════════════════════════════════════
// TABS
// ══════════════════════════════════════════════════════════════
function switchTab(id) {{
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  const btns = document.querySelectorAll('.tab-btn');
  const labels = ['overview', 'd1', 'd2', 'd3', 'd4'];
  btns[labels.indexOf(id)].classList.add('active');
  if (id !== 'overview' && !chartsRendered[id]) renderDTab(id);
}}

// ══════════════════════════════════════════════════════════════
// OVERVIEW CHARTS
// ══════════════════════════════════════════════════════════════
function renderOverview() {{
  // Overall distribution pie
  new Chart(document.getElementById('chartOverallDist'), {{
    type: 'doughnut',
    data: {{ labels: D_LABELS, datasets: [{{ data: [{overall_d[0]}, {overall_d[1]}, {overall_d[2]}, {overall_d[3]}], backgroundColor: D_COLORS, borderWidth: 2, borderColor: '#fff' }}] }},
    options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
  }});

  // Goal-level stacked bar
  const goalLabels = GOAL_ORDER.map(g => g.length > 25 ? g.substring(0, 22) + '...' : g);
  const goalDatasets = D_LABELS.map((lbl, i) => ({{
    label: lbl,
    data: GOAL_ORDER.map(g => GOAL_DATA[g].pct[i]),
    backgroundColor: D_COLORS[i],
    borderRadius: 2,
  }}));
  new Chart(document.getElementById('chartGoalDepth'), {{
    type: 'bar',
    data: {{ labels: goalLabels, datasets: goalDatasets }},
    options: {{ responsive: true, scales: {{ x: {{ stacked: true }}, y: {{ stacked: true, max: 100, title: {{ display: true, text: '%' }} }} }},
      plugins: {{ legend: {{ position: 'bottom' }} }} }}
  }});

  // Branch avg depth (sorted)
  const sortedBranches = [...BRANCHES].sort((a, b) => b.avg - a.avg);
  const bLabels = sortedBranches.map(b => b.name.length > 30 ? b.name.substring(0, 27) + '...' : b.name);
  const bAvgs = sortedBranches.map(b => b.avg);
  const bColors = bAvgs.map(v => v >= 2 ? '#3182ce' : v >= 1.5 ? '#38a169' : v >= 1 ? '#ed8936' : '#e53e3e');
  new Chart(document.getElementById('chartBranchAvg'), {{
    type: 'bar',
    data: {{ labels: bLabels, datasets: [{{ label: 'Avg Depth (0\u20133)', data: bAvgs, backgroundColor: bColors, borderRadius: 4 }}] }},
    options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      scales: {{ x: {{ min: 0, max: 3, title: {{ display: true, text: 'Average Depth Score' }} }} }},
      plugins: {{ legend: {{ display: false }} }} }},
  }});
  document.getElementById('chartBranchAvg').parentElement.style.minHeight = (sortedBranches.length * 28 + 60) + 'px';
}}

// ══════════════════════════════════════════════════════════════
// D-TAB RENDERING
// ══════════════════════════════════════════════════════════════
const chartsRendered = {{ d1: false, d2: false, d3: false, d4: false }};
let tabTeachers = {{ d1: [], d2: [], d3: [], d4: [] }};

function renderDTab(dKey) {{
  const idx = ['d1','d2','d3','d4'].indexOf(dKey);
  chartsRendered[dKey] = true;

  // Sort branches by D% for this depth level (highest first)
  const sortedB = [...BRANCHES].sort((a, b) => b.pct[idx] - a.pct[idx]);
  const bLabels = sortedB.map(b => b.name.length > 30 ? b.name.substring(0, 27) + '...' : b.name);
  const bPcts = sortedB.map(b => b.pct[idx]);
  new Chart(document.getElementById('chartBranch' + dKey.toUpperCase()), {{
    type: 'bar',
    data: {{ labels: bLabels, datasets: [{{ label: D_LABELS[idx] + ' %', data: bPcts, backgroundColor: D_COLORS[idx] + 'cc', borderRadius: 4 }}] }},
    options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      scales: {{ x: {{ min: 0, max: 100, title: {{ display: true, text: '% of responses at ' + D_LABELS[idx] }} }} }},
      plugins: {{ legend: {{ display: false }} }} }},
  }});
  document.getElementById('chartBranch' + dKey.toUpperCase()).parentElement.style.minHeight = (sortedB.length * 28 + 60) + 'px';

  // Sort teachers by this D% (highest first)
  tabTeachers[dKey] = [...TEACHERS].sort((a, b) => b.pct[idx] - a.pct[idx] || b.d[idx] - a.d[idx]);
  renderTeacherTable(dKey, tabTeachers[dKey]);
}}

function renderTeacherTable(dKey, data) {{
  const idx = ['d1','d2','d3','d4'].indexOf(dKey);
  const tbody = document.getElementById('tbody' + dKey.toUpperCase());
  let html = '';
  data.forEach((t, i) => {{
    const total = t.total || 1;
    const barSegs = t.d.map((v, j) => '<div class="seg d' + (j + 1) + '" style="width:' + (v / total * 100) + '%"></div>').join('');
    const avgBadge = t.avg >= 2 ? 'high' : t.avg >= 1.5 ? 'med' : t.avg >= 1 ? 'low' : 'vlow';
    html += '<tr data-search="' + (t.name + ' ' + t.branch).toLowerCase() + '">' +
      '<td>' + (i + 1) + '</td>' +
      '<td><strong>' + esc(t.name) + '</strong></td>' +
      '<td style="font-size:11px">' + esc(t.branch) + '</td>' +
      '<td style="text-align:center;font-weight:700">' + t.d[idx] + '</td>' +
      '<td style="text-align:center;font-weight:700;color:' + D_COLORS[idx] + '">' + t.pct[idx] + '%</td>' +
      '<td><div class="depth-bar">' + barSegs + '</div></td>' +
      '<td style="text-align:center"><span class="score-badge ' + avgBadge + '">' + t.avg + '</span></td>' +
      '</tr>';
  }});
  tbody.innerHTML = html;
  document.getElementById('count' + dKey.toUpperCase()).textContent = data.length + ' teachers';
}}

function filterTable(dKey) {{
  const idx = ['d1','d2','d3','d4'].indexOf(dKey);
  const q = document.getElementById('filter' + dKey.toUpperCase()).value.toLowerCase();
  const filtered = q ? tabTeachers[dKey].filter(t => (t.name + ' ' + t.branch).toLowerCase().includes(q)) : tabTeachers[dKey];
  renderTeacherTable(dKey, filtered);
}}

function esc(s) {{ const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}

// ══════════════════════════════════════════════════════════════
// CSV DOWNLOAD
// ══════════════════════════════════════════════════════════════
function csvEsc(v) {{
  const s = String(v);
  return s.includes(',') || s.includes('"') || s.includes('\\n') ? '"' + s.replace(/"/g, '""') + '"' : s;
}}

function downloadCSV(key) {{
  let rows = [];
  let filename = '';

  if (key === 'overview-teachers') {{
    // All teachers with full depth profile, sorted by avg depth desc
    const sorted = [...TEACHERS].sort((a, b) => b.avg - a.avg);
    rows.push(['Rank','Teacher','Branch','BranchCode','D1_Count','D1_Pct','D2_Count','D2_Pct','D3_Count','D3_Pct','D4_Count','D4_Pct','Total','AvgDepth']);
    sorted.forEach((t, i) => {{
      rows.push([i+1, t.name, t.branch, t.branchCode, t.d[0], t.pct[0], t.d[1], t.pct[1], t.d[2], t.pct[2], t.d[3], t.pct[3], t.total, t.avg]);
    }});
    filename = 'intent_depth_teacher_summary.csv';

  }} else if (key === 'overview-branches') {{
    const sorted = [...BRANCHES].sort((a, b) => b.avg - a.avg);
    rows.push(['Rank','Branch','BranchCode','Teachers','D1_Count','D1_Pct','D2_Count','D2_Pct','D3_Count','D3_Pct','D4_Count','D4_Pct','TotalResponses','AvgDepth']);
    sorted.forEach((b, i) => {{
      rows.push([i+1, b.name, b.code, b.teachers, b.d[0], b.pct[0], b.d[1], b.pct[1], b.d[2], b.pct[2], b.d[3], b.pct[3], b.total, b.avg]);
    }});
    filename = 'intent_depth_branch_summary.csv';

  }} else {{
    // d1-teachers, d2-branches, etc.
    const parts = key.split('-');
    const dKey = parts[0];
    const type = parts[1];
    const idx = ['d1','d2','d3','d4'].indexOf(dKey);
    const dLabel = D_LABELS[idx];

    if (type === 'teachers') {{
      const sorted = [...TEACHERS].sort((a, b) => b.pct[idx] - a.pct[idx] || b.d[idx] - a.d[idx]);
      rows.push(['Rank','Teacher','Branch','BranchCode', dLabel + '_Count', dLabel + '_Pct','D1_Count','D2_Count','D3_Count','D4_Count','Total','AvgDepth']);
      sorted.forEach((t, i) => {{
        rows.push([i+1, t.name, t.branch, t.branchCode, t.d[idx], t.pct[idx], t.d[0], t.d[1], t.d[2], t.d[3], t.total, t.avg]);
      }});
      filename = 'intent_depth_' + dKey + '_teacher_ranking.csv';

    }} else {{
      const sorted = [...BRANCHES].sort((a, b) => b.pct[idx] - a.pct[idx]);
      rows.push(['Rank','Branch','BranchCode','Teachers', dLabel + '_Count', dLabel + '_Pct','D1_Pct','D2_Pct','D3_Pct','D4_Pct','TotalResponses','AvgDepth']);
      sorted.forEach((b, i) => {{
        rows.push([i+1, b.name, b.code, b.teachers, b.d[idx], b.pct[idx], b.pct[0], b.pct[1], b.pct[2], b.pct[3], b.total, b.avg]);
      }});
      filename = 'intent_depth_' + dKey + '_branch_ranking.csv';
    }}
  }}

  const csvContent = rows.map(r => r.map(csvEsc).join(',')).join('\\n');
  const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}}

// ══════════════════════════════════════════════════════════════
// INIT
// ══════════════════════════════════════════════════════════════
renderOverview();
</script>
</body>
</html>"""

OUTPUT.write_text(HTML, encoding='utf-8')
size_kb = OUTPUT.stat().st_size // 1024
print(f"Dashboard written to {OUTPUT} ({size_kb}KB)")
print(f"  {total_teachers} teachers | {len(branches)} branches | {total_responses} responses")
print(f"  D1={overall_d[0]} ({round(overall_d[0]/total_responses*100,1)}%) | D2={overall_d[1]} ({round(overall_d[1]/total_responses*100,1)}%) | D3={overall_d[2]} ({round(overall_d[2]/total_responses*100,1)}%) | D4={overall_d[3]} ({round(overall_d[3]/total_responses*100,1)}%)")
print(f"  Avg depth score: {overall_avg}")
