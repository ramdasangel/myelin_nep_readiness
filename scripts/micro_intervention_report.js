// Micro-Intervention Tasks Report Generator
// Generates CSV: UserId, Name, School, Branch, BranchCode, Role, TasksChosenCount, TaskList, DatesLogged

// Build task ID -> task info mapping
const taskMap = {};
db.MicroInterventionTasks.find().sort({_id: 1}).forEach(t => {
  taskMap[t._id.toString()] = {
    prefix: t.task.en.TaskPrefix,
    title: t.task.en.title
  };
});

// Build positional mapping for the duplicate set (697b1e3b series)
const dupIds = [
  "697b1e3bc671c89acb64125a",
  "697b1e3bc671c89acb64125b",
  "697b1e3bc671c89acb64125c",
  "697b1e3bc671c89acb64125d",
  "697b1e3bc671c89acb64125e",
  "697b1e3bc671c89acb64125f",
  "697b1e3bc671c89acb641260",
  "697b1e3bc671c89acb641261",
  "697b1e3bc671c89acb641262",
  "697b1e3bc671c89acb641263",
  "697b1e3bc671c89acb641264",
  "697b1e3bc671c89acb641265"
];
const origIds = Object.keys(taskMap).sort();
dupIds.forEach((dupId, idx) => {
  if (origIds[idx]) {
    taskMap[dupId] = taskMap[origIds[idx]];
  }
});

// Build branch cache
const branchCache = {};
db.SchoolBranches.find({}, {BranchName: 1, School: 1, BranchCode: 1, BranchMedium: 1}).forEach(b => {
  branchCache[b._id.toString()] = {
    branchName: b.BranchName || "",
    schoolName: (b.School && b.School.SchoolName) ? b.School.SchoolName : "",
    branchCode: b.BranchCode || ""
  };
});

// Build user daily progress index: UserTempId -> array of {date, tasks checked}
const progressMap = {};
db.UserDailyProgress.find().forEach(p => {
  const uid = p.UserTempId.toString();
  if (!progressMap[uid]) progressMap[uid] = [];
  const dateStr = p.SubmitDate ? p.SubmitDate.toISOString().split("T")[0] : (p.CreatedAt ? p.CreatedAt.toISOString().split("T")[0] : "");
  progressMap[uid].push(dateStr);
});

// CSV header
print("UserId,FirstName,LastName,FullName,Role,SchoolName,BranchName,BranchCode,TasksChosenCount,TaskList,DatesLogged,TotalDaysLogged");

// Process each UserTaskMapping
db.UserTaskMapping.find().sort({createdAt: 1}).forEach(utm => {
  const userTempId = utm.userTempId.toString();

  // Get user info
  const user = db.UserTemp.findOne({_id: utm.userTempId});
  const firstName = user ? (user.firstName || "") : "Unknown";
  const lastName = user ? (user.lastName || "") : "Unknown";
  const fullName = (firstName + " " + lastName).trim();
  const role = user ? (user.RoleName || "") : "";

  // Get branch info
  let schoolName = "";
  let branchName = "";
  let branchCode = "";
  if (user && user.selectedBranchId) {
    const bInfo = branchCache[user.selectedBranchId.toString()];
    if (bInfo) {
      schoolName = bInfo.schoolName;
      branchName = bInfo.branchName;
      branchCode = bInfo.branchCode;
    }
  }

  // Get selected tasks
  const taskCount = utm.SelectedTasks ? utm.SelectedTasks.length : 0;
  const taskList = utm.SelectedTasks ? utm.SelectedTasks.map(t => {
    const tInfo = taskMap[t.taskId.toString()];
    return tInfo ? (tInfo.prefix + "-" + tInfo.title) : t.taskId.toString();
  }).join(" | ") : "";

  // Get dates logged from UserDailyProgress
  const dates = progressMap[userTempId] || [];
  const uniqueDates = [...new Set(dates)].sort();
  const datesStr = uniqueDates.join(" | ");
  const totalDays = uniqueDates.length;

  // Escape CSV fields
  const esc = (s) => '"' + String(s).replace(/"/g, '""') + '"';

  print([
    esc(userTempId),
    esc(firstName),
    esc(lastName),
    esc(fullName),
    esc(role),
    esc(schoolName),
    esc(branchName),
    esc(branchCode),
    taskCount,
    esc(taskList),
    esc(datesStr),
    totalDays
  ].join(","));
});
