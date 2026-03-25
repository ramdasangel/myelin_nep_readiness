"""
Build C3 Capacity Readiness detail dashboard.
Output: output/dashboards/sri/03_c3_capacity.html
"""

import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
from scripts.dashboards.sri.html_utils import (
    html_doc, jdumps, C_COLORS, C_NAMES, C_MAX
)

DATA_PATH = os.path.join(ROOT, "output", "reports", "sri_unified.json")
OUT_PATH = os.path.join(ROOT, "output", "dashboards", "sri", "03_c3_capacity.html")
CPDS = ["CPD1", "CPD2", "CPD3", "CPD4"]
CPD_LABELS = {
    "CPD1": "Higher-order Thinking",
    "CPD2": "Decomposition",
    "CPD3": "Revision",
    "CPD4": "Consistency",
}
CPD_DESC = {
    "CPD1": "Measures the proportion of tasks selected that target higher-order cognitive skills (analyse, evaluate, create).",
    "CPD2": "Measures how well users break down complex tasks into sub-steps, reflecting planning depth.",
    "CPD3": "Captures revision behavior -- whether users revisit and refine their daily progress entries.",
    "CPD4": "Measures sustained engagement across the intervention period, rewarding consistent daily participation.",
}


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def build_html(data):
    branches = data["branches"]
    bcs = sorted(branches.keys())

    rows = []
    for bc in bcs:
        d = branches[bc].get("c3_detail")
        if not d:
            continue
        rows.append({"bc": bc, **d})

    valid_bcs = [r["bc"] for r in rows]
    avg_c3 = sum(r["C3"] for r in rows) / len(rows) if rows else 0
    avg_cpi = sum(r.get("cpi", 0) for r in rows) / len(rows) if rows else 0
    total_users = sum(r.get("respondents", 0) for r in rows)
    branches_with_data = len(rows)

    # Collect all user CPIs for histogram
    all_cpis = []
    for r in rows:
        all_cpis.extend(r.get("user_cpis", []))

    # Histogram bins
    bins = [(0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
    bin_labels = ["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]
    bin_counts = [0] * 5
    for v in all_cpis:
        for i, (lo, hi) in enumerate(bins):
            if lo <= v < hi or (i == 4 and v == 1.0):
                bin_counts[i] += 1
                break

    # Sort rows by CPI for bar chart
    sorted_rows = sorted(rows, key=lambda x: x.get("cpi", 0), reverse=True)

    # --- Tab 1: CPI Overview ---
    cpi_bcs = [r["bc"] for r in sorted_rows]
    cpi_vals = [round(r.get("cpi", 0), 4) for r in sorted_rows]
    cpi_colors = [("#16a34a" if v >= 0.7 else "#d97706" if v >= 0.5 else "#dc2626") for v in cpi_vals]

    tab1 = f'''<div id="tab1" class="content active">
<div class="cards">
  <div class="card"><div class="label">Avg C3 Score</div><div class="value" style="color:{C_COLORS['C3']}">{avg_c3:.1f}<span style="font-size:14px;color:var(--muted)">/{C_MAX['C3']}</span></div><div class="sub">{avg_c3/C_MAX['C3']*100:.0f}% across {branches_with_data} branches</div></div>
  <div class="card"><div class="label">Total Users</div><div class="value">{total_users}</div><div class="sub">With micro-intervention data</div></div>
  <div class="card"><div class="label">Branches with Data</div><div class="value">{branches_with_data}</div><div class="sub">Out of {len(bcs)} total</div></div>
  <div class="card"><div class="label">Avg CPI</div><div class="value">{avg_cpi:.3f}</div><div class="sub">Composite Performance Index</div></div>
</div>
<div class="info-box">CPI (Composite Performance Index) aggregates four capacity dimensions (CPD1-CPD4) into a single 0-1 score per user. Branch CPI is the mean of user CPIs. C3 = CPI x {C_MAX['C3']}.</div>
<div class="chart-box"><h3>CPI by Branch (sorted)</h3>
<canvas id="cpiChart" height="80"></canvas></div></div>'''

    # --- Tab 2: CPD Dimensions ---
    cpd_colors = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b"]
    cpd_datasets = []
    for i, cpd in enumerate(CPDS):
        vals = [round(branches[bc]["c3_detail"]["cpd_means"].get(cpd, 0), 4) for bc in valid_bcs]
        cpd_datasets.append({
            "label": cpd,
            "data": vals,
            "backgroundColor": cpd_colors[i],
        })

    cpd_cards = ""
    for i, cpd in enumerate(CPDS):
        all_vals = [r.get("cpd_means", {}).get(cpd, 0) for r in rows]
        mean_val = sum(all_vals) / len(all_vals) if all_vals else 0
        cpd_cards += f'''<div class="card">
<div class="label" style="color:{cpd_colors[i]}">{cpd}: {CPD_LABELS[cpd]}</div>
<div class="value" style="color:{cpd_colors[i]}">{mean_val:.3f}</div>
<div class="sub">{CPD_DESC[cpd]}</div></div>'''

    tab2 = f'''<div id="tab2" class="content">
<div class="cards">{cpd_cards}</div>
<div class="chart-box"><h3>CPD Dimensions by Branch</h3>
<div style="overflow-x:auto"><canvas id="cpdChart" height="90"></canvas></div></div></div>'''

    # --- Tab 3: User Distribution ---
    hist_colors = ["#dc2626", "#f59e0b", "#d97706", "#2563eb", "#16a34a"]

    tab3 = f'''<div id="tab3" class="content">
<div class="info-box">Distribution of individual user CPI scores across all {total_users} users from {branches_with_data} branches.</div>
<div class="cards">
  <div class="card"><div class="label">Total Users</div><div class="value">{len(all_cpis)}</div></div>
  <div class="card"><div class="label">Mean CPI</div><div class="value">{sum(all_cpis)/len(all_cpis):.3f}</div></div>
  <div class="card"><div class="label">Min CPI</div><div class="value">{min(all_cpis):.3f}</div></div>
  <div class="card"><div class="label">Max CPI</div><div class="value">{max(all_cpis):.3f}</div></div>
</div>
<div class="grid-2">
<div class="chart-box"><h3>User CPI Histogram</h3>
<canvas id="histChart" height="250"></canvas></div>
<div class="chart-box"><h3>Distribution Summary</h3>
<table><thead><tr><th>Bin</th><th>Count</th><th>%</th></tr></thead><tbody>
{"".join(f'<tr><td>{bin_labels[i]}</td><td>{bin_counts[i]}</td><td>{bin_counts[i]/len(all_cpis)*100:.1f}%</td></tr>' for i in range(5))}
</tbody></table></div>
</div></div>'''

    # --- Tab 4: Branch Detail ---
    csv_data = [["Branch", "C3", "CPI", "CPD1", "CPD2", "CPD3", "CPD4", "Respondents"]]
    detail_rows = ""
    for r in sorted(rows, key=lambda x: x["bc"]):
        cpd = r.get("cpd_means", {})
        csv_row = [
            r["bc"], f'{r["C3"]:.2f}', f'{r.get("cpi",0):.4f}',
            *[f'{cpd.get(c,0):.4f}' for c in CPDS],
            str(r.get("respondents", 0))
        ]
        csv_data.append(csv_row)
        detail_rows += f'''<tr>
<td>{r["bc"]}</td>
<td><strong>{r["C3"]:.2f}</strong></td>
<td>{r.get("cpi",0):.4f}</td>
{"".join(f'<td>{cpd.get(c,0):.4f}</td>' for c in CPDS)}
<td>{r.get("respondents",0)}</td>
</tr>'''

    tab4 = f'''<div id="tab4" class="content">
<div style="margin-bottom:12px">
  <button class="btn btn-blue" onclick="downloadCSV({jdumps(csv_data)},'c3_capacity_detail.csv')">Download CSV</button>
</div>
<div class="tbl-wrap"><table id="detailTable">
<thead><tr>
<th onclick="sortTable('detailTable',0,'str')">Branch</th>
<th onclick="sortTable('detailTable',1,'num')">C3</th>
<th onclick="sortTable('detailTable',2,'num')">CPI</th>
<th onclick="sortTable('detailTable',3,'num')">CPD1</th>
<th onclick="sortTable('detailTable',4,'num')">CPD2</th>
<th onclick="sortTable('detailTable',5,'num')">CPD3</th>
<th onclick="sortTable('detailTable',6,'num')">CPD4</th>
<th onclick="sortTable('detailTable',7,'num')">Respondents</th>
</tr></thead>
<tbody>{detail_rows}</tbody></table></div></div>'''

    tabs_html = '''<div class="tabs">
<div class="tab active" onclick="showTab('tab1')">CPI Overview</div>
<div class="tab" onclick="showTab('tab2')">CPD Dimensions</div>
<div class="tab" onclick="showTab('tab3')">User Distribution</div>
<div class="tab" onclick="showTab('tab4')">Branch Detail</div>
</div>'''

    content_html = tab1 + tab2 + tab3 + tab4

    extra_js = f"""
// Tab 1: CPI bar chart
new Chart(document.getElementById('cpiChart'), {{
  type: 'bar',
  data: {{
    labels: {jdumps(cpi_bcs)},
    datasets: [{{
      label: 'CPI',
      data: {jdumps(cpi_vals)},
      backgroundColor: {jdumps(cpi_colors)}
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ y: {{ beginAtZero: true, max: 1, title: {{ display: true, text: 'CPI (0-1)' }} }} }}
  }}
}});

// Tab 2: CPD grouped bar
new Chart(document.getElementById('cpdChart'), {{
  type: 'bar',
  data: {{ labels: {jdumps(valid_bcs)}, datasets: {jdumps(cpd_datasets)} }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{ y: {{ beginAtZero: true, max: 1, title: {{ display: true, text: 'CPD Mean (0-1)' }} }} }}
  }}
}});

// Tab 3: Histogram
new Chart(document.getElementById('histChart'), {{
  type: 'bar',
  data: {{
    labels: {jdumps(bin_labels)},
    datasets: [{{
      label: 'Users',
      data: {jdumps(bin_counts)},
      backgroundColor: {jdumps(hist_colors)},
      borderWidth: 1,
      borderColor: '#fff'
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      y: {{ beginAtZero: true, title: {{ display: true, text: 'Number of Users' }} }},
      x: {{ title: {{ display: true, text: 'CPI Range' }} }}
    }}
  }}
}});
"""

    return html_doc(
        "C3: Capacity Readiness Detail",
        "03_c3_capacity.html",
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
