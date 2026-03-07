# Functional Steps: User Task Mapping & Daily Logging

**Module:** Stage 5 — Micro-Intervention Practice
**Program:** Myelin NEP Readiness Pilot | Deccan Education Society
**Date:** 2026-02-18
**Audience:** Program managers, school leaders, technical team

---

## 1. Overview

Stage 5 of the NEP Readiness pilot enables teachers and school leaders to select daily micro-intervention tasks aligned to NEP 2020's Foundational Principles and track their classroom practice through a daily logging mechanism.

**User Roles:** Teacher (~70%) | Leader (~30%)
**Duration:** 21-day practice window
**Languages:** English + Marathi (bilingual)

---

## 2. Foundational Principles (FP-1 to FP-5)

| Code | Principle | Core Idea |
|------|-----------|-----------|
| **FP-1** | Every Child is Unique | Recognizing individual differences, inclusive observation |
| **FP-2** | Holistic & Experiential Learning | Learning by doing, connecting to real life |
| **FP-3** | Teacher as Reflective Practitioner | Self-reflection, continuous improvement |
| **FP-4** | Assessment for Learning | Formative assessment, understanding over marks |
| **FP-5** | Collaboration & Community | Teacher-parent-community partnership |

---

## 3. The 12 Micro-Intervention Tasks

### 3.1 Task Library

| Code | Task Name | FP | Depth | Description |
|------|-----------|----|-------|-------------|
| T01 | Notice One Learner | FP-1 | D1→D2 | Quietly watch one student — notice how they sit, listen, respond, or try |
| T02 | One Adjustment | FP-1 | D2→D3 | Change one small thing for a student — speak slower, give a simpler example, or pair them up |
| T03 | Change One Example | FP-2 | D1→D2 | Replace the textbook example with something from daily life students already know |
| T04 | Ask a Why/How | FP-2 | D2→D3 | Ask at least one "Why do you think this happens?" or "How did you get this answer?" |
| T05 | End-of-Class Reflection | FP-3 | D1→D2 | After class, think: What went well? What didn't work? |
| T06 | Try One Small Change | FP-3 | D2→D3 | In the next class, change one thing based on what you noticed earlier |
| T07 | Quick Check | FP-4 | D1→D2 | Ask 2–3 students to explain the answer in their own words |
| T08 | Spot One Pattern | FP-4 | D2→D3 | Notice if many students make the same mistake or get confused at the same place |
| T09 | Teacher Touchpoint | FP-5 | D1→D2 | Tell another teacher about one thing that happened in your class |
| T10 | Parent Signal | FP-5 | D1→D2 | Share one good learning observation about a child with a parent |
| T11 | Student Voice | FP-1 | Cross-FP | Ask one student: "What helped you learn today?" |
| T12 | Pause & Name | FP-4 | Cross-FP | Pause once and name what students are doing well in learning |

### 3.2 Depth Levels

| Depth | Label | Meaning |
|-------|-------|---------|
| **D1→D2** | Procedural → Responsive | Entry-level: start by noticing, then respond to what you observe |
| **D2→D3** | Responsive → Diagnostic | Growth: adjust responses based on deeper evidence and diagnosis |
| **Cross-FP** | Multi-Principle Integration | Advanced: tasks that bridge multiple foundational principles |

---

## 4. Functional Flow — Phase by Phase

### Phase 1: Task Mapping (Enrollment)

**Goal:** User selects 3–12 tasks from the task library to practice over 21 days.

```
Step 1.1  User logs in → lands on "Micro-Intervention" module
Step 1.2  System displays all 12 tasks organized by FP
            → Each task shows: Name, Description, FP tag, Depth tag
            → Bilingual toggle: EN | मराठी
Step 1.3  User selects tasks (minimum 3, maximum 12)
            → Selection highlights FP coverage visually
            → System shows depth distribution (Entry / Growth / Cross-FP)
Step 1.4  User confirms selection → "Start My Practice"
Step 1.5  System saves to UserTaskMapping collection:
            → userTempId (user reference)
            → SelectedTasks[] (array of taskId references)
            → createdAt (enrollment timestamp)
Step 1.6  User sees confirmation with selected tasks + start date
```

**Data Created:**

| Collection | Field | Value |
|------------|-------|-------|
| `UserTaskMapping` | `userTempId` | User's ObjectId |
| | `SelectedTasks[]` | Array of task ObjectIds |
| | `createdAt` | Enrollment timestamp |

**Business Rules:**
- Minimum 3 tasks, maximum 12
- User can re-select tasks at any time (overwrites previous selection)
- Tasks are role-agnostic (Teachers and Leaders see the same library)

---

### Phase 2: Daily Logging (21-day Practice Window)

**Goal:** User checks in daily to mark which tasks they practiced and optionally reflect.

```
Step 2.1  User opens "Daily Practice Log" screen
Step 2.2  System displays ONLY the user's selected tasks (not all 12)
            → Current date shown prominently
            → Each task rendered as a card with:
               ☐ Checkbox (Done / Not Done)
               📝 Optional comment field (free text)
Step 2.3  User checks off completed tasks
            → Checkbox toggles: true (practiced) / false (not practiced)
Step 2.4  User optionally adds a reflection comment
            → Short free-text (e.g., "Student responded well to the simpler example")
Step 2.5  System auto-saves on each interaction
Step 2.6  System creates a UserDailyProgress record:
            → UserTempId (user reference)
            → SubmitDate (date of practice)
            → CreatedAt (save timestamp)
            → TasksProgress[] (one entry per selected task)
Step 2.7  User sees visual confirmation (checkmarks turn green)
```

**Data Created (per daily log):**

| Collection | Field | Value |
|------------|-------|-------|
| `UserDailyProgress` | `UserTempId` | User's ObjectId |
| | `SubmitDate` | Date of practice (YYYY-MM-DD) |
| | `CreatedAt` | Record creation timestamp |
| | `TasksProgress[].taskId` | Task ObjectId |
| | `TasksProgress[].isChecked` | `true` / `false` |
| | `TasksProgress[].comment` | Free-text or empty |

**Business Rules:**
- One log record per user per day
- All selected tasks appear in each daily log (checked or unchecked)
- Comments are optional — no minimum length
- Past dates cannot be edited (logs are append-only)
- No deletion — all entries are permanent

---

### Phase 3: Progress Tracking (Dashboard View)

**Goal:** User and administrators see cumulative progress and engagement metrics.

```
Step 3.1  User navigates to "My Progress" screen
Step 3.2  System displays a 21-day progress grid:
            → Rows = selected tasks
            → Columns = calendar dates
            → Cell states: ✓ Done | ✓ + comment | ✗ Not done | — Future
Step 3.3  System calculates and displays:
            → Completion Rate = checked / (checked + unchecked) × 100
            → Consistency = days logged / days since mapping (capped at 21)
            → Comment Rate = entries with comments / total entries × 100
Step 3.4  Admin dashboard aggregates across all users:
            → KPIs: total users, active users, zero-log users
            → Charts: daily timeline, task completion, FP coverage
            → Filterable user table with per-user metrics
```

**Metrics Computed:**

| Metric | Formula | Scope |
|--------|---------|-------|
| Completion Rate | `totalChecked / (totalChecked + totalUnchecked) × 100` | Per user + global |
| Consistency | `daysLogged / min(daysSinceMapping, 21) × 100` | Per user |
| Comment Rate | `totalComments / totalLogEntries × 100` | Per user + global |
| Active Users | Count of users with ≥1 log entry | Global |

---

## 5. End-to-End Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER JOURNEY                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────────────────┐   │
│  │  LOGIN    │───►│ SELECT TASKS │───►│  DAILY PRACTICE LOG     │   │
│  │          │    │ (3–12 tasks) │    │  (repeat for 21 days)   │   │
│  └──────────┘    └──────┬───────┘    └────────────┬────────────┘   │
│                         │                         │                 │
│                         ▼                         ▼                 │
│               ┌─────────────────┐     ┌──────────────────────┐     │
│               │ UserTaskMapping │     │  UserDailyProgress   │     │
│               │                 │     │                      │     │
│               │ • userTempId    │     │ • UserTempId         │     │
│               │ • SelectedTasks │     │ • SubmitDate         │     │
│               │ • createdAt     │     │ • TasksProgress[]    │     │
│               └────────┬────────┘     │   - taskId           │     │
│                        │              │   - isChecked         │     │
│                        │              │   - comment           │     │
│                        │              └───────────┬──────────┘     │
│                        │                          │                 │
│                        └────────┬─────────────────┘                 │
│                                 ▼                                   │
│                    ┌────────────────────────┐                       │
│                    │  DASHBOARD / REPORTS   │                       │
│                    │                        │                       │
│                    │ • Progress grid        │                       │
│                    │ • Completion rate      │                       │
│                    │ • Consistency %        │                       │
│                    │ • FP coverage radar    │                       │
│                    │ • Admin user table     │                       │
│                    └────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Supporting Data Infrastructure

### 6.1 Collections Used

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| `UserTemp` | User profiles | firstName, lastName, RoleName, selectedBranchId |
| `SchoolBranches` | Branch/school info | BranchName, School.SchoolName |
| `MicroInterventionTasks` | 12 task definitions | taskCode, label (en/mr), description, FP, depth |
| `UserTaskMapping` | Task selections | userTempId, SelectedTasks[], createdAt |
| `UserDailyProgress` | Daily logs | UserTempId, SubmitDate, TasksProgress[] |

### 6.2 Task ID Mapping

Two parallel MongoDB ObjectId series exist for the same 12 tasks:

| Task | Series A (`697b1e2c...`) | Series B (`697b1e3b...`) |
|------|--------------------------|--------------------------|
| T01 | `697b1e2cc01f188423ea7e0f` | `697b1e3bc671c89acb64125a` |
| T02 | `697b1e2cc01f188423ea7e10` | `697b1e3bc671c89acb64125b` |
| T03 | `697b1e2cc01f188423ea7e11` | `697b1e3bc671c89acb64125c` |
| ... | Sequential +1 hex | Sequential +1 hex |
| T12 | `697b1e2cc01f188423ea7e1a` | `697b1e3bc671c89acb641265` |

Both series are actively used in production data.

---

## 7. Typical User Scenarios

### Scenario A: Engaged Teacher (High Consistency)

| Day | Action |
|-----|--------|
| Feb 3 | Maps 5 tasks: T01, T03, T05, T07, T09 (one per FP, all D1→D2) |
| Feb 4–17 | Logs 11 of 14 days; completion rate 85%; adds comments 4 times |
| Result | Consistency: 79% | Completion: 85% | Comment rate: 7% |

### Scenario B: Selective Leader (Medium Consistency)

| Day | Action |
|-----|--------|
| Feb 4 | Maps 3 tasks: T02, T04, T08 (all D2→D3 growth tasks) |
| Feb 5–17 | Logs 6 of 13 days; completion rate 72% |
| Result | Consistency: 46% | Completion: 72% | Comment rate: 0% |

### Scenario C: Drop-Off Teacher (Low Consistency)

| Day | Action |
|-----|--------|
| Feb 3 | Maps 7 tasks across all FPs |
| Feb 5–7 | Logs 3 days, all tasks checked enthusiastically |
| Feb 8+ | No further logs |
| Result | Consistency: 20% | Completion: 95% | Comment rate: 15% |

---

## 8. Key Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Trust-based reflection** | No surveillance; self-reported check-ins |
| **Minimal friction** | Auto-save, no submit button, card-based UI |
| **Bilingual from day 1** | English + Marathi toggle on all screens |
| **Mobile-first** | Cards on mobile, table on desktop |
| **Append-only data** | No edits or deletes; all entries permanent |
| **Role-agnostic tasks** | Same 12 tasks for Teachers and Leaders |

---

## 9. Current Production Statistics (as of 2026-02-18)

| Metric | Value |
|--------|-------|
| Total mapped users (DES) | 124 |
| Active users (≥1 log) | 119 (96%) |
| Zero-log users | 5 (4%) |
| Total task-log entries | 2,994 |
| Avg days logged (active) | 5.7 |
| Global completion rate | ~88% |
| Global comment rate | ~11% |
| Teachers | ~85 |
| Leaders | ~39 |
