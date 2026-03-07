// Explore DiagnosticAttempt setCodes and structure
let setCodes = db.DiagnosticAttempt.aggregate([
  {$group: {_id: "$setCode", count: {$sum: 1}}},
  {$sort: {_id: 1}}
]).toArray();
print("=== SetCodes in DiagnosticAttempt ===");
setCodes.forEach(s => print(s._id + ": " + s.count + " attempts"));

// Submitted status by setCode
print("\n=== Submitted counts by setCode ===");
let submitted = db.DiagnosticAttempt.aggregate([
  {$match: {isSubmitted: true}},
  {$group: {_id: "$setCode", count: {$sum: 1}}},
  {$sort: {_id: 1}}
]).toArray();
submitted.forEach(s => print(s._id + ": " + s.count + " submitted"));

// Check DiagnosticQuestionSet for setCode -> diagnostic title mapping
print("\n=== DiagnosticQuestionSet entries ===");
db.DiagnosticQuestionSet.find().forEach(dqs => {
  print(JSON.stringify({
    _id: dqs._id.toString(),
    setCode: dqs.setCode,
    title: dqs.title || dqs.diagnosticTitle || dqs.setName || dqs.name,
    diagnosticId: dqs.diagnosticId ? dqs.diagnosticId.toString() : "none"
  }));
});

// Check Diagnostic collection
print("\n=== Diagnostic entries ===");
db.Diagnostic.find().forEach(d => {
  print(JSON.stringify({
    _id: d._id.toString(),
    diagnosticType: d.diagnosticType,
    diagnosticTitle: d.diagnosticTitle,
    branchCode: d.branchCode,
    status: d.status
  }));
});

// Check a submitted attempt with responses
print("\n=== Sample submitted attempt ===");
let sa = db.DiagnosticAttempt.findOne({isSubmitted: true});
if (sa) {
  print("setCode: " + sa.setCode);
  print("userTempId: " + sa.userTempId);
  print("branchId: " + sa.branchId);
  print("responses count: " + (sa.responses ? sa.responses.length : 0));
  print("createdAt: " + sa.createdAt);
}
