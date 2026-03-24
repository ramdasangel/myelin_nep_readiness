#!/usr/bin/env python3
"""
Build SRI v2 Dashboard — self-contained HTML with Chart.js
Reads: output/reports/sri_v2_branch_scores.csv + sri_v2_detail.json
Outputs: output/dashboards/11_sri_v2_dashboard.html
"""

import csv
import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
CSV_PATH = BASE / "output" / "reports" / "sri_v2_branch_scores.csv"
JSON_PATH = BASE / "output" / "reports" / "sri_v2_detail.json"
OUT_PATH = BASE / "output" / "dashboards" / "11_sri_v2_dashboard.html"


def load_data():
    rows = []
    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    detail = {}
    if JSON_PATH.exists():
        with open(JSON_PATH) as f:
            detail = json.load(f)
    return rows, detail


def band_color(band):
    m = {
        "operationalised_structure": "#16a34a",
        "partially_institutionalised": "#2563eb",
        "emerging_structure": "#d97706",
        "structural_absence": "#dc2626",
        "no_data": "#9ca3af",
    }
    return m.get(band, "#9ca3af")


def band_badge(band):
    cls = {
        "operationalised_structure": "badge-green",
        "partially_institutionalised": "badge-blue",
        "emerging_structure": "badge-amber",
        "structural_absence": "badge-red",
        "no_data": "badge-gray",
    }
    label = band.replace("_", " ").title() if band else "No Data"
    return f'<span class="badge {cls.get(band, "badge-gray")}">{label}</span>'


def area_band_badge(band):
    cls = {"high": "badge-green", "mid": "badge-amber", "low": "badge-red"}
    return f'<span class="badge {cls.get(band, "badge-gray")}">{band.upper() if band else "—"}</span>'


def build_html(rows, detail):
    # Compute summary stats
    total_branches = len(rows)
    sri_branches = [r for r in rows if float(r["sri_system_readiness"]) > 0]
    set_branches = [r for r in rows if r["dominant_fp_teacher"]]
    avg_sri = sum(float(r["sri_system_readiness"]) for r in sri_branches) / len(sri_branches) if sri_branches else 0
    avg_a1 = sum(float(r["A1_mean"]) for r in set_branches if float(r["A1_mean"]) > 0) / max(1, sum(1 for r in set_branches if float(r["A1_mean"]) > 0))
    avg_a2 = sum(float(r["A2_mean"]) for r in set_branches if float(r["A2_mean"]) > 0) / max(1, sum(1 for r in set_branches if float(r["A2_mean"]) > 0))
    avg_a3 = sum(float(r["A3_mean"]) for r in set_branches if float(r["A3_mean"]) > 0) / max(1, sum(1 for r in set_branches if float(r["A3_mean"]) > 0))
    avg_a4 = sum(float(r["A4_mean"]) for r in set_branches if float(r["A4_mean"]) > 0) / max(1, sum(1 for r in set_branches if float(r["A4_mean"]) > 0))

    # SRI audit chart data
    sri_labels = json.dumps([r["branchCode"] for r in sri_branches])
    sri_te = json.dumps([float(r["sri_teacher_enablement"]) for r in sri_branches])
    sri_lr = json.dumps([float(r["sri_leadership_routines"]) for r in sri_branches])

    # FP distribution
    fp_counts = {"FP1": 0, "FP2": 0, "FP3": 0, "FP4": 0, "FP5": 0}
    for r in set_branches:
        fp = r.get("dominant_fp_teacher", "")
        if fp in fp_counts:
            fp_counts[fp] += 1

    # Area means across all branches (for radar)
    area_labels = ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4"]
    area_avgs = []
    for a in area_labels:
        vals = [float(r[f"{a}_mean"]) for r in set_branches if float(r[f"{a}_mean"]) > 0]
        area_avgs.append(round(sum(vals) / len(vals), 2) if vals else 0)

    # Archetype counts
    arch_counts = {}
    for r in rows:
        arch = r.get("primary_archetype", "none")
        if arch and arch != "none" and arch != "None":
            arch_counts[arch] = arch_counts.get(arch, 0) + 1

    # Branch table rows
    table_rows = ""
    for r in sorted(rows, key=lambda x: x["branchCode"]):
        sri_val = float(r["sri_system_readiness"])
        sri_pct = sri_val / 20 * 100
        table_rows += f"""<tr>
<td><strong>{r['branchCode']}</strong></td>
<td>{r.get('teacher_count','0')}</td><td>{r.get('leader_count','0')}</td>
<td><div class="bar"><div class="bar-fill" style="width:{sri_pct}%;background:{band_color(r['sri_band'])}"></div></div>
<span style="font-size:12px;font-weight:600">{sri_val}/20</span></td>
<td>{band_badge(r['sri_band'])}</td>
<td>{r['dominant_fp_teacher']}</td><td>{r['dominant_fp_leader']}</td>
<td>{float(r['A1_mean']):.2f} {area_band_badge(r['A1_band'])}</td>
<td>{float(r['A2_mean']):.2f} {area_band_badge(r['A2_band'])}</td>
<td>{float(r['A3_mean']):.2f} {area_band_badge(r['A3_band'])}</td>
<td>{float(r['A4_mean']):.2f} {area_band_badge(r['A4_band'])}</td>
<td>{float(r['B1_mean']):.2f} {area_band_badge(r['B1_band'])}</td>
<td>{float(r['B2_mean']):.2f} {area_band_badge(r['B2_band'])}</td>
<td>{float(r['B3_mean']):.2f} {area_band_badge(r['B3_band'])}</td>
<td>{float(r['B4_mean']):.2f} {area_band_badge(r['B4_band'])}</td>
<td>{r.get('primary_archetype','—')}</td>
</tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SRI v2 Dashboard — Deccan Education Society</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
:root{{--bg:#f5f6fa;--card:#fff;--border:#e0e3ea;--text:#1a1a2e;--muted:#6b7280;
--blue:#2563eb;--green:#16a34a;--amber:#d97706;--red:#dc2626;--purple:#7c3aed;--teal:#0d9488;
--radius:8px;--shadow:0 1px 3px rgba(0,0,0,.08)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.5}}
.header{{background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);color:#fff;padding:20px 32px;display:flex;align-items:center;justify-content:space-between}}
.header h1{{font-size:22px;font-weight:700;letter-spacing:-.3px}}
.header .sub{{font-size:13px;opacity:.8}}
.tabs{{display:flex;background:#fff;border-bottom:2px solid var(--border);padding:0 24px;overflow-x:auto;gap:2px}}
.tab{{padding:12px 18px;cursor:pointer;font-weight:600;font-size:13px;border-bottom:3px solid transparent;color:var(--muted);white-space:nowrap;transition:.15s}}
.tab:hover{{color:var(--text);background:#f8f9fb}}
.tab.active{{color:var(--blue);border-bottom-color:var(--blue)}}
.content{{display:none;padding:24px 32px;max-width:1800px;margin:0 auto}}
.content.active{{display:block}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow)}}
.card .label{{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);margin-bottom:4px}}
.card .value{{font-size:28px;font-weight:700}}
.card .sub{{font-size:12px;color:var(--muted);margin-top:2px}}
table{{width:100%;border-collapse:collapse;background:var(--card);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);font-size:12px}}
th{{background:#f1f3f8;font-weight:600;text-align:left;padding:8px 10px;border-bottom:2px solid var(--border);position:sticky;top:0;white-space:nowrap}}
td{{padding:6px 10px;border-bottom:1px solid var(--border)}}
tr:hover td{{background:#f8f9fc}}
.tbl-wrap{{overflow-x:auto;border-radius:var(--radius);margin-bottom:24px}}
.bar{{height:8px;border-radius:4px;background:#e5e7eb;position:relative;min-width:60px;display:inline-block;width:80px;vertical-align:middle;margin-right:6px}}
.bar-fill{{height:100%;border-radius:4px;transition:.3s}}
.badge{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:600}}
.badge-green{{background:#dcfce7;color:#166534}}.badge-amber{{background:#fef3c7;color:#92400e}}.badge-red{{background:#fee2e2;color:#991b1b}}.badge-gray{{background:#f3f4f6;color:#6b7280}}.badge-blue{{background:#dbeafe;color:#1e40af}}
.chart-box{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;box-shadow:var(--shadow);margin-bottom:24px}}
.chart-box h3{{font-size:15px;margin-bottom:12px;color:var(--text)}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.grid-3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px}}
.section-title{{font-size:17px;font-weight:700;margin:24px 0 12px;padding-bottom:8px;border-bottom:2px solid var(--border)}}
.info-box{{background:#eff6ff;border:1px solid #bfdbfe;border-radius:var(--radius);padding:14px 18px;margin-bottom:20px;font-size:13px;color:#1e40af}}
@media(max-width:900px){{.grid-2,.grid-3{{grid-template-columns:1fr}}.content{{padding:16px}}}}
</style>
</head>
<body>
<div class="header">
<div><h1>SRI v2 Dashboard</h1><div class="sub">System Readiness Index — 3-Instrument Analysis</div></div>
<div style="text-align:right"><div style="font-size:13px;opacity:.7">Deccan Education Society</div><div style="font-size:12px;opacity:.6">Generated: {__import__('datetime').date.today()}</div></div>
</div>

<div class="tabs">
<div class="tab active" onclick="showTab('overview')">Overview</div>
<div class="tab" onclick="showTab('audit')">System Audit</div>
<div class="tab" onclick="showTab('set')">SET Analysis</div>
<div class="tab" onclick="showTab('areas')">Diagnostic Areas</div>
<div class="tab" onclick="showTab('table')">Branch Detail</div>
</div>

<!-- OVERVIEW TAB -->
<div id="overview" class="content active">
<div class="cards">
<div class="card"><div class="label">Total Branches</div><div class="value" style="color:var(--blue)">{total_branches}</div><div class="sub">Production (M001-M038)</div></div>
<div class="card"><div class="label">SRI Audit Coverage</div><div class="value" style="color:var(--green)">{len(sri_branches)}</div><div class="sub">of {total_branches} branches ({len(sri_branches)*100//max(1,total_branches)}%)</div></div>
<div class="card"><div class="label">Avg System Readiness</div><div class="value" style="color:var(--purple)">{avg_sri:.1f}/20</div><div class="sub">across {len(sri_branches)} audited branches</div></div>
<div class="card"><div class="label">SET Coverage</div><div class="value" style="color:var(--teal)">{len(set_branches)}</div><div class="sub">{sum(int(r['teacher_count']) for r in set_branches)} teachers, {sum(int(r['leader_count']) for r in set_branches)} leaders</div></div>
<div class="card"><div class="label">Parent Validation</div><div class="value" style="color:var(--muted)">0</div><div class="sub">Not yet collected</div></div>
</div>

<div class="info-box">
<strong>SRI v2</strong> combines three instruments: (1) System Readiness Audit — binary structural assessment by principals, (2) Parent Validation Signal — Likert perception survey (awaiting data), (3) SET — Structured Explanation of Translation using orientation, practice depth, and diagnostic areas.
</div>

<div class="grid-2">
<div class="chart-box"><h3>Teacher Dominant FP Distribution</h3><canvas id="fpChart" height="200"></canvas></div>
<div class="chart-box"><h3>Diagnostic Area Means (All Branches)</h3><canvas id="radarChart" height="200"></canvas></div>
</div>
</div>

<!-- AUDIT TAB -->
<div id="audit" class="content">
<h2 class="section-title">Instrument 1: System Readiness Audit (0-20)</h2>
<div class="info-box">10 binary Yes/No questions answered by Principal + VP + Academic Coordinator. Teacher Enablement (E1-E5) + Leadership Routines (R1-R5). Score = sum &times; 2.</div>

<div class="cards">
{"".join(f'''<div class="card"><div class="label">{r['branchCode']}</div><div class="value" style="color:{band_color(r['sri_band'])}">{float(r['sri_system_readiness']):.0f}/20</div><div class="sub">TE: {float(r['sri_teacher_enablement']):.0f} | LR: {float(r['sri_leadership_routines']):.0f} | {band_badge(r['sri_band'])}</div></div>''' for r in sri_branches)}
</div>

<div class="chart-box"><h3>Teacher Enablement vs Leadership Routines by Branch</h3><canvas id="auditChart" height="250"></canvas></div>
</div>

<!-- SET TAB -->
<div id="set" class="content">
<h2 class="section-title">Instrument 3: SET — Structured Explanation of Translation</h2>
<div class="info-box">SET is a reading grammar, not a score. SET1 identifies WHERE intent-translation gaps exist. SET2 explains WHY using diagnostic areas. All outputs are branch/cluster level.</div>

<div class="grid-2">
<div class="chart-box"><h3>SET1: Teacher vs Leader Orientation Alignment</h3>
<div class="tbl-wrap"><table>
<tr><th>Branch</th><th>Teacher FP</th><th>Teachers</th><th>Leader FP</th><th>Leaders</th></tr>
{"".join(f"<tr><td>{r['branchCode']}</td><td><strong>{r['dominant_fp_teacher']}</strong></td><td>{r['teacher_count']}</td><td><strong>{r['dominant_fp_leader']}</strong></td><td>{r['leader_count']}</td></tr>" for r in set_branches[:20])}
</table></div></div>

<div class="chart-box"><h3>Detected Archetypes</h3>
{"".join(f'<div style="margin:8px 0;padding:10px 14px;background:#f8f9fb;border-radius:6px;border-left:4px solid var(--purple)"><strong>{arch}</strong> <span class="badge badge-blue">{count} branch{"es" if count>1 else ""}</span></div>' for arch, count in sorted(arch_counts.items(), key=lambda x: -x[1])) if arch_counts else '<div style="padding:30px;text-align:center;color:var(--muted)">No strong archetypes detected yet — more SRI audit data needed</div>'}
</div>
</div>
</div>

<!-- AREAS TAB -->
<div id="areas" class="content">
<h2 class="section-title">SET2: Diagnostic Areas</h2>
<div class="info-box">Teacher areas (A1-A4) explain classroom-side constraints. Leader areas (B1-B4) explain system-side constraints. Banding: Low &lt; 2.5, Mid 2.5-3.2, High &gt; 3.2</div>

<div class="grid-2">
<div class="chart-box"><h3>Teacher Areas (A1-A4) — Branch Averages</h3><canvas id="teacherAreaChart" height="300"></canvas></div>
<div class="chart-box"><h3>Leader Areas (B1-B4) — Branch Averages</h3><canvas id="leaderAreaChart" height="300"></canvas></div>
</div>

<h3 class="section-title" style="font-size:15px">Area Definitions</h3>
<div class="grid-2">
<div class="card"><div class="label">A1: Continuous Learning Diagnostics</div><div class="sub">Access, Usability, FollowThrough, CollectiveUse, StudentClarity</div></div>
<div class="card"><div class="label">A2: Teacher Development & Growth</div><div class="sub">Structure, Safety, PeerLearning, Experimentation, GrowthCulture</div></div>
<div class="card"><div class="label">A3: HPC Enablement</div><div class="sub">Understanding, Clarity, Time, Use, StudentRole</div></div>
<div class="card"><div class="label">A4: Parent & Community Support</div><div class="sub">Communication, Guidance, Facilitation, Recognition</div></div>
<div class="card"><div class="label">B1: NEP Governance & Ownership</div><div class="sub">OwnershipClarity, TranslationToAction, ResponsibilityDistribution</div></div>
<div class="card"><div class="label">B2: Data-Informed Decision Culture</div><div class="sub">ReviewPractice, DecisionUse, ChangeSupport</div></div>
<div class="card"><div class="label">B3: Teacher Development Culture</div><div class="sub">PLCRegularity, Safety, ExperimentationProtection</div></div>
<div class="card"><div class="label">B4: HPC & Reporting Culture</div><div class="sub">PurposeClarity, ParentOrientation, TeacherSupport</div></div>
</div>
</div>

<!-- TABLE TAB -->
<div id="table" class="content">
<h2 class="section-title">Branch-Level Detail</h2>
<div class="tbl-wrap"><table>
<tr><th>Branch</th><th>Tchr</th><th>Ldr</th><th>SRI Score</th><th>SRI Band</th><th>T-FP</th><th>L-FP</th><th>A1</th><th>A2</th><th>A3</th><th>A4</th><th>B1</th><th>B2</th><th>B3</th><th>B4</th><th>Archetype</th></tr>
{table_rows}
</table></div>
</div>

<script>
function showTab(id){{
document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('active',t.textContent.toLowerCase().includes(id.slice(0,4))));
document.querySelectorAll('.content').forEach(c=>c.classList.toggle('active',c.id===id));
}}

// FP Distribution pie
new Chart(document.getElementById('fpChart'),{{type:'doughnut',data:{{
labels:{json.dumps(list(fp_counts.keys()))},
datasets:[{{data:{json.dumps(list(fp_counts.values()))},
backgroundColor:['#3b82f6','#8b5cf6','#10b981','#f59e0b','#ef4444']}}]
}},options:{{plugins:{{legend:{{position:'right'}}}}}}}});

// Radar chart
new Chart(document.getElementById('radarChart'),{{type:'radar',data:{{
labels:{json.dumps(area_labels)},
datasets:[{{label:'Mean Score',data:{json.dumps(area_avgs)},
backgroundColor:'rgba(37,99,235,.15)',borderColor:'#2563eb',borderWidth:2,pointRadius:4}}]
}},options:{{scales:{{r:{{min:0,max:4,ticks:{{stepSize:1}}}}}}}}}});

// Audit stacked bar
new Chart(document.getElementById('auditChart'),{{type:'bar',data:{{
labels:{sri_labels},
datasets:[
{{label:'Teacher Enablement',data:{sri_te},backgroundColor:'#3b82f6'}},
{{label:'Leadership Routines',data:{sri_lr},backgroundColor:'#8b5cf6'}}
]
}},options:{{scales:{{x:{{stacked:true}},y:{{stacked:true,max:20}}}},plugins:{{legend:{{position:'top'}}}}}}}});

// Teacher area grouped bar
(function(){{
const branches={json.dumps([r['branchCode'] for r in set_branches if float(r['A1_mean'])>0])};
const a1={json.dumps([float(r['A1_mean']) for r in set_branches if float(r['A1_mean'])>0])};
const a2={json.dumps([float(r['A2_mean']) for r in set_branches if float(r['A2_mean'])>0])};
const a3={json.dumps([float(r['A3_mean']) for r in set_branches if float(r['A3_mean'])>0])};
const a4={json.dumps([float(r['A4_mean']) for r in set_branches if float(r['A4_mean'])>0])};
new Chart(document.getElementById('teacherAreaChart'),{{type:'bar',data:{{
labels:branches,datasets:[
{{label:'A1',data:a1,backgroundColor:'#3b82f6'}},
{{label:'A2',data:a2,backgroundColor:'#8b5cf6'}},
{{label:'A3',data:a3,backgroundColor:'#10b981'}},
{{label:'A4',data:a4,backgroundColor:'#f59e0b'}}
]}},options:{{scales:{{y:{{min:0,max:4}}}},plugins:{{legend:{{position:'top'}}}}}}}});
}})();

// Leader area grouped bar
(function(){{
const branches={json.dumps([r['branchCode'] for r in set_branches if float(r['B1_mean'])>0])};
const b1={json.dumps([float(r['B1_mean']) for r in set_branches if float(r['B1_mean'])>0])};
const b2={json.dumps([float(r['B2_mean']) for r in set_branches if float(r['B2_mean'])>0])};
const b3={json.dumps([float(r['B3_mean']) for r in set_branches if float(r['B3_mean'])>0])};
const b4={json.dumps([float(r['B4_mean']) for r in set_branches if float(r['B4_mean'])>0])};
new Chart(document.getElementById('leaderAreaChart'),{{type:'bar',data:{{
labels:branches,datasets:[
{{label:'B1',data:b1,backgroundColor:'#0d9488'}},
{{label:'B2',data:b2,backgroundColor:'#6366f1'}},
{{label:'B3',data:b3,backgroundColor:'#ec4899'}},
{{label:'B4',data:b4,backgroundColor:'#84cc16'}}
]}},options:{{scales:{{y:{{min:0,max:4}}}},plugins:{{legend:{{position:'top'}}}}}}}});
}})();
</script>
</body>
</html>"""
    return html


def main():
    print("Building SRI v2 dashboard...")
    rows, detail = load_data()
    print(f"  Loaded {len(rows)} branches from CSV")
    html = build_html(rows, detail)
    os.makedirs(OUT_PATH.parent, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(html)
    print(f"  Written: {OUT_PATH}")
    print(f"  Size: {os.path.getsize(OUT_PATH) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
