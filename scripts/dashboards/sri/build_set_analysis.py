"""
Build SET (Structured Explanation of Translation) analysis dashboard.
Output: output/dashboards/sri/06_set_analysis.html
"""

import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE)
from scripts.dashboards.sri.html_utils import *
from src.sri.constants import (
    FP_NAMES, DEPTH_LEVELS, ALIGNMENT_STATES,
    TEACHER_AREAS, LEADER_AREAS,
    CORE_ARCHETYPES, FP_ARCHETYPES, TENSION_ARCHETYPES,
)

DATA_PATH = os.path.join(BASE, "output", "reports", "sri_unified.json")
OUT_PATH = os.path.join(BASE, "output", "dashboards", "sri", "06_set_analysis.html")

ALIGNMENT_BADGE_MAP = {
    "intent_high_translation_low": ("badge-amber", "Intent High / Translation Low"),
    "teacher_led_intent": ("badge-blue", "Teacher-Led Intent"),
    "leader_led_intent": ("badge-purple", "Leader-Led Intent"),
    "low_attention_zone": ("badge-red", "Low Attention Zone"),
    "intent_translation_aligned": ("badge-green", "Aligned"),
}


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def alignment_badge(state):
    cls, label = ALIGNMENT_BADGE_MAP.get(state, ("badge-gray", state.replace("_", " ").title() if state else "N/A"))
    return f'<span class="badge {cls}">{label}</span>'


def build_set1_tab(branches):
    codes = sorted(c for c in branches if branches[c].get("set") and branches[c]["set"].get("set1"))

    info = '<div class="info-box"><strong>SET1: Orientation Alignment</strong> maps how teacher and leader Foundational Philosophy orientations align with practice depth. Each FP gets an alignment state per branch.</div>'

    # Summary of alignment state frequency
    state_counts = {}
    for c in codes:
        s1 = branches[c]["set"]["set1"]
        for fp, state in s1.get("alignment_state_by_fp", {}).items():
            state_counts[state] = state_counts.get(state, 0) + 1

    summary_cards = '<div class="cards">'
    for state, count in sorted(state_counts.items(), key=lambda x: -x[1]):
        cls, label = ALIGNMENT_BADGE_MAP.get(state, ("badge-gray", state.replace("_", " ").title()))
        summary_cards += f'<div class="card"><div class="label">{label}</div><div class="value">{count}</div><div class="sub">FP-branch combinations</div></div>'
    summary_cards += '</div>'

    # Per-branch table
    rows = ""
    for c in codes:
        s1 = branches[c]["set"]["set1"]
        rows += f'<tr><td><strong>{c}</strong></td>'
        rows += f'<td>{s1.get("dominant_fp_teacher", "?")}</td>'
        rows += f'<td>{s1.get("dominant_fp_leader", "?")}</td>'
        for fp in ["FP1", "FP2", "FP3", "FP4", "FP5"]:
            state = s1.get("alignment_state_by_fp", {}).get(fp, "")
            rows += f'<td>{alignment_badge(state)}</td>'
        rows += '</tr>'

    table = f'''<div class="section-title">Branch Orientation Profiles</div>
    <div class="tbl-wrap"><table id="tblSet1"><thead><tr>
      <th onclick="sortTable('tblSet1',0,'str')">Branch</th>
      <th>Dom. FP (Teacher)</th>
      <th>Dom. FP (Leader)</th>
      <th>FP1</th><th>FP2</th><th>FP3</th><th>FP4</th><th>FP5</th>
    </tr></thead><tbody>{rows}</tbody></table></div>'''

    # FP legend
    fp_legend = '<div class="section-title">Foundational Philosophies</div><div class="grid-3">'
    for fp_code, fp_name in FP_NAMES.items():
        fp_legend += f'<div class="card"><div class="label">{fp_code}</div><div style="font-size:13px;font-weight:600">{fp_name}</div></div>'
    fp_legend += '</div>'

    return info + summary_cards + table + fp_legend, ""


def build_set2_tab(branches):
    codes = sorted(c for c in branches if branches[c].get("set") and branches[c]["set"].get("set2_teacher"))

    info = '<div class="info-box"><strong>SET2: Practice Areas</strong> measures teacher (A1-A4) and leader (B1-B4) diagnostic area means, derived from baseline instrument responses. Bands: Low (&lt;2.5), Mid (2.5-3.2), High (&gt;3.2).</div>'

    # Collect data for chart
    labels = []
    t_a1, t_a2, t_a3, t_a4 = [], [], [], []
    l_b1, l_b2, l_b3, l_b4 = [], [], [], []
    for c in codes:
        s = branches[c]["set"]
        tam = s["set2_teacher"].get("area_means", {})
        lam = s["set2_leader"].get("area_means", {})
        labels.append(c)
        t_a1.append(round(tam.get("A1", 0), 2))
        t_a2.append(round(tam.get("A2", 0), 2))
        t_a3.append(round(tam.get("A3", 0), 2))
        t_a4.append(round(tam.get("A4", 0), 2))
        l_b1.append(round(lam.get("B1", 0), 2))
        l_b2.append(round(lam.get("B2", 0), 2))
        l_b3.append(round(lam.get("B3", 0), 2))
        l_b4.append(round(lam.get("B4", 0), 2))

    chart_teacher = '<div class="chart-box"><h3>Teacher Areas (A1-A4) across Branches</h3><div style="height:350px"><canvas id="set2TeacherBar"></canvas></div></div>'
    chart_leader = '<div class="chart-box"><h3>Leader Areas (B1-B4) across Branches</h3><div style="height:350px"><canvas id="set2LeaderBar"></canvas></div></div>'

    # Table with both teacher + leader
    rows = ""
    for c in codes:
        s = branches[c]["set"]
        tam = s["set2_teacher"].get("area_means", {})
        tab = s["set2_teacher"].get("area_bands", {})
        lam = s["set2_leader"].get("area_means", {})
        lab = s["set2_leader"].get("area_bands", {})
        rows += f'<tr><td><strong>{c}</strong></td>'
        for a in ["A1", "A2", "A3", "A4"]:
            rows += f'<td>{tam.get(a, 0):.2f} {band_badge(tab.get(a, "no_data"))}</td>'
        for a in ["B1", "B2", "B3", "B4"]:
            rows += f'<td>{lam.get(a, 0):.2f} {band_badge(lab.get(a, "no_data"))}</td>'
        rows += '</tr>'

    table = f'''<div class="section-title">Combined Area Scores</div>
    <div class="tbl-wrap"><table id="tblSet2"><thead><tr>
      <th onclick="sortTable('tblSet2',0,'str')">Branch</th>
      <th onclick="sortTable('tblSet2',1,'num')">A1</th>
      <th onclick="sortTable('tblSet2',2,'num')">A2</th>
      <th onclick="sortTable('tblSet2',3,'num')">A3</th>
      <th onclick="sortTable('tblSet2',4,'num')">A4</th>
      <th onclick="sortTable('tblSet2',5,'num')">B1</th>
      <th onclick="sortTable('tblSet2',6,'num')">B2</th>
      <th onclick="sortTable('tblSet2',7,'num')">B3</th>
      <th onclick="sortTable('tblSet2',8,'num')">B4</th>
    </tr></thead><tbody>{rows}</tbody></table></div>'''

    js = f"""
    new Chart(document.getElementById('set2TeacherBar'), {{
      type: 'bar',
      data: {{
        labels: {jdumps(labels)},
        datasets: [
          {{label: 'A1', data: {jdumps(t_a1)}, backgroundColor: '#3b82f6'}},
          {{label: 'A2', data: {jdumps(t_a2)}, backgroundColor: '#8b5cf6'}},
          {{label: 'A3', data: {jdumps(t_a3)}, backgroundColor: '#10b981'}},
          {{label: 'A4', data: {jdumps(t_a4)}, backgroundColor: '#f59e0b'}}
        ]
      }},
      options: {{responsive: true, maintainAspectRatio: false, scales: {{y: {{min:0, max:4, title: {{display:true, text:'Mean (1-4)'}}}}}}}}
    }});
    new Chart(document.getElementById('set2LeaderBar'), {{
      type: 'bar',
      data: {{
        labels: {jdumps(labels)},
        datasets: [
          {{label: 'B1', data: {jdumps(l_b1)}, backgroundColor: '#0d9488'}},
          {{label: 'B2', data: {jdumps(l_b2)}, backgroundColor: '#6366f1'}},
          {{label: 'B3', data: {jdumps(l_b3)}, backgroundColor: '#ec4899'}},
          {{label: 'B4', data: {jdumps(l_b4)}, backgroundColor: '#f97316'}}
        ]
      }},
      options: {{responsive: true, maintainAspectRatio: false, scales: {{y: {{min:0, max:4, title: {{display:true, text:'Mean (1-4)'}}}}}}}}
    }});
    """

    return info + '<div class="grid-2">' + chart_teacher + chart_leader + '</div>' + table, js


def build_archetypes_tab(branches):
    codes = sorted(c for c in branches if branches[c].get("set") and branches[c]["set"].get("archetypes"))

    # Collect archetype distribution
    arch_branch_map = {}
    for arch_id in CORE_ARCHETYPES:
        arch_branch_map[arch_id] = []

    for c in codes:
        arc = branches[c]["set"]["archetypes"]
        if arc.get("primary") and arc["primary"] in arch_branch_map:
            arch_branch_map[arc["primary"]].append(c)
        for sec in arc.get("secondary", []):
            if sec in arch_branch_map:
                arch_branch_map[sec].append(c)

    # Archetype cards
    arch_colors = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#0d9488"]
    cards = '<div class="section-title">Core Archetypes (ARCH-01 to ARCH-06)</div><div class="grid-2">'
    for i, (arch_id, arch) in enumerate(CORE_ARCHETYPES.items()):
        branch_list = arch_branch_map.get(arch_id, [])
        color = arch_colors[i % len(arch_colors)]
        branch_tags = " ".join(f'<span class="badge badge-blue">{b}</span>' for b in branch_list) if branch_list else '<span style="color:var(--muted);font-size:11px">No branches matched</span>'

        state_cls, state_label = ALIGNMENT_BADGE_MAP.get(arch["set1_state"], ("badge-gray", arch["set1_state"]))
        tcond = ", ".join(f"{k}={v}" for k, v in arch.get("teacher_conditions", {}).items())
        lcond = ", ".join(f"{k}={v}" for k, v in arch.get("leader_conditions", {}).items())

        cards += f'''<div class="card" style="border-left:4px solid {color}">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <div class="label" style="margin:0">{arch_id}</div>
            <span class="badge {state_cls}" style="font-size:9px">{state_label}</span>
          </div>
          <p style="font-size:13px;margin-bottom:8px">{arch["interpretation"]}</p>
          <div style="font-size:11px;color:var(--muted);margin-bottom:8px">Teacher: {tcond} | Leader: {lcond}</div>
          <div style="font-size:11px"><strong>Branches:</strong> {branch_tags}</div>
        </div>'''
    cards += '</div>'

    # Doughnut chart
    arch_labels = list(CORE_ARCHETYPES.keys())
    arch_counts = [len(arch_branch_map.get(a, [])) for a in arch_labels]

    doughnut = '<div class="chart-box" style="max-width:450px;margin:24px auto"><h3>Archetype Distribution</h3><canvas id="archDoughnut"></canvas></div>'

    # Tension + FP archetypes summary
    tension_html = '<div class="section-title">Tension Archetypes</div><div class="grid-3">'
    for tid, tarch in TENSION_ARCHETYPES.items():
        t_branches = [c for c in codes if tid in branches[c]["set"]["archetypes"].get("tension_archetypes", [])]
        branch_tags = " ".join(f'<span class="badge badge-blue">{b}</span>' for b in t_branches) if t_branches else '<span style="color:var(--muted);font-size:11px">None</span>'
        tension_html += f'''<div class="card" style="border-left:3px solid #dc2626">
          <div class="label">{tid}</div>
          <p style="font-size:12px;margin:6px 0">{tarch["description"]}</p>
          <div style="font-size:11px"><strong>Branches:</strong> {branch_tags}</div>
        </div>'''
    tension_html += '</div>'

    fp_html = '<div class="section-title">FP-Specific Archetypes</div><div class="grid-3">'
    for fid, farch in FP_ARCHETYPES.items():
        f_branches = [c for c in codes if fid in branches[c]["set"]["archetypes"].get("fp_archetypes", [])]
        branch_tags = " ".join(f'<span class="badge badge-blue">{b}</span>' for b in f_branches) if f_branches else '<span style="color:var(--muted);font-size:11px">None</span>'
        fp_html += f'''<div class="card" style="border-left:3px solid #7c3aed">
          <div class="label">{fid} ({farch["fp"]})</div>
          <p style="font-size:12px;font-weight:600;margin:4px 0">{farch["label"]}</p>
          <div style="font-size:11px"><strong>Branches:</strong> {branch_tags}</div>
        </div>'''
    fp_html += '</div>'

    js = f"""
    new Chart(document.getElementById('archDoughnut'), {{
      type: 'doughnut',
      data: {{
        labels: {jdumps(arch_labels)},
        datasets: [{{
          data: {jdumps(arch_counts)},
          backgroundColor: {jdumps(arch_colors)}
        }}]
      }},
      options: {{responsive: true, plugins: {{legend: {{position: 'right'}}}}}}
    }});
    """

    return cards + doughnut + tension_html + fp_html, js


def build_branch_explorer_tab(branches):
    codes = sorted(c for c in branches if branches[c].get("set"))

    # Build full branch data as JS object
    branch_data = {}
    for c in codes:
        s = branches[c]["set"]
        s1 = s.get("set1", {})
        s2t = s.get("set2_teacher", {})
        s2l = s.get("set2_leader", {})
        arc = s.get("archetypes", {})
        expl = s.get("explainers", {})

        branch_data[c] = {
            "set1": s1,
            "set2_teacher": s2t,
            "set2_leader": s2l,
            "archetypes": arc,
            "explainer_flags": {fp: e.get("condition_flags", []) for fp, e in expl.items()} if expl else {},
        }

    options = "".join(f'<option value="{c}">{c}</option>' for c in codes)

    html = f'''
    <div style="margin-bottom:20px">
      <label style="font-weight:600;margin-right:8px">Select Branch:</label>
      <select id="branchSelect" onchange="renderBranch(this.value)">{options}</select>
    </div>
    <div id="branchProfile"></div>
    '''

    js = f"""
    var branchData = {jdumps(branch_data)};
    var fpNames = {jdumps(FP_NAMES)};
    var alignBadgeMap = {jdumps({k: list(v) for k, v in ALIGNMENT_BADGE_MAP.items()})};
    var coreArchetypes = {jdumps({k: v["interpretation"] for k, v in CORE_ARCHETYPES.items()})};
    var tensionArchetypes = {jdumps({k: v["description"] for k, v in TENSION_ARCHETYPES.items()})};
    var fpArchetypes = {jdumps({k: v["label"] for k, v in FP_ARCHETYPES.items()})};

    function makeBadge(state) {{
      var m = alignBadgeMap[state];
      if (!m) return '<span class="badge badge-gray">' + (state||'N/A') + '</span>';
      return '<span class="badge ' + m[0] + '">' + m[1] + '</span>';
    }}
    function bandBadge(b) {{
      var cls = {{high:'badge-green',mid:'badge-amber',low:'badge-red',no_data:'badge-gray'}}[b] || 'badge-gray';
      return '<span class="badge ' + cls + '">' + (b ? b.charAt(0).toUpperCase()+b.slice(1) : 'N/A') + '</span>';
    }}

    function renderBranch(code) {{
      var d = branchData[code];
      if (!d) {{ document.getElementById('branchProfile').innerHTML = '<p>No data</p>'; return; }}
      var h = '<h3 style="margin-bottom:16px">Branch: ' + code + '</h3>';

      // Orientation
      h += '<div class="section-title">SET1: Orientation</div>';
      h += '<div class="grid-2">';
      h += '<div class="card"><div class="label">Teacher Orientation Distribution</div>';
      var tod = d.set1.teacher_orientation_dist || {{}};
      for (var fp in tod) h += '<div style="font-size:12px;margin:2px 0"><strong>'+fp+'</strong> ('+fpNames[fp]+'): '+(tod[fp]*100).toFixed(0)+'%</div>';
      h += '<div style="margin-top:8px;font-size:12px"><strong>Dominant:</strong> '+(d.set1.dominant_fp_teacher||'?')+'</div></div>';

      h += '<div class="card"><div class="label">Leader Orientation Distribution</div>';
      var lod = d.set1.leader_orientation_dist || {{}};
      for (var fp in lod) h += '<div style="font-size:12px;margin:2px 0"><strong>'+fp+'</strong> ('+fpNames[fp]+'): '+(lod[fp]*100).toFixed(0)+'%</div>';
      h += '<div style="margin-top:8px;font-size:12px"><strong>Dominant:</strong> '+(d.set1.dominant_fp_leader||'?')+'</div></div>';
      h += '</div>';

      // Alignment states
      h += '<div class="card" style="margin:16px 0"><div class="label">Alignment States by FP</div>';
      var asfp = d.set1.alignment_state_by_fp || {{}};
      for (var fp in asfp) h += '<div style="display:inline-block;margin:4px 8px 4px 0"><strong>'+fp+':</strong> '+makeBadge(asfp[fp])+'</div>';
      h += '</div>';

      // SET2 areas
      h += '<div class="section-title">SET2: Area Scores</div><div class="grid-2">';
      h += '<div class="card"><div class="label">Teacher Areas (A1-A4)</div>';
      var tam = d.set2_teacher.area_means || {{}};
      var tab = d.set2_teacher.area_bands || {{}};
      for (var a in tam) h += '<div style="font-size:12px;margin:3px 0"><strong>'+a+'</strong>: '+tam[a].toFixed(2)+' '+bandBadge(tab[a])+'</div>';
      h += '</div>';
      h += '<div class="card"><div class="label">Leader Areas (B1-B4)</div>';
      var lam = d.set2_leader.area_means || {{}};
      var lab = d.set2_leader.area_bands || {{}};
      for (var a in lam) h += '<div style="font-size:12px;margin:3px 0"><strong>'+a+'</strong>: '+lam[a].toFixed(2)+' '+bandBadge(lab[a])+'</div>';
      h += '</div></div>';

      // Archetypes
      h += '<div class="section-title">Matched Archetypes</div>';
      var arc = d.archetypes;
      if (arc.primary) h += '<div class="card" style="border-left:4px solid #3b82f6;margin-bottom:12px"><div class="label">Primary</div><strong>'+arc.primary+'</strong>: '+(coreArchetypes[arc.primary]||'')+'</div>';
      else h += '<div style="color:var(--muted);font-size:13px;margin-bottom:8px">No primary archetype matched.</div>';
      if (arc.secondary && arc.secondary.length) {{
        h += '<div class="label" style="margin:8px 0 4px">Secondary</div>';
        arc.secondary.forEach(function(s) {{ h += '<span class="badge badge-blue" style="margin-right:6px">'+s+'</span>'; }});
        h += '<br>';
      }}
      if (arc.tension_archetypes && arc.tension_archetypes.length) {{
        h += '<div class="label" style="margin:8px 0 4px">Tension Archetypes</div>';
        arc.tension_archetypes.forEach(function(t) {{ h += '<div class="card" style="border-left:3px solid #dc2626;margin:6px 0;padding:10px"><strong>'+t+'</strong>: '+(tensionArchetypes[t]||'')+'</div>'; }});
      }}
      if (arc.fp_archetypes && arc.fp_archetypes.length) {{
        h += '<div class="label" style="margin:8px 0 4px">FP Archetypes</div>';
        arc.fp_archetypes.forEach(function(f) {{ h += '<span class="badge badge-purple" style="margin-right:6px">'+f+': '+(fpArchetypes[f]||'')+'</span>'; }});
        h += '<br>';
      }}
      h += '<div style="margin-top:8px;font-size:12px;color:var(--muted)">Confidence: <strong>'+(arc.confidence||'?')+'</strong></div>';

      // Condition flags
      var flags = d.explainer_flags || {{}};
      var hasFlags = false;
      for (var fp in flags) if (flags[fp].length) {{ hasFlags = true; break; }}
      if (hasFlags) {{
        h += '<div class="section-title">Condition Flags</div>';
        for (var fp in flags) {{
          if (flags[fp].length) {{
            h += '<div style="font-size:12px;margin:4px 0"><strong>'+fp+':</strong> ';
            flags[fp].forEach(function(f) {{ h += '<span class="badge badge-red" style="margin:2px">'+f+'</span>'; }});
            h += '</div>';
          }}
        }}
      }}

      document.getElementById('branchProfile').innerHTML = h;
    }}

    // Render first branch on load
    renderBranch(document.getElementById('branchSelect').value);
    """

    return html, js


def build():
    data = load_data()
    branches = data["branches"]

    set1_html, set1_js = build_set1_tab(branches)
    set2_html, set2_js = build_set2_tab(branches)
    arch_html, arch_js = build_archetypes_tab(branches)
    explorer_html, explorer_js = build_branch_explorer_tab(branches)

    tabs_html = '''<div class="tabs">
      <div class="tab active" onclick="showTab('tab-set1')">SET1: Orientation</div>
      <div class="tab" onclick="showTab('tab-set2')">SET2: Areas</div>
      <div class="tab" onclick="showTab('tab-archetypes')">Archetypes</div>
      <div class="tab" onclick="showTab('tab-explorer')">Branch Explorer</div>
    </div>'''

    content_html = f'''
    <div id="tab-set1" class="content active">{set1_html}</div>
    <div id="tab-set2" class="content">{set2_html}</div>
    <div id="tab-archetypes" class="content">{arch_html}</div>
    <div id="tab-explorer" class="content">{explorer_html}</div>
    '''

    extra_js = set1_js + set2_js + arch_js + explorer_js

    html = html_doc("SET Analysis", "06_set_analysis.html", tabs_html, content_html, extra_js=extra_js)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(html)
    print(f"Written: {OUT_PATH}")


if __name__ == "__main__":
    build()
