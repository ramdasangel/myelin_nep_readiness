# Project Kshitij — Dashboard API & Database Query Specification

**Project:** क्षितिज (Kshitij) — NEP-2020 Readiness Index
**Prepared For:** Backend API Team
**Version:** 1.0
**Date:** 2026-02-16
**Scope:** APIs required to serve two dashboards — Task Mapping Dashboard & Daily Progress Dashboard

---

## Table of Contents

1. [Overview](#1-overview)
2. [MongoDB Collections & Schemas](#2-mongodb-collections--schemas)
3. [Static Reference Data](#3-static-reference-data)
4. [Dashboard 1 — Task Mapping](#4-dashboard-1--task-mapping)
5. [Dashboard 2 — Daily Progress](#5-dashboard-2--daily-progress)
6. [API Endpoint Specifications](#6-api-endpoint-specifications)
7. [Aggregation Pipeline Reference](#7-aggregation-pipeline-reference)
8. [Computed Metric Formulas](#8-computed-metric-formulas)
9. [Filter & Sort Requirements](#9-filter--sort-requirements)
10. [Data Volume & Performance Notes](#10-data-volume--performance-notes)

---

## 1. Overview

Both dashboards visualise data from the **Micro-Intervention** pipeline of Project Kshitij:

```
MicroInterventionTasks (12 tasks)
        │
        ▼
UserTaskMapping (user selects 3-5 tasks)
        │
        ▼
UserDailyProgress (daily check-in logs over 21-day period)
```

**Dashboard 1 (Task Mapping)** shows task selection patterns — who chose what, FP coverage, depth intent, enrollment timeline.

**Dashboard 2 (Daily Progress)** adds logging behaviour — completion rates, consistency, daily activity, FP-level engagement, and per-task mapped-vs-logged breakdowns.

**Scope:** Only users belonging to **Deccan Education Society** schools. Filter out records where `SchoolName` is blank, "Unknown", or "Myelin Model School".

---

## 2. MongoDB Collections & Schemas

### 2.1 UserTemp

Stores user profiles. This is the user identity collection for the Kshitij pilot.

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | Primary key |
| `firstName` | String | User first name |
| `lastName` | String | User last name |
| `RoleName` | String | "Teacher" or "Leader" |
| `selectedBranchId` | ObjectId | FK → SchoolBranches._id |
| `mobile` | String | Phone number |
| `email` | String | Email address |

**Query note:** Use `selectedBranchId` to join to SchoolBranches.

### 2.2 SchoolBranches

Branch-level school information. Note: `BranchCode` field is **not reliably present** in this collection — derive from `Diagnostic` collection if needed.

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | Primary key |
| `BranchName` | String | Branch display name |
| `School` | Object | Embedded object |
| `School.SchoolName` | String | Parent school/society name |
| `School.SchoolCode` | String | School code |
| `BranchCode` | String | May be empty — not reliable |
| `BranchMedium` | String | Medium of instruction |
| `IsActive` | Boolean | Active flag |

**Filter rule:** Only include branches where `School.SchoolName === "Deccan Education Society"`.

### 2.3 MicroInterventionTasks

The 12 micro-intervention task definitions. Two ObjectId series exist (original + duplicate); both map positionally to T01–T12.

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | Primary key |
| `task.en.TaskPrefix` | String | Task code, e.g., "T01" |
| `task.en.title` | String | Task title in English |
| `task.mr.title` | String | Task title in Marathi |
| `category` | String | Task category |
| `isActive` | Boolean | Active flag |

**Two ID series (both valid, map positionally T01→T12):**

| Original (`697b1e2c` series) | Duplicate (`697b1e3b` series) | Task Code |
|------------------------------|-------------------------------|-----------|
| `697b1e2cc01f188423ea7e0f` | `697b1e3bc671c89acb64125a` | T01 |
| `697b1e2cc01f188423ea7e10` | `697b1e3bc671c89acb64125b` | T02 |
| `697b1e2cc01f188423ea7e11` | `697b1e3bc671c89acb64125c` | T03 |
| `697b1e2cc01f188423ea7e12` | `697b1e3bc671c89acb64125d` | T04 |
| `697b1e2cc01f188423ea7e13` | `697b1e3bc671c89acb64125e` | T05 |
| `697b1e2cc01f188423ea7e14` | `697b1e3bc671c89acb64125f` | T06 |
| `697b1e2cc01f188423ea7e15` | `697b1e3bc671c89acb641260` | T07 |
| `697b1e2cc01f188423ea7e16` | `697b1e3bc671c89acb641261` | T08 |
| `697b1e2cc01f188423ea7e17` | `697b1e3bc671c89acb641262` | T09 |
| `697b1e2cc01f188423ea7e18` | `697b1e3bc671c89acb641263` | T10 |
| `697b1e2cc01f188423ea7e19` | `697b1e3bc671c89acb641264` | T11 |
| `697b1e2cc01f188423ea7e1a` | `697b1e3bc671c89acb641265` | T12 |

### 2.4 UserTaskMapping

One document per user — contains the array of tasks the user selected.

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | Primary key |
| `userTempId` | ObjectId | FK → UserTemp._id |
| `SelectedTasks` | Array | Array of selected task objects |
| `SelectedTasks[].taskId` | ObjectId | FK → MicroInterventionTasks._id |
| `createdAt` | Date | When the user made their selection |

**Note:** Each `SelectedTasks[]` entry contains a `taskId` that maps to one of the two ObjectId series above. Use the positional mapping to resolve to T01–T12.

### 2.5 UserDailyProgress

One document per user per day. Contains an array of task-level progress entries.

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | Primary key |
| `UserTempId` | ObjectId | FK → UserTemp._id |
| `SubmitDate` | Date | The date of the log submission |
| `CreatedAt` | Date | Server timestamp of creation |
| `TasksProgress` | Array | Array of per-task progress entries |
| `TasksProgress[].taskId` | ObjectId | FK → MicroInterventionTasks._id |
| `TasksProgress[].isChecked` | Boolean | Whether the user marked the task as done |
| `TasksProgress[].comment` | String | Optional free-text comment |

### 2.6 Diagnostic (for BranchCode derivation)

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | Primary key |
| `branchCode` | String | Branch code (M001–M038) |
| `branchId` | ObjectId | FK → SchoolBranches._id |

**Usage:** Join `Diagnostic.branchId → SchoolBranches._id` to get the branchCode for a given branch, since `SchoolBranches.BranchCode` is unreliable.

---

## 3. Static Reference Data

The following mappings are **static** and can be hardcoded or served from a config endpoint.

### 3.1 Task → FP → Depth Mapping

| Task Code | Task Title | Foundational Principle | Depth Intent | Category |
|-----------|-----------|----------------------|-------------|----------|
| T01 | Notice One Learner | FP-1: Every Child is Unique | D1→D2 | Entry |
| T02 | One Adjustment | FP-1: Every Child is Unique | D2→D3 | Growth |
| T03 | Change One Example | FP-2: Holistic & Experiential | D1→D2 | Entry |
| T04 | Ask a Why/How | FP-2: Holistic & Experiential | D2→D3 | Growth |
| T05 | End-of-Class Reflection | FP-3: Reflective Practitioner | D1→D2 | Entry |
| T06 | Try One Small Change | FP-3: Reflective Practitioner | D2→D3 | Growth |
| T07 | Quick Check | FP-4: Assessment for Learning | D1→D2 | Entry |
| T08 | Spot One Pattern | FP-4: Assessment for Learning | D2→D3 | Growth |
| T09 | Teacher Touchpoint | FP-5: Collaboration | D1→D2 | Entry |
| T10 | Parent Signal | FP-5: Collaboration | D1→D2 | Entry |
| T11 | Student Voice | FP-1: Every Child is Unique | Cross-FP | Cross |
| T12 | Pause & Name | FP-4: Assessment for Learning | Cross-FP | Cross |

### 3.2 Foundational Principles

| Code | Full Name |
|------|-----------|
| FP-1 | Every Child is Unique |
| FP-2 | Holistic & Experiential Learning |
| FP-3 | Reflective Practitioner |
| FP-4 | Assessment for Learning |
| FP-5 | Collaboration & Community |

---

## 4. Dashboard 1 — Task Mapping

### 4.1 KPI Cards (6 metrics)

| KPI | Definition | Data Source |
|-----|-----------|-------------|
| Total Users Enrolled | Count of DES users with a UserTaskMapping record | `UserTaskMapping` + `UserTemp` + `SchoolBranches` |
| Users Who Logged ≥1 Day | Users with at least one `UserDailyProgress` document | `UserDailyProgress` |
| Avg Tasks / User | Mean of `SelectedTasks.length` across all DES users | `UserTaskMapping` |
| Teachers | Count where `UserTemp.RoleName = "Teacher"` | `UserTemp` |
| Leaders | Count where `UserTemp.RoleName = "Leader"` | `UserTemp` |
| Zero Logs | Users with no `UserDailyProgress` records | `UserDailyProgress` |

### 4.2 Charts (7 visualisations)

| # | Chart | Type | X-Axis | Y-Axis | Data Needed |
|---|-------|------|--------|--------|-------------|
| 1 | Task Adoption — Users per Task | Vertical Bar | T01–T12 (label) | User count | Count of users who selected each task |
| 2 | FP Coverage — Selections by FP | Vertical Bar | FP-1 to FP-5 | Selection count | Sum of task selections grouped by FP |
| 3 | Depth Intent Distribution | Doughnut | — | — | Count of selections by depth category (D1→D2, D2→D3, Cross-FP) |
| 4 | Tasks Chosen per User — Distribution | Vertical Bar | Task count (1,2,3,4,5) | User count | Histogram of `SelectedTasks.length` |
| 5 | Role Distribution | Pie | — | — | Count by `RoleName` |
| 6 | FP Coverage — Radar | Radar | FP-1 to FP-5 | User count | Users covering each FP (distinct) |
| 7 | Enrollment Timeline | Bar + Line | Date (with day name) | Users per day (bar) + Cumulative (line) | Group `UserTaskMapping.createdAt` by date |

### 4.3 User Detail Table (10 columns)

| Column | Source | Computation |
|--------|--------|-------------|
| Name | `UserTemp.firstName` + `UserTemp.lastName` | Concatenate |
| Role | `UserTemp.RoleName` | Direct |
| School / Branch (Code) | `SchoolBranches.BranchName`, `School.SchoolName`, `Diagnostic.branchCode` | Join via `selectedBranchId` |
| Tasks | `UserTaskMapping.SelectedTasks.length` | Count |
| FP Coverage | Map each selected taskId → task code → FP | Derive from Task→FP mapping |
| Depth Intent | Map each selected taskId → task code → depth | Derive from Task→Depth mapping |
| Selected Tasks | List of task codes (T01, T05, etc.) | Map taskId → task code |
| Mapped On | `UserTaskMapping.createdAt` | Direct (date part) |
| Days Logged | Count of distinct `UserDailyProgress.SubmitDate` for this user | Aggregate |

---

## 5. Dashboard 2 — Daily Progress

### 5.1 KPI Cards (8 metrics)

| KPI | Definition | Formula |
|-----|-----------|---------|
| Total Users | Count of DES users with UserTaskMapping | `count(users)` |
| Active (≥1 Log) | Users with at least one UserDailyProgress | `count(users where daysLogged > 0)` |
| Zero Logs | Users with no daily progress | `totalUsers - activeUsers` |
| Avg Days (Active) | Mean days logged among active users | `sum(daysLogged) / activeUsers` |
| Completion Rate | Global checked vs total | `totalChecked / (totalChecked + totalUnchecked) × 100` |
| Comment Rate | Entries with non-empty comment | `totalComments / totalLogEntries × 100` |
| Avg Consistency | Mean consistency across users with consistency > 0 | See Section 8 |
| Total Log Entries | Sum of all task-level log rows | `sum(TasksProgress[] entries across all docs)` |

### 5.2 Role Comparison Cards

For each role (Teacher, Leader):

| Metric | Formula |
|--------|---------|
| Count | `count(users where role = X)` |
| Avg Days Logged | `sum(daysLogged for role X) / count(role X)` |
| Avg Consistency | `sum(consistency for role X) / count(role X)` |
| Avg Completion Rate | `sum(completionRate for active role X) / count(active role X)` |

### 5.3 Charts (7 visualisations)

| # | Chart | Type | Data Needed |
|---|-------|------|-------------|
| 1 | Daily Activity Timeline | Stacked Bar + Line | Per-date: count of checked entries, unchecked entries, distinct active users. X-axis labels include day name (Mon, Tue, ...) |
| 2 | Task Completion Rate (T01–T12) | Horizontal Bar | Per-task: `checked / (checked + unchecked) × 100` |
| 3 | FP: Mapped vs Logged Users | Grouped Bar | Per-FP: count of users who mapped ≥1 task in that FP vs count who checked ≥1 entry in that FP |
| 4 | Depth: Selections vs Checked Logs | Grouped Bar | Per-depth-category: mapped count, checked count, unchecked count |
| 5 | Consistency Distribution | Bar | Bucket users into: 0%, 1-10%, 11-20%, 21-30%, 31-50%, >50% |
| 6 | Correlation: Tasks Mapped vs Days Logged | Scatter | Per-user: x = tasksMappedCount, y = daysLogged, colour = role |
| 7 | Completion Rate by FP | Radar | Per-FP: `checked / (checked + unchecked) × 100` across all tasks in that FP |

### 5.4 User Detail Table (15 columns)

| Column | Source | Computation |
|--------|--------|-------------|
| Name | `UserTemp` | `firstName + lastName` |
| Role | `UserTemp.RoleName` | Direct |
| School / Branch | `SchoolBranches` + `Diagnostic` | Join via `selectedBranchId` |
| Mapped (count) | `UserTaskMapping.SelectedTasks.length` | Count |
| FP | Selected tasks → FP mapping | Derive unique FPs |
| Depth | Selected tasks → Depth mapping | Derive unique depths |
| Mapped On | `UserTaskMapping.createdAt` | Date part. If missing, infer as `firstLogDate - 1 day` |
| Days Logged | Distinct `SubmitDate` count from `UserDailyProgress` | Aggregate |
| Checked | Count of `TasksProgress[].isChecked === true` | Aggregate |
| Unchecked | Count of `TasksProgress[].isChecked === false` | Aggregate |
| Comments | Count of `TasksProgress[].comment` non-empty | Aggregate |
| Completion % | `checked / (checked + unchecked) × 100` | Computed |
| Consistency % | See Section 8 | Computed |
| Mapped→Logged | Per-task breakdown: "T01: 8/10, T05: 7/10" | Per-task checked vs total |

---

## 6. API Endpoint Specifications

### API 1: `GET /api/dashboard/task-mapping`

**Purpose:** Returns all data needed for Dashboard 1.

**Response Structure:**

```json
{
  "summary": {
    "totalUsers": 124,
    "activeLoggers": 119,
    "zeroLogs": 5,
    "avgTasksPerUser": 3.4,
    "teachers": 91,
    "leaders": 33
  },
  "charts": {
    "taskAdoption": {
      "T01": 72, "T02": 45, "...": "..."
    },
    "fpCoverage": {
      "FP-1": 210, "FP-2": 130, "FP-3": 98, "FP-4": 85, "FP-5": 100
    },
    "depthDistribution": {
      "D1→D2": 250, "D2→D3": 120, "Cross-FP": 55
    },
    "tasksPerUserDistribution": {
      "1": 0, "2": 5, "3": 80, "4": 25, "5": 14
    },
    "roleDistribution": {
      "Teacher": 91, "Leader": 33
    },
    "fpRadar": {
      "FP-1": 110, "FP-2": 75, "FP-3": 60, "FP-4": 55, "FP-5": 70
    },
    "enrollmentTimeline": [
      {"date": "2026-02-03", "dayName": "Mon", "count": 20, "cumulative": 20},
      {"date": "2026-02-04", "dayName": "Tue", "count": 56, "cumulative": 76}
    ]
  },
  "users": [
    {
      "userId": "696ddd09c6f1e9689723f2b4",
      "name": "Priya Mandlik",
      "role": "Teacher",
      "schoolName": "Deccan Education Society",
      "branchName": "NAVIN MARATHI SHALA,PUNE",
      "branchCode": "M001",
      "tasksMapped": ["T01", "T03", "T09", "T10"],
      "tasksMappedCount": 4,
      "fpCoverage": ["FP-1", "FP-2", "FP-5"],
      "depthIntent": ["D1→D2", "D2→D3"],
      "mappedOn": "2026-02-03",
      "daysLogged": 11
    }
  ]
}
```

**Database Queries Required:**

```javascript
// 1. Get all DES user IDs with task mappings
const desBranches = db.SchoolBranches.find(
  {"School.SchoolName": "Deccan Education Society"},
  {_id: 1}
).map(b => b._id);

const desUsers = db.UserTemp.find(
  {selectedBranchId: {$in: desBranches}},
  {firstName: 1, lastName: 1, RoleName: 1, selectedBranchId: 1}
);

// 2. Get task mappings for DES users
db.UserTaskMapping.find(
  {userTempId: {$in: desUserIds}},
  {userTempId: 1, SelectedTasks: 1, createdAt: 1}
);

// 3. Get daily progress summary (days logged per user)
db.UserDailyProgress.aggregate([
  {$match: {UserTempId: {$in: desUserIds}}},
  {$group: {
    _id: "$UserTempId",
    daysLogged: {$addToSet: "$SubmitDate"},
  }},
  {$project: {
    _id: 1,
    daysLogged: {$size: "$daysLogged"}
  }}
]);

// 4. Branch code derivation
db.Diagnostic.aggregate([
  {$match: {branchId: {$in: desBranches}}},
  {$group: {
    _id: "$branchId",
    branchCode: {$first: "$branchCode"}
  }}
]);
```

---

### API 2: `GET /api/dashboard/daily-progress`

**Purpose:** Returns all data needed for Dashboard 2.

**Response Structure:**

```json
{
  "summary": {
    "totalUsers": 124,
    "activeUsers": 119,
    "zeroLogs": 5,
    "avgDaysActive": 5.7,
    "globalCompletionRate": 87.9,
    "globalCommentRate": 10.7,
    "avgConsistency": 47.9,
    "totalLogEntries": 2502
  },
  "roleComparison": {
    "Teacher": {
      "count": 91,
      "avgDays": 5.5,
      "avgConsistency": 47.1,
      "avgCompletion": 88.4
    },
    "Leader": {
      "count": 33,
      "avgDays": 5.2,
      "avgConsistency": 43.0,
      "avgCompletion": 85.5
    }
  },
  "charts": {
    "dailyTimeline": [
      {
        "date": "2026-02-03",
        "dayName": "Tue",
        "checked": 201,
        "unchecked": 15,
        "activeUsers": 72
      }
    ],
    "taskCompletionRate": {
      "T01": 90.1,
      "T02": 88.5
    },
    "fpMappedVsLogged": {
      "FP-1": {"mappedUsers": 110, "loggedUsers": 105},
      "FP-2": {"mappedUsers": 75, "loggedUsers": 70}
    },
    "depthMappedVsLogged": {
      "D1→D2 (Entry)": {"mapped": 250, "checked": 1200, "unchecked": 150},
      "D2→D3 (Growth)": {"mapped": 120, "checked": 600, "unchecked": 80},
      "Cross-FP": {"mapped": 55, "checked": 300, "unchecked": 40}
    },
    "consistencyDistribution": {
      "0%": 6, "1-10%": 3, "11-20%": 5,
      "21-30%": 10, "31-50%": 40, ">50%": 60
    },
    "scatter": [
      {"userId": "...", "tasksMapped": 4, "daysLogged": 11, "role": "Teacher"}
    ],
    "fpCompletionRadar": {
      "FP-1": 90.1, "FP-2": 87.6, "FP-3": 83.4,
      "FP-4": 87.0, "FP-5": 87.7
    }
  },
  "users": [
    {
      "userId": "696ddd09c6f1e9689723f2b4",
      "name": "Priya Mandlik",
      "role": "Teacher",
      "schoolName": "Deccan Education Society",
      "branchName": "NAVIN MARATHI SHALA,PUNE",
      "branchCode": "M001",
      "tasksMapped": ["T01", "T03", "T09", "T10"],
      "tasksMappedCount": 4,
      "fpCoverage": ["FP-1", "FP-2", "FP-5"],
      "depthIntent": ["D1→D2", "D2→D3"],
      "mappedOn": "2026-02-03",
      "daysLogged": 11,
      "totalChecked": 44,
      "totalUnchecked": 0,
      "totalComments": 0,
      "completionRate": 100.0,
      "commentRate": 0.0,
      "consistency": 84.6,
      "taskLogSummary": {
        "T01": {"checked": 11, "unchecked": 0, "total": 11},
        "T03": {"checked": 11, "unchecked": 0, "total": 11},
        "T09": {"checked": 11, "unchecked": 0, "total": 11},
        "T10": {"checked": 11, "unchecked": 0, "total": 11}
      }
    }
  ]
}
```

**Database Queries Required:**

```javascript
// 1. DES branch + user filtering (same as API 1)
// ...reuse from API 1...

// 2. Full daily progress with task-level detail
db.UserDailyProgress.aggregate([
  {$match: {UserTempId: {$in: desUserIds}}},
  {$unwind: "$TasksProgress"},
  {$project: {
    userId: "$UserTempId",
    submitDate: "$SubmitDate",
    createdAt: "$CreatedAt",
    taskId: "$TasksProgress.taskId",
    isChecked: "$TasksProgress.isChecked",
    hasComment: {
      $and: [
        {$ne: ["$TasksProgress.comment", null]},
        {$ne: [{$trim: {input: {$ifNull: ["$TasksProgress.comment", ""]}}}, ""]}
      ]
    }
  }}
]);

// 3. Daily activity timeline aggregate
db.UserDailyProgress.aggregate([
  {$match: {UserTempId: {$in: desUserIds}}},
  {$unwind: "$TasksProgress"},
  {$group: {
    _id: "$SubmitDate",
    checked: {$sum: {$cond: ["$TasksProgress.isChecked", 1, 0]}},
    unchecked: {$sum: {$cond: ["$TasksProgress.isChecked", 0, 1]}},
    activeUsers: {$addToSet: "$UserTempId"}
  }},
  {$project: {
    date: "$_id",
    checked: 1,
    unchecked: 1,
    activeUsers: {$size: "$activeUsers"}
  }},
  {$sort: {date: 1}}
]);

// 4. Per-user summary aggregate
db.UserDailyProgress.aggregate([
  {$match: {UserTempId: {$in: desUserIds}}},
  {$unwind: "$TasksProgress"},
  {$group: {
    _id: {
      userId: "$UserTempId",
      taskId: "$TasksProgress.taskId"
    },
    checked: {$sum: {$cond: ["$TasksProgress.isChecked", 1, 0]}},
    unchecked: {$sum: {$cond: ["$TasksProgress.isChecked", 0, 1]}},
    comments: {$sum: {$cond: [
      {$and: [
        {$ne: ["$TasksProgress.comment", null]},
        {$gt: [{$strLenCP: {$trim: {input: {$ifNull: ["$TasksProgress.comment", ""]}}}}, 0]}
      ]}, 1, 0
    ]}},
    dates: {$addToSet: "$SubmitDate"}
  }},
  {$group: {
    _id: "$_id.userId",
    tasks: {$push: {
      taskId: "$_id.taskId",
      checked: "$checked",
      unchecked: "$unchecked",
      comments: "$comments"
    }},
    totalChecked: {$sum: "$checked"},
    totalUnchecked: {$sum: "$unchecked"},
    totalComments: {$sum: "$comments"},
    allDates: {$push: "$dates"}
  }},
  {$project: {
    tasks: 1,
    totalChecked: 1,
    totalUnchecked: 1,
    totalComments: 1,
    daysLogged: {$size: {$reduce: {
      input: "$allDates",
      initialValue: [],
      in: {$setUnion: ["$$value", "$$this"]}
    }}}
  }}
]);
```

---

### API 3: `GET /api/reference/task-metadata`

**Purpose:** Returns static task metadata (FP mapping, depth intent).

**Response:**

```json
{
  "tasks": {
    "T01": {"label": "Notice One Learner", "fp": "FP-1", "depth": "D1→D2", "category": "entry"},
    "T02": {"label": "One Adjustment", "fp": "FP-1", "depth": "D2→D3", "category": "growth"},
    "T03": {"label": "Change One Example", "fp": "FP-2", "depth": "D1→D2", "category": "entry"},
    "T04": {"label": "Ask a Why/How", "fp": "FP-2", "depth": "D2→D3", "category": "growth"},
    "T05": {"label": "End-of-Class Reflection", "fp": "FP-3", "depth": "D1→D2", "category": "entry"},
    "T06": {"label": "Try One Small Change", "fp": "FP-3", "depth": "D2→D3", "category": "growth"},
    "T07": {"label": "Quick Check", "fp": "FP-4", "depth": "D1→D2", "category": "entry"},
    "T08": {"label": "Spot One Pattern", "fp": "FP-4", "depth": "D2→D3", "category": "growth"},
    "T09": {"label": "Teacher Touchpoint", "fp": "FP-5", "depth": "D1→D2", "category": "entry"},
    "T10": {"label": "Parent Signal", "fp": "FP-5", "depth": "D1→D2", "category": "entry"},
    "T11": {"label": "Student Voice", "fp": "FP-1", "depth": "Cross-FP", "category": "cross"},
    "T12": {"label": "Pause & Name", "fp": "FP-4", "depth": "Cross-FP", "category": "cross"}
  },
  "taskIdMapping": {
    "697b1e2cc01f188423ea7e0f": "T01",
    "697b1e3bc671c89acb64125a": "T01",
    "...": "..."
  },
  "fps": {
    "FP-1": "Every Child is Unique",
    "FP-2": "Holistic & Experiential Learning",
    "FP-3": "Reflective Practitioner",
    "FP-4": "Assessment for Learning",
    "FP-5": "Collaboration & Community"
  }
}
```

**Database Query:**

```javascript
db.MicroInterventionTasks.find({}, {
  "task.en.TaskPrefix": 1,
  "task.en.title": 1,
  category: 1
}).sort({_id: 1});
```

---

## 7. Aggregation Pipeline Reference

### 7.1 Task Adoption Count (Dashboard 1, Chart 1)

```javascript
db.UserTaskMapping.aggregate([
  {$match: {userTempId: {$in: desUserIds}}},
  {$unwind: "$SelectedTasks"},
  {$group: {
    _id: "$SelectedTasks.taskId",
    userCount: {$sum: 1}
  }},
  {$sort: {_id: 1}}
]);
// Post-process: map taskId → taskCode using the ID mapping table
```

### 7.2 Enrollment Timeline (Dashboard 1, Chart 7)

```javascript
db.UserTaskMapping.aggregate([
  {$match: {userTempId: {$in: desUserIds}}},
  {$group: {
    _id: {$dateToString: {format: "%Y-%m-%d", date: "$createdAt"}},
    count: {$sum: 1}
  }},
  {$sort: {_id: 1}}
]);
// Post-process: compute cumulative sum, add dayOfWeek name
```

### 7.3 Per-Task Completion Rate (Dashboard 2, Chart 2)

```javascript
db.UserDailyProgress.aggregate([
  {$match: {UserTempId: {$in: desUserIds}}},
  {$unwind: "$TasksProgress"},
  {$group: {
    _id: "$TasksProgress.taskId",
    checked: {$sum: {$cond: ["$TasksProgress.isChecked", 1, 0]}},
    unchecked: {$sum: {$cond: ["$TasksProgress.isChecked", 0, 1]}}
  }},
  {$project: {
    taskId: "$_id",
    checked: 1,
    unchecked: 1,
    completionRate: {
      $round: [{$multiply: [{$divide: ["$checked", {$add: ["$checked", "$unchecked"]}]}, 100]}, 1]
    }
  }},
  {$sort: {_id: 1}}
]);
```

### 7.4 FP Mapped vs Logged (Dashboard 2, Chart 3)

```javascript
// Mapped: count distinct users who selected any task in each FP
// Logged: count distinct users who have isChecked=true for any task in each FP

// This requires post-processing:
// 1. For each user, get their selected tasks → map to FPs → count per FP (mapped)
// 2. From daily progress, for each user, get tasks with isChecked=true → map to FPs (logged)
// 3. Per FP, count distinct users in each set
```

### 7.5 Consistency Distribution (Dashboard 2, Chart 5)

```javascript
// Computed in application layer after calculating per-user consistency
// See Section 8 for consistency formula
// Bucket users into: 0%, 1-10%, 11-20%, 21-30%, 31-50%, >50%
```

---

## 8. Computed Metric Formulas

### 8.1 Completion Rate (per user)

```
completionRate = totalChecked / (totalChecked + totalUnchecked) × 100
```

- **totalChecked**: Count of `TasksProgress[]` entries where `isChecked === true` across all the user's `UserDailyProgress` documents
- **totalUnchecked**: Count where `isChecked === false`
- If no log entries exist → `0%`

### 8.2 Comment Rate (per user)

```
commentRate = totalComments / (totalChecked + totalUnchecked) × 100
```

- **totalComments**: Count of `TasksProgress[]` entries where `comment` is non-null and non-empty (after trim)

### 8.3 Consistency (per user)

```
consistency = daysLogged / min(daysSinceMapping, 21) × 100
```

- **daysLogged**: Count of distinct `SubmitDate` values across the user's `UserDailyProgress` documents
- **daysSinceMapping**: `(currentDate - mappingDate)` in days
  - `mappingDate` = `UserTaskMapping.createdAt` (date part)
  - If `mappingDate` is missing/null and user has logs: **infer as `firstLogDate - 1 day`**
  - Cap at **21 days** (the intervention program duration per PRD)
- If `mappingDate` is missing AND no logs exist → `0%`

### 8.4 Per-Task Log Summary

For each user and each task in their `SelectedTasks`:

```
checked  = count(TasksProgress entries for this taskId where isChecked = true)
unchecked = count(TasksProgress entries for this taskId where isChecked = false)
total    = checked + unchecked
```

Display format in table: `T01: {checked}/{total}`

### 8.5 FP Completion Rate (Radar chart)

For each FP, across all users:

```
fpCompletionRate = totalCheckedForFP / (totalCheckedForFP + totalUncheckedForFP) × 100
```

Where totals are summed across all tasks belonging to that FP.

---

## 9. Filter & Sort Requirements

### 9.1 Filters (both dashboards)

| Filter | Type | Options | Applies To |
|--------|------|---------|------------|
| Search | Text | Free text match on name, school, branch | User table |
| Role | Dropdown | All, Teacher, Leader | All charts + table |
| Activity | Dropdown | All, Active (≥1 log), Zero Logs | All charts + table |
| FP | Dropdown (Dashboard 1 only) | All, FP-1, FP-2, FP-3, FP-4, FP-5 | Charts + table |

### 9.2 Sort Options (user table)

| Column | Sort | Direction |
|--------|------|-----------|
| Name | Alphabetical | Asc / Desc |
| Role | Alphabetical | Asc / Desc |
| School / Branch | Alphabetical | Asc / Desc |
| Tasks Mapped | Numeric | Asc / Desc |
| Days Logged | Numeric | Asc / Desc |
| Completion % | Numeric | Asc / Desc |
| Consistency % | Numeric | Asc / Desc |
| Mapped On | Date | Asc / Desc |

### 9.3 Default Sort

- Dashboard 1: by Mapped On (ascending), then Days Logged (descending)
- Dashboard 2: by Consistency % (descending), then Days Logged (descending), then Name (ascending)

---

## 10. Data Volume & Performance Notes

### Current Data Volumes

| Collection | Total Records | DES Filtered |
|-----------|--------------|-------------|
| UserTaskMapping | ~138 documents | 124 users |
| UserDailyProgress | ~700 documents | ~650 documents (124 users × ~5.3 avg days) |
| TasksProgress (unwound) | ~3,140 entries | ~2,502 entries |
| MicroInterventionTasks | 12 (×2 series = 24 ObjectIds) | 12 tasks |

### Indexing Recommendations

```javascript
// Critical indexes for dashboard queries
db.UserTemp.createIndex({selectedBranchId: 1});
db.SchoolBranches.createIndex({"School.SchoolName": 1});
db.UserTaskMapping.createIndex({userTempId: 1});
db.UserDailyProgress.createIndex({UserTempId: 1, SubmitDate: 1});
db.Diagnostic.createIndex({branchId: 1});
```

### Caching Strategy

- **Task metadata** (API 3): Cache indefinitely — static data, changes only on task redesign
- **Task mapping** (API 1): Cache for 1 hour — changes only when new users enroll
- **Daily progress** (API 2): Cache for 15 minutes — changes as users submit daily logs
- Consider pre-computing aggregates nightly if user volume grows beyond 500

### Field Name Casing Warning

MongoDB field names are **inconsistent** across collections:

| Collection | Casing Pattern | Examples |
|-----------|---------------|----------|
| UserTemp | camelCase | `firstName`, `lastName`, `selectedBranchId` |
| UserTemp | PascalCase | `RoleName` |
| SchoolBranches | PascalCase | `BranchName`, `School.SchoolName` |
| UserTaskMapping | camelCase | `userTempId`, `createdAt` |
| UserTaskMapping | PascalCase | `SelectedTasks` |
| UserDailyProgress | PascalCase | `UserTempId`, `SubmitDate`, `CreatedAt`, `TasksProgress` |
| UserDailyProgress (nested) | camelCase | `TasksProgress[].taskId`, `TasksProgress[].isChecked`, `TasksProgress[].comment` |

**Backend must handle mixed casing carefully in all queries.**

---

*Document Version: 1.0 | Project Kshitij | Myelin | Confidential*
*Generated: 2026-02-16*
