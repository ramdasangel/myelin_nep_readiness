// Explore Stage-2 Baseline question sets (base001-base004)
// Teacher: base001 (English), base003 (Marathi)
// Leader: base002 (English), base004 (Marathi)

print("=== DiagnosticQuestionSet for baseline ===");
["base001", "base002", "base003", "base004"].forEach(code => {
  let dqs = db.DiagnosticQuestionSet.findOne({setCode: code});
  if (dqs) {
    print("\n--- " + code + ": " + dqs.title + " ---");
    printjson({
      _id: dqs._id.toString(),
      setCode: dqs.setCode,
      title: dqs.title,
      keys: Object.keys(dqs)
    });
  }
});

// Get all questions for base001 (Teacher English)
print("\n\n=== Questions for base001 (Teacher English) ===");
let dqs1 = db.DiagnosticQuestionSet.findOne({setCode: "base001"});
if (dqs1) {
  let questions = db.DiagnosticQuestion.find({questionSetId: dqs1._id}).sort({sequenceNo: 1}).toArray();
  print("Total questions: " + questions.length);
  if (questions.length === 0) {
    // Try alternate field names
    questions = db.DiagnosticQuestion.find({setCode: "base001"}).sort({sequenceNo: 1}).toArray();
    print("By setCode: " + questions.length);
  }
  if (questions.length === 0) {
    questions = db.DiagnosticQuestion.find({diagnosticQuestionSetId: dqs1._id}).toArray();
    print("By diagnosticQuestionSetId: " + questions.length);
  }
  questions.forEach((q, i) => {
    print("\nQ" + (i+1) + ": " + JSON.stringify({
      _id: q._id.toString(),
      questionText: q.questionText || q.question || q.text,
      area: q.area || q.areaCode || q.category || q.fpLevel,
      subArea: q.subArea || q.subCategory || q.depthLevel,
      weight: q.weight || q.points || q.score,
      options: q.options,
      metadata: q.metadata || q.responseMetadata,
      keys: Object.keys(q)
    }));
  });
}

// Get all questions for base002 (Leader English)
print("\n\n=== Questions for base002 (Leader English) ===");
let dqs2 = db.DiagnosticQuestionSet.findOne({setCode: "base002"});
if (dqs2) {
  let questions = db.DiagnosticQuestion.find({questionSetId: dqs2._id}).sort({sequenceNo: 1}).toArray();
  print("Total questions: " + questions.length);
  if (questions.length === 0) {
    questions = db.DiagnosticQuestion.find({setCode: "base002"}).sort({sequenceNo: 1}).toArray();
    print("By setCode: " + questions.length);
  }
  if (questions.length === 0) {
    questions = db.DiagnosticQuestion.find({diagnosticQuestionSetId: dqs2._id}).toArray();
    print("By diagnosticQuestionSetId: " + questions.length);
  }
  questions.forEach((q, i) => {
    print("\nQ" + (i+1) + ": " + JSON.stringify({
      _id: q._id.toString(),
      questionText: q.questionText || q.question || q.text,
      area: q.area || q.areaCode || q.category || q.fpLevel,
      subArea: q.subArea || q.subCategory || q.depthLevel,
      weight: q.weight || q.points || q.score,
      metadata: q.metadata || q.responseMetadata,
      keys: Object.keys(q)
    }));
  });
}
