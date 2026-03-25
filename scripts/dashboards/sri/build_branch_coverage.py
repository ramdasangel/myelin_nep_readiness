#!/usr/bin/env python3
"""
Build Branch Coverage Dashboard — shows per-branch data availability
across all instruments, stages, and constructs.
"""

import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE)
from scripts.dashboards.sri.html_utils import *

DATA_PATH = os.path.join(BASE, "output", "reports", "sri_unified.json")
OUT_PATH = os.path.join(BASE, "output", "dashboards", "sri", "07_branch_coverage.html")


INTENT_DIR = os.path.join(BASE, "data", "extracted", "intent")
BASELINE_DIR = os.path.join(BASE, "data", "extracted", "baseline")


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def load_role_counts():
    """Load per-branch per-instrument role counts from CSVs."""
    import csv
    from collections import defaultdict

    # {branchCode: {instrument: {role: set of userIds}}}
    role_data = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))

    # Intent surveys
    intent_files = {
        "intent_teacher_english_responses.csv": "Stage-1 Intent (EN)",
        "intent_teacher_marathi_responses.csv": "Stage-1 Intent (MR)",
        "intent_leader_english_responses.csv": "Stage-1 Intent (EN)",
        "intent_leader_marathi_responses.csv": "Stage-1 Intent (MR)",
    }
    for fname, inst in intent_files.items():
        fpath = os.path.join(INTENT_DIR, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath) as f:
            for row in csv.DictReader(f):
                bc = row.get("branchCode", "").strip()
                uid = row.get("userId", "")
                role = row.get("role", "").strip()
                if bc and uid and role and not bc.startswith("m"):
                    role_data[bc][inst][role].add(uid)

    # Baseline surveys
    baseline_files = {
        "base001_teacher_english.csv": "Stage-2 Baseline (EN)",
        "base003_teacher_marathi.csv": "Stage-2 Baseline (MR)",
        "base002_leader_english.csv": "Stage-2 Baseline (EN)",
        "base004_leader_marathi.csv": "Stage-2 Baseline (MR)",
    }
    for fname, inst in baseline_files.items():
        fpath = os.path.join(BASELINE_DIR, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath) as f:
            for row in csv.DictReader(f):
                bc = row.get("branchCode", "").strip()
                uid = row.get("userId", "")
                role = row.get("roleName", "").strip()
                if bc and uid and role and not bc.startswith("m"):
                    role_data[bc][inst][role].add(uid)

    # Convert sets to counts
    result = {}
    for bc in role_data:
        result[bc] = {}
        for inst in role_data[bc]:
            result[bc][inst] = {role: len(uids) for role, uids in role_data[bc][inst].items()}

    return result


def build_html(data):
    branches = data["branches"]
    bcs = sorted(branches.keys())
    role_counts = load_role_counts()

    # ── Compute coverage stats ──
    coverage = {}
    for bc in bcs:
        b = branches[bc]
        c1 = b.get("c1_detail")
        c2 = b.get("c2_detail")
        c3 = b.get("c3_detail")
        c4 = b.get("c4_detail")
        audit = b.get("sri_audit")
        sset = b.get("set")

        t_count = c1["teacher_count"] if c1 else 0
        l_count = c1["leader_count"] if c1 else 0
        c3_resp = c3["respondents"] if c3 else 0
        audit_resp = audit["respondent_count"] if audit else 0

        # Area data presence (from c4_detail)
        a_areas = 0
        b_areas = 0
        if c4:
            for a in ["A1", "A2", "A3", "A4"]:
                if c4.get("area_means_teacher", {}).get(a, 0) > 0:
                    a_areas += 1
            for b_code in ["B1", "B2", "B3", "B4"]:
                if c4.get("area_means_leader", {}).get(b_code, 0) > 0:
                    b_areas += 1

        constructs_with_data = sum([
            1 if c1 else 0,
            1 if c2 else 0,
            1 if c3 else 0,
            1 if c4 and float(b["summary"].get("C4", 0)) > 0 else 0,
            0,  # C5 never
        ])

        coverage[bc] = {
            "branchName": b.get("branchName", ""),
            "schoolName": b.get("schoolName", ""),
            "teacher_count": t_count,
            "leader_count": l_count,
            "total_respondents": t_count + l_count + c3_resp + audit_resp,
            "c1_has": bool(c1),
            "c2_has": bool(c2),
            "c3_has": bool(c3),
            "c3_resp": c3_resp,
            "c4_has": bool(c4 and float(b["summary"].get("C4", 0)) > 0),
            "c5_has": False,
            "audit_has": bool(audit),
            "audit_resp": audit_resp,
            "set_has": bool(sset),
            "a_areas": a_areas,
            "b_areas": b_areas,
            "constructs_covered": constructs_with_data,
            "sri_total": b["summary"]["SRI_Total"],
            "sri_pct": b["summary"]["SRI_Pct"],
        }

    # ── Summary stats ──
    total = len(bcs)
    c1_count = sum(1 for v in coverage.values() if v["c1_has"])
    c2_count = sum(1 for v in coverage.values() if v["c2_has"])
    c3_count = sum(1 for v in coverage.values() if v["c3_has"])
    c4_count = sum(1 for v in coverage.values() if v["c4_has"])
    audit_count = sum(1 for v in coverage.values() if v["audit_has"])
    total_teachers = sum(v["teacher_count"] for v in coverage.values())
    total_leaders = sum(v["leader_count"] for v in coverage.values())
    total_c3 = sum(v["c3_resp"] for v in coverage.values())
    full_coverage = sum(1 for v in coverage.values() if v["constructs_covered"] >= 4)

    # ── JSON for charts ──
    chart_labels = jdumps(bcs)
    chart_c1 = jdumps([1 if coverage[bc]["c1_has"] else 0 for bc in bcs])
    chart_c2 = jdumps([1 if coverage[bc]["c2_has"] else 0 for bc in bcs])
    chart_c3 = jdumps([1 if coverage[bc]["c3_has"] else 0 for bc in bcs])
    chart_c4 = jdumps([1 if coverage[bc]["c4_has"] else 0 for bc in bcs])
    chart_audit = jdumps([1 if coverage[bc]["audit_has"] else 0 for bc in bcs])

    respondent_teachers = jdumps([coverage[bc]["teacher_count"] for bc in bcs])
    respondent_leaders = jdumps([coverage[bc]["leader_count"] for bc in bcs])
    respondent_c3 = jdumps([coverage[bc]["c3_resp"] for bc in bcs])

    # ── Coverage matrix rows ──
    def cell(has, count=None):
        if has:
            badge = '<span style="color:#16a34a;font-weight:700">&#10003;</span>'
            if count and count > 0:
                badge += f' <span style="font-size:10px;color:var(--muted)">{count}</span>'
            return f'<td style="text-align:center;background:#f0fdf4">{badge}</td>'
        return '<td style="text-align:center;color:#d1d5db">—</td>'

    matrix_rows = ""
    for bc in bcs:
        c = coverage[bc]
        pct_color = "#16a34a" if c["constructs_covered"] >= 4 else ("#d97706" if c["constructs_covered"] >= 3 else "#dc2626")
        matrix_rows += f"""<tr>
<td><strong>{bc}</strong></td>
<td style="font-size:11px">{c['branchName'][:35]}</td>
{cell(c['c1_has'], c['teacher_count'])}
{cell(c['c2_has'], c['teacher_count'])}
{cell(c['c3_has'], c['c3_resp'])}
{cell(c['c4_has'], c['teacher_count'] + c['leader_count'])}
{cell(c['c5_has'])}
{cell(c['audit_has'], c['audit_resp'])}
{cell(c['set_has'])}
<td style="text-align:center"><strong>{c['a_areas']}</strong>/4</td>
<td style="text-align:center"><strong>{c['b_areas']}</strong>/4</td>
<td style="text-align:center;font-weight:700;color:{pct_color}">{c['constructs_covered']}/5</td>
<td style="text-align:right;font-weight:600">{c['sri_total']:.1f}</td>
</tr>"""

    # ── Respondent detail table ──
    resp_rows = ""
    for bc in sorted(bcs, key=lambda x: -coverage[x]["total_respondents"]):
        c = coverage[bc]
        resp_rows += f"""<tr>
<td><strong>{bc}</strong></td>
<td style="font-size:11px">{c['branchName'][:40]}</td>
<td style="text-align:right">{c['teacher_count']}</td>
<td style="text-align:right">{c['leader_count']}</td>
<td style="text-align:right">{c['c3_resp']}</td>
<td style="text-align:right">{c['audit_resp']}</td>
<td style="text-align:right;font-weight:700">{c['total_respondents']}</td>
</tr>"""

    # ── Gaps analysis ──
    no_c3 = [bc for bc in bcs if not coverage[bc]["c3_has"]]
    no_audit = [bc for bc in bcs if not coverage[bc]["audit_has"]]
    low_leaders = [(bc, coverage[bc]["leader_count"]) for bc in bcs if coverage[bc]["leader_count"] < 2]

    gap_cards = ""
    gap_cards += f"""<div class="card" style="border-left:4px solid var(--red)">
<div class="label">Missing C3 (MathAngle)</div>
<div class="value" style="color:var(--red)">{len(no_c3)}</div>
<div class="sub">branches without cognitive capacity data</div>
<div style="margin-top:8px;font-size:10px;color:var(--muted)">{', '.join(no_c3[:15])}{'...' if len(no_c3) > 15 else ''}</div></div>"""

    gap_cards += f"""<div class="card" style="border-left:4px solid var(--amber)">
<div class="label">Missing SRI Audit</div>
<div class="value" style="color:var(--amber)">{len(no_audit)}</div>
<div class="sub">branches without system readiness audit (E1-R5)</div>
<div style="margin-top:8px;font-size:10px;color:var(--muted)">{', '.join(no_audit[:15])}{'...' if len(no_audit) > 15 else ''}</div></div>"""

    gap_cards += f"""<div class="card" style="border-left:4px solid var(--purple)">
<div class="label">Low Leader Coverage (&lt;2)</div>
<div class="value" style="color:var(--purple)">{len(low_leaders)}</div>
<div class="sub">branches with fewer than 2 leader responses</div>
<div style="margin-top:8px;font-size:10px;color:var(--muted)">{', '.join(f'{bc}({n})' for bc, n in low_leaders[:10])}</div></div>"""

    gap_cards += f"""<div class="card" style="border-left:4px solid var(--green)">
<div class="label">Full Coverage (4/5 constructs)</div>
<div class="value" style="color:var(--green)">{full_coverage}</div>
<div class="sub">of {total} branches have all available constructs</div></div>"""

    # ── Role coverage table ──
    # Per-branch: Teacher/Leader/Principal counts per instrument
    instruments = ["Stage-1 Intent (EN)", "Stage-1 Intent (MR)", "Stage-2 Baseline (EN)", "Stage-2 Baseline (MR)"]
    role_rows = ""
    total_by_role = {"Teacher": 0, "Leader": 0}
    total_by_inst = {inst: {"Teacher": 0, "Leader": 0} for inst in instruments}

    for bc in bcs:
        rc = role_counts.get(bc, {})
        cells = f"<td><strong>{bc}</strong></td><td style='font-size:11px'>{coverage[bc]['branchName'][:30]}</td>"

        bc_teachers = 0
        bc_leaders = 0

        for inst in instruments:
            inst_roles = rc.get(inst, {})
            t = inst_roles.get("Teacher", 0)
            l = inst_roles.get("Leader", 0)
            bc_teachers += t
            bc_leaders += l
            total_by_inst[inst]["Teacher"] += t
            total_by_inst[inst]["Leader"] += l

            t_cell = f'<span style="color:var(--blue);font-weight:600">{t}</span>' if t > 0 else '<span style="color:#d1d5db">0</span>'
            l_cell = f'<span style="color:var(--purple);font-weight:600">{l}</span>' if l > 0 else '<span style="color:#d1d5db">0</span>'
            cells += f'<td style="text-align:center">{t_cell} / {l_cell}</td>'

        # SRI Audit (leaders only)
        audit_n = coverage[bc]["audit_resp"]
        audit_cell = f'<span style="color:var(--teal);font-weight:600">{audit_n}</span>' if audit_n > 0 else '<span style="color:#d1d5db">0</span>'
        cells += f'<td style="text-align:center">{audit_cell}</td>'

        # Totals
        total_by_role["Teacher"] += bc_teachers
        total_by_role["Leader"] += bc_leaders

        total_n = bc_teachers + bc_leaders + audit_n
        cells += f'<td style="text-align:right;font-weight:700">{total_n}</td>'

        role_rows += f"<tr>{cells}</tr>"

    # Role summary chart data
    role_chart_teachers = jdumps([sum(role_counts.get(bc, {}).get(inst, {}).get("Teacher", 0) for inst in instruments) for bc in bcs])
    role_chart_leaders = jdumps([sum(role_counts.get(bc, {}).get(inst, {}).get("Leader", 0) for inst in instruments) for bc in bcs])
    role_chart_audit = jdumps([coverage[bc]["audit_resp"] for bc in bcs])

    # ── Build HTML ──
    tabs_html = """<div class="tabs">
<div class="tab active" onclick="showTab('overview')">Overview</div>
<div class="tab" onclick="showTab('roles')">Role Coverage</div>
<div class="tab" onclick="showTab('matrix')">Coverage Matrix</div>
<div class="tab" onclick="showTab('respondents')">Respondent Counts</div>
<div class="tab" onclick="showTab('gaps')">Gap Analysis</div>
</div>"""

    content_html = f"""
<!-- OVERVIEW -->
<div id="overview" class="content active">
<div class="cards">
{construct_card('C1', c1_count, total, f'{c1_count}/{total} branches | {total_teachers} teachers + {total_leaders} leaders')}
{construct_card('C2', c2_count, total, f'{c2_count}/{total} branches | from teacher intent data')}
{construct_card('C3', c3_count, total, f'{c3_count}/{total} branches | {total_c3} MathAngle users')}
{construct_card('C4', c4_count, total, f'{c4_count}/{total} branches | baseline surveys')}
{construct_card('C5', 0, total, '0/{0} branches | data not yet collected'.format(total))}
<div class="card">
<div class="label">SRI Audit (SRI001)</div>
<div class="value" style="color:var(--teal)">{audit_count}<span style="font-size:14px;color:var(--muted)">/{total}</span></div>
<div class="sub">{audit_count} branches with E1-R5 audit data</div></div>
</div>

<div class="info-box">
<strong>Branch Coverage Dashboard</strong> — Shows which branches have data for each SRI construct and instrument.
C5 (Ecosystem Readiness) has no data yet. Max achievable SRI = 85/100 without C5.
</div>

<div class="grid-2">
<div class="chart-box"><h3>Construct Coverage by Branch</h3><canvas id="coverageChart" height="400"></canvas></div>
<div class="chart-box"><h3>Respondent Distribution</h3><canvas id="respondentChart" height="400"></canvas></div>
</div>
</div>

<!-- ROLES -->
<div id="roles" class="content">
<h2 class="section-title">Role Coverage: Teacher / Leader / Principal</h2>
<div class="info-box">
Shows unique respondent counts per branch by role across each instrument stage.
<strong>T</strong> = Teacher, <strong>L</strong> = Leader/Principal.
SRI Audit is completed by Principals/VPs/Academic Coordinators (counted as Leaders).
</div>

<div class="cards" style="grid-template-columns:repeat(3,1fr)">
<div class="card" style="border-left:4px solid var(--blue)">
<div class="label">Total Teachers</div>
<div class="value" style="color:var(--blue)">{total_by_role['Teacher']}</div>
<div class="sub">unique teacher submissions across all instruments</div></div>
<div class="card" style="border-left:4px solid var(--purple)">
<div class="label">Total Leaders</div>
<div class="value" style="color:var(--purple)">{total_by_role['Leader']}</div>
<div class="sub">unique leader submissions across all instruments</div></div>
<div class="card" style="border-left:4px solid var(--teal)">
<div class="label">SRI Audit (Principal/VP/AC)</div>
<div class="value" style="color:var(--teal)">{sum(coverage[bc]['audit_resp'] for bc in bcs)}</div>
<div class="sub">system readiness audit respondents</div></div>
</div>

<div class="chart-box"><h3>Teacher vs Leader vs Audit by Branch</h3><canvas id="roleChart" height="400"></canvas></div>

<div class="tbl-wrap"><table>
<thead><tr>
<th>Branch</th><th>Name</th>
<th style="text-align:center">Intent EN<br><span style="font-size:9px;color:var(--muted)">T / L</span></th>
<th style="text-align:center">Intent MR<br><span style="font-size:9px;color:var(--muted)">T / L</span></th>
<th style="text-align:center">Baseline EN<br><span style="font-size:9px;color:var(--muted)">T / L</span></th>
<th style="text-align:center">Baseline MR<br><span style="font-size:9px;color:var(--muted)">T / L</span></th>
<th style="text-align:center">SRI Audit<br><span style="font-size:9px;color:var(--muted)">L</span></th>
<th style="text-align:right">Total</th>
</tr></thead>
<tbody>{role_rows}</tbody>
</table></div>
</div>

<!-- MATRIX -->
<div id="matrix" class="content">
<h2 class="section-title">Coverage Matrix</h2>
<div class="info-box">Green checkmark = data available (number = respondent count). Gray dash = no data. Constructs/5 shows how many of the 5 SRI constructs have data for each branch.</div>
<button class="btn btn-blue" onclick="downloadCoverageCSV()" style="margin-bottom:12px">Download CSV</button>
<div class="tbl-wrap"><table id="coverageTable">
<thead><tr>
<th onclick="sortTable('coverageTable',0,'str')">Branch</th>
<th>Name</th>
<th style="text-align:center" onclick="sortTable('coverageTable',2,'str')">C1</th>
<th style="text-align:center" onclick="sortTable('coverageTable',3,'str')">C2</th>
<th style="text-align:center" onclick="sortTable('coverageTable',4,'str')">C3</th>
<th style="text-align:center" onclick="sortTable('coverageTable',5,'str')">C4</th>
<th style="text-align:center">C5</th>
<th style="text-align:center" onclick="sortTable('coverageTable',7,'str')">Audit</th>
<th style="text-align:center">SET</th>
<th style="text-align:center">A areas</th>
<th style="text-align:center">B areas</th>
<th style="text-align:center" onclick="sortTable('coverageTable',11,'num')">Score</th>
<th style="text-align:right" onclick="sortTable('coverageTable',12,'num')">SRI</th>
</tr></thead>
<tbody>{matrix_rows}</tbody>
</table></div>
</div>

<!-- RESPONDENTS -->
<div id="respondents" class="content">
<h2 class="section-title">Respondent Counts by Branch</h2>
<div class="cards" style="grid-template-columns:repeat(4,1fr)">
<div class="card"><div class="label">Total Teachers</div><div class="value" style="color:var(--blue)">{total_teachers}</div></div>
<div class="card"><div class="label">Total Leaders</div><div class="value" style="color:var(--purple)">{total_leaders}</div></div>
<div class="card"><div class="label">MathAngle Users</div><div class="value" style="color:var(--green)">{total_c3}</div></div>
<div class="card"><div class="label">SRI Audit Respondents</div><div class="value" style="color:var(--teal)">{sum(coverage[bc]['audit_resp'] for bc in bcs)}</div></div>
</div>
<div class="tbl-wrap"><table>
<thead><tr>
<th>Branch</th><th>Name</th><th style="text-align:right">Teachers</th><th style="text-align:right">Leaders</th><th style="text-align:right">MathAngle</th><th style="text-align:right">Audit</th><th style="text-align:right">Total</th>
</tr></thead>
<tbody>{resp_rows}</tbody>
</table></div>
</div>

<!-- GAPS -->
<div id="gaps" class="content">
<h2 class="section-title">Gap Analysis</h2>
<div class="info-box">Identifies branches with missing data, low coverage, or incomplete instrument collection. Prioritise these for follow-up data collection.</div>
<div class="cards">{gap_cards}</div>

<div class="chart-box"><h3>Constructs Covered per Branch</h3><canvas id="gapChart" height="250"></canvas></div>
</div>
"""

    constructs_covered = jdumps([coverage[bc]["constructs_covered"] for bc in bcs])

    extra_js = f"""
// Role chart
new Chart(document.getElementById('roleChart'), {{
  type: 'bar',
  data: {{
    labels: {chart_labels},
    datasets: [
      {{label: 'Teachers', data: {role_chart_teachers}, backgroundColor: '#3b82f6'}},
      {{label: 'Leaders', data: {role_chart_leaders}, backgroundColor: '#8b5cf6'}},
      {{label: 'SRI Audit (Principal/VP)', data: {role_chart_audit}, backgroundColor: '#0d9488'}}
    ]
  }},
  options: {{
    indexAxis: 'y',
    scales: {{x: {{stacked: true}}, y: {{stacked: true}}}},
    plugins: {{legend: {{position: 'top'}}}}
  }}
}});

// Coverage stacked bar
new Chart(document.getElementById('coverageChart'), {{
  type: 'bar',
  data: {{
    labels: {chart_labels},
    datasets: [
      {{label: 'C1 Intent', data: {chart_c1}, backgroundColor: '#3b82f6'}},
      {{label: 'C2 Practice', data: {chart_c2}, backgroundColor: '#8b5cf6'}},
      {{label: 'C3 Capacity', data: {chart_c3}, backgroundColor: '#10b981'}},
      {{label: 'C4 System', data: {chart_c4}, backgroundColor: '#f59e0b'}},
      {{label: 'SRI Audit', data: {chart_audit}, backgroundColor: '#0d9488'}}
    ]
  }},
  options: {{
    indexAxis: 'y',
    scales: {{x: {{stacked: true, max: 5}}, y: {{stacked: true}}}},
    plugins: {{legend: {{position: 'top'}}}}
  }}
}});

// Respondent distribution
new Chart(document.getElementById('respondentChart'), {{
  type: 'bar',
  data: {{
    labels: {chart_labels},
    datasets: [
      {{label: 'Teachers', data: {respondent_teachers}, backgroundColor: '#3b82f6'}},
      {{label: 'Leaders', data: {respondent_leaders}, backgroundColor: '#8b5cf6'}},
      {{label: 'MathAngle', data: {respondent_c3}, backgroundColor: '#10b981'}}
    ]
  }},
  options: {{
    indexAxis: 'y',
    scales: {{x: {{stacked: true}}, y: {{stacked: true}}}},
    plugins: {{legend: {{position: 'top'}}}}
  }}
}});

// Gap chart — constructs per branch
new Chart(document.getElementById('gapChart'), {{
  type: 'bar',
  data: {{
    labels: {chart_labels},
    datasets: [{{
      label: 'Constructs with data',
      data: {constructs_covered},
      backgroundColor: {jdumps([('#16a34a' if coverage[bc]['constructs_covered'] >= 4 else '#d97706' if coverage[bc]['constructs_covered'] >= 3 else '#dc2626') for bc in bcs])}
    }}]
  }},
  options: {{
    scales: {{y: {{max: 5, ticks: {{stepSize: 1}}}}}},
    plugins: {{legend: {{display: false}}}}
  }}
}});

// CSV download
function downloadCoverageCSV() {{
  var rows = [['BranchCode','BranchName','SchoolName','Teachers','Leaders','C1','C2','C3','C3_Respondents','C4','C5','SRI_Audit','SRI_Audit_Respondents','SET','A_Areas','B_Areas','Constructs_Covered','SRI_Total']];
  var cov = {jdumps({bc: coverage[bc] for bc in bcs})};
  Object.keys(cov).sort().forEach(function(bc) {{
    var c = cov[bc];
    rows.push([bc, c.branchName, c.schoolName, c.teacher_count, c.leader_count,
      c.c1_has?'Y':'N', c.c2_has?'Y':'N', c.c3_has?'Y':'N', c.c3_resp,
      c.c4_has?'Y':'N', c.c5_has?'Y':'N', c.audit_has?'Y':'N', c.audit_resp,
      c.set_has?'Y':'N', c.a_areas, c.b_areas, c.constructs_covered, c.sri_total]);
  }});
  downloadCSV(rows, 'sri_branch_coverage.csv');
}}
"""

    return html_doc(
        "Branch Coverage",
        "07_branch_coverage.html",
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
    size = os.path.getsize(OUT_PATH)
    print(f"Written: {OUT_PATH} ({size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
