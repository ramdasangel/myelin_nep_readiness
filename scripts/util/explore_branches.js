// Check how branchCode maps to SchoolBranches
// Get some branchIds from DiagnosticAttempt and look them up
let attempts = db.DiagnosticAttempt.find({isSubmitted: true}).limit(5).toArray();
attempts.forEach(a => {
  let branch = db.SchoolBranches.findOne({_id: a.branchId});
  if (branch) {
    print("branchId: " + a.branchId + " -> BranchName: " + branch.BranchName + " | BranchCode: " + (branch.BranchCode || "N/A"));
  }
});

// Check Diagnostic branchCode to see branch code mapping
print("\n=== Unique branchCodes in Diagnostic ===");
let branchCodes = db.Diagnostic.distinct("branchCode");
printjson(branchCodes);

// Check if SchoolBranches have BranchCode field
print("\n=== SchoolBranches with BranchCode field ===");
let withCode = db.SchoolBranches.find({BranchCode: {$exists: true, $ne: null}}).limit(5).toArray();
withCode.forEach(b => {
  print(b._id + " | " + b.BranchName + " | BranchCode: " + b.BranchCode);
});
let withCodeCount = db.SchoolBranches.countDocuments({BranchCode: {$exists: true, $ne: null}});
print("Total with BranchCode: " + withCodeCount);

// Check branchCode in UserTemp
print("\n=== UserTemp branchId -> SchoolBranches check ===");
let users = db.UserTemp.find({selectedBranchId: {$exists: true}}).limit(5).toArray();
users.forEach(u => {
  let branch = db.SchoolBranches.findOne({_id: u.selectedBranchId});
  if (branch) {
    print(u.firstName + " " + u.lastName + " -> " + branch.BranchName + " | School: " + (branch.School ? branch.School.SchoolName : "N/A") + " | BranchCode: " + (branch.BranchCode || "N/A"));
  }
});

// Check all SchoolBranches fields for anything code-like
print("\n=== First branch all keys ===");
let firstBranch = db.SchoolBranches.findOne();
printjson(Object.keys(firstBranch));

// Try to find the branchCode mapping - maybe in Diagnostic collection
print("\n=== Diagnostic branchCode -> branchId mapping ===");
let diags = db.Diagnostic.find().limit(5).toArray();
diags.forEach(d => {
  print("branchCode: " + d.branchCode + " | branchId: " + (d.branchId || "N/A") + " | title: " + d.diagnosticTitle);
});
