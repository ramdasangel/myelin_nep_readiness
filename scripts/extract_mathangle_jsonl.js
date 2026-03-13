// Extract Mathangle assessment data into 3 JSONL files
// Reads from: OnlineAssesmentStudentResult, DiagnosticQuestion, UserTemp, SchoolBranches, Diagnostic
// Writes to: /tmp/mathangle_raw.jsonl, /tmp/mathangle_exit_levels.jsonl, /tmp/mathangle_indecision.jsonl
//
// Usage:
//   scp scripts/extract_mathangle_jsonl.js ec2-user@13.200.74.24:~/myelin_stat_ro/
//   ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
//     'cd ~/myelin_stat_ro && mongosh --port 27017 -u Shridhar -p "ShriDhar@Myelin" --authenticationDatabase pdea_pilot pdea_pilot < extract_mathangle_jsonl.js'
//   scp -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24:/tmp/mathangle_*.jsonl /tmp/

// ─── Build lookup maps ───

// User info
const userCache = {};
db.UserTemp.find({}, {firstName:1, lastName:1, RoleName:1, selectedBranchId:1}).forEach(u => {
  userCache[u._id.toString()] = {
    firstName: u.firstName || "",
    lastName: u.lastName || "",
    role: u.RoleName || "",
    branchId: u.selectedBranchId ? u.selectedBranchId.toString() : ""
  };
});

// Branch info
const branchCache = {};
db.SchoolBranches.find({}, {BranchName:1, School:1}).forEach(b => {
  branchCache[b._id.toString()] = {
    branchName: b.BranchName || "",
    schoolName: (b.School && b.School.SchoolName) ? b.School.SchoolName : ""
  };
});

// BranchCode from Diagnostic
const branchCodeMap = {};
db.Diagnostic.find({}, {branchId:1, branchCode:1}).forEach(d => {
  if (d.branchId && d.branchCode) {
    branchCodeMap[d.branchId.toString()] = d.branchCode;
  }
});

// Get Mathangle OnlineAssesmentIDs (keep as ObjectId for queries)
const oaIdToBranch = {};
const oaIds = [];
db.Diagnostic.find({setCode: {$in: ["Mathangle (English)", "Mathangle (मराठी)"]}}).forEach(d => {
  if (d.onlineAssesmentID) {
    oaIds.push(d.onlineAssesmentID);
    oaIdToBranch[d.onlineAssesmentID.toString()] = {
      branchId: d.branchId ? d.branchId.toString() : "",
      branchCode: d.branchCode || "",
      setCode: d.setCode,
      lang: d.setCode === "Mathangle (English)" ? "EN" : "MR"
    };
  }
});
print("Mathangle assessments: " + oaIds.length);

// Get OnlineAssesmentQuestions metadata (subtopic, cognitiveLevel, difficultyLevel)
// NOTE: MathAngle questions live in OnlineAssesmentQuestions, NOT DiagnosticQuestion
const questionMeta = {};
db.OnlineAssesmentQuestions.find(
  {OnlineAssesmentID: {$in: oaIds}},
  {Subtopic:1, Topic:1, ChapterName:1, CognitiveLevels:1, Cognitive_Level:1, Question_Level:1, LevelsOfDifficulty:1, Question:1, ActualAnswer:1}
).forEach(q => {
  questionMeta[q._id.toString()] = {
    subtopic: q.Subtopic || q.Topic || "",
    competencyArea: q.ChapterName || "",
    cognitiveLevel: q.CognitiveLevels || q.Cognitive_Level || "",
    difficultyLevel: String(q.Question_Level || q.LevelsOfDifficulty || ""),
    questionText: q.Question || "",
    correctAnswer: q.ActualAnswer != null ? String(q.ActualAnswer) : ""
  };
});
print("Question metadata loaded: " + Object.keys(questionMeta).length + " questions");

// Subtopic → Competency Area mapping
const SUBTOPIC_MAP = {
  "Multiplication": "Multiplication",
  "Currency, openarions on money": "Money",
  "LCM": "Factors & Multiples",
  "LCM, Time measurement": "Factors & Multiples",
  "Divisibility Tests": "Factors & Multiples",
  "Division": "Division",
  "Length measurement": "Measurement",
  "Length measurement, conversion": "Measurement",
  "Addition, Subtraction": "Addition & Subtraction",
  "Minutes, Hours, Seconds measurement": "Time & Calendar",
  "Types of angles and shapes": "Geometry",
  "Measuring angles": "Geometry"
};

// Chapter mapping (for chapterWise grouping in raw.jsonl)
const CHAPTER_MAP = {
  "Addition": "Addition & Subtraction", "बेरीज": "Addition & Subtraction",
  "Multiplication": "Multiplication", "गुणाकार": "Multiplication",
  "Division": "Division", "भागाकार": "Division",
  "Factors & Multiples": "Factors & Multiples", "विभाज्य आणि विभाजक": "Factors & Multiples",
  "Geometry": "Geometry", "भूमिती": "Geometry",
  "Measurement": "Measurement", "मापन": "Measurement",
  "Money": "Money", "पैसे": "Money",
  "Time & Calendar": "Time & Calendar", "वेळ आणि दिनदर्शिका": "Time & Calendar"
};

function mapChapter(ch) {
  return CHAPTER_MAP[ch] || SUBTOPIC_MAP[ch] || ch;
}

// ─── Process results ───

const rawLines = [];
const exitLines = [];
const indecisionLines = [];

let processed = 0;

db.OnlineAssesmentStudentResult.find({
  OnlineAssesmentID: {$in: oaIds},
  SubmitFlag: 1,
  "AssesmentResult.0": {$exists: true}
}).forEach(result => {
  const sid = result.StudentID;
  const user = userCache[sid] || {firstName: "Unknown", lastName: "", role: "", branchId: ""};
  const oaInfo = oaIdToBranch[result.OnlineAssesmentID.toString()] || {lang: "EN", branchCode: ""};
  const branchId = user.branchId || oaInfo.branchId;
  const branchInfo = branchCache[branchId] || {branchName: "", schoolName: ""};
  const branchCode = branchCodeMap[branchId] || oaInfo.branchCode;

  const questions = result.AssesmentResult || [];
  const totalMarks = result.TotalTestMarks || questions.length;
  const obtainedMarks = result.TotalObtainedMarks || 0;

  // Get test name from OnlineAssesment
  const testName = oaInfo.lang === "EN" ? "MathTangle Assessment EN" : "मराठी MathTangle Assessment";

  // ─── RAW JSONL ───
  // chapterWise aggregation
  const chapterAgg = {};
  const cogAgg = {};
  const levelAgg = {};

  questions.forEach(q => {
    const qMeta = questionMeta[q._id.toString()] || {};
    const subtopic = qMeta.subtopic || "";
    const chapter = mapChapter(subtopic);
    const cogLevel = qMeta.cognitiveLevel || "";
    const diffLevel = qMeta.difficultyLevel || "";
    const isCorrect = q.ObtainedMarks > 0;

    // Chapter aggregation
    if (chapter) {
      if (!chapterAgg[chapter]) chapterAgg[chapter] = {right: 0, total: 0};
      chapterAgg[chapter].total++;
      if (isCorrect) chapterAgg[chapter].right++;
    }

    // Cognitive level aggregation
    if (cogLevel) {
      if (!cogAgg[cogLevel]) cogAgg[cogLevel] = {right: 0, total: 0};
      cogAgg[cogLevel].total++;
      if (isCorrect) cogAgg[cogLevel].right++;
    }

    // Difficulty level aggregation
    const lvl = parseInt(diffLevel) || 0;
    if (lvl > 0) {
      if (!levelAgg[lvl]) levelAgg[lvl] = {right: 0, total: 0};
      levelAgg[lvl].total++;
      if (isCorrect) levelAgg[lvl].right++;
    }
  });

  // Format chapterWise
  const chapterWise = Object.entries(chapterAgg).map(([ch, d]) => ({
    chapter: ch, right: d.right, total: d.total
  }));

  // Format cognitiveLevel
  const cogLevels = ["Understand", "Apply", "Analyze", "Evaluate"];
  const cognitiveLevel = cogLevels.map(level => {
    const d = cogAgg[level] || {right: 0, total: 0};
    return {level, right: d.right, total: d.total, pct: d.total > 0 ? Math.round(d.right / d.total * 100) : null};
  });

  // Format questionLevel
  const questionLevel = [1, 2, 3].map(lvl => {
    const d = levelAgg[lvl] || {right: 0, total: 0};
    return {level: lvl, right: d.right, total: d.total};
  });

  // Calculate time
  const totalTime = questions.reduce((sum, q) => sum + (q.TimeTaken || 0), 0);
  const mins = Math.floor(totalTime / 60);
  const secs = totalTime % 60;
  const timeTaken = mins + " mins " + secs + " secs";

  const rawObj = {
    studentId: sid,
    firstName: user.firstName,
    lastName: user.lastName,
    role: user.role,
    branchName: branchInfo.branchName,
    schoolName: branchInfo.schoolName,
    testName: testName,
    totalObtained: obtainedMarks,
    totalMarks: totalMarks,
    percentage: totalMarks > 0 ? Math.round(obtainedMarks / totalMarks * 1000) / 10 : 0,
    timeTaken: timeTaken,
    chapterWise: chapterWise,
    cognitiveLevel: cognitiveLevel,
    questionLevel: questionLevel
  };
  rawLines.push(JSON.stringify(rawObj));

  // ─── EXIT LEVELS JSONL ───
  const topicLevels = {};
  questions.forEach(q => {
    const qMeta = questionMeta[q._id.toString()] || {};
    const subtopic = qMeta.subtopic || "";
    const area = mapChapter(subtopic) || subtopic;
    const lvl = parseInt(qMeta.difficultyLevel) || 0;
    const isCorrect = q.ObtainedMarks > 0;

    if (area && lvl > 0) {
      if (!topicLevels[area]) topicLevels[area] = {};
      if (!topicLevels[area][lvl]) topicLevels[area][lvl] = {right: 0, total: 0};
      topicLevels[area][lvl].total++;
      if (isCorrect) topicLevels[area][lvl].right++;
    }
  });

  const exitObj = {
    studentId: sid,
    name: (user.firstName + " " + user.lastName).trim(),
    role: user.role,
    branch: branchInfo.branchName,
    lang: oaInfo.lang,
    topicLevels: topicLevels
  };
  exitLines.push(JSON.stringify(exitObj));

  // ─── INDECISION JSONL ───
  let totalChanges = 0;
  let totalFlipFlops = 0;
  let changeTime = 0;
  const perQuestion = [];

  questions.forEach(q => {
    const qMeta = questionMeta[q._id.toString()] || {};
    const subtopic = qMeta.subtopic || "";
    const lvl = parseInt(qMeta.difficultyLevel) || 0;
    const isCorrect = q.ObtainedMarks > 0;
    const timeTakenQ = q.TimeTaken || 0;

    // Get selected option text
    const selectedOpts = (q.Options || []).filter(o => o.Check === 1);
    const finalChoice = selectedOpts.length > 0 ? selectedOpts[0].Option : "";
    const correctAnswer = q.ActualAnswer || "";

    // Use userOptionSequence for indecision tracking
    const seq = q.userOptionSequence || [];
    const seqLen = seq.length;
    const firstChoice = seqLen > 0 ? seq[0].optionText : finalChoice;
    const numChanges = Math.max(0, seqLen - 1);

    // Flip-flop: returned to a previously selected option
    let flipFlop = false;
    if (seqLen >= 3) {
      const seen = {};
      for (let si = 0; si < seq.length; si++) {
        const opt = seq[si].optionText;
        if (seen[opt]) { flipFlop = true; break; }
        seen[opt] = true;
      }
    }

    // Deliberation time: time between first and last option change
    let deliberationTime = 0;
    if (seqLen >= 2) {
      const t0 = seq[0].time || 0;
      const tN = seq[seqLen - 1].time || 0;
      deliberationTime = Math.abs(tN - t0);
    }

    // Check if changed away from or to correct answer
    const changedFromCorrect = seqLen >= 2 && firstChoice === correctAnswer && finalChoice !== correctAnswer;
    const changedToCorrect = seqLen >= 2 && firstChoice !== correctAnswer && finalChoice === correctAnswer;

    totalChanges += numChanges;
    if (flipFlop) totalFlipFlops++;
    changeTime += deliberationTime;

    perQuestion.push({
      qId: q._id.toString(),
      subtopic: subtopic,
      qLevel: lvl,
      correct: isCorrect,
      timeTaken: timeTakenQ,
      seqLen: seqLen,
      numChanges: numChanges,
      flipFlop: flipFlop,
      deliberationTime: deliberationTime,
      firstChoice: firstChoice,
      finalChoice: finalChoice,
      correctAnswer: correctAnswer,
      changedFromCorrect: changedFromCorrect,
      changedToCorrect: changedToCorrect
    });
  });

  const indecisionObj = {
    studentId: sid,
    name: (user.firstName + " " + user.lastName).trim(),
    role: user.role,
    branch: branchInfo.branchName,
    lang: oaInfo.lang,
    totalQs: questions.length,
    totalChanges: totalChanges,
    totalFlipFlops: totalFlipFlops,
    totalTime: totalTime,
    changeTime: changeTime,
    perQuestion: perQuestion
  };
  indecisionLines.push(JSON.stringify(indecisionObj));

  processed++;
});

print("Processed " + processed + " student results");

// ─── Write JSONL files ───
// mongosh doesn't have fs module, so we print with markers for extraction
print("JSONL_START_RAW");
rawLines.forEach(line => print(line));
print("JSONL_END_RAW");

print("JSONL_START_EXIT");
exitLines.forEach(line => print(line));
print("JSONL_END_EXIT");

print("JSONL_START_INDECISION");
indecisionLines.forEach(line => print(line));
print("JSONL_END_INDECISION");

print("\nDone! Raw: " + rawLines.length + ", Exit: " + exitLines.length + ", Indecision: " + indecisionLines.length);
