// Extract SRI System Readiness Audit data (setCode: SRI001)
// Run on prod:
//   ssh -i $SSH_KEY $PROD_USER@$PROD_HOST \
//     'cd ~/myelin_stat_ro && mongosh --port 27017 -u $MONGO_USER -p $MONGO_PASS \
//      --authenticationDatabase pdea_pilot pdea_pilot < extract_sri_audit.js > sri_audit_output.txt 2>&1'

const SET_CODE = "SRI001";

// 1. Get question set and questions
const qset = db.DiagnosticQuestionSet.findOne({ setCode: SET_CODE });
if (!qset) { print("ERROR: No question set found for " + SET_CODE); quit(); }

print("SET_CODE: " + SET_CODE);
print("SET_NAME: " + qset.setName);
print("QUESTION_COUNT: " + qset.questionIds.length);
print("");

// Load questions
const questions = [];
qset.questionIds.forEach(function(qid) {
  const q = db.DiagnosticQuestion.findOne({ _id: qid });
  if (q) {
    questions.push({
      _id: q._id.toString(),
      questionText: q.questionText || q.question || "",
      goal: (q.metadata && q.metadata.goal) || "",
      description: (q.metadata && q.metadata.description) || "",
      options: (q.options || []).map(function(o) { return o.text || o.optionText || ""; })
    });
  }
});

print("=== QUESTIONS ===");
print(JSON.stringify(questions));
print("");

// 2. Get all submitted attempts
const attempts = db.DiagnosticAttempt.find({
  setCode: SET_CODE,
  isSubmitted: true
}).toArray();

print("SUBMITTED_ATTEMPTS: " + attempts.length);
print("");

// 3. Resolve users and branches for each attempt
const branchCache = {};
const userCache = {};

function resolveBranch(branchId) {
  const key = branchId.toString();
  if (branchCache[key]) return branchCache[key];
  const branch = db.SchoolBranches.findOne({ _id: branchId });
  if (branch) {
    // Get branchCode from Diagnostic collection
    const diag = db.Diagnostic.findOne({ branchId: branchId, branchCode: { $regex: /^M\d+$/ } });
    branchCache[key] = {
      branchName: branch.BranchName || "",
      schoolName: (branch.School && branch.School.SchoolName) || "",
      branchCode: diag ? diag.branchCode : ""
    };
  } else {
    branchCache[key] = { branchName: "", schoolName: "", branchCode: "" };
  }
  return branchCache[key];
}

function resolveUser(userTempId) {
  const key = userTempId.toString();
  if (userCache[key]) return userCache[key];
  const user = db.UserTemp.findOne({ _id: userTempId });
  if (user) {
    const branch = user.selectedBranchId ? resolveBranch(user.selectedBranchId) : {};
    userCache[key] = {
      firstName: user.firstName || "",
      lastName: user.lastName || "",
      role: user.RoleName || "",
      branchId: user.selectedBranchId ? user.selectedBranchId.toString() : "",
      branchName: branch.branchName || "",
      schoolName: branch.schoolName || "",
      branchCode: branch.branchCode || ""
    };
  } else {
    userCache[key] = { firstName: "", lastName: "", role: "", branchId: "", branchName: "", schoolName: "", branchCode: "" };
  }
  return userCache[key];
}

// 4. Output attempt data as JSONL
print("=== ATTEMPTS ===");
attempts.forEach(function(att) {
  const user = resolveUser(att.userTempId);
  const responses = (att.responses || []).map(function(r) {
    return {
      questionId: r.questionId ? r.questionId.toString() : "",
      selectedOption: r.selectedOption
    };
  });

  const record = {
    attemptId: att._id.toString(),
    userTempId: att.userTempId.toString(),
    firstName: user.firstName,
    lastName: user.lastName,
    role: user.role,
    branchCode: user.branchCode,
    branchName: user.branchName,
    schoolName: user.schoolName,
    setCode: att.setCode,
    isSubmitted: att.isSubmitted,
    startTime: att.startTime,
    endTime: att.endTime,
    updatedAt: att.updatedAt,
    responses: responses
  };

  print(JSON.stringify(record));
});

print("");
print("=== DONE ===");
