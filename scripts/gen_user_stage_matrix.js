// Generate user_stage_matrix.csv from production data
// Columns: School---BranchName---BranchCode, FullName, Stage-1-Readiness-of-Teachers,
//          Stage-1-Readiness-of-Leaders, Stage-2-Baseline-of-Teachers,
//          Stage-2-Baseline-of-Leaders, Dev-Test

// Stage definitions by setCode
const STAGE_1_TEACHER = new Set(["1234", "103"]);
const STAGE_1_LEADER = new Set(["7890", "104"]);
const STAGE_2_TEACHER = new Set(["base001", "base003"]);
const STAGE_2_LEADER = new Set(["base002", "base004"]);
const DEV_TEST = new Set(["101", "102", "1000"]);

// 1. Build branchId -> branchCode mapping from Diagnostic collection
const branchCodeMap = {};
db.Diagnostic.find().forEach(d => {
  if (d.branchId && d.branchCode) {
    branchCodeMap[d.branchId.toString()] = d.branchCode;
  }
});

// 2. Build branchId -> {schoolName, branchName} from SchoolBranches
const branchInfoMap = {};
db.SchoolBranches.find({}, {BranchName: 1, School: 1}).forEach(b => {
  branchInfoMap[b._id.toString()] = {
    branchName: b.BranchName || "",
    schoolName: (b.School && b.School.SchoolName) ? b.School.SchoolName : ""
  };
});

// 3. Build userTempId -> user info from UserTemp
const userMap = {};
db.UserTemp.find().forEach(u => {
  userMap[u._id.toString()] = {
    firstName: u.firstName || "",
    lastName: u.lastName || "",
    fullName: ((u.firstName || "") + " " + (u.lastName || "")).trim(),
    role: u.RoleName || "",
    branchId: u.selectedBranchId ? u.selectedBranchId.toString() : ""
  };
});

// 4. Process all submitted DiagnosticAttempts - build per-user stage completion
const userStages = {};
db.DiagnosticAttempt.find({isSubmitted: true}).forEach(a => {
  const uid = a.userTempId.toString();
  const setCode = a.setCode;
  const branchId = a.branchId ? a.branchId.toString() : "";

  if (!userStages[uid]) {
    userStages[uid] = {
      branchId: branchId,
      stage1Teacher: false,
      stage1Leader: false,
      stage2Teacher: false,
      stage2Leader: false,
      devTest: false
    };
  }

  // Update branchId if not set
  if (!userStages[uid].branchId && branchId) {
    userStages[uid].branchId = branchId;
  }

  if (STAGE_1_TEACHER.has(setCode)) userStages[uid].stage1Teacher = true;
  if (STAGE_1_LEADER.has(setCode)) userStages[uid].stage1Leader = true;
  if (STAGE_2_TEACHER.has(setCode)) userStages[uid].stage2Teacher = true;
  if (STAGE_2_LEADER.has(setCode)) userStages[uid].stage2Leader = true;
  if (DEV_TEST.has(setCode)) userStages[uid].devTest = true;
});

// 5. Build output rows
const rows = [];
for (const uid in userStages) {
  const stages = userStages[uid];
  const user = userMap[uid];
  const fullName = user ? user.fullName : "Unknown";

  // Get branch info
  const branchId = (user && user.branchId) ? user.branchId : stages.branchId;
  const bInfo = branchId ? branchInfoMap[branchId] : null;
  const schoolName = bInfo ? bInfo.schoolName : "";
  const branchName = bInfo ? bInfo.branchName : "";
  const branchCode = branchId ? (branchCodeMap[branchId] || "") : "";

  const schoolBranchKey = schoolName + "---" + branchName + "---" + branchCode;

  rows.push({
    key: schoolBranchKey,
    fullName: fullName,
    stage1Teacher: stages.stage1Teacher ? "Yes" : "No",
    stage1Leader: stages.stage1Leader ? "Yes" : "No",
    stage2Teacher: stages.stage2Teacher ? "Yes" : "No",
    stage2Leader: stages.stage2Leader ? "Yes" : "No",
    devTest: stages.devTest ? "Yes" : "No"
  });
}

// 6. Sort by school---branch---code, then by fullName
rows.sort((a, b) => {
  if (a.key !== b.key) return a.key.localeCompare(b.key);
  return a.fullName.localeCompare(b.fullName);
});

// 7. Print CSV
print("School---BranchName---BranchCode,FullName,Stage-1-Readiness-of-Teachers,Stage-1-Readiness-of-Leaders,Stage-2-Baseline-of-Teachers,Stage-2-Baseline-of-Leaders,Dev-Test");
rows.forEach(r => {
  const esc = (s) => {
    if (s.includes(",") || s.includes('"')) return '"' + s.replace(/"/g, '""') + '"';
    return s;
  };
  print([esc(r.key), esc(r.fullName), r.stage1Teacher, r.stage1Leader, r.stage2Teacher, r.stage2Leader, r.devTest].join(","));
});
