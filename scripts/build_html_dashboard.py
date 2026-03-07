"""Build baseline_dashboard.html with embedded data and CSV/JSON import capability."""
import json, csv, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def csv_to_json(path):
    with open(path) as f:
        return list(csv.DictReader(f))

teacher_data = json.dumps(csv_to_json(os.path.join(BASE, "output", "baseline_scores_teacher.csv")))
leader_data = json.dumps(csv_to_json(os.path.join(BASE, "output", "baseline_scores_leader.csv")))

html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stage 4.3 Practice Diagnostics — Enablement &amp; Systems Baseline</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
:root {
  --primary: #1a365d; --accent: #2b6cb0; --green: #38a169; --amber: #d69e2e;
  --orange: #ed8936; --red: #e53e3e; --bg: #f7fafc; --card: #ffffff;
  --border: #e2e8f0; --text: #2d3748; --muted: #718096; --light: #ebf4ff;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
.header { background: linear-gradient(135deg, var(--primary), var(--accent)); color: white; padding: 24px 32px; }
.header h1 { font-size: 22px; margin-bottom: 4px; }
.header p { font-size: 13px; opacity: 0.85; }
.tabs { display: flex; border-bottom: 2px solid var(--border); background: white; padding: 0 24px; position: sticky; top: 0; z-index: 100; }
.tab { padding: 14px 28px; cursor: pointer; font-weight: 600; color: var(--muted); border-bottom: 3px solid transparent; transition: all 0.2s; font-size: 14px; }
.tab:hover { color: var(--accent); background: var(--light); }
.tab.active { color: var(--accent); border-bottom-color: var(--accent); }
.tab-content { display: none; padding: 24px; max-width: 1400px; margin: 0 auto; }
.tab-content.active { display: block; }
.import-bar { background: white; border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px; margin-bottom: 20px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.import-bar label { font-weight: 600; font-size: 13px; color: var(--primary); }
.import-bar input[type="file"] { font-size: 12px; }
.import-bar button { padding: 8px 18px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600; }
.import-bar button:hover { background: var(--primary); }
.import-bar .or { color: var(--muted); font-size: 12px; padding: 0 4px; }
.import-bar textarea { font-size: 11px; font-family: monospace; resize: vertical; height: 60px; flex: 1; min-width: 200px; border: 1px solid var(--border); border-radius: 4px; padding: 6px; }
.stats-bar { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.stat-chip { background: white; border: 1px solid var(--border); border-radius: 8px; padding: 10px 18px; font-size: 13px; }
.stat-chip strong { color: var(--primary); }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
.card { background: white; border-radius: 12px; padding: 20px; text-align: center; border-left: 4px solid var(--amber); box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.card.strong { border-left-color: var(--green); }
.card.developing { border-left-color: var(--orange); }
.card.limited { border-left-color: var(--red); }
.card .area-code { font-size: 14px; font-weight: 700; color: var(--primary); }
.card .area-name { font-size: 11px; color: var(--muted); margin: 4px 0 10px; line-height: 1.3; }
.card .score { font-size: 32px; font-weight: 800; }
.card .score.strong { color: var(--green); }
.card .score.moderate { color: var(--amber); }
.card .score.developing { color: var(--orange); }
.card .score.limited { color: var(--red); }
.card .pct { font-size: 13px; color: var(--muted); }
.card .band { display: inline-block; margin-top: 8px; padding: 3px 12px; border-radius: 12px; font-size: 11px; font-weight: 700; }
.band-strong { background: #f0fff4; color: var(--green); }
.band-moderate { background: #fffff0; color: var(--amber); }
.band-developing { background: #fffaf0; color: var(--orange); }
.band-limited { background: #fff5f5; color: var(--red); }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.chart-box { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); position: relative; }
.chart-box h3 { font-size: 14px; color: var(--primary); margin-bottom: 12px; }
.chart-box canvas { max-height: 320px; }
.heatmap-section { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 24px; overflow-x: auto; position: relative; }
.heatmap-section h3 { font-size: 14px; color: var(--primary); margin-bottom: 12px; }
table.heatmap { width: 100%; border-collapse: collapse; font-size: 12px; }
table.heatmap th { background: var(--primary); color: white; padding: 8px 10px; text-align: center; position: sticky; top: 0; }
table.heatmap th:first-child { text-align: left; min-width: 280px; }
table.heatmap td { padding: 6px 10px; text-align: center; border-bottom: 1px solid var(--border); font-weight: 600; }
table.heatmap td:first-child { text-align: left; font-weight: 400; font-size: 11px; }
table.heatmap tr:hover { background: var(--light); }
.goal-table { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 24px; position: relative; }
.goal-table h3 { font-size: 14px; color: var(--primary); margin-bottom: 12px; }
/* ── Sticky Note ── */
.info-toggle { position: absolute; bottom: 10px; right: 12px; width: 26px; height: 26px; border-radius: 50%; background: var(--light); border: 1px solid var(--border); display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 14px; color: var(--accent); transition: all 0.2s; z-index: 10; user-select: none; }
.info-toggle:hover { background: var(--accent); color: white; transform: scale(1.1); }
.sticky-note { display: none; position: absolute; bottom: 42px; right: 10px; width: 320px; background: #fefce8; border: 1px solid #facc15; border-radius: 8px; padding: 14px 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.12); z-index: 20; font-size: 12px; line-height: 1.6; color: #713f12; }
.sticky-note.visible { display: block; animation: fadeIn 0.2s ease; }
.sticky-note .note-title { font-weight: 700; font-size: 12px; color: #854d0e; margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }
.sticky-note .note-title::before { content: ''; display: inline-block; width: 8px; height: 8px; border-radius: 2px; background: #facc15; }
.sticky-note .note-close { position: absolute; top: 6px; right: 10px; cursor: pointer; font-size: 16px; color: #a16207; line-height: 1; }
.sticky-note .note-close:hover { color: #713f12; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.cards-wrapper { position: relative; margin-bottom: 24px; }
table.goals { width: 100%; border-collapse: collapse; font-size: 12px; }
table.goals th { background: var(--primary); color: white; padding: 8px 10px; text-align: left; }
table.goals td { padding: 6px 10px; border-bottom: 1px solid var(--border); }
table.goals tr:nth-child(even) { background: #f8fafc; }
@media (max-width: 900px) { .chart-grid { grid-template-columns: 1fr; } .cards { grid-template-columns: 1fr 1fr; } }
@media (max-width: 600px) { .cards { grid-template-columns: 1fr; } }
</style>
</head>
<body>

<div class="header">
  <h1>Stage 4.3 Practice Diagnostics — Enablement &amp; Systems Baseline</h1>
  <p>Response Scale: Strongly Agree (4) / Agree (3) / Disagree (2) / Strongly Disagree (1) &nbsp;|&nbsp; Equal weight per question within area</p>
</div>

<div class="tabs">
  <div class="tab active" onclick="switchTab('teacher')">Teacher Lens (A1–A4)</div>
  <div class="tab" onclick="switchTab('leader')">Leadership Lens (B1–B5)</div>
</div>

<!-- ═══ TEACHER TAB ═══ -->
<div id="tab-teacher" class="tab-content active">
  <div class="import-bar">
    <label>Import Teacher Data:</label>
    <input type="file" id="teacher-file" accept=".csv,.json" onchange="handleFileImport('teacher', this)">
    <span class="or">— or paste —</span>
    <textarea id="teacher-paste" placeholder="Paste CSV or JSON here..."></textarea>
    <button onclick="handlePasteImport('teacher')">Load</button>
    <button onclick="resetData('teacher')" style="background:#e53e3e">Reset</button>
  </div>
  <div id="teacher-stats" class="stats-bar"></div>
  <div class="cards-wrapper">
    <div id="teacher-cards" class="cards"></div>
    <div class="info-toggle" onclick="toggleNote(this)">i</div>
    <div class="sticky-note" data-note="cards">
      <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
      <div class="note-title">Score Cards</div>
      Each card shows one area's average score across all respondents on a 1–4 scale.
      Colour bands indicate readiness level: Strong (&ge;3.5), Moderate (2.5–3.5),
      Developing (1.5–2.5), or Limited (&lt;1.5). The percentage reflects how close
      the cohort is to the maximum possible score of 4.
    </div>
  </div>
  <div class="chart-grid">
    <div class="chart-box">
      <h3>Overall Area Averages</h3><canvas id="teacher-bar"></canvas>
      <div class="info-toggle" onclick="toggleNote(this)">i</div>
      <div class="sticky-note" data-note="bar">
        <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
        <div class="note-title">Area Averages</div>
        Horizontal bars compare area-level averages side-by-side. Longer bars indicate
        stronger perceived enablement. The dashed line at 2.5 marks the threshold between
        Moderate and Developing bands. Use this to quickly spot which areas need
        the most attention relative to others.
      </div>
    </div>
    <div class="chart-box">
      <h3>Score Band Distribution</h3><canvas id="teacher-dist"></canvas>
      <div class="info-toggle" onclick="toggleNote(this)">i</div>
      <div class="sticky-note" data-note="dist">
        <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
        <div class="note-title">Band Distribution</div>
        Shows the percentage of respondents falling into each readiness band per area.
        A large green segment means most respondents strongly agree with enablement
        statements. Red/orange segments highlight pockets of concern even when the
        overall average looks healthy. Useful for detecting hidden variance.
      </div>
    </div>
    <div class="chart-box">
      <h3>Area Profile (Radar)</h3><canvas id="teacher-radar"></canvas>
      <div class="info-toggle" onclick="toggleNote(this)">i</div>
      <div class="sticky-note" data-note="radar">
        <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
        <div class="note-title">Radar Profile</div>
        The spider chart visualises the overall shape of enablement across all areas.
        A balanced polygon suggests even support; spikes or dips reveal relative
        strengths and gaps. The outer ring represents a perfect score of 4.
        Compare the shaded area to the full polygon to gauge overall readiness.
      </div>
    </div>
    <div class="chart-box">
      <h3>Score Distribution (Box Approximation)</h3><canvas id="teacher-box"></canvas>
      <div class="info-toggle" onclick="toggleNote(this)">i</div>
      <div class="sticky-note" data-note="box">
        <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
        <div class="note-title">Score Spread</div>
        A stacked representation of Min, Q1, Median, Q3 and Max for each area.
        Taller stacks indicate wider spread in responses — meaning respondents
        have very different experiences. Narrow stacks mean consensus. Compare
        the median position across areas to understand central tendency.
      </div>
    </div>
  </div>
  <div class="heatmap-section">
    <h3>Branch &times; Area Heatmap</h3><table class="heatmap" id="teacher-heatmap"></table>
    <div class="info-toggle" onclick="toggleNote(this)">i</div>
    <div class="sticky-note" data-note="heatmap">
      <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
      <div class="note-title">Branch Heatmap</div>
      Each row is a school branch; each cell shows the branch-level average for that area.
      Green cells indicate strong enablement, amber is moderate, and red signals gaps.
      Branches are sorted top-to-bottom by their overall average. Use this to identify
      which specific branches need targeted intervention in which areas.
    </div>
  </div>
  <div class="goal-table">
    <h3>Area Summary &amp; Sub-Areas</h3><table class="goals" id="teacher-summary"></table>
    <div class="info-toggle" onclick="toggleNote(this)">i</div>
    <div class="sticky-note" data-note="summary">
      <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
      <div class="note-title">Summary Table</div>
      A statistical overview of each area: mean, median, standard deviation and readiness band.
      The Sub-Areas column lists the specific dimensions measured within each area.
      Wt/Q shows the equal weight each question carries. Use Std Dev to assess
      how much agreement or divergence exists among respondents.
    </div>
  </div>
</div>

<!-- ═══ LEADER TAB ═══ -->
<div id="tab-leader" class="tab-content">
  <div class="import-bar">
    <label>Import Leader Data:</label>
    <input type="file" id="leader-file" accept=".csv,.json" onchange="handleFileImport('leader', this)">
    <span class="or">— or paste —</span>
    <textarea id="leader-paste" placeholder="Paste CSV or JSON here..."></textarea>
    <button onclick="handlePasteImport('leader')">Load</button>
    <button onclick="resetData('leader')" style="background:#e53e3e">Reset</button>
  </div>
  <div id="leader-stats" class="stats-bar"></div>
  <div class="cards-wrapper">
    <div id="leader-cards" class="cards"></div>
    <div class="info-toggle" onclick="toggleNote(this)">i</div>
    <div class="sticky-note" data-note="cards">
      <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
      <div class="note-title">Score Cards</div>
      Each card shows one area's average score across all leader respondents on a 1–4 scale.
      Colour bands indicate readiness: Strong (&ge;3.5), Moderate (2.5–3.5),
      Developing (1.5–2.5), or Limited (&lt;1.5). The percentage reflects proximity
      to the maximum score. Leaders' English and Marathi responses are merged.
    </div>
  </div>
  <div class="chart-grid">
    <div class="chart-box">
      <h3>Overall Area Averages</h3><canvas id="leader-bar"></canvas>
      <div class="info-toggle" onclick="toggleNote(this)">i</div>
      <div class="sticky-note" data-note="bar">
        <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
        <div class="note-title">Area Averages</div>
        Horizontal bars compare leadership area averages side-by-side. Longer bars mean
        stronger perceived systems readiness. The dashed line at 2.5 marks the Moderate/Developing
        threshold. With only 67 respondents, individual branch variation can shift
        these averages significantly — check the heatmap for branch-level detail.
      </div>
    </div>
    <div class="chart-box">
      <h3>Score Band Distribution</h3><canvas id="leader-dist"></canvas>
      <div class="info-toggle" onclick="toggleNote(this)">i</div>
      <div class="sticky-note" data-note="dist">
        <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
        <div class="note-title">Band Distribution</div>
        Percentage of leaders in each readiness band per area. A dominant green segment
        signals strong system-level alignment. Orange/red segments indicate leaders who
        perceive gaps in enablement. Even small red segments matter given the
        smaller sample size — each represents real leadership concern.
      </div>
    </div>
    <div class="chart-box">
      <h3>Area Profile (Radar)</h3><canvas id="leader-radar"></canvas>
      <div class="info-toggle" onclick="toggleNote(this)">i</div>
      <div class="sticky-note" data-note="radar">
        <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
        <div class="note-title">Radar Profile</div>
        The spider chart shows the leadership enablement shape across all five B-areas.
        A balanced pentagon suggests consistent systems support; visible dips flag
        areas where governance or culture may lag. The outer ring is 4 (maximum).
        Compare this shape with the Teacher radar to spot alignment gaps.
      </div>
    </div>
    <div class="chart-box">
      <h3>Score Distribution (Box Approximation)</h3><canvas id="leader-box"></canvas>
      <div class="info-toggle" onclick="toggleNote(this)">i</div>
      <div class="sticky-note" data-note="box">
        <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
        <div class="note-title">Score Spread</div>
        Shows Min, Q1, Median, Q3, Max spread for each area across leaders.
        Wide spreads indicate disagreement among leaders about enablement quality —
        some branches may have strong systems while others don't. Narrow spreads
        suggest consistent experience across all schools.
      </div>
    </div>
  </div>
  <div class="heatmap-section">
    <h3>Branch &times; Area Heatmap</h3><table class="heatmap" id="leader-heatmap"></table>
    <div class="info-toggle" onclick="toggleNote(this)">i</div>
    <div class="sticky-note" data-note="heatmap">
      <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
      <div class="note-title">Branch Heatmap</div>
      Each row is a school branch; cells show the branch average per leadership area.
      Green = strong, amber = moderate, red = gap. Many branches have only 1–2 leader
      responses, so interpret cautiously. Sorted by overall average descending.
      Cross-reference with teacher heatmap to find schools where both lenses agree.
    </div>
  </div>
  <div class="goal-table">
    <h3>Area Summary &amp; Sub-Areas</h3><table class="goals" id="leader-summary"></table>
    <div class="info-toggle" onclick="toggleNote(this)">i</div>
    <div class="sticky-note" data-note="summary">
      <span class="note-close" onclick="toggleNote(this.parentElement.previousElementSibling)">&times;</span>
      <div class="note-title">Summary Table</div>
      Statistical overview: mean, median, std dev and readiness band for each B-area.
      Sub-Areas list the governance/culture dimensions measured. Note: Marathi leader
      questions cover parallel but differently worded dimensions (merged by B-code).
      High Std Dev areas deserve deeper branch-level investigation.
    </div>
  </div>
</div>

<script>
// ── CONFIG ──
const AREA_META = {
  A1: { name: "Continuous Learning Diagnostics", goals: ["Access","Usability","Follow-through","Collective Use","Student Clarity"], qs: 5 },
  A2: { name: "Teacher Development & Growth Support", goals: ["Structure","Safety","Peer Learning","Experimentation","Growth Culture"], qs: 5 },
  A3: { name: "HPC Teacher Enablement", goals: ["Understanding","Clarity","Time","Use","Student Role"], qs: 5 },
  A4: { name: "Parent & Community Support", goals: ["Communication","Guidance","Facilitation","Recognition"], qs: 4 },
  B1: { name: "NEP Governance & Ownership", goals: ["Ownership","Translation","Distribution"], qs: 3 },
  B2: { name: "Data-Informed Decision Culture", goals: ["Review","Decisions","Support"], qs: 3 },
  B3: { name: "Teacher Development Culture", goals: ["Peer Learning Circles","Safety","Experimentation"], qs: 3 },
  B4: { name: "HPC & Reporting Culture", goals: ["Purpose","Parent Clarity","Teacher Support"], qs: 3 },
  B5: { name: "Parent & Community Partnerships", goals: ["Strategy","Activation","Feedback"], qs: 3 },
};
const TEACHER_AREAS = ["A1","A2","A3","A4"];
const LEADER_AREAS = ["B1","B2","B3","B4","B5"];
const COLORS = { strong: "#38a169", moderate: "#d69e2e", developing: "#ed8936", limited: "#e53e3e" };

function scoreBand(avg) {
  if (avg >= 3.5) return { label: "Strong", color: COLORS.strong, cls: "strong" };
  if (avg >= 2.5) return { label: "Moderate", color: COLORS.moderate, cls: "moderate" };
  if (avg >= 1.5) return { label: "Developing", color: COLORS.developing, cls: "developing" };
  return { label: "Limited", color: COLORS.limited, cls: "limited" };
}

function heatColor(val) {
  const t = Math.max(0, Math.min(1, (val - 1) / 3));
  const r = Math.round(229 - t * 173), g = Math.round(62 + t * 99), b = Math.round(62 - t * 17);
  if (t < 0.33) return `rgb(${229-Math.round(t*3*60)}, ${62+Math.round(t*3*75)}, ${62+Math.round(t*3*10)})`;
  if (t < 0.66) return `rgb(${169-Math.round((t-0.33)*3*40)}, ${137+Math.round((t-0.33)*3*30)}, ${72-Math.round((t-0.33)*3*30)})`;
  return `rgb(${56}, ${161-Math.round((t-0.66)*3*0)}, ${105-Math.round((t-0.66)*3*60)})`;
}

// ── EMBEDDED DATA ──
const BUILTIN_TEACHER = __TEACHER_DATA__;
const BUILTIN_LEADER = __LEADER_DATA__;

let currentData = { teacher: BUILTIN_TEACHER, leader: BUILTIN_LEADER };
let charts = {};

// ── CSV PARSER ──
function parseCSV(text) {
  const lines = text.trim().split('\n');
  if (lines.length < 2) return [];
  const headers = parseCSVLine(lines[0]);
  return lines.slice(1).map(line => {
    const vals = parseCSVLine(line);
    const obj = {};
    headers.forEach((h, i) => obj[h.trim()] = (vals[i] || '').trim());
    return obj;
  });
}

function parseCSVLine(line) {
  const result = []; let current = ''; let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"' && line[i+1] === '"') { current += '"'; i++; }
      else if (ch === '"') inQuotes = false;
      else current += ch;
    } else {
      if (ch === '"') inQuotes = true;
      else if (ch === ',') { result.push(current); current = ''; }
      else current += ch;
    }
  }
  result.push(current);
  return result;
}

function detectAndParse(text) {
  text = text.trim();
  if (text.startsWith('[') || text.startsWith('{')) return JSON.parse(text.startsWith('{') ? '['+text+']' : text);
  return parseCSV(text);
}

// ── COMPUTE STATS ──
function computeStats(data, areas) {
  const areaKey = (a, suffix) => `${a}_${suffix}`;
  const areaStats = {};
  const branchData = {};

  areas.forEach(a => { areaStats[a] = { vals: [], sum: 0 }; });

  data.forEach(r => {
    const bc = r.BranchCode || r.bc || '';
    const branch = r.Branch || r.branch || bc;
    if (bc && !branchData[bc]) branchData[bc] = { name: branch, n: 0, areas: {} };
    if (bc) { branchData[bc].n++; areas.forEach(a => { if (!branchData[bc].areas[a]) branchData[bc].areas[a] = []; }); }

    areas.forEach(a => {
      const avg = parseFloat(r[areaKey(a, 'Avg')] || r[`${a}_avg`] || 0);
      if (avg > 0) {
        areaStats[a].vals.push(avg);
        areaStats[a].sum += avg;
        if (bc) branchData[bc].areas[a].push(avg);
      }
    });
  });

  const result = { n: data.length, branches: Object.keys(branchData).length, areas: {}, branchMatrix: branchData };
  areas.forEach(a => {
    const v = areaStats[a].vals.sort((x, y) => x - y);
    const n = v.length;
    result.areas[a] = {
      mean: n ? v.reduce((s, x) => s + x, 0) / n : 0,
      median: n ? (n % 2 ? v[Math.floor(n/2)] : (v[n/2-1] + v[n/2]) / 2) : 0,
      std: n ? Math.sqrt(v.reduce((s, x) => s + (x - (areaStats[a].sum/n)) ** 2, 0) / n) : 0,
      min: n ? v[0] : 0, max: n ? v[n-1] : 0, n: n,
      q1: n >= 4 ? v[Math.floor(n * 0.25)] : (n ? v[0] : 0),
      q3: n >= 4 ? v[Math.floor(n * 0.75)] : (n ? v[n-1] : 0),
      pct: n ? v.reduce((s, x) => s + x, 0) / n / 4 * 100 : 0,
      dist: { strong: 0, moderate: 0, developing: 0, limited: 0 }
    };
    v.forEach(val => {
      if (val >= 3.5) result.areas[a].dist.strong++;
      else if (val >= 2.5) result.areas[a].dist.moderate++;
      else if (val >= 1.5) result.areas[a].dist.developing++;
      else result.areas[a].dist.limited++;
    });
  });
  return result;
}

// ── RENDER ──
function renderDashboard(lens) {
  const data = currentData[lens];
  const areas = lens === 'teacher' ? TEACHER_AREAS : LEADER_AREAS;
  const stats = computeStats(data, areas);

  // Destroy old charts
  ['bar','dist','radar','box'].forEach(t => { if (charts[`${lens}-${t}`]) charts[`${lens}-${t}`].destroy(); });

  // Stats bar
  const langs = {}; data.forEach(r => { const l = r.Language || r.lang || '?'; langs[l] = (langs[l]||0)+1; });
  const langStr = Object.entries(langs).map(([k,v]) => `${k}: ${v}`).join(', ');
  document.getElementById(`${lens}-stats`).innerHTML =
    `<div class="stat-chip"><strong>${stats.n}</strong> Respondents</div>` +
    `<div class="stat-chip"><strong>${stats.branches}</strong> Branches</div>` +
    `<div class="stat-chip">Language: ${langStr}</div>` +
    `<div class="stat-chip">Areas: <strong>${areas.join(', ')}</strong></div>`;

  // Score cards
  let cardsHtml = '';
  areas.forEach(a => {
    const s = stats.areas[a]; const band = scoreBand(s.mean);
    cardsHtml += `<div class="card ${band.cls}">
      <div class="area-code">${a}</div>
      <div class="area-name">${AREA_META[a].name}</div>
      <div class="score ${band.cls}">${s.mean.toFixed(2)}</div>
      <div class="pct">${s.pct.toFixed(0)}%</div>
      <div class="band band-${band.cls}">${band.label}</div>
    </div>`;
  });
  document.getElementById(`${lens}-cards`).innerHTML = cardsHtml;

  // Bar chart
  const barCtx = document.getElementById(`${lens}-bar`).getContext('2d');
  charts[`${lens}-bar`] = new Chart(barCtx, {
    type: 'bar', data: {
      labels: areas.map(a => `${a}: ${AREA_META[a].name.split(' ').slice(0,3).join(' ')}`),
      datasets: [{ data: areas.map(a => stats.areas[a].mean.toFixed(2)),
        backgroundColor: areas.map(a => scoreBand(stats.areas[a].mean).color + '99'),
        borderColor: areas.map(a => scoreBand(stats.areas[a].mean).color),
        borderWidth: 2, borderRadius: 6 }]
    }, options: { indexAxis: 'y', scales: { x: { min: 0, max: 4, title: { display: true, text: 'Avg Score (0-4)' } } },
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => `Score: ${ctx.raw}` } } } }
  });

  // Distribution chart
  const distCtx = document.getElementById(`${lens}-dist`).getContext('2d');
  charts[`${lens}-dist`] = new Chart(distCtx, {
    type: 'bar', data: {
      labels: areas,
      datasets: [
        { label: 'Strong (≥3.5)', data: areas.map(a => stats.areas[a].n ? (stats.areas[a].dist.strong / stats.areas[a].n * 100).toFixed(1) : 0), backgroundColor: COLORS.strong },
        { label: 'Moderate (2.5–3.5)', data: areas.map(a => stats.areas[a].n ? (stats.areas[a].dist.moderate / stats.areas[a].n * 100).toFixed(1) : 0), backgroundColor: COLORS.moderate },
        { label: 'Developing (1.5–2.5)', data: areas.map(a => stats.areas[a].n ? (stats.areas[a].dist.developing / stats.areas[a].n * 100).toFixed(1) : 0), backgroundColor: COLORS.developing },
        { label: 'Limited (<1.5)', data: areas.map(a => stats.areas[a].n ? (stats.areas[a].dist.limited / stats.areas[a].n * 100).toFixed(1) : 0), backgroundColor: COLORS.limited },
      ]
    }, options: { indexAxis: 'y', scales: { x: { stacked: true, max: 100, title: { display: true, text: '% of respondents' } }, y: { stacked: true } },
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } } } }
  });

  // Radar chart
  const radarCtx = document.getElementById(`${lens}-radar`).getContext('2d');
  charts[`${lens}-radar`] = new Chart(radarCtx, {
    type: 'radar', data: {
      labels: areas.map(a => `${a} (${stats.areas[a].mean.toFixed(2)})`),
      datasets: [{ data: areas.map(a => stats.areas[a].mean), fill: true,
        backgroundColor: 'rgba(43,108,176,0.15)', borderColor: '#2b6cb0', pointBackgroundColor: '#2b6cb0', pointRadius: 5, borderWidth: 2.5 }]
    }, options: { scales: { r: { min: 0, max: 4, ticks: { stepSize: 1, font: { size: 10 } } } },
      plugins: { legend: { display: false } } }
  });

  // Box-like chart (min/q1/median/q3/max per area)
  const boxCtx = document.getElementById(`${lens}-box`).getContext('2d');
  charts[`${lens}-box`] = new Chart(boxCtx, {
    type: 'bar', data: {
      labels: areas,
      datasets: [
        { label: 'Min', data: areas.map(a => stats.areas[a].min.toFixed(2)), backgroundColor: '#e2e8f0', borderRadius: 4 },
        { label: 'Q1', data: areas.map(a => (stats.areas[a].q1 - stats.areas[a].min).toFixed(2)), backgroundColor: COLORS.developing + '88', borderRadius: 4 },
        { label: 'Median', data: areas.map(a => (stats.areas[a].median - stats.areas[a].q1).toFixed(2)), backgroundColor: COLORS.moderate + 'cc', borderRadius: 4 },
        { label: 'Q3', data: areas.map(a => (stats.areas[a].q3 - stats.areas[a].median).toFixed(2)), backgroundColor: COLORS.moderate + '88', borderRadius: 4 },
        { label: 'Max', data: areas.map(a => (stats.areas[a].max - stats.areas[a].q3).toFixed(2)), backgroundColor: '#e2e8f0', borderRadius: 4 },
      ]
    }, options: { scales: { x: {}, y: { stacked: true, min: 0, max: 4.5, title: { display: true, text: 'Score' } } },
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 10 } } },
        tooltip: { callbacks: { label: ctx => {
          const a = areas[ctx.dataIndex]; const s = stats.areas[a];
          return `${ctx.dataset.label}: Min=${s.min.toFixed(1)} Q1=${s.q1.toFixed(1)} Med=${s.median.toFixed(1)} Q3=${s.q3.toFixed(1)} Max=${s.max.toFixed(1)}`;
        }}}
      }, responsive: true }
  });

  // Heatmap table
  const bm = stats.branchMatrix;
  const sortedBranches = Object.keys(bm).sort((a, b) => {
    const avgA = areas.reduce((s, ar) => s + (bm[a].areas[ar].length ? bm[a].areas[ar].reduce((x,y)=>x+y,0)/bm[a].areas[ar].length : 0), 0) / areas.length;
    const avgB = areas.reduce((s, ar) => s + (bm[b].areas[ar].length ? bm[b].areas[ar].reduce((x,y)=>x+y,0)/bm[b].areas[ar].length : 0), 0) / areas.length;
    return avgB - avgA;
  });

  let hmHtml = `<tr><th>Branch (Code) [n]</th>${areas.map(a => `<th>${a}</th>`).join('')}<th>Overall</th></tr>`;
  sortedBranches.forEach(bc => {
    const b = bm[bc]; let rowAvgs = [];
    let row = `<td>${b.name} (${bc}) [n=${b.n}]</td>`;
    areas.forEach(a => {
      const vals = b.areas[a];
      const avg = vals.length ? vals.reduce((s,x)=>s+x,0)/vals.length : 0;
      rowAvgs.push(avg);
      const band = scoreBand(avg);
      row += `<td style="background:${band.color}22; color:${band.color}">${avg.toFixed(2)}</td>`;
    });
    const overall = rowAvgs.length ? rowAvgs.reduce((s,x)=>s+x,0)/rowAvgs.length : 0;
    const ob = scoreBand(overall);
    row += `<td style="background:${ob.color}22; color:${ob.color}; font-weight:700">${overall.toFixed(2)}</td>`;
    hmHtml += `<tr>${row}</tr>`;
  });
  document.getElementById(`${lens}-heatmap`).innerHTML = hmHtml;

  // Summary table
  let sumHtml = `<tr><th>Area</th><th>Name</th><th>N</th><th>Mean</th><th>Median</th><th>Std</th><th>%</th><th>Band</th><th>Sub-Areas (Goals)</th><th>Qs</th><th>Wt/Q</th></tr>`;
  areas.forEach(a => {
    const s = stats.areas[a]; const band = scoreBand(s.mean); const m = AREA_META[a];
    sumHtml += `<tr>
      <td><strong>${a}</strong></td><td>${m.name}</td><td>${s.n}</td>
      <td><strong>${s.mean.toFixed(2)}</strong></td><td>${s.median.toFixed(2)}</td><td>${s.std.toFixed(2)}</td>
      <td>${s.pct.toFixed(0)}%</td><td><span class="band band-${band.cls}">${band.label}</span></td>
      <td style="font-size:11px">${m.goals.join(', ')}</td>
      <td>${m.qs}</td><td>${(1/m.qs).toFixed(2)}</td>
    </tr>`;
  });
  document.getElementById(`${lens}-summary`).innerHTML = sumHtml;
}

// ── TAB SWITCHING ──
function switchTab(lens) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelector(`.tab:nth-child(${lens === 'teacher' ? 1 : 2})`).classList.add('active');
  document.getElementById(`tab-${lens}`).classList.add('active');
  renderDashboard(lens);
}

// ── FILE IMPORT ──
function handleFileImport(lens, input) {
  const file = input.files[0]; if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    try {
      const parsed = detectAndParse(e.target.result);
      if (parsed.length) { currentData[lens] = parsed; renderDashboard(lens); alert(`Loaded ${parsed.length} records for ${lens}.`); }
      else alert('No records found in file.');
    } catch (err) { alert('Parse error: ' + err.message); }
  };
  reader.readAsText(file);
}

function handlePasteImport(lens) {
  const text = document.getElementById(`${lens}-paste`).value;
  if (!text.trim()) { alert('Paste CSV or JSON data first.'); return; }
  try {
    const parsed = detectAndParse(text);
    if (parsed.length) { currentData[lens] = parsed; renderDashboard(lens); alert(`Loaded ${parsed.length} records for ${lens}.`); }
    else alert('No records found.');
  } catch (err) { alert('Parse error: ' + err.message); }
}

function resetData(lens) {
  currentData[lens] = lens === 'teacher' ? BUILTIN_TEACHER : BUILTIN_LEADER;
  document.getElementById(`${lens}-file`).value = '';
  document.getElementById(`${lens}-paste`).value = '';
  renderDashboard(lens);
}

// ── STICKY NOTE TOGGLE ──
function toggleNote(trigger) {
  // Find the sibling sticky-note
  let note;
  if (trigger.classList.contains('info-toggle')) {
    note = trigger.nextElementSibling;
  } else {
    // Called from close button — walk up
    note = trigger.closest('.sticky-note');
    if (note) { note.classList.remove('visible'); return; }
  }
  if (!note || !note.classList.contains('sticky-note')) return;
  note.classList.toggle('visible');

  // Close other open notes
  document.querySelectorAll('.sticky-note.visible').forEach(n => {
    if (n !== note) n.classList.remove('visible');
  });
}

// Close notes when clicking outside
document.addEventListener('click', e => {
  if (!e.target.closest('.sticky-note') && !e.target.closest('.info-toggle')) {
    document.querySelectorAll('.sticky-note.visible').forEach(n => n.classList.remove('visible'));
  }
});

// ── INIT ──
document.addEventListener('DOMContentLoaded', () => {
  renderDashboard('teacher');
});
</script>
</body>
</html>
'''

# Inject data
html = html.replace('__TEACHER_DATA__', teacher_data)
html = html.replace('__LEADER_DATA__', leader_data)

out_path = os.path.join(BASE, "output", "baseline_dashboard.html")
with open(out_path, 'w') as f:
    f.write(html)
print(f"Dashboard written to: {out_path}")
print(f"File size: {os.path.getsize(out_path) / 1024:.0f} KB")
