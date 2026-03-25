"""
Build C5 Ecosystem Readiness placeholder dashboard.
Parent Validation data collection has not yet started.
Output: output/dashboards/sri/05_c5_ecosystem.html
"""

import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE)
from scripts.dashboards.sri.html_utils import *
from src.sri.constants import PARENT_QUESTION_CODES, PARENT_LIKERT_MAP, PARENT_INTERPRETATION_BANDS, PARENT_MIN_RESPONSE_RATE

OUT_PATH = os.path.join(BASE, "output", "dashboards", "sri", "05_c5_ecosystem.html")


def build_status_tab():
    status_box = '''<div style="background:#fef3c7;border:2px solid #f59e0b;border-radius:12px;padding:32px;text-align:center;margin-bottom:24px">
      <div style="font-size:48px;margin-bottom:12px;color:#d97706">&#9888;</div>
      <h2 style="font-size:22px;color:#92400e;margin-bottom:8px">Parent Validation data collection has not yet started.</h2>
      <p style="font-size:14px;color:#92400e">C5 Ecosystem Readiness scores will be calculated once parent survey responses are collected.</p>
    </div>'''

    cards = '''<div class="cards">
      <div class="card"><div class="label">Responses Collected</div><div class="value" style="color:var(--muted)">0</div><div class="sub">No data yet</div></div>
      <div class="card"><div class="label">Branches Covered</div><div class="value" style="color:var(--muted)">0</div><div class="sub">Target: all 37 branches</div></div>
      <div class="card"><div class="label">Survey Instrument</div><div class="value" style="font-size:18px">P1-P5</div><div class="sub">5-item Likert survey</div></div>
      <div class="card"><div class="label">Min Response Rate</div><div class="value" style="font-size:18px">30%</div><div class="sub">Required for valid branch score</div></div>
    </div>'''

    return status_box + cards


def build_methodology_tab():
    # Questions table
    q_rows = ""
    for code, q in PARENT_QUESTION_CODES.items():
        q_rows += f'''<tr>
          <td><strong>{code}</strong></td>
          <td>{q["text_en"]}</td>
          <td style="font-size:11px">{q["text_mr"]}</td>
          <td style="font-size:11px;color:var(--muted)">{q["why"]}</td>
        </tr>'''

    q_table = f'''<div class="section-title">Parent Validation Questions (P1-P5)</div>
    <div class="tbl-wrap"><table><thead><tr>
      <th>Code</th><th>English</th><th>Marathi</th><th>Purpose</th>
    </tr></thead><tbody>{q_rows}</tbody></table></div>'''

    # Scoring
    scoring_items = ""
    labels = {0: "Strongly Disagree", 1: "Disagree", 2: "Neutral", 3: "Agree", 4: "Strongly Agree"}
    for idx, score in PARENT_LIKERT_MAP.items():
        scoring_items += f'<tr><td>{labels.get(idx, idx)}</td><td style="text-align:center">{idx}</td><td style="text-align:center;font-weight:700">{score:.2f}</td></tr>'

    scoring = f'''<div class="section-title">Scoring</div>
    <div class="grid-2">
      <div class="card">
        <div class="label">Likert Response Scoring</div>
        <table><thead><tr><th>Response</th><th>Option Index</th><th>Score</th></tr></thead>
        <tbody>{scoring_items}</tbody></table>
      </div>
      <div class="card">
        <div class="label">Formula</div>
        <div style="font-size:14px;padding:16px;background:#f8f9fb;border-radius:8px;margin-top:8px">
          <p style="margin-bottom:8px"><strong>ParentIndex</strong> = mean(P1, P2, P3, P4, P5)</p>
          <p style="margin-bottom:8px">Each P<sub>i</sub> in [0, 1]</p>
          <p style="font-size:16px;font-weight:700;color:var(--c5)">ParentReadiness (0-7) = 7 &times; ParentIndex</p>
          <p style="margin-top:12px;font-size:12px;color:var(--muted)">C5 weight in SRI: {C_MAX["C5"]} points</p>
        </div>
      </div>
    </div>'''

    # Interpretation bands
    band_rows = ""
    band_display = {
        "weak_parent_alignment": ("0 - 2", "Weak", "badge-red"),
        "partial_visibility": ("2 - 4", "Partial", "badge-amber"),
        "strong_communication_trust": ("4 - 6", "Strong", "badge-blue"),
        "high_ecosystem_validation": ("6 - 7", "High", "badge-green"),
    }
    for bname, (rng, label, cls) in band_display.items():
        band_rows += f'<tr><td>{rng}</td><td><span class="badge {cls}">{label}</span></td><td>{bname.replace("_", " ").title()}</td></tr>'

    bands = f'''<div class="section-title">Interpretation Bands</div>
    <div class="tbl-wrap"><table><thead><tr><th>Score Range</th><th>Band</th><th>Label</th></tr></thead>
    <tbody>{band_rows}</tbody></table></div>'''

    return q_table + scoring + bands


def build_student_signals_tab():
    return '''<div class="card" style="max-width:600px;margin:24px auto;text-align:center;padding:32px">
      <div style="font-size:36px;margin-bottom:12px;color:var(--c5)">&#128218;</div>
      <h3 style="margin-bottom:12px">Student Cognitive Assessment Data</h3>
      <p style="font-size:13px;color:var(--muted);margin-bottom:16px">
        Student cognitive assessment data from MathAngle Sharable exams is available in the MathAngle dashboard.
        This data provides complementary signals about student-level learning outcomes that will feed into the C5 ecosystem validation
        once parent survey data is also collected.
      </p>
      <a href="./07_mathangle_dashboard.html" class="btn btn-blue" style="text-decoration:none">View MathAngle Dashboard</a>
    </div>
    <div class="info-box">
      <strong>Note:</strong> C5 Ecosystem Readiness will combine:
      <ul style="margin-top:8px;padding-left:20px">
        <li><strong>Parent Validation Signal</strong> (P1-P5 Likert survey) &mdash; not yet collected</li>
        <li><strong>Student Cognitive Signal</strong> (MathAngle data) &mdash; available</li>
      </ul>
      Both signals are required for a complete C5 score.
    </div>'''


def build():
    tabs_html = '''<div class="tabs">
      <div class="tab active" onclick="showTab('tab-status')">Status</div>
      <div class="tab" onclick="showTab('tab-methodology')">Methodology</div>
      <div class="tab" onclick="showTab('tab-student')">Student Signals</div>
    </div>'''

    content_html = f'''
    <div id="tab-status" class="content active">{build_status_tab()}</div>
    <div id="tab-methodology" class="content">{build_methodology_tab()}</div>
    <div id="tab-student" class="content">{build_student_signals_tab()}</div>
    '''

    html = html_doc("C5: Ecosystem Readiness", "05_c5_ecosystem.html", tabs_html, content_html)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(html)
    print(f"Written: {OUT_PATH}")


if __name__ == "__main__":
    build()
