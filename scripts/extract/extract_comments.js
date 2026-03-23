// Extract non-empty comments from UserDailyProgress with metadata
// Output: userId,submitDate,createdAt,taskId,isChecked,comment
// Only emits rows where tp.comment is non-empty

print("userId,submitDate,createdAt,taskId,isChecked,comment");

db.UserDailyProgress.find().sort({SubmitDate: 1}).forEach(p => {
  const uid = p.UserTempId.toString();
  const submitDate = p.SubmitDate ? p.SubmitDate.toISOString().split("T")[0] : "";
  const createdAt = p.CreatedAt ? p.CreatedAt.toISOString() : "";

  if (p.TasksProgress && Array.isArray(p.TasksProgress)) {
    p.TasksProgress.forEach(tp => {
      const comment = tp.comment ? tp.comment.trim() : "";
      if (comment.length === 0) return;

      const taskId = tp.taskId ? tp.taskId.toString() : "";
      const isChecked = tp.isChecked === true ? "true" : "false";

      // CSV-escape: replace newlines/carriage returns, double-quote the field
      const escaped = '"' + comment.replace(/\r?\n/g, " ").replace(/"/g, '""') + '"';

      print(uid + "," + submitDate + "," + createdAt + "," + taskId + "," + isChecked + "," + escaped);
    });
  }
});
