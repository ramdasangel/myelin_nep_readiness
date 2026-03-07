// Extract data for ALL SRI constructs from prod
// Construct 1 (Intent) already done. Need: 2-Practice, 3-Capacity, 4-System, 5-Ecosystem

// ============================
// STEP 0: List ALL question sets to see what instruments exist
// ============================
print("=== ALL QUESTION SETS IN PROD ===");
print("JSON_START_ALLSETS");
const allSets = [];
db.DiagnosticQuestionSet.find().forEach(qs => {
  allSets.push({
    setCode: qs.setCode || "",
    setName: qs.setName || qs.title || "",
    questionCount: (qs.questionIds || []).length,
    createdAt: qs.createdAt || ""
  });
});
print(JSON.stringify(allSets));
print("JSON_END_ALLSETS");

// ============================
// STEP 1: Check all Diagnostic types (for Practice Readiness instruments)
// ============================
print("\n=== DIAGNOSTIC TYPES ===");
const diagTypes = {};
db.Diagnostic.find().forEach(d => {
  const t = d.diagnosticType || d.type || "unknown";
  diagTypes[t] = (diagTypes[t] || 0) + 1;
});
Object.keys(diagTypes).sort().forEach(k => {
  print("  " + k + ": " + diagTypes[k]);
});

// ============================
// STEP 2: Extract Stage-2 Baseline data (System Readiness - Construct 4)
// setCodes: base001 (teacher en), base003 (teacher mr), base002 (leader en), base004 (leader mr)
// ============================
const BASELINE_CODES = ["base001", "base002", "base003", "base004"];

// Build lookup maps
const userMap = {};
db.UserTemp.find({}, {firstName:1, lastName:1, RoleName:1, selectedBranchId:1, mobileNo:1}).forEach(u => {
  userMap[u._id.toString()] = {
    firstName: u.firstName || "",
    lastName: u.lastName || "",
    role: u.RoleName || "",
    branchId: u.selectedBranchId ? u.selectedBranchId.toString() : "",
    mobile: u.mobileNo || ""
  };
});

const branchInfoMap = {};
db.SchoolBranches.find({}, {BranchName:1, School:1}).forEach(b => {
  branchInfoMap[b._id.toString()] = {
    branchName: b.BranchName || "",
    schoolName: (b.School && b.School.SchoolName) ? b.School.SchoolName : ""
  };
});

const branchCodeMap = {};
db.Diagnostic.find({}, {branchId:1, branchCode:1}).forEach(d => {
  if (d.branchId && d.branchCode) {
    branchCodeMap[d.branchId.toString()] = d.branchCode;
  }
});

// Get baseline question details
const baselineQIds = [];
BASELINE_CODES.forEach(code => {
  const qs = db.DiagnosticQuestionSet.findOne({setCode: code});
  if (qs && qs.questionIds) {
    qs.questionIds.forEach(qid => baselineQIds.push(qid));
  }
});

print("\n=== BASELINE QUESTIONS (SYSTEM READINESS) ===");
print("JSON_START_BASELINE_Q");
const baselineQuestions = [];
db.DiagnosticQuestion.find({_id: {$in: baselineQIds}}).forEach(q => {
  const opts = (q.options || []).map((o, idx) => ({
    index: idx,
    text: o.text || o.optionText || "",
    fp: o.fp || o.fpLevel || "",
    depth: o.depth || o.depthLevel || ""
  }));
  baselineQuestions.push({
    questionId: q._id.toString(),
    questionText: q.questionText || q.text || "",
    questionType: q.questionType || "",
    goal: (q.metadata && q.metadata.goal) ? q.metadata.goal : "",
    description: (q.metadata && q.metadata.description) ? q.metadata.description : "",
    options: opts
  });
});
print(JSON.stringify(baselineQuestions));
print("JSON_END_BASELINE_Q");

// Get baseline attempts
print("\n=== BASELINE ATTEMPTS ===");
print("JSON_START_BASELINE_A");
const baselineAttempts = [];
db.DiagnosticAttempt.find({
  setCode: {$in: BASELINE_CODES},
  isSubmitted: true
}).forEach(a => {
  const uid = a.userTempId ? a.userTempId.toString() : "";
  const user = userMap[uid] || {};
  const branchId = user.branchId || (a.branchId ? a.branchId.toString() : "");
  const bInfo = branchInfoMap[branchId] || {};
  const branchCode = branchCodeMap[branchId] || "";

  const responses = (a.responses || []).map(r => ({
    questionId: r.questionId ? r.questionId.toString() : "",
    selectedOption: r.selectedOption
  }));

  baselineAttempts.push({
    attemptId: a._id.toString(),
    userId: uid,
    firstName: user.firstName || "",
    lastName: user.lastName || "",
    role: user.role || "",
    branchId: branchId,
    branchName: bInfo.branchName || "",
    schoolName: bInfo.schoolName || "",
    branchCode: branchCode,
    setCode: a.setCode || "",
    submittedAt: a.submittedAt || a.updatedAt || "",
    responseCount: responses.length,
    responses: responses
  });
});
print(JSON.stringify(baselineAttempts));
print("JSON_END_BASELINE_A");

// ============================
// STEP 3: MathTangle / Cognitive Probe data (Capacity Readiness - Construct 3)
// Check for MathTangle diagnostics
// ============================
print("\n=== MATHTANGLE DIAGNOSTICS ===");
const mtDiags = [];
db.Diagnostic.find({diagnosticType: /math/i}).forEach(d => {
  mtDiags.push({
    id: d._id.toString(),
    title: d.diagnosticTitle || d.title || "",
    type: d.diagnosticType || "",
    branchCode: d.branchCode || "",
    branchId: d.branchId ? d.branchId.toString() : ""
  });
});
if (mtDiags.length === 0) {
  // Try broader search
  db.Diagnostic.find({$or: [
    {diagnosticTitle: /math/i},
    {diagnosticTitle: /tangle/i},
    {diagnosticTitle: /cognitive/i},
    {diagnosticType: /cognitive/i}
  ]}).forEach(d => {
    mtDiags.push({
      id: d._id.toString(),
      title: d.diagnosticTitle || d.title || "",
      type: d.diagnosticType || "",
      branchCode: d.branchCode || "",
      branchId: d.branchId ? d.branchId.toString() : ""
    });
  });
}
print("MathTangle/Cognitive diagnostics found: " + mtDiags.length);

// Check for MathTangle question sets
print("\n=== MATHTANGLE QUESTION SETS ===");
const mtSets = [];
db.DiagnosticQuestionSet.find({$or: [
  {setName: /math/i},
  {setName: /tangle/i},
  {setName: /cognitive/i},
  {setCode: /math/i},
  {setCode: /mt/i}
]}).forEach(qs => {
  mtSets.push({
    setCode: qs.setCode || "",
    setName: qs.setName || "",
    questionCount: (qs.questionIds || []).length
  });
});
print(JSON.stringify(mtSets));

// Also check DiagnosticAttempt for any cognitive/mathtangle setCodes
print("\n=== ATTEMPT SETCODES (distinct) ===");
const distinctCodes = db.DiagnosticAttempt.distinct("setCode");
print(JSON.stringify(distinctCodes));

// ============================
// STEP 4: Check for Parent/Student instruments (Ecosystem Readiness - Construct 5)
// ============================
print("\n=== PARENT/STUDENT INSTRUMENTS ===");
const parentSets = [];
db.DiagnosticQuestionSet.find({$or: [
  {setName: /parent/i},
  {setName: /student/i},
  {setName: /ecosystem/i},
  {setName: /पालक/i}
]}).forEach(qs => {
  parentSets.push({
    setCode: qs.setCode || "",
    setName: qs.setName || "",
    questionCount: (qs.questionIds || []).length
  });
});
print("Parent/Student sets found: " + parentSets.length);
if (parentSets.length > 0) print(JSON.stringify(parentSets));

// ============================
// STEP 5: Check for Practice Depth instruments (Practice Readiness - Construct 2)
// ============================
print("\n=== PRACTICE DEPTH INSTRUMENTS ===");
const practiceSets = [];
db.DiagnosticQuestionSet.find({$or: [
  {setName: /practice/i},
  {setName: /depth/i},
  {setName: /classroom/i},
  {setName: /enactment/i},
  {setName: /अभ्यास/i}
]}).forEach(qs => {
  practiceSets.push({
    setCode: qs.setCode || "",
    setName: qs.setName || "",
    questionCount: (qs.questionIds || []).length
  });
});
print("Practice depth sets found: " + practiceSets.length);
if (practiceSets.length > 0) print(JSON.stringify(practiceSets));

// ============================
// STEP 6: Check UserRoles distribution
// ============================
print("\n=== USER ROLE DISTRIBUTION ===");
const roleCounts = {};
db.UserTemp.find({}, {RoleName:1}).forEach(u => {
  const r = u.RoleName || "unknown";
  roleCounts[r] = (roleCounts[r] || 0) + 1;
});
Object.keys(roleCounts).sort().forEach(k => {
  print("  " + k + ": " + roleCounts[k]);
});

// ============================
// SUMMARY
// ============================
print("\n=== FINAL SUMMARY ===");
print("Baseline attempts: " + baselineAttempts.length);
const blByCode = {};
baselineAttempts.forEach(a => {
  blByCode[a.setCode] = (blByCode[a.setCode] || 0) + 1;
});
Object.keys(blByCode).sort().forEach(k => {
  print("  " + k + ": " + blByCode[k]);
});
print("MathTangle diagnostics: " + mtDiags.length);
print("MathTangle sets: " + mtSets.length);
print("Parent/Student sets: " + parentSets.length);
print("Practice depth sets: " + practiceSets.length);
