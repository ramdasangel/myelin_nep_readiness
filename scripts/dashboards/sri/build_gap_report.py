#!/usr/bin/env python3
"""
Build Instrument Gap Report — branches with no representation per instrument.
EN + MR are treated as one instrument per purpose.
Also shows per-language breakdown and role-level detail.
"""

import csv
import json
import os
import sys
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE)
from scripts.dashboards.sri.html_utils import *

UNIFIED_PATH = os.path.join(BASE, "output", "reports", "sri_unified.json")
INTENT_DIR = os.path.join(BASE, "data", "extracted", "intent")
BASELINE_DIR = os.path.join(BASE, "data", "extracted", "baseline")
OUT_PATH = os.path.join(BASE, "output", "reports", "instrument_gap_report.html")

# Combined instruments (EN + MR = same purpose)
COMBINED_INSTRUMENTS = [
    ("Intent Teacher", ["1234", "103"], "Teacher"),
    ("Intent Leader", ["7890", "104"], "Leader"),
    ("Baseline Teacher", ["base001", "base003"], "Teacher"),
    ("Baseline Leader", ["base002", "base004"], "Leader"),
    ("SRI Audit", ["SRI001"], "Leader/Principal"),
]

# Per-language instruments (for detail breakdown)
LANG_INSTRUMENTS = [
    ("Intent Teacher EN", "1234", "Teacher", "English"),
    ("Intent Teacher MR", "103", "Teacher", "Marathi"),
    ("Intent Leader EN", "7890", "Leader", "English"),
    ("Intent Leader MR", "104", "Leader", "Marathi"),
    ("Baseline Teacher EN", "base001", "Teacher", "English"),
    ("Baseline Teacher MR", "base003", "Teacher", "Marathi"),
    ("Baseline Leader EN", "base002", "Leader", "English"),
    ("Baseline Leader MR", "base004", "Leader", "Marathi"),
    ("SRI Audit", "SRI001", "Leader/Principal", "Bilingual"),
]

CSV_FILE_MAP = {
    "1234": ("intent_teacher_english_responses.csv", INTENT_DIR),
    "103": ("intent_teacher_marathi_responses.csv", INTENT_DIR),
    "7890": ("intent_leader_english_responses.csv", INTENT_DIR),
    "104": ("intent_leader_marathi_responses.csv", INTENT_DIR),
    "base001": ("base001_teacher_english.csv", BASELINE_DIR),
    "base003": ("base003_teacher_marathi.csv", BASELINE_DIR),
    "base002": ("base002_leader_english.csv", BASELINE_DIR),
    "base004": ("base004_leader_marathi.csv", BASELINE_DIR),
}


def load_per_language_counts():
    """Load unique user counts per branch × setCode from CSVs."""
    # {(branchCode, setCode) → set of userIds}
    counts = defaultdict(set)
    for scode, (fname, base_dir) in CSV_FILE_MAP.items():
        fpath = os.path.join(base_dir, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath) as f:
            for row in csv.DictReader(f):
                bc = row.get("branchCode", "").strip()
                uid = row.get("userId", "")
                if bc and uid and not bc.startswith("m"):
                    counts[(bc, scode)].add(uid)
    return {k: len(v) for k, v in counts.items()}


def load_role_counts():
    """Load per branch × setCode role breakdown."""
    # {(branchCode, setCode) → {role → count}}
    roles = defaultdict(lambda: defaultdict(set))
    for scode, (fname, base_dir) in CSV_FILE_MAP.items():
        fpath = os.path.join(base_dir, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath) as f:
            for row in csv.DictReader(f):
                bc = row.get("branchCode", "").strip()
                uid = row.get("userId", "")
                role = row.get("role", row.get("roleName", "")).strip()
                if bc and uid and role and not bc.startswith("m"):
                    roles[(bc, scode)][role].add(uid)
    return {k: {r: len(uids) for r, uids in v.items()} for k, v in roles.items()}


def main():
    with open(UNIFIED_PATH) as f:
        unified = json.load(f)

    branches = unified["branches"]
    all_bcs = sorted(branches.keys())
    lang_counts = load_per_language_counts()
    role_data = load_role_counts()

    # Load SRI audit counts from unified JSON
    for bc in all_bcs:
        audit = branches[bc].get("sri_audit")
        if audit and audit.get("respondent_count", 0) > 0:
            lang_counts[(bc, "SRI001")] = audit["respondent_count"]

    # ── Combined instrument analysis ──
    combined_gaps = {}  # instrument → [missing branches]
    branch_gap_count = {bc: 0 for bc in all_bcs}

    for inst_name, scodes, role in COMBINED_INSTRUMENTS:
        missing = []
        for bc in all_bcs:
            has_any = any(lang_counts.get((bc, sc), 0) > 0 for sc in scodes)
            if not has_any:
                missing.append(bc)
                branch_gap_count[bc] += 1
        combined_gaps[inst_name] = missing

    total_instruments = len(COMBINED_INSTRUMENTS)
    total_combos = len(all_bcs) * total_instruments
    total_gaps = sum(len(v) for v in combined_gaps.values())
    coverage_pct = round((1 - total_gaps / total_combos) * 100, 1)
    full_branches = [bc for bc in all_bcs if branch_gap_count[bc] == 0]

    # ── Per-language detail for each branch ──
    # Build heatmap data: branch × (combined instrument + language breakdown)
    gap_set = set()
    for inst_name, missing in combined_gaps.items():
        for bc in missing:
            gap_set.add((bc, inst_name))

    # ── Heatmap rows (combined) ──
    heatmap_rows = ""
    for bc in all_bcs:
        b = branches.get(bc, {})
        bname = b.get("branchName", "")[:35]
        gc = branch_gap_count[bc]
        row_bg = "#fef2f2" if gc >= 3 else ("#fefce8" if gc >= 2 else "#f0fdf4" if gc == 0 else "#fff")

        cells = f'<td><strong>{bc}</strong></td><td style="font-size:11px">{bname}</td>'
        for inst_name, scodes, role in COMBINED_INSTRUMENTS:
            if (bc, inst_name) in gap_set:
                cells += '<td style="text-align:center;background:#fee2e2;color:#991b1b;font-weight:700">MISSING</td>'
            else:
                # Show count
                n = sum(lang_counts.get((bc, sc), 0) for sc in scodes)
                cells += f'<td style="text-align:center;background:#dcfce7;color:#166534">{n}</td>'
        gc_color = "#dc2626" if gc >= 3 else ("#d97706" if gc >= 1 else "#16a34a")
        cells += f'<td style="text-align:center;font-weight:700;color:{gc_color}">{gc}/{total_instruments}</td>'
        heatmap_rows += f'<tr style="background:{row_bg}">{cells}</tr>'

    # ── Language breakdown table ──
    lang_rows = ""
    for bc in all_bcs:
        b = branches.get(bc, {})
        bname = b.get("branchName", "")[:30]
        cells = f'<td><strong>{bc}</strong></td><td style="font-size:10px">{bname}</td>'
        for inst_name, scode, role, lang in LANG_INSTRUMENTS:
            n = lang_counts.get((bc, scode), 0)
            if n > 0:
                roles = role_data.get((bc, scode), {})
                t = roles.get("Teacher", 0)
                l = roles.get("Leader", 0)
                role_txt = ""
                if t > 0 and l > 0:
                    role_txt = f'<span style="color:var(--blue)">{t}T</span>+<span style="color:var(--purple)">{l}L</span>'
                elif t > 0:
                    role_txt = f'<span style="color:var(--blue)">{t}T</span>'
                elif l > 0:
                    role_txt = f'<span style="color:var(--purple)">{l}L</span>'
                else:
                    role_txt = str(n)
                cells += f'<td style="text-align:center;background:#f0fdf4;font-size:10px">{role_txt}</td>'
            else:
                cells += '<td style="text-align:center;color:#d1d5db;font-size:10px">—</td>'
        lang_rows += f'<tr>{cells}</tr>'

    # ── Per-instrument cards ──
    inst_cards = ""
    for inst_name, scodes, role in COMBINED_INSTRUMENTS:
        missing = combined_gaps[inst_name]
        n = len(missing)
        pct = n / len(all_bcs) * 100
        color = "#dc2626" if pct > 50 else ("#d97706" if pct > 20 else "#16a34a")
        badge_cls = "badge-red" if pct > 50 else ("badge-amber" if pct > 20 else "badge-green")

        # Language breakdown for covered branches
        covered = [bc for bc in all_bcs if bc not in missing]
        en_only = sum(1 for bc in covered if lang_counts.get((bc, scodes[0]), 0) > 0 and (len(scodes) < 2 or lang_counts.get((bc, scodes[-1]), 0) == 0))
        mr_only = sum(1 for bc in covered if len(scodes) > 1 and lang_counts.get((bc, scodes[-1]), 0) > 0 and lang_counts.get((bc, scodes[0]), 0) == 0)
        both = sum(1 for bc in covered if lang_counts.get((bc, scodes[0]), 0) > 0 and (len(scodes) < 2 or lang_counts.get((bc, scodes[-1]), 0) > 0))

        lang_detail = ""
        if len(scodes) > 1:
            lang_detail = f'<div style="font-size:10px;color:var(--muted);margin-top:4px">EN only: {en_only} | MR only: {mr_only} | Both: {both}</div>'

        missing_list = ", ".join(f'<strong>{bc}</strong>' for bc in sorted(missing)) if missing else '<span style="color:var(--green)">All branches covered</span>'

        # Total respondents for this instrument
        total_resp = sum(lang_counts.get((bc, sc), 0) for bc in all_bcs for sc in scodes)

        inst_cards += f'''<div class="card" style="border-left:4px solid {color}">
<div class="label">{inst_name} <span style="font-size:9px;color:var(--muted)">({" / ".join(scodes)} | {role})</span></div>
<div style="margin:6px 0"><span class="badge {badge_cls}">{n}/{len(all_bcs)} missing ({pct:.0f}%)</span> <span style="font-size:10px;color:var(--muted)">{total_resp} total respondents</span></div>
{lang_detail}
<div style="font-size:11px;color:var(--muted);line-height:1.6;margin-top:4px">{missing_list}</div>
</div>'''

    # ── Priority action table ──
    priority_rows = ""
    for bc in sorted(all_bcs, key=lambda x: -branch_gap_count[x]):
        gc = branch_gap_count[bc]
        if gc == 0:
            continue
        b = branches.get(bc, {})
        bname = b.get("branchName", "")[:40]
        missing_insts = [inst for inst, scodes, _ in COMBINED_INSTRUMENTS if bc in combined_gaps[inst]]
        missing_teacher = [i for i in missing_insts if "Teacher" in i]
        missing_leader = [i for i in missing_insts if "Leader" in i or "Audit" in i]

        t_badge = f'<span class="badge badge-blue">{len(missing_teacher)} teacher</span> ' if missing_teacher else ''
        l_badge = f'<span class="badge badge-purple">{len(missing_leader)} leader</span>' if missing_leader else ''

        sri = b.get("summary", {}).get("SRI_Total", 0)
        gc_color = "#dc2626" if gc >= 3 else "#d97706"
        priority_rows += f'''<tr>
<td><strong>{bc}</strong></td><td style="font-size:11px">{bname}</td>
<td style="text-align:center;font-weight:700;color:{gc_color}">{gc}/{total_instruments}</td>
<td>{t_badge}{l_badge}</td>
<td style="font-size:10px;color:var(--muted)">{", ".join(missing_insts)}</td>
<td style="text-align:right">{sri:.1f}</td></tr>'''

    # ── Role summary stats ──
    total_teachers = 0
    total_leaders = 0
    for bc in all_bcs:
        for scode in ["1234", "103", "base001", "base003"]:
            roles = role_data.get((bc, scode), {})
            total_teachers += roles.get("Teacher", 0)
        for scode in ["7890", "104", "base002", "base004", "SRI001"]:
            roles = role_data.get((bc, scode), {})
            total_leaders += roles.get("Leader", 0)

    # ── Chart data ──
    chart_bcs = jdumps(all_bcs)
    chart_gap_counts = jdumps([branch_gap_count[bc] for bc in all_bcs])
    chart_gap_colors = jdumps(["#dc2626" if branch_gap_count[bc] >= 3 else "#d97706" if branch_gap_count[bc] >= 1 else "#16a34a" for bc in all_bcs])
    chart_inst_names = jdumps([i[0] for i in COMBINED_INSTRUMENTS])
    chart_inst_covered = jdumps([len(all_bcs) - len(combined_gaps[i[0]]) for i in COMBINED_INSTRUMENTS])
    chart_inst_missing = jdumps([len(combined_gaps[i[0]]) for i in COMBINED_INSTRUMENTS])

    # Teacher vs Leader gap comparison
    teacher_insts = [i[0] for i in COMBINED_INSTRUMENTS if "Teacher" in i[0]]
    leader_insts = [i[0] for i in COMBINED_INSTRUMENTS if "Leader" in i[0] or "Audit" in i[0]]
    teacher_gap_pct = round(sum(len(combined_gaps[i]) for i in teacher_insts) / (len(all_bcs) * len(teacher_insts)) * 100, 1)
    leader_gap_pct = round(sum(len(combined_gaps[i]) for i in leader_insts) / (len(all_bcs) * len(leader_insts)) * 100, 1)

    # ── Build HTML ──
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Instrument Coverage Gap Report — SRI</title>
{CHART_JS_CDN}
<style>{BASE_CSS}
.lang-header {{font-size:9px;writing-mode:vertical-lr;height:90px;text-align:center}}
</style>
</head>
<body>
{header("Instrument Coverage Gap Report", "Branches with No Representation — EN + MR Combined")}

<div style="padding:24px 32px;max-width:1800px;margin:0 auto">

<!-- Summary Cards -->
<div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(180px,1fr))">
<div class="card"><div class="label">Branches</div><div class="value" style="color:var(--blue)">{len(all_bcs)}</div><div class="sub">M001–M038 (production)</div></div>
<div class="card"><div class="label">Instruments</div><div class="value" style="color:var(--purple)">{total_instruments}</div><div class="sub">EN+MR counted as one</div></div>
<div class="card"><div class="label" style="color:var(--red)">Gaps</div><div class="value" style="color:var(--red)">{total_gaps}</div><div class="sub">{total_gaps}/{total_combos} ({100-coverage_pct:.0f}% missing)</div></div>
<div class="card"><div class="label" style="color:var(--green)">Full Coverage</div><div class="value" style="color:var(--green)">{len(full_branches)}</div><div class="sub">all 5 instruments present</div></div>
<div class="card"><div class="label">Teachers</div><div class="value" style="color:var(--blue)">{total_teachers}</div><div class="sub">unique across intent+baseline</div></div>
<div class="card"><div class="label">Leaders</div><div class="value" style="color:var(--purple)">{total_leaders}</div><div class="sub">unique across intent+baseline+audit</div></div>
<div class="card"><div class="label">Teacher Gap Rate</div><div class="value" style="color:{'#16a34a' if teacher_gap_pct < 10 else '#d97706'}">{teacher_gap_pct}%</div><div class="sub">intent + baseline teacher</div></div>
<div class="card"><div class="label">Leader Gap Rate</div><div class="value" style="color:{'#dc2626' if leader_gap_pct > 30 else '#d97706'}">{leader_gap_pct}%</div><div class="sub">intent + baseline + audit leader</div></div>
</div>

<div class="info-box">
<strong>EN + MR combined:</strong> A branch with Marathi coverage is NOT a gap even if English is missing — they measure the same construct.
<strong>{total_gaps} gaps</strong> in {total_combos} combinations. Teacher coverage is <strong>{100-teacher_gap_pct:.0f}%</strong>. Leader coverage is <strong>{100-leader_gap_pct:.0f}%</strong>.
The <strong>SRI Audit</strong> (principal-level, 59% missing) is the single biggest data gap.
Full coverage: <strong>{', '.join(full_branches)}</strong>
</div>

<!-- Charts -->
<div class="grid-2">
<div class="chart-box"><h3>Gaps per Branch (of 5 instruments)</h3><canvas id="branchChart" height="400"></canvas></div>
<div class="chart-box"><h3>Coverage by Instrument (EN+MR combined)</h3><canvas id="instChart" height="250"></canvas>
<div style="margin-top:16px"><h3>Teacher vs Leader Gap</h3><canvas id="roleGapChart" height="120"></canvas></div></div>
</div>

<!-- Per-Instrument Breakdown -->
<h2 class="section-title">Per-Instrument Breakdown (EN + MR Combined)</h2>
<div class="cards" style="grid-template-columns:1fr 1fr">{inst_cards}</div>

<!-- Combined Heatmap -->
<h2 class="section-title">Coverage Heatmap — Combined Instruments</h2>
<div class="info-box" style="font-size:12px">Numbers show unique respondent count. <span style="background:#dcfce7;padding:2px 6px;border-radius:4px">Green = data present</span> <span style="background:#fee2e2;padding:2px 6px;border-radius:4px">Red = MISSING</span></div>
<div class="tbl-wrap"><table>
<thead><tr>
<th>Branch</th><th>Name</th>
{"".join(f'<th style="text-align:center;font-size:10px">{i[0]}<br><span style="font-size:8px;color:var(--muted)">{i[2]}</span></th>' for i in COMBINED_INSTRUMENTS)}
<th style="text-align:center">Gaps</th>
</tr></thead>
<tbody>{heatmap_rows}</tbody>
</table></div>

<!-- Language Breakdown -->
<h2 class="section-title">Per-Language Detail (EN and MR separately)</h2>
<div class="info-box" style="font-size:12px"><span style="color:var(--blue);font-weight:600">T</span> = Teacher count, <span style="color:var(--purple);font-weight:600">L</span> = Leader count. This shows which language each branch used.</div>
<div class="tbl-wrap"><table style="font-size:11px">
<thead><tr>
<th>Branch</th><th>Name</th>
{"".join(f'<th class="lang-header">{i[0]}<br>({i[3][0]})</th>' for i in LANG_INSTRUMENTS)}
</tr></thead>
<tbody>{lang_rows}</tbody>
</table></div>

<!-- Priority Action -->
<h2 class="section-title">Priority Action List</h2>
<div class="tbl-wrap"><table>
<thead><tr><th>Branch</th><th>Name</th><th style="text-align:center">Gaps</th><th>Role Gap</th><th>Missing Instruments</th><th style="text-align:right">Current SRI</th></tr></thead>
<tbody>{priority_rows}</tbody>
</table></div>

</div>

<script>
new Chart(document.getElementById('branchChart'), {{
  type:'bar', data:{{labels:{chart_bcs},datasets:[{{label:'Missing instruments',data:{chart_gap_counts},backgroundColor:{chart_gap_colors}}}]}},
  options:{{indexAxis:'y',scales:{{x:{{max:{total_instruments},ticks:{{stepSize:1}}}}}},plugins:{{legend:{{display:false}}}}}}
}});

new Chart(document.getElementById('instChart'), {{
  type:'bar', data:{{labels:{chart_inst_names},datasets:[
    {{label:'Covered',data:{chart_inst_covered},backgroundColor:'#16a34a'}},
    {{label:'Missing',data:{chart_inst_missing},backgroundColor:'#dc2626'}}
  ]}}, options:{{scales:{{x:{{stacked:true}},y:{{stacked:true,max:{len(all_bcs)}}}}},plugins:{{legend:{{position:'top'}}}}}}
}});

new Chart(document.getElementById('roleGapChart'), {{
  type:'bar', data:{{labels:['Teacher instruments','Leader instruments'],datasets:[
    {{label:'Coverage %',data:[{100-teacher_gap_pct},{100-leader_gap_pct}],backgroundColor:['#3b82f6','#8b5cf6']}}
  ]}}, options:{{indexAxis:'y',scales:{{x:{{max:100}}}},plugins:{{legend:{{display:false}}}}}}
}});
</script>

{footer()}
</body></html>"""

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(html)
    print(f"Written: {OUT_PATH} ({os.path.getsize(OUT_PATH) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
