// Extract all submitted baseline responses - output as strict JSON
const setCodes = ["base001", "base002", "base003", "base004"];
const STAGE_TEACHER = new Set(["base001", "base003"]);

// Question-to-Area mapping
const areaMap = {};
setCodes.forEach(code => {
  let dqs = db.DiagnosticQuestionSet.findOne({setCode: code});
  if (!dqs || !dqs.questionIds) return;
  db.DiagnosticQuestion.find({_id: {$in: dqs.questionIds}}).forEach(q => {
    let desc = (q.metadata && q.metadata.description) || "";
    let match = desc.match(/^([AB]\d)/);
    areaMap[q._id.toString()] = {
      area: match ? match[1] : "",
      goal: (q.metadata && q.metadata.goal) || ""
    };
  });
});

// Branch info
const branchCache = {};
db.SchoolBranches.find({}, {BranchName: 1, School: 1}).forEach(b => {
  branchCache[b._id.toString()] = {
    bn: b.BranchName || "",
    sn: (b.School && b.School.SchoolName) ? b.School.SchoolName : ""
  };
});
const branchCodeMap = {};
db.Diagnostic.find().forEach(d => {
  if (d.branchId && d.branchCode) branchCodeMap[d.branchId.toString()] = d.branchCode;
});

// User info
const userCache = {};
db.UserTemp.find().forEach(u => {
  userCache[u._id.toString()] = {
    fn: ((u.firstName || "") + " " + (u.lastName || "")).trim(),
    role: u.RoleName || "",
    bid: u.selectedBranchId ? u.selectedBranchId.toString() : ""
  };
});

function optionScore(sel) {
  let idx = parseInt(sel);
  return isNaN(idx) ? 0 : (4 - idx);
}

// Process attempts - output as CSV-like JSON lines for easy parsing
const results = [];
db.DiagnosticAttempt.find({setCode: {$in: setCodes}, isSubmitted: true}).forEach(a => {
  let uid = a.userTempId.toString();
  let u = userCache[uid] || {fn: "Unknown", role: "", bid: ""};
  let bid = u.bid || (a.branchId ? a.branchId.toString() : "");
  let bi = branchCache[bid] || {bn: "", sn: ""};
  let bc = branchCodeMap[bid] || "";
  let isT = STAGE_TEACHER.has(a.setCode);
  let lang = (a.setCode === "base001" || a.setCode === "base002") ? "en" : "mr";

  // Area scores
  let areas = {};
  if (a.responses) {
    a.responses.forEach(r => {
      let qm = r.questionMetadata || {};
      let desc = qm.description || "";
      let match = desc.match(/^([AB]\d)/);
      let ac = match ? match[1] : "";
      if (!ac && r.questionId) {
        let am = areaMap[r.questionId.toString()];
        if (am) ac = am.area;
      }
      if (!ac) return;
      if (!areas[ac]) areas[ac] = {t: 0, c: 0};
      areas[ac].t += optionScore(r.selectedOption);
      areas[ac].c += 1;
    });
  }

  // Build area scores object
  let aObj = {};
  for (let k in areas) {
    aObj[k] = {s: areas[k].t, n: areas[k].c, avg: +(areas[k].t / areas[k].c).toFixed(2), pct: +(areas[k].t / (areas[k].c * 4) * 100).toFixed(1)};
  }

  results.push({
    uid: uid, name: u.fn, role: u.role, lens: isT ? "T" : "L", lang: lang,
    sc: a.setCode, school: bi.sn, branch: bi.bn, bc: bc,
    areas: aObj
  });
});

print(JSON.stringify(results));
