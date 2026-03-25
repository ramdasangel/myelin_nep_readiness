"""
Build C4 System Readiness detail dashboard.
Output: output/dashboards/sri/04_c4_system.html
"""

import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE)
from scripts.dashboards.sri.html_utils import *

DATA_PATH = os.path.join(BASE, "output", "reports", "sri_unified.json")
OUT_PATH = os.path.join(BASE, "output", "dashboards", "sri", "04_c4_system.html")

TEACHER_AREA_NAMES = {
    "A1": "Continuous Learning Diagnostics",
    "A2": "Teacher Development & Growth",
    "A3": "Holistic Progress Card Enablement",
    "A4": "Parent & Community Support",
}

LEADER_AREA_NAMES = {
    "B1": "NEP Governance & Ownership",
    "B2": "Data-Informed Decision Culture",
    "B3": "Teacher Development Culture",
    "B4": "HPC & Reporting Culture",
}


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def build_overview_tab(branches):
    codes = sorted(branches.keys())
    audit_codes = [c for c in codes if branches[c].get("sri_audit") and branches[c]["sri_audit"].get("system_readiness") is not None]

    c4_scores = [branches[c]["c4_detail"]["C4"] for c in codes if branches[c].get("c4_detail")]
    avg_c4 = sum(c4_scores) / len(c4_scores) if c4_scores else 0

    cards = f'''<div class="cards">
      <div class="card"><div class="label">Avg C4 Score</div><div class="value" style="color:var(--c4)">{avg_c4:.1f}<span style="font-size:14px;color:var(--muted)">/20</span></div><div class="sub">{len(c4_scores)} branches</div></div>
      <div class="card"><div class="label">Branches with Audit</div><div class="value" style="color:var(--c4)">{len(audit_codes)}</div><div class="sub">SRI instrument responses</div></div>
      <div class="card"><div class="label">Avg Enablement</div><div class="value">{sum(branches[c]["c4_detail"]["enablement"] for c in codes if branches[c].get("c4_detail")) / max(len(c4_scores),1):.2f}</div><div class="sub">Index (0-1)</div></div>
      <div class="card"><div class="label">Avg Routine</div><div class="value">{sum(branches[c]["c4_detail"]["routine"] for c in codes if branches[c].get("c4_detail")) / max(len(c4_scores),1):.2f}</div><div class="sub">Index (0-1)</div></div>
    </div>'''

    info = '<div class="info-box">C4 System Readiness measures institutional enablement and leadership routines. Enablement (0-10) + Routine (0-10) = C4 (0-20). Scores combine baseline diagnostic areas with SRI audit data where available.</div>'

    # Stacked bar chart data
    labels = []
    enablement_vals = []
    routine_vals = []
    for c in codes:
        d = branches[c].get("c4_detail")
        if d:
            labels.append(c)
            enablement_vals.append(round(d["enablement"] * 10, 2))
            routine_vals.append(round(d["routine"] * 10, 2))

    chart = f'''<div class="chart-box"><h3>C4 Breakdown: Enablement + Routine per Branch</h3>
    <div style="height:400px"><canvas id="c4StackedBar"></canvas></div></div>'''

    js = f"""
    new Chart(document.getElementById('c4StackedBar'), {{
      type: 'bar',
      data: {{
        labels: {jdumps(labels)},
        datasets: [
          {{label: 'Enablement (0-10)', data: {jdumps(enablement_vals)}, backgroundColor: '#f59e0b'}},
          {{label: 'Routine (0-10)', data: {jdumps(routine_vals)}, backgroundColor: '#d97706'}}
        ]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{legend: {{position:'top'}}}},
        scales: {{x: {{stacked: true}}, y: {{stacked: true, max: 20, title: {{display:true, text:'Score (0-20)'}}}}}}
      }}
    }});
    """

    return cards + info + chart, js


def build_teacher_areas_tab(branches):
    codes = sorted(branches.keys())
    labels = []
    a1, a2, a3, a4 = [], [], [], []
    for c in codes:
        d = branches[c].get("c4_detail")
        if d and d.get("area_means_teacher"):
            labels.append(c)
            am = d["area_means_teacher"]
            a1.append(round(am.get("A1", 0), 2))
            a2.append(round(am.get("A2", 0), 2))
            a3.append(round(am.get("A3", 0), 2))
            a4.append(round(am.get("A4", 0), 2))

    info = '<div class="info-box"><strong>Teacher Areas (A1-A4):</strong><br>'
    for k, v in TEACHER_AREA_NAMES.items():
        info += f"<strong>{k}</strong>: {v}<br>"
    info += 'Scores are means on a 1-4 Likert scale. Bands: Low (&lt;2.5), Mid (2.5-3.2), High (&gt;3.2)</div>'

    chart = '<div class="chart-box"><h3>Teacher Area Means by Branch</h3><div style="height:400px"><canvas id="teacherAreasBar"></canvas></div></div>'

    # Table with band badges
    rows = ""
    for i, c in enumerate(labels):
        d = branches[c]["c4_detail"]
        ab = d.get("area_bands_teacher", {})
        rows += f'<tr><td><strong>{c}</strong></td>'
        for area in ["A1", "A2", "A3", "A4"]:
            val = d["area_means_teacher"].get(area, 0)
            bnd = ab.get(area, "no_data")
            rows += f'<td>{val:.2f} {band_badge(bnd)}</td>'
        rows += '</tr>'

    table = f'''<div class="tbl-wrap"><table id="tblTeacher"><thead><tr>
    <th onclick="sortTable('tblTeacher',0,'str')">Branch</th>
    <th onclick="sortTable('tblTeacher',1,'num')">A1</th>
    <th onclick="sortTable('tblTeacher',2,'num')">A2</th>
    <th onclick="sortTable('tblTeacher',3,'num')">A3</th>
    <th onclick="sortTable('tblTeacher',4,'num')">A4</th>
    </tr></thead><tbody>{rows}</tbody></table></div>'''

    js = f"""
    new Chart(document.getElementById('teacherAreasBar'), {{
      type: 'bar',
      data: {{
        labels: {jdumps(labels)},
        datasets: [
          {{label: 'A1', data: {jdumps(a1)}, backgroundColor: '#3b82f6'}},
          {{label: 'A2', data: {jdumps(a2)}, backgroundColor: '#8b5cf6'}},
          {{label: 'A3', data: {jdumps(a3)}, backgroundColor: '#10b981'}},
          {{label: 'A4', data: {jdumps(a4)}, backgroundColor: '#f59e0b'}}
        ]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{legend: {{position:'top'}}}},
        scales: {{y: {{min: 0, max: 4, title: {{display:true, text:'Mean (1-4)'}}}}}}
      }}
    }});
    """

    return info + chart + table, js


def build_leader_areas_tab(branches):
    codes = sorted(branches.keys())
    labels = []
    b1, b2, b3, b4 = [], [], [], []
    for c in codes:
        d = branches[c].get("c4_detail")
        if d and d.get("area_means_leader"):
            labels.append(c)
            am = d["area_means_leader"]
            b1.append(round(am.get("B1", 0), 2))
            b2.append(round(am.get("B2", 0), 2))
            b3.append(round(am.get("B3", 0), 2))
            b4.append(round(am.get("B4", 0), 2))

    info = '<div class="info-box"><strong>Leader Areas (B1-B4):</strong><br>'
    for k, v in LEADER_AREA_NAMES.items():
        info += f"<strong>{k}</strong>: {v}<br>"
    info += 'Scores are means on a 1-4 Likert scale. Bands: Low (&lt;2.5), Mid (2.5-3.2), High (&gt;3.2). Note: Many branches have limited leader respondents.</div>'

    chart = '<div class="chart-box"><h3>Leader Area Means by Branch</h3><div style="height:400px"><canvas id="leaderAreasBar"></canvas></div></div>'

    rows = ""
    for c in labels:
        d = branches[c]["c4_detail"]
        ab = d.get("area_bands_leader", {})
        rows += f'<tr><td><strong>{c}</strong></td>'
        for area in ["B1", "B2", "B3", "B4"]:
            val = d["area_means_leader"].get(area, 0)
            bnd = ab.get(area, "no_data")
            rows += f'<td>{val:.2f} {band_badge(bnd)}</td>'
        rows += '</tr>'

    table = f'''<div class="tbl-wrap"><table id="tblLeader"><thead><tr>
    <th onclick="sortTable('tblLeader',0,'str')">Branch</th>
    <th onclick="sortTable('tblLeader',1,'num')">B1</th>
    <th onclick="sortTable('tblLeader',2,'num')">B2</th>
    <th onclick="sortTable('tblLeader',3,'num')">B3</th>
    <th onclick="sortTable('tblLeader',4,'num')">B4</th>
    </tr></thead><tbody>{rows}</tbody></table></div>'''

    js = f"""
    new Chart(document.getElementById('leaderAreasBar'), {{
      type: 'bar',
      data: {{
        labels: {jdumps(labels)},
        datasets: [
          {{label: 'B1', data: {jdumps(b1)}, backgroundColor: '#0d9488'}},
          {{label: 'B2', data: {jdumps(b2)}, backgroundColor: '#6366f1'}},
          {{label: 'B3', data: {jdumps(b3)}, backgroundColor: '#ec4899'}},
          {{label: 'B4', data: {jdumps(b4)}, backgroundColor: '#f97316'}}
        ]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{legend: {{position:'top'}}}},
        scales: {{y: {{min: 0, max: 4, title: {{display:true, text:'Mean (1-4)'}}}}}}
      }}
    }});
    """

    return info + chart + table, js


def build_sri_audit_tab(branches):
    audit_codes = sorted(c for c in branches if branches[c].get("sri_audit") and branches[c]["sri_audit"].get("system_readiness") is not None)

    if not audit_codes:
        return '<div class="no-data"><h3>No SRI Audit Data</h3><p>No branches have completed the System Readiness Instrument.</p></div>', ""

    info = '<div class="info-box">The SRI Audit is a binary (Yes/No) instrument completed by school leadership. E1-E5 measure Teacher Enablement; R1-R5 measure Leadership Routines. System Readiness = Enablement(0-10) + Routines(0-10) = 0-20.</div>'

    rows = ""
    for c in audit_codes:
        a = branches[c]["sri_audit"]
        rows += f'<tr><td><strong>{c}</strong></td>'
        for code in ["E1", "E2", "E3", "E4", "E5"]:
            val = a["enablement_items"].get(code, 0)
            cls = "background:#dcfce7;color:#166534" if val == 1 else "background:#fee2e2;color:#991b1b"
            label = "Yes" if val == 1 else "No"
            rows += f'<td style="{cls};text-align:center;font-weight:600">{label}</td>'
        for code in ["R1", "R2", "R3", "R4", "R5"]:
            val = a["routine_items"].get(code, 0)
            cls = "background:#dcfce7;color:#166534" if val == 1 else "background:#fee2e2;color:#991b1b"
            label = "Yes" if val == 1 else "No"
            rows += f'<td style="{cls};text-align:center;font-weight:600">{label}</td>'
        sr = a["system_readiness"]
        bnd = a["band"]
        rows += f'<td style="text-align:center"><strong>{sr:.0f}</strong></td>'
        rows += f'<td>{band_badge(bnd)}</td>'
        rows += f'<td style="text-align:center">{a.get("respondent_count", "?")}</td>'
        rows += '</tr>'

    table = f'''<div class="tbl-wrap"><table id="tblAudit"><thead><tr>
    <th>Branch</th>
    <th>E1</th><th>E2</th><th>E3</th><th>E4</th><th>E5</th>
    <th>R1</th><th>R2</th><th>R3</th><th>R4</th><th>R5</th>
    <th>Score</th><th>Band</th><th>N</th>
    </tr></thead><tbody>{rows}</tbody></table></div>'''

    # E/R item descriptions
    e_labels = {
        "E1": "Scheduled weekly planning period",
        "E2": "Monthly academic review meeting",
        "E3": "Access to performance insights beyond marks",
        "E4": "Protection of instructional time",
        "E5": "Directive encouraging experimentation",
    }
    r_labels = {
        "R1": "Structured observation framework",
        "R2": "Observation calendar with frequency",
        "R3": "Written feedback after observations",
        "R4": "Teacher-level intervention tracking",
        "R5": "Consolidated academic review dashboard",
    }

    legend = '<div class="section-title">Item Descriptions</div><div class="grid-2">'
    legend += '<div class="card"><div class="label">Enablement Items (E1-E5)</div>'
    for k, v in e_labels.items():
        legend += f'<div style="font-size:12px;margin:4px 0"><strong>{k}</strong>: {v}</div>'
    legend += '</div>'
    legend += '<div class="card"><div class="label">Routine Items (R1-R5)</div>'
    for k, v in r_labels.items():
        legend += f'<div style="font-size:12px;margin:4px 0"><strong>{k}</strong>: {v}</div>'
    legend += '</div></div>'

    return info + table + legend, ""


def build_branch_detail_tab(branches):
    codes = sorted(branches.keys())

    csv_rows = [["Branch", "C4", "A1", "A1_Band", "A2", "A2_Band", "A3", "A3_Band", "A4", "A4_Band",
                 "B1", "B1_Band", "B2", "B2_Band", "B3", "B3_Band", "B4", "B4_Band", "Enablement", "Routine"]]

    rows = ""
    for c in codes:
        d = branches[c].get("c4_detail")
        if not d:
            continue
        at = d.get("area_means_teacher", {})
        abt = d.get("area_bands_teacher", {})
        al = d.get("area_means_leader", {})
        abl = d.get("area_bands_leader", {})

        rows += f'<tr><td><strong>{c}</strong></td><td style="font-weight:700;color:var(--c4)">{d["C4"]:.1f}</td>'
        csv_row = [c, f'{d["C4"]:.1f}']
        for area in ["A1", "A2", "A3", "A4"]:
            val = at.get(area, 0)
            bnd = abt.get(area, "no_data")
            rows += f'<td>{val:.2f} {band_badge(bnd)}</td>'
            csv_row.extend([f'{val:.2f}', bnd])
        for area in ["B1", "B2", "B3", "B4"]:
            val = al.get(area, 0)
            bnd = abl.get(area, "no_data")
            rows += f'<td>{val:.2f} {band_badge(bnd)}</td>'
            csv_row.extend([f'{val:.2f}', bnd])
        rows += f'<td>{d["enablement"]:.2f}</td><td>{d["routine"]:.2f}</td></tr>'
        csv_row.extend([f'{d["enablement"]:.2f}', f'{d["routine"]:.2f}'])
        csv_rows.append(csv_row)

    dl_btn = f'<button class="btn btn-blue" onclick="downloadCSV({jdumps(csv_rows)}, \'c4_branch_detail.csv\')" style="margin-bottom:16px">Download CSV</button>'

    table = f'''<div class="tbl-wrap"><table id="tblDetail"><thead><tr>
    <th onclick="sortTable('tblDetail',0,'str')">Branch</th>
    <th onclick="sortTable('tblDetail',1,'num')">C4</th>
    <th onclick="sortTable('tblDetail',2,'num')">A1</th>
    <th onclick="sortTable('tblDetail',3,'num')">A2</th>
    <th onclick="sortTable('tblDetail',4,'num')">A3</th>
    <th onclick="sortTable('tblDetail',5,'num')">A4</th>
    <th onclick="sortTable('tblDetail',6,'num')">B1</th>
    <th onclick="sortTable('tblDetail',7,'num')">B2</th>
    <th onclick="sortTable('tblDetail',8,'num')">B3</th>
    <th onclick="sortTable('tblDetail',9,'num')">B4</th>
    <th onclick="sortTable('tblDetail',10,'num')">Enablement</th>
    <th onclick="sortTable('tblDetail',11,'num')">Routine</th>
    </tr></thead><tbody>{rows}</tbody></table></div>'''

    return dl_btn + table, ""


def build():
    data = load_data()
    branches = data["branches"]

    overview_html, overview_js = build_overview_tab(branches)
    teacher_html, teacher_js = build_teacher_areas_tab(branches)
    leader_html, leader_js = build_leader_areas_tab(branches)
    audit_html, audit_js = build_sri_audit_tab(branches)
    detail_html, detail_js = build_branch_detail_tab(branches)

    tabs_html = '''<div class="tabs">
      <div class="tab active" onclick="showTab('tab-overview')">Overview</div>
      <div class="tab" onclick="showTab('tab-teacher')">Teacher Areas (A1-A4)</div>
      <div class="tab" onclick="showTab('tab-leader')">Leader Areas (B1-B4)</div>
      <div class="tab" onclick="showTab('tab-audit')">SRI Audit</div>
      <div class="tab" onclick="showTab('tab-detail')">Branch Detail</div>
    </div>'''

    content_html = f'''
    <div id="tab-overview" class="content active">{overview_html}</div>
    <div id="tab-teacher" class="content">{teacher_html}</div>
    <div id="tab-leader" class="content">{leader_html}</div>
    <div id="tab-audit" class="content">{audit_html}</div>
    <div id="tab-detail" class="content">{detail_html}</div>
    '''

    extra_js = overview_js + teacher_js + leader_js + audit_js + detail_js

    html = html_doc("C4: System Readiness", "04_c4_system.html", tabs_html, content_html, extra_js=extra_js)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(html)
    print(f"Written: {OUT_PATH}")


if __name__ == "__main__":
    build()
