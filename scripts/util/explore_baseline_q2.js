// Get questions via questionIds array in DiagnosticQuestionSet
["base001", "base002", "base003", "base004"].forEach(code => {
  let dqs = db.DiagnosticQuestionSet.findOne({setCode: code});
  if (!dqs) return;
  print("\n========================================");
  print("SET: " + code + " | Name: " + dqs.setName + " | Questions: " + (dqs.questionIds ? dqs.questionIds.length : 0));
  print("========================================");

  if (dqs.questionIds && dqs.questionIds.length > 0) {
    let questions = db.DiagnosticQuestion.find({_id: {$in: dqs.questionIds}}).toArray();
    print("Found in DiagnosticQuestion: " + questions.length);

    if (questions.length > 0) {
      // Show first question with all fields
      print("\n--- First question ALL fields ---");
      printjson(questions[0]);

      // Show all questions summary
      print("\n--- All questions ---");
      questions.forEach((q, i) => {
        let text = q.questionText || q.question || q.text || "";
        if (typeof text === "object") text = JSON.stringify(text);
        let area = q.area || q.areaCode || q.category || q.fpLevel || q.tag || "";
        let sub = q.subArea || q.subCategory || q.depthLevel || q.subTag || "";
        let weight = q.weight || q.points || q.score || "";
        let meta = q.metadata || q.responseMetadata || {};
        print("Q" + (i+1) + " | area=" + area + " | sub=" + sub + " | weight=" + weight + " | meta=" + JSON.stringify(meta) + " | text=" + (typeof text === "string" ? text.substring(0, 80) : JSON.stringify(text).substring(0, 80)));
      });
    }
  }
});

// Also check the DiagnosticAttempt responses to see how responses are stored
print("\n\n========================================");
print("SAMPLE RESPONSE DATA");
print("========================================");
["base001", "base002"].forEach(code => {
  print("\n--- Submitted attempt for " + code + " ---");
  let attempt = db.DiagnosticAttempt.findOne({setCode: code, isSubmitted: true});
  if (attempt && attempt.responses) {
    print("Response count: " + attempt.responses.length);
    // Show first 3 responses
    attempt.responses.slice(0, 3).forEach((r, i) => {
      print("R" + (i+1) + ": " + JSON.stringify(r));
    });
  }
});
