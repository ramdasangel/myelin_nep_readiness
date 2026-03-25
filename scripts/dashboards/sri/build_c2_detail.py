"""
Build C2 Practice Readiness detail dashboard.
Output: output/dashboards/sri/02_c2_practice.html
"""

import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
from scripts.dashboards.sri.html_utils import (
    html_doc, jdumps, C_COLORS, C_NAMES, C_MAX
)

DATA_PATH = os.path.join(ROOT, "output", "reports", "sri_unified.json")
OUT_PATH = os.path.join(ROOT, "output", "dashboards", "sri", "02_c2_practice.html")
FPS = ["FP1", "FP2", "FP3", "FP4", "FP5"]
DEPTHS = ["D1", "D2", "D3", "D4"]
# Non-observable cells (zero by design)
NON_OBS = {("FP1", "D1"), ("FP1", "D4"), ("FP2", "D4")}
DEPTH_LABELS = {
    "D1": "Recall / Reproduce",
    "D2": "Apply / Understand",
    "D3": "Analyse / Evaluate",
    "D4": "Create / Transfer",
}


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def build_html(data):
    branches = data["branches"]
    bcs = sorted(branches.keys())

    rows = []
    for bc in bcs:
        d = branches[bc].get("c2_detail")
        if not d:
            continue
        rows.append({"bc": bc, **d})

    valid_bcs = [r["bc"] for r in rows]
    avg_c2 = sum(r["C2"] for r in rows) / len(rows) if rows else 0
    c2_vals = [r["C2"] for r in rows]
    c2_range = f"{min(c2_vals):.1f} - {max(c2_vals):.1f}" if c2_vals else "N/A"
    avg_de = sum(r.get("depth_effectiveness", 0) for r in rows) / len(rows) if rows else 0
    avg_cov = sum(r.get("coverage_fp", 0) for r in rows) / len(rows) if rows else 0

    # Build branch options for PDDM dropdown
    branch_options = "".join(f'<option value="{r["bc"]}">{r["bc"]}</option>' for r in rows)

    # Pre-build PDDM data for all branches as JS object
    pddm_all = {}
    for r in rows:
        pddm_all[r["bc"]] = r.get("pddm", {})

    # --- Tab 1: PDDM Overview ---
    tab1 = f'''<div id="tab1" class="content active">
<div class="info-box">PDDM (Practice Depth Distribution Matrix) shows how many daily-log entries fall into each Focus Priority x Depth combination. Non-observable cells are grayed out.</div>
<div style="margin-bottom:16px">
  <label style="font-weight:600;font-size:13px;margin-right:8px">Select Branch:</label>
  <select id="pddmBranch" onchange="renderPDDM(this.value)">{branch_options}</select>
</div>
<div class="chart-box"><h3 id="pddmTitle">PDDM: {rows[0]["bc"] if rows else ""}</h3>
<div class="tbl-wrap">
<table id="pddmTable">
<thead><tr><th>FP</th><th>D1<br><span style="font-weight:400;font-size:10px">{DEPTH_LABELS["D1"]}</span></th><th>D2<br><span style="font-weight:400;font-size:10px">{DEPTH_LABELS["D2"]}</span></th><th>D3<br><span style="font-weight:400;font-size:10px">{DEPTH_LABELS["D3"]}</span></th><th>D4<br><span style="font-weight:400;font-size:10px">{DEPTH_LABELS["D4"]}</span></th><th>Row Total</th></tr></thead>
<tbody id="pddmBody"></tbody>
</table>
</div></div></div>'''

    # --- Tab 2: Depth Effectiveness ---
    de_bcs = [r["bc"] for r in sorted(rows, key=lambda x: x["C2"], reverse=True)]
    de_vals = [r["C2"] for r in sorted(rows, key=lambda x: x["C2"], reverse=True)]
    de_colors = [("#16a34a" if v >= 18 else "#d97706" if v >= 12 else "#dc2626") for v in de_vals]

    tab2 = f'''<div id="tab2" class="content">
<div class="cards">
  <div class="card"><div class="label">Avg C2 Score</div><div class="value" style="color:{C_COLORS['C2']}">{avg_c2:.1f}<span style="font-size:14px;color:var(--muted)">/{C_MAX['C2']}</span></div><div class="sub">{avg_c2/C_MAX['C2']*100:.0f}% across {len(rows)} branches</div></div>
  <div class="card"><div class="label">C2 Range</div><div class="value" style="font-size:22px">{c2_range}</div><div class="sub">Min to Max</div></div>
  <div class="card"><div class="label">Avg Depth Effectiveness</div><div class="value">{avg_de:.3f}</div><div class="sub">Normalized 0-1</div></div>
  <div class="card"><div class="label">Avg FP Coverage</div><div class="value">{avg_cov:.3f}</div><div class="sub">{sum(1 for r in rows if r.get("coverage_fp",0)==1.0)} branches at 100%</div></div>
</div>
<div class="chart-box"><h3>C2 Score by Branch (sorted)</h3>
<canvas id="deChart" height="80"></canvas></div></div>'''

    # --- Tab 3: FP Depth (Radar) ---
    # Mean e_norm across valid branches
    mean_enorm = {}
    for fp in FPS:
        vals = [r.get("e_norm", {}).get(fp, 0) for r in rows]
        mean_enorm[fp] = sum(vals) / len(vals) if vals else 0
    radar_vals = [round(mean_enorm[fp], 4) for fp in FPS]

    enorm_rows_html = ""
    for r in rows:
        en = r.get("e_norm", {})
        enorm_rows_html += f'''<tr>
<td>{r["bc"]}</td>
{"".join(f'<td>{en.get(fp,0):.4f}</td>' for fp in FPS)}
<td><strong>{r.get("mean_e_norm",0):.4f}</strong></td>
</tr>'''

    enorm_th = "".join(
        '<th onclick="sortTable(\'enormTable\',{},\'num\')">{}</th>'.format(i + 1, fp)
        for i, fp in enumerate(FPS)
    )

    tab3 = f'''<div id="tab3" class="content">
<div class="grid-2">
<div class="chart-box"><h3>Mean Normalized Depth (e_norm) by FP</h3>
<canvas id="radarChart" height="300"></canvas></div>
<div class="chart-box"><h3>e_norm Interpretation</h3>
<div style="font-size:13px;line-height:1.8">
<p><strong>e_norm</strong> captures how deep practice observations go for each Focus Priority, normalized to 0-1.</p>
<ul style="margin:8px 0 0 16px">
<li><strong>FP1</strong> has only D2-D3 observable (max depth 3)</li>
<li><strong>FP2</strong> has D1-D3 observable (max depth 3)</li>
<li><strong>FP3-FP5</strong> have all D1-D4 observable (max depth 4)</li>
</ul>
<p style="margin-top:12px">Higher e_norm = deeper practice across depth levels.</p>
</div></div>
</div>
<div class="section-title">Per-Branch e_norm Values</div>
<div class="tbl-wrap"><table id="enormTable">
<thead><tr>
<th onclick="sortTable('enormTable',0,'str')">Branch</th>
{enorm_th}
<th onclick="sortTable('enormTable',6,'num')">Mean</th>
</tr></thead>
<tbody>{enorm_rows_html}</tbody></table></div></div>'''

    # --- Tab 4: Branch Detail ---
    csv_data = [["Branch", "C2", "Depth_Effectiveness", "Coverage_FP", "Mean_e_norm",
                 "e_FP1", "e_FP2", "e_FP3", "e_FP4", "e_FP5"]]
    detail_rows = ""
    for r in rows:
        en = r.get("e_norm", {})
        csv_row = [
            r["bc"], f'{r["C2"]:.2f}', f'{r.get("depth_effectiveness",0):.4f}',
            f'{r.get("coverage_fp",0):.3f}', f'{r.get("mean_e_norm",0):.4f}',
            *[f'{en.get(fp,0):.4f}' for fp in FPS]
        ]
        csv_data.append(csv_row)
        detail_rows += f'''<tr>
<td>{r["bc"]}</td>
<td><strong>{r["C2"]:.2f}</strong></td>
<td>{r.get("depth_effectiveness",0):.4f}</td>
<td>{r.get("coverage_fp",0):.3f}</td>
<td>{r.get("mean_e_norm",0):.4f}</td>
{"".join(f'<td>{en.get(fp,0):.4f}</td>' for fp in FPS)}
</tr>'''

    tab4 = f'''<div id="tab4" class="content">
<div style="margin-bottom:12px">
  <button class="btn btn-blue" onclick="downloadCSV({jdumps(csv_data)},'c2_practice_detail.csv')">Download CSV</button>
</div>
<div class="tbl-wrap"><table id="detailTable">
<thead><tr>
<th onclick="sortTable('detailTable',0,'str')">Branch</th>
<th onclick="sortTable('detailTable',1,'num')">C2</th>
<th onclick="sortTable('detailTable',2,'num')">Depth Eff.</th>
<th onclick="sortTable('detailTable',3,'num')">Coverage</th>
<th onclick="sortTable('detailTable',4,'num')">Mean e_norm</th>
<th onclick="sortTable('detailTable',5,'num')">e_FP1</th>
<th onclick="sortTable('detailTable',6,'num')">e_FP2</th>
<th onclick="sortTable('detailTable',7,'num')">e_FP3</th>
<th onclick="sortTable('detailTable',8,'num')">e_FP4</th>
<th onclick="sortTable('detailTable',9,'num')">e_FP5</th>
</tr></thead>
<tbody>{detail_rows}</tbody></table></div></div>'''

    tabs_html = '''<div class="tabs">
<div class="tab active" onclick="showTab('tab1')">PDDM Overview</div>
<div class="tab" onclick="showTab('tab2')">Depth Effectiveness</div>
<div class="tab" onclick="showTab('tab3')">FP Depth</div>
<div class="tab" onclick="showTab('tab4')">Branch Detail</div>
</div>'''

    content_html = tab1 + tab2 + tab3 + tab4

    non_obs_js = jdumps([list(x) for x in NON_OBS])

    extra_js = f"""
var pddmAll = {jdumps(pddm_all)};
var nonObs = {non_obs_js};
var nonObsSet = new Set(nonObs.map(function(x){{ return x[0]+'-'+x[1]; }}));
var fps = {jdumps(FPS)};
var depths = {jdumps(DEPTHS)};

function renderPDDM(bc) {{
  var pddm = pddmAll[bc] || {{}};
  document.getElementById('pddmTitle').textContent = 'PDDM: ' + bc;
  var tbody = document.getElementById('pddmBody');
  tbody.innerHTML = '';
  var maxVal = 0;
  fps.forEach(function(fp) {{
    depths.forEach(function(d) {{
      var v = (pddm[fp] || {{}})[d] || 0;
      if (v > maxVal) maxVal = v;
    }});
  }});
  fps.forEach(function(fp) {{
    var tr = document.createElement('tr');
    var rowTotal = 0;
    var cells = '<td><strong>' + fp + '</strong></td>';
    depths.forEach(function(d) {{
      var key = fp + '-' + d;
      var v = (pddm[fp] || {{}})[d] || 0;
      rowTotal += v;
      if (nonObsSet.has(key)) {{
        cells += '<td style="background:#f3f4f6;color:#9ca3af;text-align:center">N/O</td>';
      }} else {{
        var intensity = maxVal > 0 ? v / maxVal : 0;
        var bg = 'rgba(139,92,246,' + (0.08 + intensity * 0.6) + ')';
        cells += '<td style="background:' + bg + ';text-align:center;font-weight:600">' + v + '</td>';
      }}
    }});
    cells += '<td style="font-weight:600">' + rowTotal + '</td>';
    tr.innerHTML = cells;
    tbody.appendChild(tr);
  }});
}}
renderPDDM('{rows[0]["bc"] if rows else ""}');

// Tab 2: Depth Effectiveness bar
new Chart(document.getElementById('deChart'), {{
  type: 'bar',
  data: {{
    labels: {jdumps(de_bcs)},
    datasets: [{{
      label: 'C2 Score',
      data: {jdumps(de_vals)},
      backgroundColor: {jdumps(de_colors)}
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ y: {{ beginAtZero: true, max: {C_MAX['C2']}, title: {{ display: true, text: 'C2 Score (0-{C_MAX["C2"]})' }} }} }}
  }}
}});

// Tab 3: Radar
new Chart(document.getElementById('radarChart'), {{
  type: 'radar',
  data: {{
    labels: {jdumps(FPS)},
    datasets: [{{
      label: 'Mean e_norm',
      data: {jdumps(radar_vals)},
      backgroundColor: 'rgba(139,92,246,0.2)',
      borderColor: '#8b5cf6',
      borderWidth: 2,
      pointBackgroundColor: '#8b5cf6'
    }}]
  }},
  options: {{
    responsive: true,
    scales: {{ r: {{ beginAtZero: true, max: 1, ticks: {{ stepSize: 0.2 }} }} }},
    plugins: {{ legend: {{ display: false }} }}
  }}
}});
"""

    return html_doc(
        "C2: Practice Readiness Detail",
        "02_c2_practice.html",
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
