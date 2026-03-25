"""
Shared HTML utilities for all SRI dashboard pages.
Provides consistent CSS, navigation, headers, and helper functions.
"""

import json
from datetime import date

CHART_JS_CDN = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>'

# Construct colors
C_COLORS = {
    "C1": "#3b82f6",  # blue
    "C2": "#8b5cf6",  # purple
    "C3": "#10b981",  # green
    "C4": "#f59e0b",  # amber
    "C5": "#ef4444",  # red/coral
}

C_NAMES = {
    "C1": "Intent Readiness",
    "C2": "Practice Readiness",
    "C3": "Capacity Readiness",
    "C4": "System Readiness",
    "C5": "Ecosystem Readiness",
}

C_MAX = {"C1": 20, "C2": 25, "C3": 20, "C4": 20, "C5": 15}

PAGES = [
    ("00_sri_summary.html", "SRI Summary"),
    ("01_c1_intent.html", "C1 Intent"),
    ("02_c2_practice.html", "C2 Practice"),
    ("03_c3_capacity.html", "C3 Capacity"),
    ("04_c4_system.html", "C4 System"),
    ("05_c5_ecosystem.html", "C5 Ecosystem"),
    ("06_set_analysis.html", "SET Analysis"),
]


BASE_CSS = """
:root{--bg:#f5f6fa;--card:#fff;--border:#e0e3ea;--text:#1a1a2e;--muted:#6b7280;
--blue:#2563eb;--green:#16a34a;--amber:#d97706;--red:#dc2626;--purple:#7c3aed;--teal:#0d9488;
--c1:#3b82f6;--c2:#8b5cf6;--c3:#10b981;--c4:#f59e0b;--c5:#ef4444;
--radius:8px;--shadow:0 1px 3px rgba(0,0,0,.08)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.5}
.header{background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);color:#fff;padding:16px 32px;display:flex;align-items:center;justify-content:space-between}
.header h1{font-size:20px;font-weight:700;letter-spacing:-.3px}
.header .sub{font-size:12px;opacity:.8}
.nav-bar{display:flex;background:#1e293b;padding:0 24px;gap:2px;overflow-x:auto}
.nav-pill{padding:8px 14px;font-size:11px;font-weight:600;color:#94a3b8;text-decoration:none;white-space:nowrap;border-bottom:2px solid transparent;transition:.15s}
.nav-pill:hover{color:#e2e8f0;background:rgba(255,255,255,.05)}
.nav-pill.active{color:#fff;border-bottom-color:#3b82f6;background:rgba(59,130,246,.15)}
.tabs{display:flex;background:#fff;border-bottom:2px solid var(--border);padding:0 24px;overflow-x:auto;gap:2px;position:sticky;top:0;z-index:100}
.tab{padding:12px 18px;cursor:pointer;font-weight:600;font-size:13px;border-bottom:3px solid transparent;color:var(--muted);white-space:nowrap;transition:.15s}
.tab:hover{color:var(--text);background:#f8f9fb}
.tab.active{color:var(--blue);border-bottom-color:var(--blue)}
.content{display:none;padding:24px 32px;max-width:1800px;margin:0 auto}
.content.active{display:block}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow)}
.card .label{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);margin-bottom:4px}
.card .value{font-size:28px;font-weight:700}
.card .sub{font-size:12px;color:var(--muted);margin-top:2px}
table{width:100%;border-collapse:collapse;background:var(--card);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);font-size:12px}
th{background:#f1f3f8;font-weight:600;text-align:left;padding:8px 10px;border-bottom:2px solid var(--border);position:sticky;top:0;white-space:nowrap;cursor:pointer}
th:hover{background:#e2e5eb}
td{padding:6px 10px;border-bottom:1px solid var(--border)}
tr:hover td{background:#f8f9fc}
.tbl-wrap{overflow-x:auto;border-radius:var(--radius);margin-bottom:24px}
.bar{height:8px;border-radius:4px;background:#e5e7eb;position:relative;min-width:60px;display:inline-block;width:80px;vertical-align:middle;margin-right:6px}
.bar-fill{height:100%;border-radius:4px;transition:.3s}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:600}
.badge-green{background:#dcfce7;color:#166534}
.badge-amber{background:#fef3c7;color:#92400e}
.badge-red{background:#fee2e2;color:#991b1b}
.badge-gray{background:#f3f4f6;color:#6b7280}
.badge-blue{background:#dbeafe;color:#1e40af}
.badge-purple{background:#ede9fe;color:#5b21b6}
.chart-box{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;box-shadow:var(--shadow);margin-bottom:24px}
.chart-box h3{font-size:15px;margin-bottom:12px;color:var(--text)}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px}
.section-title{font-size:17px;font-weight:700;margin:24px 0 12px;padding-bottom:8px;border-bottom:2px solid var(--border)}
.section-title:first-child{margin-top:0}
.info-box{background:#eff6ff;border:1px solid #bfdbfe;border-radius:var(--radius);padding:14px 18px;margin-bottom:20px;font-size:13px;color:#1e40af}
.no-data{text-align:center;padding:40px 20px;color:var(--muted)}
.no-data h3{font-size:18px;margin-bottom:8px}
.btn{display:inline-block;padding:6px 14px;border-radius:6px;font-size:11px;font-weight:600;cursor:pointer;border:1px solid var(--border);background:#fff;color:var(--text);transition:.15s}
.btn:hover{background:#f1f3f8}
.btn-blue{background:var(--blue);color:#fff;border-color:var(--blue)}
.btn-blue:hover{background:#1d4ed8}
select{padding:6px 10px;border-radius:6px;border:1px solid var(--border);font-size:12px;background:#fff}
@media(max-width:900px){.grid-2,.grid-3{grid-template-columns:1fr}.content{padding:16px}}
@media print{.nav-bar,.tabs{display:none}.content{display:block!important;padding:10px}.header{padding:10px 20px;-webkit-print-color-adjust:exact;print-color-adjust:exact}.cards{grid-template-columns:repeat(3,1fr)}.chart-box{page-break-inside:avoid}canvas{max-height:300px}}
"""

TAB_JS = """
function showTab(id){
  document.querySelectorAll('.tab').forEach(function(t){t.classList.remove('active')});
  document.querySelectorAll('.content').forEach(function(c){c.classList.remove('active')});
  event.target.classList.add('active');
  document.getElementById(id).classList.add('active');
}
"""

SORT_JS = """
function sortTable(tableId, col, type) {
  var table = document.getElementById(tableId);
  var tbody = table.querySelector('tbody');
  var rows = Array.from(tbody.querySelectorAll('tr'));
  var dir = table.dataset.sortDir === 'asc' ? 'desc' : 'asc';
  table.dataset.sortDir = dir;
  rows.sort(function(a, b) {
    var av = a.cells[col].textContent.trim();
    var bv = b.cells[col].textContent.trim();
    if (type === 'num') { av = parseFloat(av) || 0; bv = parseFloat(bv) || 0; }
    if (dir === 'asc') return av > bv ? 1 : -1;
    return av < bv ? 1 : -1;
  });
  rows.forEach(function(r) { tbody.appendChild(r); });
}
"""

CSV_DOWNLOAD_JS = """
function downloadCSV(rows, filename) {
  var csvContent = rows.map(function(r) {
    return r.map(function(c) {
      var s = String(c);
      return s.indexOf(',') >= 0 || s.indexOf('"') >= 0 ? '"' + s.replace(/"/g, '""') + '"' : s;
    }).join(',');
  }).join('\\n');
  var blob = new Blob([csvContent], {type: 'text/csv;charset=utf-8;'});
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}
"""


def nav_bar(active_file):
    """Generate inter-page navigation bar."""
    pills = []
    for fname, label in PAGES:
        cls = ' active' if fname == active_file else ''
        pills.append(f'<a class="nav-pill{cls}" href="./{fname}">{label}</a>')
    return f'<nav class="nav-bar">{"".join(pills)}</nav>'


def header(title, subtitle="System Readiness Index — Project Kshitij"):
    return f'''<div class="header">
<div><h1>{title}</h1><div class="sub">{subtitle}</div></div>
<div style="text-align:right"><div style="font-size:12px;opacity:.7">Deccan Education Society</div>
<div style="font-size:11px;opacity:.5">Generated: {date.today()}</div></div></div>'''


def footer():
    return f'<div style="text-align:center;padding:20px;color:var(--muted);font-size:11px">Project Kshitij | Myelin | Generated {date.today()}</div>'


def html_doc(title, active_file, tabs_html, content_html, extra_head="", extra_js=""):
    """Build a complete HTML document."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — SRI Dashboard</title>
{CHART_JS_CDN}
<style>{BASE_CSS}</style>
{extra_head}
</head>
<body>
{header(title)}
{nav_bar(active_file)}
{tabs_html}
{content_html}
{footer()}
<script>
{TAB_JS}
{SORT_JS}
{CSV_DOWNLOAD_JS}
{extra_js}
</script>
</body>
</html>"""


def construct_card(cx, score, max_score=None, sub_text=""):
    """Generate a construct summary card."""
    if max_score is None:
        max_score = C_MAX.get(cx, 20)
    color = C_COLORS.get(cx, "#6b7280")
    name = C_NAMES.get(cx, cx)
    pct = (score / max_score * 100) if max_score > 0 else 0
    return f'''<div class="card">
<div class="label">{cx}: {name}</div>
<div class="value" style="color:{color}">{score:.1f}<span style="font-size:14px;color:var(--muted)">/{max_score}</span></div>
<div class="sub">{pct:.0f}% | {sub_text}</div></div>'''


def band_color(band):
    return {
        "operationalised_structure": "#16a34a",
        "partially_institutionalised": "#2563eb",
        "emerging_structure": "#d97706",
        "structural_absence": "#dc2626",
        "high": "#16a34a", "mid": "#d97706", "low": "#dc2626",
        "no_data": "#9ca3af",
    }.get(band, "#9ca3af")


def band_badge(band):
    cls_map = {
        "operationalised_structure": "badge-green",
        "partially_institutionalised": "badge-blue",
        "emerging_structure": "badge-amber",
        "structural_absence": "badge-red",
        "high": "badge-green", "mid": "badge-amber", "low": "badge-red",
        "no_data": "badge-gray",
    }
    label = band.replace("_", " ").title() if band else "No Data"
    return f'<span class="badge {cls_map.get(band, "badge-gray")}">{label}</span>'


def jdumps(obj):
    """Compact JSON dumps for embedding in HTML."""
    return json.dumps(obj, default=str, ensure_ascii=False)
