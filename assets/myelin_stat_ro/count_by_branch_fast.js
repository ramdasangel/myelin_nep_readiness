// Fast aggregation-based count by BranchID
// Run: mongosh --port 27017 -u Shridhar -p 'ShriDhar@Myelin' --authenticationDatabase pdea_pilot pdea_pilot < count_by_branch_fast.js

// Get branch info
var branches = db.SchoolBranches.find({}, {_id: 1, BranchName: 1, Location: 1, "School.SchoolName": 1}).toArray();
print("Total Branches: " + branches.length);

// Collections that have BranchID field (from previous analysis)
var collectionsWithBranchID = [
  "Attendance", "Students", "Teachers", "ConversationMessages", "NotificationEventsCalendar",
  "StudentUnitTestResult", "Parent_Promptness", "SyllabusSubjectMapping", "ClassTimeTable",
  "StudentCompilanceAttendance", "OnlineAssesmentAnalysisStudentLevel", "OAwithQuestions",
  "StaffAttendance", "SchoolBranchCalendar", "UsersApplicationVersion", "SampleNudge",
  "ClassCompilanceAttendance", "TeacherRecommander", "Gallery", "SchoolTiles",
  "CommunicationTemplates_Backup", "SubjectUnitTest", "NotificationClassAssignments",
  "Attendance_Analysis_ClassLevel", "Teacher_Branch_Engagement_Score", "Teacher_Class_Engagement_Score",
  "AttendanceBySlot", "ConversationIntent", "ConversationMessagesWithTime", "SyllabusStatus",
  "ArchiveSampleNudge", "OnlineAssesment", "UnitTestRemark", "SchoolBranchConfig",
  "StudentPromotion", "PersonalityTraitDrillDown", "TeacherObservations", "UnitTest",
  "SchoolBranchClassesView", "HomeScreen", "SchoolBranchGroup"
];

print("\nCSV Output:");
print("BranchID,BranchName,Location,SchoolName," + collectionsWithBranchID.slice(0,15).join(","));

// Use aggregation per collection - much faster
var collectionCounts = {};
collectionsWithBranchID.slice(0,15).forEach(collName => {
  try {
    var counts = db.getCollection(collName).aggregate([
      { $group: { _id: "$BranchID", count: { $sum: 1 } } }
    ]).toArray();
    collectionCounts[collName] = {};
    counts.forEach(c => {
      if (c._id) collectionCounts[collName][c._id.toString()] = c.count;
    });
  } catch(e) {
    collectionCounts[collName] = {};
  }
});

// Output CSV
branches.forEach(b => {
  var bid = b._id.toString();
  var row = [
    bid,
    '"' + (b.BranchName || "").replace(/"/g, '""') + '"',
    '"' + (b.Location || "").replace(/"/g, '""') + '"',
    '"' + (b.School && b.School.SchoolName ? b.School.SchoolName.replace(/"/g, '""') : "") + '"'
  ];

  collectionsWithBranchID.slice(0,15).forEach(collName => {
    row.push(collectionCounts[collName][bid] || 0);
  });

  print(row.join(","));
});
