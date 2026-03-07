// Count documents by BranchID for all collections
// Run: mongosh --port 27017 -u Shridhar -p 'ShriDhar@Myelin' --authenticationDatabase pdea_pilot pdea_pilot < count_by_branch.js > branch_counts_output.json

// Step 1: Get all unique Branch IDs from SchoolBranchClassesView
print("=== Extracting Branch IDs from SchoolBranchClassesView ===");

const branchData = db.SchoolBranchClassesView.aggregate([
  {
    $group: {
      _id: "$_id",
      BranchName: { $first: "$BranchName" },
      Location: { $first: "$Location" },
      SchoolName: { $first: "$School.SchoolName" },
      SchoolID: { $first: "$School.SchoolID" }
    }
  },
  { $sort: { SchoolName: 1, BranchName: 1 } }
]).toArray();

print("Total Branches Found: " + branchData.length);
print("\n=== Branch List ===");
branchData.forEach(b => {
  print(JSON.stringify({
    BranchID: b._id,
    BranchName: b.BranchName,
    Location: b.Location,
    SchoolName: b.SchoolName,
    SchoolID: b.SchoolID
  }));
});

const branchIds = branchData.map(b => b._id);

// Collections list from collections_count.csv
const collections = [
  "Attendance", "HomeScreen", "SchoolAppPackageMapping", "SchoolBranchGroup", "ArchiveSylllabusPlanner",
  "ReviewerBatch", "CommTemplatesBackup", "OutcomeActivityMapping", "ArchiveSchoolBranchCalendar", "testDemo",
  "ClassSubjectMapping", "Assessment", "ClassName", "MytriFAQ", "Monthly_Attendance_Report",
  "ArchiveNotificationClassAssignments", "LessonPlanExampleMapping", "InputFormStudentStatus", "StudentUnitTestResult",
  "Outcome", "EvaluationClassMapping", "SyllabusRole", "SchoolCalendarNotificationSent", "StudentAchievements",
  "OnlineAssesmentQuestionsBackup1", "Parent_Engagement_Score", "DiagnosticQuestionSet", "SchoolBranchClasses_MATERIALIZED",
  "PhicommercePaymentAdvice", "MasterChapter", "Goals", "UserTaskMapping", "EventRegistration_backup",
  "AttendanceReportStudentLevel", "SubjectCode", "ConversationSubjectliking", "PeerDuration", "StudentObservation",
  "EvaluationResult", "studentCustomMessageNotice", "QuestionTraceability", "useractivitylogs", "Branchwise_Numbers_facts",
  "TestResult", "AttendanceReportClassLevel", "InputFormFields", "DailyFeedback", "PaymentLink",
  "AssessmentRubricMaster", "ConversationMessages", "ALLusers", "Roles", "CommunicationTemplates",
  "Test", "Exception_Lowest_Classwise_Daywise", "Users", "SchoolMenuList", "SchoolObservationMarathi",
  "Branchwise_Genderwise_Daywise_Attendance", "Parent_Promptness", "StudentActivitySummary_2", "Homework",
  "HPCTermConfiguration", "RoleMenuMapping", "EventRegistration", "ApplicationVersion", "my_oa_backup",
  "LearningCompetency", "MytriSubject", "Token", "Attendance_Analysis", "SchoolObservation",
  "HolidayCalender", "NotificationClassAssignmentsTemp", "MobileAppVersion", "MasterClassCode", "HpcClassSubjectMapping",
  "Monthly_Attendance_Class_Report", "SchoolStatements", "SyllabusSubjectMapping", "SubTopicObjectiveOutcomeMapping",
  "Students_Subject_Level_Score_Copy", "ArchiveClassSubject", "Roles_copy", "MasterCompetency", "NotificationEventsCalendar",
  "ArchiveStudentActivitySummary", "SubjectSubscription", "SyllabusStatus", "AssessmentRubric", "ArchiveStudents",
  "CashFreePayment", "OnlineAssesmentAnalysisStudentLevel_SVJCT", "FAQ", "StudentReport", "ArchiveTeacherClassRoleMapping",
  "Subject", "SyllabusType", "HelpContent", "OnlineAssesmentStudentResult", "UserActivityMapping",
  "ExampleTraceability", "Classwise_Categorywise_Monthwise_Attendance", "Class", "StaffAttendanceDetail",
  "HPCStageSubjectDisplayName", "Monthly_Attendance_Branch_Report", "PAYMENT_SUCCESS_WEBHOOK", "UnitTestRemark",
  "Weekly_Attendance_School_Report", "Classwise_Genderwise_Monthwise_Attendance", "FCM_NotificationOutbox",
  "ArchiveAttendance", "Activity", "Daily_Usage", "MYTemplate", "StudentConfig", "StudentPromotion",
  "Term", "LoggingDetails", "UserFeedback", "PersonalityTraitDrillDownBranch", "DiagnosticAttempt",
  "StudentDetailsByLanguage", "SampleNudge", "DiagnosticQuestion", "Students_Chapter_Level_Score", "TeacherObservation",
  "CopyUnitTestObjects", "foundations", "ActionOptionTypes", "ClassTimeTable", "LearningCompentencyDrillDown1",
  "ConversationMessagesTemp", "ObjectiveOutcomeMapping", "AttendanceReportBranchLevel", "LessonPlanOutcomeMapping",
  "Weekly_Attendance_Class_Report", "CompetencyRemarkMaster", "Peer", "UserGreetings", "BonafideTemplate",
  "BonafideReport", "SubjectLikingDrillDownBranch", "Attendance_Analysis_ClassLevel", "PersonalityTraitDrillDown",
  "HomeworkQuestions", "ArchiveTeacherSubjectMapping", "AssessmentCount", "TeacherClassRoleMapping", "SubscriptionPlans",
  "WebexID", "OutcomeExampleMapping", "MicroInterventionTasks", "SubjectGroup", "AttendanceSummary",
  "SchoolObservationResult", "studentActitvity", "ClassCompilanceAttendance", "ArchiveSyllabusSubjectMapping",
  "UserDailyProgress", "TeacherClassRoleMappingTemp", "Grade", "Favourites", "Question", "ApplicationUserLog",
  "Teacher_Subject_Class_Mapping", "remarksByPercentage", "ArchiveSchool", "UserNote", "follow_up_questions",
  "Students_Subject_Level_Score_Copy1", "SchoolBranchCalendar", "UserContribution", "otp", "Subjects",
  "SystemConfig", "ArchiveNotificationEventsCalendar", "Wordcount_for_Branch", "ConversationMessages_KMSS",
  "ArchiveCommunicationTemplates", "StudentSortingTypes", "SyllabusSubjectDetails", "Promotions",
  "MasterObjectiveOutcomeMapping", "TeacherObservations", "Notification", "NotificationSent", "Summary_Report",
  "CompetencyObjectiveOutcomeTraceability", "StudentCompilanceAttendance", "GetInTouch", "AssignmentTypes",
  "SubjectRemarkMaster", "BoardMediumMapping", "LeavingCertificateReport", "Unit", "WordCloud_For_School",
  "SchoolBusRoutes", "OnlineAssesmentQuestionsBackup2", "FormType", "Greetings", "UserLabelMapping",
  "LessonPlanActivityMapping", "LessonPlanQuestionMapping", "Exception_Highest_Student_Classwise", "RejectedStudents",
  "UnitTestRemark2", "SchoolBranchCalendartemp", "ArchiveSampleNudge", "UsersAPIUsage", "Word_Cloud_Dashboard",
  "Invite", "myAttendace", "ArchiveOnlineAssesmentQuestions", "PaymentDetailsTemp", "FeesWithDiscount",
  "AnalyticsInsights", "SubjectUnitTest", "InputForm", "sentConversationAbsent", "SchoolBus",
  "NotificationEventsCalendarTemp", "SubjectRemarkConfig", "SplashAttachments", "TeacherObservationMarathi",
  "studentCustomMessage", "UsersApplicationVersion", "AppPackageMapping", "Log", "Publication",
  "InputFormStudentDetails", "Activities", "AcademicGradeInsights", "Schools", "TeacherAttendanceConfig",
  "Diagnostic_Excel_Export", "Branchwise_Genderwise_Monthwise_Attendance", "StudentTest", "FeesInstallments",
  "AggrepayPayment", "LearningOutcomes", "ActivityObjectiveOutcomeMapping", "OnlineAssesmentQuestions",
  "UserTemp", "ActionSent", "SchoolBusStudentAttendance", "LessonPlanObjectiveMapping", "RejectedUsers",
  "Medium", "Competency_Activity", "StudentActivity", "SylllabusDetailsQuestionMapping", "ActivityTraceability",
  "SylllabusPlanner", "StageWisePerformanceKeys", "MySurroundings", "UnitTest", "Currency",
  "Exception_Lowest_Classwise_Monthwise", "ClassPromoted", "SubjectNotes", "ArchiveFeesInstallments",
  "StudentAssessmentRubric", "parentfeedbacks", "LessonPlanPredecessorMapping", "OverallObservationMaster",
  "NotificationClassAssignments", "SyllabusSubjectMapping_Temp", "OnlineAssessmentOtp", "StudentActivitySummary",
  "LessonPlan", "HPCRemark", "OTP_Authentication", "CommunicationTemplates_Backup", "AttendanceReason",
  "AccessControlList", "ConversationMessagesWithTime", "testData", "User", "ConversationIntent",
  "NotificationRules", "TeacherAppraisalRemarks", "ObservationTemplate", "CurriculumGoal", "Archive_Students_2024_2025",
  "my_result", "Branchwise_Categorywise_Daywise_Attendance", "DecodingDailyReport", "AttendanceBySlot",
  "AcademicTeacherEvaluation", "FCM_NotificationSent", "LessonPlanNotes", "TeacherRecommander", "ArchiveNotificationSent",
  "ReportTemplate", "CharacterCertificateReport", "QR", "CommunicationTemplates_keys", "SchoolBusDriversAttendants",
  "WorksheetQuestions", "Board", "Recommender_Backfill_Record", "Teacher_Class_Engagement_Score", "MytriRoles",
  "StudentHPCRemark", "NotificationBroadcastLevel", "Objective", "Competency", "FCM_NotificationTopics",
  "Comparative_Analysis_Branchlevel", "Monthly_Attendance_School_Report", "LearningCompentencyDrillDown",
  "TwinExamMapping", "StaffAttendance", "ClassSubject", "OnlineAssesmentStudentResult_SVJCT", "Students",
  "CommunicationTemplates_Backup2", "LessonPlanSuccessorMapping", "StudentEvaluation", "SchoolTimeTable",
  "ArchiveLoggingDetails", "Teacher_Promptness_ClassLevel", "Students_Subject_Level_Score", "ArchiveUsers",
  "OnlineAssesmentAnalysisStudentLevel", "WordCloud_For_Branch", "Gallery", "SucessorCompetencyMapping",
  "ContactUs", "Remark_demo", "HPCStage", "hpcactivityassessmentrubrics", "MobileAppVersionPackageID",
  "SchoolBranchConfig", "ArchiveConversationMessages", "Worksheet", "StageSubjectMapping", "Action",
  "SchoolHouses", "OnlineAssesmentRemark", "OAwithQuestions", "myresult", "Comparative_Analysis_Subject_Classlevel",
  "SubjectLikingDrillDown", "SchoolBranches", "Comparative_Analysis_Classlevel", "QuickNotes", "Subtopic",
  "Menu", "CashFreePaymentLink", "Comparative_Analysis_Subjectlevel", "NotificationCategory", "SchoolBranchClassConfig",
  "EvaluationDetails", "PredecessorCompetencyMapping", "Example", "Domain", "Chapter", "NotificationTemplates",
  "Resource", "Branchwise_Categorywise_Monthwise_Attendance", "SMSTrack", "FCM_NotificationInbox",
  "ExcelRawDataParse", "ArchiveAction", "ClassCode", "Teacher_Promptness_BranchLevel", "TilesMaster",
  "TestQuestions", "SyllabusAssigmentStatus", "StudentReportCardPath", "StudentReportCardS3Path", "Remark",
  "Students_2024_2025", "HpcActivity", "ArchiveEvaluationClassMapping", "TemplateConfig", "LeavingCertificateTemplate",
  "SubjectCompetencyMapping", "Weekly_Attendance_Branch_Report", "MytriContactUs", "SchoolTiles", "MYTemplate2",
  "HPCStudentOverallRemark", "Device", "OutcomeQuestionMapping", "SchoolBuses", "Feedback", "OnlineAssesment",
  "Exception_Lowest_Branchwise_Daywise", "ArchiveOnlineAssesmentStudentResult", "LearningObjective",
  "Teacher_Branch_Engagement_Score", "TeacherSubjectMapping", "InstallmentsUpdate", "UsersDetailsByLanguage",
  "TrackUpdatedData", "PeerFeedback", "MasterSubjectCode", "Exception_Lowest_Branchwise_Monthwise",
  "ArchiveSyllabusSubjectDetails", "StudentBlockHistory", "Diagnostic", "SchoolObservationTemplate",
  "ArchiveStudentUnitTestResult", "Teachers", "Vidyanchal_26122025", "ChapterCompetencyMapping",
  "ConversationBehaviourInsight", "AreaOfImprovementActionPlanMaster", "SchoolBranchClassesView"
];

// Common BranchID field names to check
const branchIdFields = ["BranchID", "branchId", "branchID", "Branch_ID", "branch_id", "_id"];

print("\n\n=== Counting Documents by BranchID for All Collections ===\n");

const results = {};

collections.forEach((collName, idx) => {
  try {
    const coll = db.getCollection(collName);
    const totalCount = coll.countDocuments();

    if (totalCount === 0) {
      results[collName] = { total: 0, hasBranchID: false, byBranch: {} };
      return;
    }

    // Check which BranchID field exists
    const sample = coll.findOne();
    let branchField = null;

    for (const field of branchIdFields) {
      if (sample && sample[field] !== undefined) {
        // For _id field, only use if it's the SchoolBranches collection
        if (field === "_id" && collName === "SchoolBranches") {
          branchField = field;
          break;
        } else if (field !== "_id") {
          branchField = field;
          break;
        }
      }
    }

    if (!branchField) {
      results[collName] = { total: totalCount, hasBranchID: false, byBranch: {} };
      print((idx + 1) + "/" + collections.length + " " + collName + ": " + totalCount + " docs (no BranchID field)");
      return;
    }

    // Aggregate by BranchID
    const pipeline = [
      {
        $group: {
          _id: "$" + branchField,
          count: { $sum: 1 }
        }
      },
      { $sort: { count: -1 } }
    ];

    const branchCounts = coll.aggregate(pipeline).toArray();
    const byBranch = {};
    branchCounts.forEach(bc => {
      if (bc._id) {
        byBranch[bc._id.toString()] = bc.count;
      }
    });

    results[collName] = {
      total: totalCount,
      hasBranchID: true,
      branchField: branchField,
      uniqueBranches: branchCounts.length,
      byBranch: byBranch
    };

    print((idx + 1) + "/" + collections.length + " " + collName + ": " + totalCount + " docs, " + branchCounts.length + " branches (field: " + branchField + ")");

  } catch (e) {
    results[collName] = { error: e.message };
    print((idx + 1) + "/" + collections.length + " " + collName + ": ERROR - " + e.message);
  }
});

print("\n\n=== FINAL RESULTS (JSON) ===\n");
print(JSON.stringify({
  branches: branchData,
  collectionCounts: results
}, null, 2));
