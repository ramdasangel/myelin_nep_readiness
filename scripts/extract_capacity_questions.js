// Extract MathTangle/Capacity question definitions from prod MongoDB
// Usage: SCP to prod, run with mongosh, transfer output back
//   scp scripts/extract_capacity_questions.js ec2-user@13.200.74.24:~/myelin_stat_ro/
//   ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
//     'cd ~/myelin_stat_ro && mongosh --port 27017 -u Shridhar -p "ShriDhar@Myelin" --authenticationDatabase pdea_pilot pdea_pilot < extract_capacity_questions.js > capacity_output.txt 2>&1'
//   scp ec2-user@13.200.74.24:~/myelin_stat_ro/capacity_output.txt assets/myelin_stat_ro/

// ============================
// STEP 1: Find MathTangle question set(s)
// ============================
print("=== MATHTANGLE QUESTION SETS ===");
const mtSets = [];
db.DiagnosticQuestionSet.find({$or: [
  {setName: /math/i}, {setName: /tangle/i}, {setName: /cognitive/i},
  {setCode: /math/i}, {setCode: /mt/i}
]}).forEach(qs => {
  mtSets.push({
    setCode: qs.setCode || "",
    setName: qs.setName || "",
    questionIds: (qs.questionIds || []).map(id => id.toString()),
    questionCount: (qs.questionIds || []).length
  });
});
print("Sets found: " + mtSets.length);
print(JSON.stringify(mtSets, null, 2));

// Collect all question IDs from MathTangle sets
const allQIds = [];
mtSets.forEach(s => s.questionIds.forEach(qid => allQIds.push(qid)));

// Also try to find questions from MathTangle attempts if no sets found
if (allQIds.length === 0) {
  print("\nNo MathTangle sets found, checking attempt responses for question IDs...");
  const sampleAttempt = db.DiagnosticAttempt.findOne({diagnosticType: /math/i});
  if (sampleAttempt && sampleAttempt.responses) {
    sampleAttempt.responses.forEach(r => {
      if (r.questionId) allQIds.push(r.questionId.toString());
    });
    print("Found " + allQIds.length + " questions from sample attempt");
  }
}

// ============================
// STEP 2: Extract question definitions
// ============================
print("\n=== MATHTANGLE QUESTIONS ===");
print("JSON_START_CAPACITY_Q");
const questions = [];
if (allQIds.length > 0) {
  db.DiagnosticQuestion.find({_id: {$in: allQIds.map(id => ObjectId(id))}}).forEach(q => {
    const meta = q.metadata || {};
    questions.push({
      questionId: q._id.toString(),
      questionText: q.questionText || q.text || "",
      questionType: q.questionType || "",
      subtopic: meta.subtopic || meta.topic || "",
      competencyArea: meta.competencyArea || meta.competency || "",
      cognitiveLevel: meta.cognitiveLevel || meta.cognitive || "",
      difficultyLevel: meta.difficultyLevel || meta.difficulty || meta.level || "",
      correctAnswer: q.correctAnswer != null ? q.correctAnswer : "",
      optionCount: (q.options || []).length,
      options: (q.options || []).map((o, idx) => ({
        index: idx,
        text: o.text || o.optionText || ""
      }))
    });
  });
}
print(JSON.stringify(questions));
print("JSON_END_CAPACITY_Q");
print("Total questions extracted: " + questions.length);

// ============================
// STEP 3: Branch name → branchCode lookup
// ============================
print("\n=== BRANCH NAME TO CODE MAPPING ===");
print("JSON_START_BRANCH_MAP");

const branchInfoMap = {};
db.SchoolBranches.find({}, {BranchName: 1, School: 1}).forEach(b => {
  branchInfoMap[b._id.toString()] = {
    branchName: b.BranchName || "",
    schoolName: (b.School && b.School.SchoolName) ? b.School.SchoolName : ""
  };
});

const branchCodeMap = {};
db.Diagnostic.find({}, {branchId: 1, branchCode: 1}).forEach(d => {
  if (d.branchId && d.branchCode) {
    const bid = d.branchId.toString();
    const bInfo = branchInfoMap[bid] || {};
    branchCodeMap[bInfo.branchName || bid] = {
      branchCode: d.branchCode,
      branchId: bid,
      branchName: bInfo.branchName || "",
      schoolName: bInfo.schoolName || ""
    };
  }
});

print(JSON.stringify(Object.values(branchCodeMap)));
print("JSON_END_BRANCH_MAP");
print("Branches mapped: " + Object.keys(branchCodeMap).length);

// ============================
// STEP 4: MathTangle attempt stats
// ============================
print("\n=== MATHTANGLE ATTEMPT STATS ===");
const mtAttemptCount = db.DiagnosticAttempt.countDocuments({
  $or: [
    {diagnosticType: /math/i},
    {diagnosticType: /cognitive/i}
  ],
  isSubmitted: true
});
print("Submitted MathTangle attempts: " + mtAttemptCount);
