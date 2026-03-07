// Extract full UserDailyProgress with task-level detail
// Output: userId,submitDate,taskId,isChecked,hasComment
// Each row = one task entry within one daily log

print("userId,submitDate,progressCreatedAt,taskId,isChecked,hasComment");

db.UserDailyProgress.find().sort({SubmitDate: 1}).forEach(p => {
  const uid = p.UserTempId.toString();
  const submitDate = p.SubmitDate ? p.SubmitDate.toISOString().split("T")[0] : "";
  const createdAt = p.CreatedAt ? p.CreatedAt.toISOString() : "";

  if (p.TasksProgress && Array.isArray(p.TasksProgress)) {
    p.TasksProgress.forEach(tp => {
      const taskId = tp.taskId ? tp.taskId.toString() : "";
      const isChecked = tp.isChecked === true ? "true" : "false";
      const hasComment = (tp.comment && tp.comment.trim().length > 0) ? "true" : "false";
      print(uid + "," + submitDate + "," + createdAt + "," + taskId + "," + isChecked + "," + hasComment);
    });
  }
});
