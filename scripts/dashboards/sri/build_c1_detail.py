"""
Build C1 Intent Readiness detail dashboard.
Output: output/dashboards/sri/01_c1_intent.html
"""

import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
from scripts.dashboards.sri.html_utils import (
    html_doc, jdumps, C_COLORS, C_NAMES, C_MAX, band_badge
)

DATA_PATH = os.path.join(ROOT, "output", "reports", "sri_unified.json")
OUT_PATH = os.path.join(ROOT, "output", "dashboards", "sri", "01_c1_intent.html")
FPS = ["FP1", "FP2", "FP3", "FP4", "FP5"]
FP_LABELS = {
    "FP1": "Holistic Development",
    "FP2": "Foundational Literacy & Numeracy",
    "FP3": "Competency-Based Learning",
    "FP4": "Inclusive Education",
    "FP5": "Multilingual Education",
}


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def build_html(data):
    branches = data["branches"]
    bcs = sorted(branches.keys())

    # Collect c1_detail per branch
    rows = []
    for bc in bcs:
        d = branches[bc].get("c1_detail")
        if not d:
            continue
        rows.append({"bc": bc, **d})

    # Compute aggregates
    avg_c1 = sum(r["C1"] for r in rows) / len(rows) if rows else 0
    avg_alignment = sum(r.get("alignment", 0) for r in rows) / len(rows) if rows else 0
    total_teachers = sum(r.get("teacher_count", 0) for r in rows)
    total_leaders = sum(r.get("leader_count", 0) for r in rows)
    high_align = sum(1 for r in rows if r.get("alignment", 0) >= 0.8)

    # Overall FP distribution (sum teacher ADV across branches)
    fp_totals = {fp: 0 for fp in FPS}
    for r in rows:
        tadv = r.get("teacher_adv", {})
        for fp in FPS:
            fp_totals[fp] += tadv.get(fp, 0)

    # Use only branches with valid data for charts
    valid_bcs = [r["bc"] for r in rows]

    # --- Tab 1: ADV Overview ---
    tab1_labels = jdumps(valid_bcs)
    fp_datasets = []
    fp_colors = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"]
    for i, fp in enumerate(FPS):
        vals = [branches[bc]["c1_detail"]["teacher_adv"].get(fp, 0) for bc in valid_bcs]
        fp_datasets.append({
            "label": fp,
            "data": vals,
            "backgroundColor": fp_colors[i],
        })

    tab1 = f'''<div id="tab1" class="content active">
<div class="cards">
  <div class="card"><div class="label">Avg C1 Score</div><div class="value" style="color:{C_COLORS['C1']}">{avg_c1:.1f}<span style="font-size:14px;color:var(--muted)">/{C_MAX['C1']}</span></div><div class="sub">{avg_c1/C_MAX['C1']*100:.0f}% across {len(rows)} branches</div></div>
  <div class="card"><div class="label">Avg Alignment</div><div class="value">{avg_alignment:.3f}</div><div class="sub">{high_align} branches >= 0.8</div></div>
  <div class="card"><div class="label">Total Teachers</div><div class="value">{total_teachers}</div><div class="sub">Across {len(rows)} branches</div></div>
  <div class="card"><div class="label">Total Leaders</div><div class="value">{total_leaders}</div><div class="sub">Across {len(rows)} branches</div></div>
</div>
<div class="info-box">ADV (Aggregate Direction Value) measures the proportion of respondents who agree/strongly agree with each Focus Priority. Values range 0-1.</div>
<div class="chart-box"><h3>Teacher ADV by Branch and Focus Priority</h3>
<div style="overflow-x:auto"><canvas id="advChart" height="90"></canvas></div></div>
</div>'''

    # --- Tab 2: Alignment ---
    align_rows_html = ""
    for r in rows:
        align_rows_html += f'''<tr>
<td>{r["bc"]}</td>
<td>{r.get("teacher_coverage",0):.3f}</td>
<td>{r.get("leader_coverage",0):.3f}</td>
<td>{r.get("teacher_balance",0):.3f}</td>
<td>{r.get("leader_balance",0):.3f}</td>
<td><strong>{r.get("alignment",0):.3f}</strong></td>
<td>{r.get("teacher_count",0)}</td>
<td>{r.get("leader_count",0)}</td>
</tr>'''

    align_bcs = [r["bc"] for r in rows]
    align_vals = [r.get("alignment", 0) for r in rows]

    tab2 = f'''<div id="tab2" class="content">
<div class="info-box">Alignment measures how well teacher and leader intent priorities match. Coverage = fraction of FPs with respondents. Balance = evenness across FPs.</div>
<div class="chart-box"><h3>Alignment Score by Branch</h3>
<canvas id="alignChart" height="70"></canvas></div>
<div class="section-title">Alignment Breakdown</div>
<div class="tbl-wrap"><table id="alignTable">
<thead><tr>
<th onclick="sortTable('alignTable',0,'str')">Branch</th>
<th onclick="sortTable('alignTable',1,'num')">T.Coverage</th>
<th onclick="sortTable('alignTable',2,'num')">L.Coverage</th>
<th onclick="sortTable('alignTable',3,'num')">T.Balance</th>
<th onclick="sortTable('alignTable',4,'num')">L.Balance</th>
<th onclick="sortTable('alignTable',5,'num')">Alignment</th>
<th onclick="sortTable('alignTable',6,'num')">Teachers</th>
<th onclick="sortTable('alignTable',7,'num')">Leaders</th>
</tr></thead>
<tbody>{align_rows_html}</tbody></table></div></div>'''

    # --- Tab 3: FP Distribution ---
    fp_total_vals = [round(fp_totals[fp], 2) for fp in FPS]
    fp_labels_full = [f"{fp}: {FP_LABELS.get(fp, fp)}" for fp in FPS]

    # Per-branch stacked bar data
    stacked_datasets = []
    for i, fp in enumerate(FPS):
        vals = [round(branches[bc]["c1_detail"]["teacher_adv"].get(fp, 0), 4) for bc in valid_bcs]
        stacked_datasets.append({
            "label": fp,
            "data": vals,
            "backgroundColor": fp_colors[i],
        })

    tab3 = f'''<div id="tab3" class="content">
<div class="grid-2">
<div class="chart-box"><h3>Overall Teacher FP Distribution (Sum ADV)</h3>
<canvas id="fpDoughnut" height="250"></canvas></div>
<div class="chart-box"><h3>FP Legend</h3>
<table><thead><tr><th>FP</th><th>Focus Priority</th><th>Total ADV</th></tr></thead><tbody>
{"".join(f'<tr><td><span class="badge" style="background:{fp_colors[i]};color:#fff">{FPS[i]}</span></td><td>{FP_LABELS.get(FPS[i],"")}</td><td>{fp_total_vals[i]:.2f}</td></tr>' for i in range(5))}
</tbody></table></div>
</div>
<div class="chart-box"><h3>Per-Branch Stacked ADV</h3>
<div style="overflow-x:auto"><canvas id="stackedBar" height="80"></canvas></div></div>
</div>'''

    # --- Tab 4: Branch Detail ---
    detail_rows = ""
    csv_data = [["Branch", "C1", "T_Score", "L_Score", "Alignment",
                 "T_Coverage", "L_Coverage", "T_Balance", "L_Balance",
                 "FP1", "FP2", "FP3", "FP4", "FP5", "Teachers", "Leaders"]]
    for r in rows:
        tadv = r.get("teacher_adv", {})
        csv_row = [
            r["bc"], f'{r["C1"]:.2f}', f'{r.get("teacher_score",0):.3f}',
            f'{r.get("leader_score",0):.3f}', f'{r.get("alignment",0):.3f}',
            f'{r.get("teacher_coverage",0):.3f}', f'{r.get("leader_coverage",0):.3f}',
            f'{r.get("teacher_balance",0):.3f}', f'{r.get("leader_balance",0):.3f}',
            *[f'{tadv.get(fp,0):.4f}' for fp in FPS],
            str(r.get("teacher_count", 0)), str(r.get("leader_count", 0))
        ]
        csv_data.append(csv_row)
        detail_rows += f'''<tr>
<td>{r["bc"]}</td>
<td><strong>{r["C1"]:.2f}</strong></td>
<td>{r.get("teacher_score",0):.3f}</td>
<td>{r.get("leader_score",0):.3f}</td>
<td>{r.get("alignment",0):.3f}</td>
<td>{r.get("teacher_coverage",0):.3f}</td>
<td>{r.get("leader_coverage",0):.3f}</td>
<td>{r.get("teacher_balance",0):.3f}</td>
<td>{r.get("leader_balance",0):.3f}</td>
{"".join(f'<td>{tadv.get(fp,0):.4f}</td>' for fp in FPS)}
<td>{r.get("teacher_count",0)}</td>
<td>{r.get("leader_count",0)}</td>
</tr>'''

    tab4 = f'''<div id="tab4" class="content">
<div style="margin-bottom:12px">
  <button class="btn btn-blue" onclick="downloadCSV({jdumps(csv_data)},'c1_intent_detail.csv')">Download CSV</button>
</div>
<div class="tbl-wrap"><table id="detailTable">
<thead><tr>
<th onclick="sortTable('detailTable',0,'str')">Branch</th>
<th onclick="sortTable('detailTable',1,'num')">C1</th>
<th onclick="sortTable('detailTable',2,'num')">T.Score</th>
<th onclick="sortTable('detailTable',3,'num')">L.Score</th>
<th onclick="sortTable('detailTable',4,'num')">Alignment</th>
<th onclick="sortTable('detailTable',5,'num')">T.Cov</th>
<th onclick="sortTable('detailTable',6,'num')">L.Cov</th>
<th onclick="sortTable('detailTable',7,'num')">T.Bal</th>
<th onclick="sortTable('detailTable',8,'num')">L.Bal</th>
<th onclick="sortTable('detailTable',9,'num')">FP1</th>
<th onclick="sortTable('detailTable',10,'num')">FP2</th>
<th onclick="sortTable('detailTable',11,'num')">FP3</th>
<th onclick="sortTable('detailTable',12,'num')">FP4</th>
<th onclick="sortTable('detailTable',13,'num')">FP5</th>
<th onclick="sortTable('detailTable',14,'num')">Teachers</th>
<th onclick="sortTable('detailTable',15,'num')">Leaders</th>
</tr></thead>
<tbody>{detail_rows}</tbody></table></div></div>'''

    # Tabs bar
    tabs_html = '''<div class="tabs">
<div class="tab active" onclick="showTab('tab1')">ADV Overview</div>
<div class="tab" onclick="showTab('tab2')">Alignment</div>
<div class="tab" onclick="showTab('tab3')">FP Distribution</div>
<div class="tab" onclick="showTab('tab4')">Branch Detail</div>
</div>'''

    content_html = tab1 + tab2 + tab3 + tab4

    extra_js = f"""
// Tab 1: ADV grouped bar
new Chart(document.getElementById('advChart'), {{
  type: 'bar',
  data: {{ labels: {tab1_labels}, datasets: {jdumps(fp_datasets)} }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{ y: {{ beginAtZero: true, max: 1, title: {{ display: true, text: 'ADV (0-1)' }} }} }}
  }}
}});

// Tab 2: Alignment bar
new Chart(document.getElementById('alignChart'), {{
  type: 'bar',
  data: {{
    labels: {jdumps(align_bcs)},
    datasets: [{{ label: 'Alignment', data: {jdumps(align_vals)},
      backgroundColor: {jdumps(align_vals)}.map(v => v >= 0.8 ? '#16a34a' : v >= 0.5 ? '#d97706' : '#dc2626')
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ y: {{ beginAtZero: true, max: 1, title: {{ display: true, text: 'Alignment Score' }} }} }}
  }}
}});

// Tab 3: Doughnut
new Chart(document.getElementById('fpDoughnut'), {{
  type: 'doughnut',
  data: {{
    labels: {jdumps(fp_labels_full)},
    datasets: [{{ data: {jdumps(fp_total_vals)}, backgroundColor: {jdumps(fp_colors)} }}]
  }},
  options: {{ responsive: true, plugins: {{ legend: {{ position: 'right' }} }} }}
}});

// Tab 3: Stacked bar
new Chart(document.getElementById('stackedBar'), {{
  type: 'bar',
  data: {{ labels: {tab1_labels}, datasets: {jdumps(stacked_datasets)} }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{
      x: {{ stacked: true }},
      y: {{ stacked: true, title: {{ display: true, text: 'Cumulative ADV' }} }}
    }}
  }}
}});
"""

    return html_doc(
        "C1: Intent Readiness Detail",
        "01_c1_intent.html",
        tabs_html,
        content_html,
        extra_js=extra_js,
    )


def main():
    data = load_data()
    html = build_html(data)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(html)
    print(f"Written: {OUT_PATH}")


if __name__ == "__main__":
    main()
