#!/usr/bin/env python3
"""
Build the SRI Summary Dashboard (00_sri_summary.html).

Reads sri_unified.json and produces a self-contained HTML dashboard
with 4 tabs: Overview, Branch Ranking, Radar Comparison, Data Coverage.

Usage:
    python3 scripts/dashboards/sri/build_sri_summary.py
"""

import json
import sys
from pathlib import Path

# Resolve paths relative to project root
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]
sys.path.insert(0, str(SCRIPT_DIR))

from html_utils import (
    C_COLORS, C_MAX, C_NAMES,
    construct_card, band_badge, jdumps,
    html_doc, nav_bar, header, footer,
)

DATA_FILE = PROJECT_ROOT / "output" / "reports" / "sri_unified.json"
OUT_DIR = PROJECT_ROOT / "output" / "dashboards" / "sri"
OUT_FILE = OUT_DIR / "00_sri_summary.html"

CONSTRUCTS = ["C1", "C2", "C3", "C4", "C5"]


def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)


def compute_stats(data):
    """Compute per-construct averages and coverage across branches."""
    branches = data["branches"]
    n = len(branches)
    stats = {}
    for cx in CONSTRUCTS:
        detail_key = f"{cx.lower()}_detail"
        scores = []
        has_data = 0
        for b in branches.values():
            s = b["summary"].get(cx, 0)
            scores.append(s)
            if b.get(detail_key) is not None:
                has_data += 1
        avg = sum(scores) / len(scores) if scores else 0
        stats[cx] = {"avg": avg, "max": C_MAX[cx], "coverage": has_data, "total": n}

    # SRI total
    totals = [b["summary"]["SRI_Total"] for b in branches.values()]
    stats["SRI"] = {
        "avg": sum(totals) / len(totals) if totals else 0,
        "max": 100,
        "scores": totals,
    }
    return stats


def _respondent_counts(branch):
    """Extract respondent counts per construct for a branch."""
    counts = {}
    c1 = branch.get("c1_detail")
    if c1:
        counts["C1"] = (c1.get("teacher_count", 0) or 0) + (c1.get("leader_count", 0) or 0)
    else:
        counts["C1"] = 0
    c2 = branch.get("c2_detail")
    # C2 uses the same respondent pool as C1 (baseline), count via coverage flag
    counts["C2"] = counts["C1"] if c2 is not None else 0
    c3 = branch.get("c3_detail")
    counts["C3"] = c3.get("respondents", 0) if c3 else 0
    c4 = branch.get("c4_detail")
    if c4:
        # teacher + leader baseline respondents
        t = c1.get("teacher_count", 0) if c1 else 0
        l = c1.get("leader_count", 0) if c1 else 0
        counts["C4"] = t + l
    else:
        counts["C4"] = 0
    c5 = branch.get("c5_detail")
    counts["C5"] = 1 if c5 is not None else 0
    return counts


# ── Tab 1: Overview ─────────────────────────────────────────────────
def build_overview(data, stats):
    branches = data["branches"]

    # Summary cards
    cards_html = '<div class="cards">'
    for cx in CONSTRUCTS:
        s = stats[cx]
        sub = f"{s['coverage']}/{s['total']} branches"
        cards_html += construct_card(cx, s["avg"], s["max"], sub)
    # SRI Total card
    sri = stats["SRI"]
    cards_html += f'''<div class="card">
<div class="label" style="color:#1e3a5f">SRI Total</div>
<div class="value" style="color:#1e3a5f">{sri["avg"]:.1f}<span style="font-size:14px;color:var(--muted)">/100</span></div>
<div class="sub">{sri["avg"]:.0f}% | {len(branches)} branches</div></div>'''
    cards_html += "</div>"

    # Prepare data for stacked bar chart
    branch_codes = sorted(branches.keys())
    bar_labels = json.dumps(branch_codes)
    datasets_js = []
    for cx in CONSTRUCTS:
        vals = [branches[bc]["summary"].get(cx, 0) for bc in branch_codes]
        datasets_js.append(
            f'{{label:"{cx} {C_NAMES[cx]}",data:{json.dumps(vals)},'
            f'backgroundColor:"{C_COLORS[cx]}"}}'
        )

    # SRI histogram data
    totals = [round(b["summary"]["SRI_Total"], 1) for b in branches.values()]
    bins = list(range(0, 101, 10))
    hist_counts = [0] * (len(bins) - 1)
    for t in totals:
        idx = min(int(t // 10), len(hist_counts) - 1)
        hist_counts[idx] += 1
    hist_labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins) - 1)]

    return f'''
<div class="content active" id="tab-overview">
  {cards_html}
  <div class="grid-2">
    <div class="chart-box">
      <h3>SRI Construct Breakdown by Branch</h3>
      <div style="overflow-x:auto"><canvas id="stackedBarChart" height="500"></canvas></div>
    </div>
    <div class="chart-box">
      <h3>SRI Total Distribution</h3>
      <canvas id="histChart" height="300"></canvas>
    </div>
  </div>
</div>
<script>
(function(){{
  var ctx1 = document.getElementById('stackedBarChart').getContext('2d');
  new Chart(ctx1, {{
    type: 'bar',
    data: {{
      labels: {bar_labels},
      datasets: [{",".join(datasets_js)}]
    }},
    options: {{
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{position:'top', labels:{{boxWidth:12, font:{{size:10}}}}}},
        tooltip: {{
          callbacks: {{
            label: function(ctx) {{ return ctx.dataset.label + ': ' + ctx.raw.toFixed(1); }}
          }}
        }}
      }},
      scales: {{
        x: {{stacked:true, max:100, title:{{display:true, text:'SRI Score'}}}},
        y: {{stacked:true, ticks:{{font:{{size:10}}}}}}
      }}
    }}
  }});

  var ctx2 = document.getElementById('histChart').getContext('2d');
  new Chart(ctx2, {{
    type: 'bar',
    data: {{
      labels: {json.dumps(hist_labels)},
      datasets: [{{
        label: 'Branches',
        data: {json.dumps(hist_counts)},
        backgroundColor: '#2563eb',
        borderRadius: 4
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{legend:{{display:false}}}},
      scales: {{
        y: {{beginAtZero:true, title:{{display:true, text:'Count'}}, ticks:{{stepSize:1}}}},
        x: {{title:{{display:true, text:'SRI Total Range'}}}}
      }}
    }}
  }});
}})();
</script>
'''


# ── Tab 2: Branch Ranking ──────────────────────────────────────────
def build_ranking(data):
    branches = data["branches"]
    sorted_codes = sorted(branches.keys(), key=lambda k: branches[k]["summary"]["SRI_Total"], reverse=True)

    def cell_color(val, mx):
        if mx == 0:
            return "background:#f3f4f6"
        pct = val / mx * 100
        if pct >= 70:
            return "background:#dcfce7;color:#166534"
        elif pct >= 40:
            return "background:#fef3c7;color:#92400e"
        else:
            return "background:#fee2e2;color:#991b1b"

    rows_html = ""
    csv_rows = [["Rank", "BranchCode", "BranchName", "C1", "C2", "C3", "C4", "C5", "SRI_Total", "SRI_%"]]
    for rank, bc in enumerate(sorted_codes, 1):
        b = branches[bc]
        s = b["summary"]
        name = b["branchName"]
        row = f"<tr><td>{rank}</td><td><b>{bc}</b></td><td>{name}</td>"
        for cx in CONSTRUCTS:
            v = s.get(cx, 0)
            row += f'<td style="{cell_color(v, C_MAX[cx])};text-align:center;font-weight:600">{v:.1f}</td>'
        row += f'<td style="text-align:center;font-weight:700">{s["SRI_Total"]:.1f}</td>'
        row += f'<td style="text-align:center">{s["SRI_Pct"]:.0f}%</td></tr>'
        rows_html += row
        csv_rows.append([rank, bc, name] + [round(s.get(cx, 0), 2) for cx in CONSTRUCTS] + [round(s["SRI_Total"], 2), round(s["SRI_Pct"], 1)])

    csv_data_js = json.dumps(csv_rows, default=str, ensure_ascii=False)

    return f'''
<div class="content" id="tab-ranking">
  <div style="margin-bottom:12px;display:flex;justify-content:space-between;align-items:center">
    <div class="info-box" style="margin-bottom:0;flex:1;margin-right:12px">
      Color coding: <span class="badge badge-green">>=70%</span>
      <span class="badge badge-amber">40-70%</span>
      <span class="badge badge-red">&lt;40%</span> of construct maximum
    </div>
    <button class="btn btn-blue" onclick="downloadCSV({csv_data_js}, 'sri_branch_ranking.csv')">Download CSV</button>
  </div>
  <div class="tbl-wrap">
    <table id="tblRanking">
      <thead><tr>
        <th onclick="sortTable('tblRanking',0,'num')">#</th>
        <th onclick="sortTable('tblRanking',1,'str')">Branch</th>
        <th onclick="sortTable('tblRanking',2,'str')">Name</th>
        <th onclick="sortTable('tblRanking',3,'num')">C1 /{C_MAX["C1"]}</th>
        <th onclick="sortTable('tblRanking',4,'num')">C2 /{C_MAX["C2"]}</th>
        <th onclick="sortTable('tblRanking',5,'num')">C3 /{C_MAX["C3"]}</th>
        <th onclick="sortTable('tblRanking',6,'num')">C4 /{C_MAX["C4"]}</th>
        <th onclick="sortTable('tblRanking',7,'num')">C5 /{C_MAX["C5"]}</th>
        <th onclick="sortTable('tblRanking',8,'num')">SRI Total</th>
        <th onclick="sortTable('tblRanking',9,'num')">SRI %</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>
</div>
'''


# ── Tab 3: Radar Comparison ────────────────────────────────────────
def build_radar(data):
    branches = data["branches"]
    sorted_codes = sorted(branches.keys())
    options_html = "".join(f'<option value="{bc}">{bc} - {branches[bc]["branchName"][:40]}</option>' for bc in sorted_codes)

    # Prepare normalized data (0-100%) for radar
    radar_data = {}
    for bc, b in branches.items():
        s = b["summary"]
        radar_data[bc] = [round(s.get(cx, 0) / C_MAX[cx] * 100, 1) for cx in CONSTRUCTS]

    radar_colors = ["rgba(37,99,235,0.7)", "rgba(220,38,38,0.7)", "rgba(22,163,74,0.7)"]
    radar_bg = ["rgba(37,99,235,0.1)", "rgba(220,38,38,0.1)", "rgba(22,163,74,0.1)"]

    return f'''
<div class="content" id="tab-radar">
  <div class="info-box">Select up to 3 branches to compare on a radar chart. Axes show % of construct maximum.</div>
  <div style="display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap">
    <select id="radar-sel-0" onchange="updateRadar()"><option value="">-- Branch 1 --</option>{options_html}</select>
    <select id="radar-sel-1" onchange="updateRadar()"><option value="">-- Branch 2 --</option>{options_html}</select>
    <select id="radar-sel-2" onchange="updateRadar()"><option value="">-- Branch 3 --</option>{options_html}</select>
  </div>
  <div class="chart-box" style="max-width:700px;margin:0 auto">
    <canvas id="radarChart" height="400"></canvas>
  </div>
</div>
<script>
(function(){{
  var RADAR_DATA = {json.dumps(radar_data)};
  var LABELS = {json.dumps([f"{cx} {C_NAMES[cx]}" for cx in CONSTRUCTS])};
  var COLORS = {json.dumps(radar_colors)};
  var BG = {json.dumps(radar_bg)};
  var radarChart = null;

  window.updateRadar = function() {{
    var datasets = [];
    for (var i = 0; i < 3; i++) {{
      var sel = document.getElementById('radar-sel-' + i);
      var bc = sel.value;
      if (bc && RADAR_DATA[bc]) {{
        datasets.push({{
          label: bc,
          data: RADAR_DATA[bc],
          borderColor: COLORS[i],
          backgroundColor: BG[i],
          borderWidth: 2,
          pointRadius: 4,
          pointBackgroundColor: COLORS[i]
        }});
      }}
    }}
    if (radarChart) radarChart.destroy();
    var ctx = document.getElementById('radarChart').getContext('2d');
    radarChart = new Chart(ctx, {{
      type: 'radar',
      data: {{ labels: LABELS, datasets: datasets }},
      options: {{
        responsive: true,
        plugins: {{ legend: {{ position: 'top' }} }},
        scales: {{
          r: {{
            min: 0, max: 100,
            ticks: {{ stepSize: 20, font: {{ size: 10 }} }},
            pointLabels: {{ font: {{ size: 11 }} }}
          }}
        }}
      }}
    }});
  }};
  updateRadar();
}})();
</script>
'''


# ── Tab 4: Data Coverage ───────────────────────────────────────────
def build_coverage(data):
    branches = data["branches"]
    sorted_codes = sorted(branches.keys())

    rows_html = ""
    for bc in sorted_codes:
        b = branches[bc]
        counts = _respondent_counts(b)
        row = f'<tr><td><b>{bc}</b></td><td style="font-size:11px">{b["branchName"][:35]}</td>'
        for cx in CONSTRUCTS:
            detail_key = f"{cx.lower()}_detail"
            has = b.get(detail_key) is not None
            cnt = counts.get(cx, 0)
            if has:
                row += f'<td style="text-align:center;background:#dcfce7;color:#166534;font-weight:600">&#10003; {cnt}</td>'
            else:
                row += '<td style="text-align:center;color:#9ca3af">&mdash;</td>'
        row += "</tr>"
        rows_html += row

    # Coverage summary counts
    coverage_summary = {}
    for cx in CONSTRUCTS:
        detail_key = f"{cx.lower()}_detail"
        coverage_summary[cx] = sum(1 for b in branches.values() if b.get(detail_key) is not None)
    summary_row = "<tr style='font-weight:700;background:#f1f3f8'><td colspan='2'>Total with data</td>"
    for cx in CONSTRUCTS:
        summary_row += f"<td style='text-align:center'>{coverage_summary[cx]}/{len(branches)}</td>"
    summary_row += "</tr>"

    return f'''
<div class="content" id="tab-coverage">
  <div class="info-box">Green checkmark with respondent count indicates data exists for that construct. Dash indicates no data.</div>
  <div class="tbl-wrap">
    <table>
      <thead><tr>
        <th>Branch</th><th>Name</th>
        <th style="text-align:center;color:{C_COLORS["C1"]}">C1 Intent</th>
        <th style="text-align:center;color:{C_COLORS["C2"]}">C2 Practice</th>
        <th style="text-align:center;color:{C_COLORS["C3"]}">C3 Capacity</th>
        <th style="text-align:center;color:{C_COLORS["C4"]}">C4 System</th>
        <th style="text-align:center;color:{C_COLORS["C5"]}">C5 Ecosystem</th>
      </tr></thead>
      <tbody>{rows_html}{summary_row}</tbody>
    </table>
  </div>
</div>
'''


# ── Assemble ────────────────────────────────────────────────────────
def main():
    data = load_data()
    stats = compute_stats(data)

    tabs_html = '''<div class="tabs">
<div class="tab active" onclick="showTab('tab-overview')">Overview</div>
<div class="tab" onclick="showTab('tab-ranking')">Branch Ranking</div>
<div class="tab" onclick="showTab('tab-radar')">Radar Comparison</div>
<div class="tab" onclick="showTab('tab-coverage')">Data Coverage</div>
</div>'''

    content = ""
    content += build_overview(data, stats)
    content += build_ranking(data)
    content += build_radar(data)
    content += build_coverage(data)

    page = html_doc(
        title="SRI Summary",
        active_file="00_sri_summary.html",
        tabs_html=tabs_html,
        content_html=content,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(page, encoding="utf-8")
    print(f"[OK] Written {OUT_FILE} ({len(page):,} bytes)")


if __name__ == "__main__":
    main()
