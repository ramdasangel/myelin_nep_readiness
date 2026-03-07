// Extract all submitted baseline responses (base001-base004) with user + branch info
// Output: JSON array of user records with area scores

// --- Question-to-Area mapping ---
// Build from DiagnosticQuestionSet questionIds + DiagnosticQuestion metadata
const areaMap = {}; // questionId -> { area: "A1", goal: "Access", description: "..." }

["base001", "base002", "base003", "base004"].forEach(code => {
  let dqs = db.DiagnosticQuestionSet.findOne({setCode: code});
  if (!dqs || !dqs.questionIds) return;
  let questions = db.DiagnosticQuestion.find({_id: {$in: dqs.questionIds}}).toArray();
  questions.forEach(q => {
    let desc = (q.metadata && q.metadata.description) || "";
    // Extract area code: "A1. Continuous..." -> "A1" or "B1. NEP..." -> "B1"
    let areaCode = "";
    let match = desc.match(/^([AB]\d)/);
    if (match) areaCode = match[1];
    areaMap[q._id.toString()] = {
      area: areaCode,
      goal: (q.metadata && q.metadata.goal) || "",
      description: desc,
      questionText: q.questionText || "",
      setCode: code,
      tags: q.tags || []
    };
  });
});

// --- Branch info cache ---
const branchCache = {};
db.SchoolBranches.find({}, {BranchName: 1, School: 1}).forEach(b => {
  branchCache[b._id.toString()] = {
    branchName: b.BranchName || "",
    schoolName: (b.School && b.School.SchoolName) ? b.School.SchoolName : ""
  };
});

// --- BranchCode from Diagnostic ---
const branchCodeMap = {};
db.Diagnostic.find().forEach(d => {
  if (d.branchId && d.branchCode) {
    branchCodeMap[d.branchId.toString()] = d.branchCode;
  }
});

// --- User info cache ---
const userCache = {};
db.UserTemp.find().forEach(u => {
  userCache[u._id.toString()] = {
    firstName: u.firstName || "",
    lastName: u.lastName || "",
    fullName: ((u.firstName || "") + " " + (u.lastName || "")).trim(),
    role: u.RoleName || "",
    branchId: u.selectedBranchId ? u.selectedBranchId.toString() : ""
  };
});

// --- Scoring: selectedOption index -> score ---
// 0=Strongly Agree=4, 1=Agree=3, 2=Disagree=2, 3=Strongly Disagree=1
function optionScore(sel) {
  let idx = parseInt(sel);
  if (isNaN(idx)) return 0;
  return 4 - idx; // 0->4, 1->3, 2->2, 3->1
}

// --- Process all submitted attempts ---
const results = [];
const setCodes = ["base001", "base002", "base003", "base004"];

db.DiagnosticAttempt.find({setCode: {$in: setCodes}, isSubmitted: true}).forEach(attempt => {
  let uid = attempt.userTempId.toString();
  let user = userCache[uid] || {firstName: "Unknown", lastName: "Unknown", fullName: "Unknown", role: "", branchId: ""};
  let branchId = user.branchId || (attempt.branchId ? attempt.branchId.toString() : "");
  let bInfo = branchCache[branchId] || {branchName: "", schoolName: ""};
  let branchCode = branchCodeMap[branchId] || "";

  // Determine lens type
  let isTeacher = (attempt.setCode === "base001" || attempt.setCode === "base003");
  let lens = isTeacher ? "Teacher" : "Leader";
  let lang = (attempt.setCode === "base001" || attempt.setCode === "base002") ? "English" : "Marathi";

  // Process responses into area scores
  let areaScores = {};    // area -> {total, count, questions: [{goal, score, text}]}
  let responseDetails = [];

  if (attempt.responses && attempt.responses.length > 0) {
    attempt.responses.forEach(r => {
      let qId = r.questionId ? r.questionId.toString() : "";
      let qMeta = r.questionMetadata || {};
      let desc = qMeta.description || "";
      let goal = qMeta.goal || "";

      // Extract area code from response metadata
      let areaCode = "";
      let match = desc.match(/^([AB]\d)/);
      if (match) areaCode = match[1];

      // Fallback to areaMap
      if (!areaCode && areaMap[qId]) areaCode = areaMap[qId].area;

      let score = optionScore(r.selectedOption);
      let qText = r.questionText || "";

      if (!areaScores[areaCode]) {
        areaScores[areaCode] = {total: 0, count: 0, maxPossible: 0, description: desc, questions: []};
      }
      areaScores[areaCode].total += score;
      areaScores[areaCode].count += 1;
      areaScores[areaCode].maxPossible += 4;
      areaScores[areaCode].questions.push({goal: goal, score: score, questionText: qText.substring(0, 100)});

      responseDetails.push({
        questionId: qId,
        area: areaCode,
        goal: goal,
        selectedOption: r.selectedOption,
        score: score
      });
    });
  }

  // Compute area averages and percentages
  let areaSummary = {};
  for (let area in areaScores) {
    let s = areaScores[area];
    areaSummary[area] = {
      totalScore: s.total,
      questionCount: s.count,
      maxPossible: s.maxPossible,
      avgScore: s.count > 0 ? +(s.total / s.count).toFixed(2) : 0,
      percentage: s.maxPossible > 0 ? +(s.total / s.maxPossible * 100).toFixed(1) : 0,
      description: s.description,
      questions: s.questions
    };
  }

  results.push({
    userId: uid,
    fullName: user.fullName,
    role: user.role,
    lens: lens,
    language: lang,
    setCode: attempt.setCode,
    schoolName: bInfo.schoolName,
    branchName: bInfo.branchName,
    branchCode: branchCode,
    branchId: branchId,
    submittedAt: attempt.updatedAt ? attempt.updatedAt.toISOString() : "",
    totalResponses: attempt.responses ? attempt.responses.length : 0,
    areaSummary: areaSummary,
    responseDetails: responseDetails
  });
});

// Output as JSON
printjson(results);
