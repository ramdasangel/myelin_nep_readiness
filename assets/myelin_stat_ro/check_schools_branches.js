// Query SchoolBranchClassesView to check schools with branches
// Run on prod: mongosh --port 27017 -u Shridhar -p 'ShriDhar@Myelin' --authenticationDatabase pdea_pilot pdea_pilot < check_schools_branches.js

// Check the structure of SchoolBranchClassesView
print("=== SchoolBranchClassesView Sample Documents ===");
db.SchoolBranchClassesView.find().limit(5).forEach(doc => printjson(doc));

print("\n=== Total Documents in SchoolBranchClassesView ===");
print(db.SchoolBranchClassesView.countDocuments());

print("\n=== Unique Schools in SchoolBranchClassesView ===");
db.SchoolBranchClassesView.aggregate([
  {
    $group: {
      _id: "$School.SchoolID",
      SchoolName: { $first: "$School.SchoolName" },
      BranchCount: { $addToSet: "$_id" }
    }
  },
  {
    $project: {
      _id: 1,
      SchoolName: 1,
      BranchCount: { $size: "$BranchCount" }
    }
  },
  { $sort: { SchoolName: 1 } }
]).forEach(doc => printjson(doc));

print("\n=== Schools with Branches Summary ===");
db.SchoolBranchClassesView.aggregate([
  {
    $group: {
      _id: {
        SchoolID: "$School.SchoolID",
        SchoolName: "$School.SchoolName",
        BranchID: "$BranchID",
        BranchName: "$BranchName"
      },
      ClassCount: { $sum: 1 }
    }
  },
  {
    $group: {
      _id: {
        SchoolID: "$_id.SchoolID",
        SchoolName: "$_id.SchoolName"
      },
      Branches: {
        $push: {
          BranchID: "$_id.BranchID",
          BranchName: "$_id.BranchName",
          ClassCount: "$ClassCount"
        }
      },
      TotalBranches: { $sum: 1 },
      TotalClasses: { $sum: "$ClassCount" }
    }
  },
  { $sort: { "_id.SchoolName": 1 } }
]).forEach(doc => printjson(doc));
