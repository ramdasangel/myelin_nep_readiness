#!/usr/bin/env python3
"""
Build Instrument Gap Report — branches with no representation per instrument.
"""

import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE)
from scripts.dashboards.sri.html_utils import *

DATA_PATH = os.path.join(BASE, "output", "reports", "instrument_coverage_gaps.json")
UNIFIED_PATH = os.path.join(BASE, "output", "reports", "sri_unified.json")
OUT_PATH = os.path.join(BASE, "output", "reports", "instrument_gap_report.html")

INSTRUMENTS = [
    ("Intent Teacher EN", "1234", "Teacher"),
    ("Intent Teacher MR", "103", "Teacher"),
    ("Intent Leader EN", "7890", "Leader"),
    ("Intent Leader MR", "104", "Leader"),
    ("Baseline Teacher EN", "base001", "Teacher"),
    ("Baseline Teacher MR", "base003", "Teacher"),
    ("Baseline Leader EN", "base002", "Leader"),
    ("Baseline Leader MR", "base004", "Leader"),
    ("SRI Audit", "SRI001", "Leader/Principal"),
]


def main():
    with open(DATA_PATH) as f:
        gap_data = json.load(f)
    with open(UNIFIED_PATH) as f:
        unified = json.load(f)

    branches = unified["branches"]
    all_bcs = sorted(branches.keys())
    gaps = gap_data["gaps"]
    gap_set = set((g["branchCode"], g["instrument"]) for g in gaps)

    total = gap_data["total_combinations"]
    total_gaps = gap_data["total_gaps"]
    coverage_pct = gap_data["coverage_pct"]
    inst_gaps = gap_data["instrument_gaps"]
    branch_gaps = gap_data["branch_gaps"]
    full_branches = gap_data["full_coverage_branches"]

    # ── Heatmap: branches × instruments ──
    heatmap_rows = ""
    for bc in all_bcs:
        b = branches.get(bc, {})
        bname = b.get("branchName", "")[:35]
        gap_count = branch_gaps.get(bc, 0)
        row_color = "#fef2f2" if gap_count >= 6 else ("#fefce8" if gap_count >= 3 else "#f0fdf4" if gap_count == 0 else "#fff")

        cells = f'<td><strong>{bc}</strong></td><td style="font-size:11px">{bname}</td>'
        for inst_name, scode, role in INSTRUMENTS:
            if (bc, inst_name) in gap_set:
                cells += '<td style="text-align:center;background:#fee2e2;color:#991b1b;font-weight:700">MISSING</td>'
            else:
                cells += '<td style="text-align:center;background:#dcfce7;color:#166534">&#10003;</td>'
        cells += f'<td style="text-align:center;font-weight:700;color:{"#dc2626" if gap_count >= 5 else "#d97706" if gap_count >= 2 else "#16a34a"}">{gap_count}/9</td>'
        heatmap_rows += f'<tr style="background:{row_color}">{cells}</tr>'

    # ── Per-instrument breakdown ──
    inst_detail = ""
    for inst_name, scode, role in INSTRUMENTS:
        missing_bcs = [g["branchCode"] for g in gaps if g["instrument"] == inst_name]
        n = len(missing_bcs)
        pct = n / len(all_bcs) * 100
        color = "#dc2626" if pct > 50 else ("#d97706" if pct > 20 else "#16a34a")
        badge = f'<span class="badge badge-{"red" if pct > 50 else "amber" if pct > 20 else "green"}">{n}/{len(all_bcs)} missing ({pct:.0f}%)</span>'

        missing_list = ", ".join(f'<strong>{bc}</strong>' for bc in sorted(missing_bcs)) if missing_bcs else '<span style="color:var(--green)">All branches covered</span>'

        inst_detail += f'''<div class="card" style="border-left:4px solid {color}">
<div class="label">{inst_name} <span style="font-size:9px;color:var(--muted)">({scode} | {role})</span></div>
<div style="margin:6px 0">{badge}</div>
<div style="font-size:11px;color:var(--muted);line-height:1.6">{missing_list}</div>
</div>'''

    # ── Priority action list ──
    # Branches sorted by gap count desc
    priority_rows = ""
    for bc in sorted(all_bcs, key=lambda x: -branch_gaps.get(x, 0)):
        gap_n = branch_gaps.get(bc, 0)
        if gap_n == 0:
            continue
        b = branches.get(bc, {})
        bname = b.get("branchName", "")[:40]
        missing_insts = [g["instrument"] for g in gaps if g["branchCode"] == bc]

        # Categorize missing
        missing_teacher = [i for i in missing_insts if "Teacher" in i]
        missing_leader = [i for i in missing_insts if "Leader" in i or "Audit" in i]

        teacher_badge = f'<span class="badge badge-red">{len(missing_teacher)} teacher</span>' if missing_teacher else ''
        leader_badge = f'<span class="badge badge-purple">{len(missing_leader)} leader</span>' if missing_leader else ''

        sri = b.get("summary", {}).get("SRI_Total", 0)
        priority_rows += f'''<tr>
<td><strong>{bc}</strong></td>
<td style="font-size:11px">{bname}</td>
<td style="text-align:center;font-weight:700;color:{"#dc2626" if gap_n >= 5 else "#d97706"}">{gap_n}/9</td>
<td>{teacher_badge} {leader_badge}</td>
<td style="font-size:10px;color:var(--muted)">{", ".join(missing_insts)}</td>
<td style="text-align:right">{sri:.1f}</td>
</tr>'''

    # ── Build full HTML ──
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Instrument Coverage Gap Report — SRI</title>
{CHART_JS_CDN}
<style>{BASE_CSS}
.highlight-row td {{background:#fef2f2!important}}
</style>
</head>
<body>
{header("Instrument Coverage Gap Report", "Branches with No Representation — SRI")}

<div style="padding:24px 32px;max-width:1800px;margin:0 auto">

<!-- Summary Cards -->
<div class="cards" style="grid-template-columns:repeat(5,1fr)">
<div class="card"><div class="label">Total Branches</div><div class="value" style="color:var(--blue)">{len(all_bcs)}</div><div class="sub">M001-M038</div></div>
<div class="card"><div class="label">Total Instruments</div><div class="value" style="color:var(--purple)">9</div><div class="sub">4 intent + 4 baseline + SRI audit</div></div>
<div class="card"><div class="label">Total Combinations</div><div class="value">{total}</div><div class="sub">branch x instrument</div></div>
<div class="card"><div class="label" style="color:var(--red)">GAPS (No Data)</div><div class="value" style="color:var(--red)">{total_gaps}</div><div class="sub">{100 - coverage_pct:.0f}% missing</div></div>
<div class="card"><div class="label" style="color:var(--green)">Full Coverage</div><div class="value" style="color:var(--green)">{len(full_branches)}</div><div class="sub">branches with all 9 instruments</div></div>
</div>

<div class="info-box">
This report identifies <strong>{total_gaps} gaps</strong> where a branch has <strong>zero submitted responses</strong> for an instrument.
Most critical gaps: <strong>Intent Leader EN (68%)</strong>, <strong>Baseline Leader EN (58%)</strong>, and <strong>SRI Audit (58%)</strong> — all leader/principal instruments.
Full coverage branches: <strong>{', '.join(full_branches)}</strong>
</div>

<!-- Charts -->
<div class="grid-2">
<div class="chart-box">
<h3>Missing Instruments per Branch</h3>
<canvas id="branchGapChart" height="400"></canvas>
</div>
<div class="chart-box">
<h3>Gap Rate by Instrument</h3>
<canvas id="instGapChart" height="400"></canvas>
</div>
</div>

<!-- Per-Instrument Detail -->
<h2 class="section-title">Per-Instrument Breakdown</h2>
<div class="cards" style="grid-template-columns:1fr 1fr">{inst_detail}</div>

<!-- Heatmap -->
<h2 class="section-title">Coverage Heatmap — All Branches x Instruments</h2>
<div class="tbl-wrap"><table>
<thead><tr>
<th>Branch</th><th>Name</th>
{"".join(f'<th style="text-align:center;font-size:10px;writing-mode:vertical-lr;height:80px">{inst_name}</th>' for inst_name, _, _ in INSTRUMENTS)}
<th style="text-align:center">Gaps</th>
</tr></thead>
<tbody>{heatmap_rows}</tbody>
</table></div>

<!-- Priority Action -->
<h2 class="section-title">Priority Action List (branches with gaps, sorted by severity)</h2>
<div class="tbl-wrap"><table>
<thead><tr><th>Branch</th><th>Name</th><th style="text-align:center">Gaps</th><th>Category</th><th>Missing Instruments</th><th style="text-align:right">Current SRI</th></tr></thead>
<tbody>{priority_rows}</tbody>
</table></div>

</div>

<script>
// Branch gap chart
new Chart(document.getElementById('branchGapChart'), {{
  type: 'bar',
  data: {{
    labels: {jdumps(all_bcs)},
    datasets: [{{
      label: 'Missing instruments',
      data: {jdumps([branch_gaps.get(bc, 0) for bc in all_bcs])},
      backgroundColor: {jdumps(["#dc2626" if branch_gaps.get(bc, 0) >= 5 else "#d97706" if branch_gaps.get(bc, 0) >= 2 else "#16a34a" for bc in all_bcs])}
    }}]
  }},
  options: {{
    indexAxis: 'y',
    scales: {{x: {{max: 9, ticks: {{stepSize: 1}}}}}},
    plugins: {{legend: {{display: false}}}}
  }}
}});

// Instrument gap chart
new Chart(document.getElementById('instGapChart'), {{
  type: 'bar',
  data: {{
    labels: {jdumps([inst_name for inst_name, _, _ in INSTRUMENTS])},
    datasets: [
      {{label: 'Covered', data: {jdumps([len(all_bcs) - inst_gaps.get(inst_name, 0) for inst_name, _, _ in INSTRUMENTS])}, backgroundColor: '#16a34a'}},
      {{label: 'Missing', data: {jdumps([inst_gaps.get(inst_name, 0) for inst_name, _, _ in INSTRUMENTS])}, backgroundColor: '#dc2626'}}
    ]
  }},
  options: {{
    scales: {{x: {{stacked: true}}, y: {{stacked: true, max: {len(all_bcs)}}}}},
    plugins: {{legend: {{position: 'top'}}}}
  }}
}});
</script>

{footer()}
</body>
</html>"""

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(html)
    print(f"Written: {OUT_PATH} ({os.path.getsize(OUT_PATH) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
