// Extract Intent Readiness data from prod
// Stage-1 Teacher Readiness: setCodes 1234 (en), 103 (mr)
// Stage-1 Leader Readiness: setCodes 7890 (en), 104 (mr)

const STAGE1_TEACHER = ["1234", "103"];
const STAGE1_LEADER = ["7890", "104"];
const ALL_CODES = STAGE1_TEACHER.concat(STAGE1_LEADER);

// 1. Get question set info
print("=== QUESTION SETS ===");
print("setCode,setName,questionCount,questionIds");
ALL_CODES.forEach(code => {
  const qs = db.DiagnosticQuestionSet.findOne({setCode: code});
  if (qs) {
    const qIds = (qs.questionIds || []).map(id => id.toString());
    print(JSON.stringify({
      setCode: code,
      setName: qs.setName || qs.title || "",
      questionCount: qIds.length,
      questionIds: qIds
    }));
  } else {
    print(JSON.stringify({setCode: code, setName: "NOT FOUND", questionCount: 0, questionIds: []}));
  }
});

// 2. Collect all question IDs across all 4 sets
const allQuestionIds = [];
ALL_CODES.forEach(code => {
  const qs = db.DiagnosticQuestionSet.findOne({setCode: code});
  if (qs && qs.questionIds) {
    qs.questionIds.forEach(qid => allQuestionIds.push(qid));
  }
});

// 3. Get question details
print("\n=== QUESTIONS ===");
print("JSON_START_QUESTIONS");
const questions = [];
db.DiagnosticQuestion.find({_id: {$in: allQuestionIds}}).forEach(q => {
  const opts = (q.options || []).map((o, idx) => ({
    index: idx,
    text: o.text || o.optionText || "",
    fp: o.fp || o.fpLevel || "",
    depth: o.depth || o.depthLevel || ""
  }));
  questions.push({
    questionId: q._id.toString(),
    questionText: q.questionText || q.text || "",
    questionType: q.questionType || "",
    goal: (q.metadata && q.metadata.goal) ? q.metadata.goal : "",
    description: (q.metadata && q.metadata.description) ? q.metadata.description : "",
    options: opts
  });
});
print(JSON.stringify(questions));
print("JSON_END_QUESTIONS");

// 4. Get all submitted attempts for Stage-1 setCodes
print("\n=== ATTEMPTS ===");
print("JSON_START_ATTEMPTS");

// Build user info map
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

// Build branch info map
const branchInfoMap = {};
db.SchoolBranches.find({}, {BranchName:1, School:1}).forEach(b => {
  branchInfoMap[b._id.toString()] = {
    branchName: b.BranchName || "",
    schoolName: (b.School && b.School.SchoolName) ? b.School.SchoolName : ""
  };
});

// Build branchCode map from Diagnostic
const branchCodeMap = {};
db.Diagnostic.find({}, {branchId:1, branchCode:1}).forEach(d => {
  if (d.branchId && d.branchCode) {
    branchCodeMap[d.branchId.toString()] = d.branchCode;
  }
});

// Get attempts
const attempts = [];
db.DiagnosticAttempt.find({
  setCode: {$in: ALL_CODES},
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

  attempts.push({
    attemptId: a._id.toString(),
    userId: uid,
    firstName: user.firstName || "",
    lastName: user.lastName || "",
    role: user.role || "",
    mobile: user.mobile || "",
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

print(JSON.stringify(attempts));
print("JSON_END_ATTEMPTS");

print("\n=== SUMMARY ===");
print("Total question sets: " + ALL_CODES.length);
print("Total questions: " + questions.length);
print("Total submitted attempts: " + attempts.length);

// Count by setCode
const byCodes = {};
attempts.forEach(a => {
  byCodes[a.setCode] = (byCodes[a.setCode] || 0) + 1;
});
Object.keys(byCodes).sort().forEach(k => {
  print("  setCode " + k + ": " + byCodes[k] + " attempts");
});
