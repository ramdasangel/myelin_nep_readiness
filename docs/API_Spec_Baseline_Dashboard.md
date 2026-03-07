# API Specification — Stage 4.3 Practice Diagnostics (Enablement & Systems Baseline)

**Version:** 1.0
**Date:** 2026-02-09
**Status:** Draft
**Author:** Data & Analytics Team
**Consumers:** Baseline Dashboard HTML (`baseline_dashboard.html`)

---

## 1. Overview

This document specifies two REST API endpoints that supply per-user area scores for the **Stage 4.3 Practice Diagnostics (Enablement & Systems Baseline)** dashboard. The dashboard has two tabs — **Teacher Lens** (areas A1–A4) and **Leadership Lens** (areas B1–B5). Each endpoint must return data in either **CSV** or **JSON** format based on the `Accept` header or a query parameter.

### 1.1 Context

Stage 4.3 measures how well school systems enable NEP-2020 implementation from two perspectives:

| Lens | Areas | Question Sets | Total Questions |
|------|-------|---------------|-----------------|
| Teacher | A1, A2, A3, A4 | `base001` (English), `base003` (Marathi) | 19 |
| Leader | B1, B2, B3, B4, B5 | `base002` (English), `base004` (Marathi) | 15 |

Both English and Marathi respondents are **merged** into a single cohort per lens. Responses use a 4-point Likert scale.

---

## 2. Endpoints

### 2.1 Teacher Baseline Scores

```
GET /api/v1/diagnostics/baseline/teacher
```

### 2.2 Leader Baseline Scores

```
GET /api/v1/diagnostics/baseline/leader
```

### 2.3 Common Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `format` | string | No | `json` | Response format: `json` or `csv` |
| `branchCode` | string | No | — | Filter by branch code (e.g. `M001`). Comma-separated for multiple. |
| `language` | string | No | — | Filter by language: `en`, `mr`, or omit for both merged |
| `submittedAfter` | ISO date | No | — | Only include attempts submitted after this date |
| `submittedBefore` | ISO date | No | — | Only include attempts submitted before this date |

The `Accept` header can also drive format: `text/csv` returns CSV, `application/json` returns JSON (default).

---

## 3. Response Schema — Teacher Lens

### 3.1 CSV Format

**Header row:**
```
UserId,FullName,Role,Language,School,Branch,BranchCode,A1_Score,A1_Avg,A1_Pct,A2_Score,A2_Avg,A2_Pct,A3_Score,A3_Avg,A3_Pct,A4_Score,A4_Avg,A4_Pct,OverallAvg
```

**Example row:**
```
697851cb82c04511c8aa53e8,Abhi Ghodekar,Teacher,mr,Myelin Model School,Myelin Cbse Primary & Secondary School,m942e,5,1.00,25.0,6,1.20,30.0,9,1.80,45.0,6,1.50,37.5,1.38
```

### 3.2 JSON Format

```json
{
  "meta": {
    "lens": "teacher",
    "areas": ["A1", "A2", "A3", "A4"],
    "totalRecords": 609,
    "generatedAt": "2026-02-09T10:30:00Z",
    "setCodes": ["base001", "base003"],
    "scoreScale": { "min": 1, "max": 4 }
  },
  "data": [
    {
      "UserId": "697851cb82c04511c8aa53e8",
      "FullName": "Abhi Ghodekar",
      "Role": "Teacher",
      "Language": "mr",
      "School": "Myelin Model School",
      "Branch": "Myelin Cbse Primary & Secondary School",
      "BranchCode": "m942e",
      "A1_Score": 5,
      "A1_Avg": 1.00,
      "A1_Pct": 25.0,
      "A2_Score": 6,
      "A2_Avg": 1.20,
      "A2_Pct": 30.0,
      "A3_Score": 9,
      "A3_Avg": 1.80,
      "A3_Pct": 45.0,
      "A4_Score": 6,
      "A4_Avg": 1.50,
      "A4_Pct": 37.5,
      "OverallAvg": 1.38
    }
  ]
}
```

---

## 4. Response Schema — Leader Lens

### 4.1 CSV Format

**Header row:**
```
UserId,FullName,Role,Language,School,Branch,BranchCode,B1_Score,B1_Avg,B1_Pct,B2_Score,B2_Avg,B2_Pct,B3_Score,B3_Avg,B3_Pct,B4_Score,B4_Avg,B4_Pct,B5_Score,B5_Avg,B5_Pct,OverallAvg
```

**Example row:**
```
696ddca67c028268c457d95a,Deepa Abhyankar,Leader,en,Deccan Education Society,AHILYADEVI HIGH SCHOOL FOR GIRLS,M001,8,2.67,66.7,10,3.33,83.3,10,3.33,83.3,9,3.00,75.0,9,3.00,75.0,3.07
```

### 4.2 JSON Format

Same structure as Teacher, with `B1`–`B5` fields replacing `A1`–`A4`.

---

## 5. Field Definitions

### 5.1 Identity & Context Fields

| Field | Type | Source Collection | Source Field | Description |
|-------|------|-------------------|--------------|-------------|
| `UserId` | string (ObjectId) | `DiagnosticAttempt` | `userTempId` | The temp user ID from the diagnostic flow |
| `FullName` | string | `UserTemp` | `firstName` + `lastName` | Concatenated full name. `"Unknown"` if user not found in `UserTemp` |
| `Role` | string | `UserTemp` | `RoleName` | `"Teacher"` or `"Leader"`. Empty if user not found |
| `Language` | string | Derived | — | `"en"` if setCode is `base001`/`base002`; `"mr"` if `base003`/`base004` |
| `School` | string | `SchoolBranches` | `School.SchoolName` | Parent school/organisation name |
| `Branch` | string | `SchoolBranches` | `BranchName` | Branch (school unit) name |
| `BranchCode` | string | `Diagnostic` | `branchCode` | Code like `M001`–`M038`. Derived via `branchId` join (see Section 7) |

### 5.2 Area Score Fields (per area)

For each area `X` (A1–A4 for Teacher, B1–B5 for Leader):

| Field | Type | Description | Computation |
|-------|------|-------------|-------------|
| `X_Score` | integer | Raw sum of scores for all questions in this area | `SUM(score)` where `score = 4 - selectedOption` |
| `X_Avg` | float (2 dp) | Average score per question | `X_Score / question_count` |
| `X_Pct` | float (1 dp) | Percentage of maximum possible | `X_Score / (question_count * 4) * 100` |

### 5.3 Aggregate Field

| Field | Type | Description | Computation |
|-------|------|-------------|-------------|
| `OverallAvg` | float (2 dp) | Mean of all area averages | `MEAN(A1_Avg, A2_Avg, A3_Avg, A4_Avg)` for teacher; `MEAN(B1_Avg ... B5_Avg)` for leader |

---

## 6. Scoring Logic

### 6.1 Response Scale

All questions use a 4-option Likert scale. The `selectedOption` field in `DiagnosticAttempt.responses[]` stores a **0-based index**:

| selectedOption | Label (English) | Label (Marathi) | Score |
|----------------|-----------------|-----------------|-------|
| `"0"` | Strongly Agree | पूर्णतः सहमत | **4** |
| `"1"` | Agree | सहमत | **3** |
| `"2"` | Disagree | असहमत | **2** |
| `"3"` | Strongly Disagree | पूर्णतः असहमत | **1** |

**Formula:** `score = 4 - parseInt(selectedOption)`

### 6.2 Area Mapping

Each question maps to an area via `response.questionMetadata.description`. Extract the area code using regex: `/^([AB]\d)/`

**Example:** `"A1. Continuous learning diagnostics"` → area = `A1`

**Fallback:** If `questionMetadata` is missing, look up the `questionId` in the `DiagnosticQuestion` collection and read `metadata.description`.

### 6.3 Area Definitions — Teacher Lens

| Area | Name | Questions | Sub-Areas (Goals) | Max Score |
|------|------|-----------|-------------------|-----------|
| **A1** | Continuous Learning Diagnostics | 5 | Access, Usability, Follow-through, Collective Use, Student Clarity | 20 |
| **A2** | Teacher Development & Growth Support | 5 | Structure, Safety, Peer Learning, Experimentation, Growth Culture | 20 |
| **A3** | HPC Teacher Enablement | 5 | Understanding, Clarity, Time, Use, Student Role | 20 |
| **A4** | Parent & Community Support | 4 | Communication, Guidance, Facilitation, Recognition | 16 |

**Weight:** Equal weight per question within each area (`1/N` where N = question count).

### 6.4 Area Definitions — Leader Lens

| Area | Name | Questions | Sub-Areas (Goals) — English `base002` | Max Score |
|------|------|-----------|---------------------------------------|-----------|
| **B1** | NEP Governance & Ownership | 3 | Ownership, Translation, Distribution | 12 |
| **B2** | Data-Informed Decision Culture | 3 | Review, Decisions, Support | 12 |
| **B3** | Teacher Development Culture | 3 | Peer Learning Circles, Safety, Experimentation | 12 |
| **B4** | HPC & Reporting Culture | 3 | Purpose, Parent Clarity, Teacher Support | 12 |
| **B5** | Parent & Community Partnerships | 3 | Strategy, Activation, Feedback | 12 |

> **Note:** The Marathi leader set (`base004`) covers parallel but **differently-worded** dimensions under the same B1–B5 area codes. Both are merged by area code.

### 6.5 Readiness Bands (for dashboard display)

| Band | Average Score Range | Interpretation |
|------|-------------------|----------------|
| **Strong** | ≥ 3.50 | Systems strongly support this area |
| **Moderate** | 2.50 – 3.49 | Partial enablement; some gaps exist |
| **Developing** | 1.50 – 2.49 | Significant gaps; needs attention |
| **Limited** | < 1.50 | Minimal enablement; urgent action needed |

---

## 7. Database Schema & Query Logic

### 7.1 Collections Involved

```
Database: pdea_pilot
```

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| `DiagnosticAttempt` | Core response data | `userTempId`, `setCode`, `isSubmitted`, `branchId`, `responses[]`, `updatedAt` |
| `DiagnosticQuestionSet` | Set → question mapping | `setCode`, `questionIds[]`, `setName` |
| `DiagnosticQuestion` | Question metadata | `_id`, `questionText`, `metadata.goal`, `metadata.description`, `options[]`, `tags[]` |
| `UserTemp` | User profiles | `_id`, `firstName`, `lastName`, `RoleName`, `selectedBranchId` |
| `SchoolBranches` | Branch info | `_id`, `BranchName`, `School.SchoolName` |
| `Diagnostic` | Branch code mapping | `branchId`, `branchCode` |

### 7.2 Entity Relationships

```
DiagnosticAttempt.userTempId  →  UserTemp._id
DiagnosticAttempt.branchId    →  SchoolBranches._id
DiagnosticAttempt.setCode     →  DiagnosticQuestionSet.setCode
DiagnosticAttempt.responses[].questionId  →  DiagnosticQuestion._id
UserTemp.selectedBranchId     →  SchoolBranches._id
Diagnostic.branchId           →  SchoolBranches._id     (for branchCode lookup)
```

### 7.3 Query: Get Submitted Baseline Attempts

```javascript
// Teacher
db.DiagnosticAttempt.find({
  setCode: { $in: ["base001", "base003"] },
  isSubmitted: true
})

// Leader
db.DiagnosticAttempt.find({
  setCode: { $in: ["base002", "base004"] },
  isSubmitted: true
})
```

### 7.4 Query: Resolve BranchCode

`SchoolBranches` does **NOT** have a `BranchCode` field. The branch code must be derived from the `Diagnostic` collection:

```javascript
// Build branchId → branchCode map
const branchCodeMap = {};
db.Diagnostic.find({}, { branchId: 1, branchCode: 1 }).forEach(d => {
  if (d.branchId && d.branchCode) {
    branchCodeMap[d.branchId.toString()] = d.branchCode;
  }
});
```

Branch codes follow the pattern `M001`–`M038` for DES schools, `m942e`/`m56b0` for test schools.

### 7.5 Response Object Structure

Each `DiagnosticAttempt.responses[]` element:

```json
{
  "_id": "ObjectId",
  "questionId": "ObjectId",
  "selectedOption": "0",          // string: "0","1","2","3"
  "metadata": {
    "depthLevel": "",
    "fpLevel": ""
  },
  "questionText": "You have access to simple tools...",
  "type": "MCQ",
  "questionMetadata": {
    "goal": "Access",
    "description": "A1. Continuous learning diagnostics"
  },
  "options": [
    { "text": "Strongly Agree",    "metadata": { "depthLevel": "", "fpLevel": "" } },
    { "text": "Agree",             "metadata": { "depthLevel": "", "fpLevel": "" } },
    { "text": "Disagree",          "metadata": { "depthLevel": "", "fpLevel": "" } },
    { "text": "Strongly Disagree", "metadata": { "depthLevel": "", "fpLevel": "" } }
  ]
}
```

**Area extraction:** Parse `questionMetadata.description` with regex `/^([AB]\d)/` to get area code.

---

## 8. Processing Algorithm (Pseudocode)

```
FUNCTION generateBaselineScores(lens):  // lens = "teacher" or "leader"

  IF lens == "teacher":
    setCodes = ["base001", "base003"]
    areas = ["A1", "A2", "A3", "A4"]
  ELSE:
    setCodes = ["base002", "base004"]
    areas = ["B1", "B2", "B3", "B4", "B5"]

  // 1. Load lookup tables
  branchCodeMap  = buildBranchCodeMap()       // Diagnostic → branchId:branchCode
  branchInfoMap  = buildBranchInfoMap()       // SchoolBranches → branchId:{name,school}
  userMap        = buildUserMap()             // UserTemp → userId:{name,role,branchId}

  // 2. Query submitted attempts
  attempts = DiagnosticAttempt.find({ setCode: {$in: setCodes}, isSubmitted: true })

  // 3. Process each attempt
  results = []
  FOR EACH attempt IN attempts:
    user     = userMap[attempt.userTempId]       // may be null
    branchId = user?.selectedBranchId OR attempt.branchId
    branch   = branchInfoMap[branchId]
    code     = branchCodeMap[branchId]
    language = setCodes[0,1] contains attempt.setCode ? "en" : "mr"

    // 4. Compute area scores from responses
    areaScores = {}  // area → { totalScore, questionCount }
    FOR EACH response IN attempt.responses:
      areaCode = extractArea(response.questionMetadata.description)
      IF areaCode is empty:
        areaCode = lookupAreaFromQuestion(response.questionId)  // fallback
      score = 4 - parseInt(response.selectedOption)
      areaScores[areaCode].totalScore += score
      areaScores[areaCode].questionCount += 1

    // 5. Build output record
    record = {
      UserId:     attempt.userTempId,
      FullName:   user?.fullName OR "Unknown",
      Role:       user?.role OR "",
      Language:   language,
      School:     branch?.schoolName OR "",
      Branch:     branch?.branchName OR "",
      BranchCode: code OR "",
    }

    FOR EACH area IN areas:
      s = areaScores[area]
      record[area + "_Score"] = s.totalScore
      record[area + "_Avg"]   = ROUND(s.totalScore / s.questionCount, 2)
      record[area + "_Pct"]   = ROUND(s.totalScore / (s.questionCount * 4) * 100, 1)

    record.OverallAvg = ROUND(MEAN(all area _Avg values), 2)
    results.append(record)

  RETURN results
```

---

## 9. Question Bank Reference

### 9.1 Teacher Questions (base001 English / base003 Marathi)

| # | Area | Sub-Area (Goal) | Question Text (English) |
|---|------|-----------------|------------------------|
| Q1 | A1 | Access | You have access to simple tools or formats to understand students' learning levels |
| Q2 | A1 | Usability | These tools help you clearly identify what students are struggling with |
| Q3 | A1 | Follow-through | You get time or support to act on diagnostic insights |
| Q4 | A1 | Collective Use | Diagnostic insights are discussed with other teachers (meetings / peer learning) |
| Q5 | A1 | Student Clarity | Students are informed about what they are working towards based on diagnostics |
| Q6 | A2 | Structure | You have a clear plan or pathway for your professional growth aligned to NEP |
| Q7 | A2 | Safety | You have safe spaces to discuss classroom challenges openly |
| Q8 | A2 | Peer Learning | You have opportunities to learn from other teachers regularly |
| Q9 | A2 | Experimentation | You are encouraged to try new approaches without fear of evaluation |
| Q10 | A2 | Growth Culture | Teacher growth is discussed beyond annual reviews |
| Q11 | A3 | Understanding | You clearly understand what to observe beyond marks for HPC |
| Q12 | A3 | Clarity | HPC indicators are clearly explained and documented |
| Q13 | A3 | Time | You get time to record and reflect on HPC inputs |
| Q14 | A3 | Use | HPC discussions are used to guide learning conversations |
| Q15 | A3 | Student Role | Students are involved in reflecting on their own progress |
| Q16 | A4 | Communication | You feel supported in communicating learning progress to parents |
| Q17 | A4 | Guidance | You receive clear guidance on how to engage parents meaningfully |
| Q18 | A4 | Facilitation | Community interactions are facilitated by the school (not left to you alone) |
| Q19 | A4 | Recognition | Efforts to involve parents or community are recognised |

### 9.2 Leader Questions — English (base002)

| # | Area | Sub-Area (Goal) | Question Text |
|---|------|-----------------|---------------|
| Q1 | B1 | Ownership | You have a clearly identified role or team responsible for NEP implementation |
| Q2 | B1 | Translation | NEP priorities are translated into term-wise focus areas |
| Q3 | B1 | Distribution | Responsibility for NEP implementation is shared across the school |
| Q4 | B2 | Review | You review learning diagnostic insights at leadership level |
| Q5 | B2 | Decisions | Academic decisions are influenced by learning trends |
| Q6 | B2 | Support | Teachers are supported when data suggests changes are needed |
| Q7 | B3 | Peer Learning Circles | You have regular and purposeful teacher reflection forums |
| Q8 | B3 | Safety | Teachers are encouraged to share challenges without fear |
| Q9 | B3 | Experimentation | Experimentation is protected and valued by leadership |
| Q10 | B4 | Purpose | HPC is discussed as a learning narrative, not just reporting |
| Q11 | B4 | Parent Clarity | Parents are oriented to what HPC represents |
| Q12 | B4 | Teacher Support | Teachers are supported in shifting beyond marks-based reporting |
| Q13 | B5 | Strategy | You have a school-level approach to parent engagement |
| Q14 | B5 | Activation | Community resources are identified and used intentionally |
| Q15 | B5 | Feedback | Parent feedback is used to improve learning processes |

### 9.3 Leader Questions — Marathi (base004)

> **Important:** Marathi leader questions cover **different sub-topics** under the same B1–B5 codes.

| # | Area | Sub-Area (Goal) | Question Text (Marathi summary) |
|---|------|-----------------|-------------------------------|
| Q1 | B1 | Ownership | NEP implementation responsibilities clearly assigned at school level |
| Q2 | B1 | Decision-making | NEP decision process is transparent in school |
| Q3 | B1 | Accountability | Leadership regularly reviews NEP implementation |
| Q4 | B2 | Availability | Resources (human, physical, financial) available for NEP |
| Q5 | B2 | Capacity building | Planned efforts for teacher and staff capacity building |
| Q6 | B2 | Support | Time and support provided for new initiatives |
| Q7 | B3 | Culture | Positive culture of accepting change and learning exists |
| Q8 | B3 | Psychological Safety | Failure seen as learning opportunity |
| Q9 | B3 | Innovation | Teachers and staff encouraged to experiment |
| Q10 | B4 | Clarity | NEP processes documented in school |
| Q11 | B4 | Consistency | Consistency maintained in process implementation |
| Q12 | B4 | Feedback loops | Feedback used to improve systems |
| Q13 | B5 | Indicators | Clear indicators defined for measuring NEP progress |
| Q14 | B5 | Review | Regular reviews lead to improvement decisions |
| Q15 | B5 | Communication | Review findings communicated to all stakeholders |

---

## 10. SetCode Reference

| SetCode | Lens | Language | Title | Question Count |
|---------|------|----------|-------|---------------|
| `base001` | Teacher | English | Teacher - NEP-2020 Readiness – Enablement & Systems Baseline | 19 |
| `base002` | Leader | English | Leader - NEP-2020 Readiness – Enablement & Systems Baseline | 15 |
| `base003` | Teacher | Marathi | Teacher - NEP-2020 Readiness – Enablement & Systems Baseline (Marathi) | 19 |
| `base004` | Leader | Marathi | Leader - NEP-2020 Readiness – Enablement & Systems Baseline (Marathi) | 15 |

---

## 11. Error Handling

| Scenario | Handling |
|----------|----------|
| `userTempId` not found in `UserTemp` | Set `FullName = "Unknown"`, `Role = ""`, derive `branchId` from `DiagnosticAttempt.branchId` |
| `branchId` not found in `SchoolBranches` | Set `School = ""`, `Branch = ""` |
| `branchId` not found in `Diagnostic` | Set `BranchCode = ""` |
| `selectedOption` is non-numeric or null | Score = 0 (treat as unanswered) |
| `questionMetadata.description` missing | Fall back to `DiagnosticQuestion.metadata.description` via `questionId` |
| `isSubmitted = false` | **Exclude** — only return submitted attempts |
| Area code not extractable | Skip that response (do not count towards any area) |

---

## 12. Data Volumes (Current Production)

| Metric | Value |
|--------|-------|
| Teacher submitted attempts | 609 (base001: 249, base003: 360) |
| Leader submitted attempts | 67 (base002: 25, base004: 42) |
| Total DES branches | 37 (M001–M038, with gaps) |
| Test branches | 2 (m942e, m56b0) |
| Users not found in UserTemp | ~5 (early test records) |

---

## 13. Dashboard Integration

The HTML dashboard (`baseline_dashboard.html`) consumes this API data via:

1. **Embedded data** — JSON arrays baked into the HTML at build time
2. **File upload** — user uploads a `.csv` or `.json` file
3. **Paste import** — user pastes CSV or JSON text

### 13.1 Expected Input Detection

The dashboard auto-detects format:
- Starts with `[` → JSON array
- Otherwise → CSV with header row

### 13.2 Required Field Names

The dashboard expects **exact** column/key names. Both formats are supported:

**Primary (CSV-style keys):**
```
UserId, FullName, Role, Language, School, Branch, BranchCode,
A1_Score, A1_Avg, A1_Pct, A2_Score, A2_Avg, A2_Pct, ...
OverallAvg
```

**Alternate (compact JSON keys):**
```json
{
  "uid": "...", "name": "...", "role": "...", "lang": "en",
  "school": "...", "branch": "...", "bc": "M001",
  "areas": {
    "A1": { "s": 15, "n": 5, "avg": 3.00, "pct": 75.0 },
    ...
  }
}
```

The dashboard attempts to read fields in order: `BranchCode` → `bc`, `Branch` → `branch`, `A1_Avg` → `A1_avg`, etc.

---

## 14. Sample API Responses

### 14.1 JSON — Teacher (truncated)

```json
{
  "meta": {
    "lens": "teacher",
    "areas": ["A1", "A2", "A3", "A4"],
    "totalRecords": 609,
    "generatedAt": "2026-02-09T10:30:00Z",
    "setCodes": ["base001", "base003"],
    "scoreScale": { "min": 1, "max": 4 },
    "areaDefinitions": {
      "A1": { "name": "Continuous Learning Diagnostics", "questionCount": 5, "maxScore": 20, "weightPerQuestion": 0.20, "goals": ["Access", "Usability", "Follow-through", "Collective Use", "Student Clarity"] },
      "A2": { "name": "Teacher Development & Growth Support", "questionCount": 5, "maxScore": 20, "weightPerQuestion": 0.20, "goals": ["Structure", "Safety", "Peer Learning", "Experimentation", "Growth Culture"] },
      "A3": { "name": "HPC Teacher Enablement", "questionCount": 5, "maxScore": 20, "weightPerQuestion": 0.20, "goals": ["Understanding", "Clarity", "Time", "Use", "Student Role"] },
      "A4": { "name": "Parent & Community Support", "questionCount": 4, "maxScore": 16, "weightPerQuestion": 0.25, "goals": ["Communication", "Guidance", "Facilitation", "Recognition"] }
    }
  },
  "data": [
    {
      "UserId": "697851cb82c04511c8aa53e8",
      "FullName": "Abhi Ghodekar",
      "Role": "Teacher",
      "Language": "mr",
      "School": "Myelin Model School",
      "Branch": "Myelin Cbse Primary & Secondary School",
      "BranchCode": "m942e",
      "A1_Score": 5,
      "A1_Avg": 1.00,
      "A1_Pct": 25.0,
      "A2_Score": 6,
      "A2_Avg": 1.20,
      "A2_Pct": 30.0,
      "A3_Score": 9,
      "A3_Avg": 1.80,
      "A3_Pct": 45.0,
      "A4_Score": 6,
      "A4_Avg": 1.50,
      "A4_Pct": 37.5,
      "OverallAvg": 1.38
    }
  ]
}
```

### 14.2 JSON — Leader (truncated)

```json
{
  "meta": {
    "lens": "leader",
    "areas": ["B1", "B2", "B3", "B4", "B5"],
    "totalRecords": 67,
    "generatedAt": "2026-02-09T10:30:00Z",
    "setCodes": ["base002", "base004"],
    "scoreScale": { "min": 1, "max": 4 },
    "areaDefinitions": {
      "B1": { "name": "NEP Governance & Ownership", "questionCount": 3, "maxScore": 12, "weightPerQuestion": 0.33, "goals": ["Ownership", "Translation", "Distribution"] },
      "B2": { "name": "Data-Informed Decision Culture", "questionCount": 3, "maxScore": 12, "weightPerQuestion": 0.33, "goals": ["Review", "Decisions", "Support"] },
      "B3": { "name": "Teacher Development Culture", "questionCount": 3, "maxScore": 12, "weightPerQuestion": 0.33, "goals": ["Peer Learning Circles", "Safety", "Experimentation"] },
      "B4": { "name": "HPC & Reporting Culture", "questionCount": 3, "maxScore": 12, "weightPerQuestion": 0.33, "goals": ["Purpose", "Parent Clarity", "Teacher Support"] },
      "B5": { "name": "Parent & Community Partnerships", "questionCount": 3, "maxScore": 12, "weightPerQuestion": 0.33, "goals": ["Strategy", "Activation", "Feedback"] }
    }
  },
  "data": [
    {
      "UserId": "696ddca67c028268c457d95a",
      "FullName": "Deepa Abhyankar",
      "Role": "Leader",
      "Language": "en",
      "School": "Deccan Education Society",
      "Branch": "AHILYADEVI HIGH SCHOOL FOR GIRLS",
      "BranchCode": "M001",
      "B1_Score": 8,
      "B1_Avg": 2.67,
      "B1_Pct": 66.7,
      "B2_Score": 10,
      "B2_Avg": 3.33,
      "B2_Pct": 83.3,
      "B3_Score": 10,
      "B3_Avg": 3.33,
      "B3_Pct": 83.3,
      "B4_Score": 9,
      "B4_Avg": 3.00,
      "B4_Pct": 75.0,
      "B5_Score": 9,
      "B5_Avg": 3.00,
      "B5_Pct": 75.0,
      "OverallAvg": 3.07
    }
  ]
}
```

### 14.3 CSV — Teacher (first 3 rows)

```csv
UserId,FullName,Role,Language,School,Branch,BranchCode,A1_Score,A1_Avg,A1_Pct,A2_Score,A2_Avg,A2_Pct,A3_Score,A3_Avg,A3_Pct,A4_Score,A4_Avg,A4_Pct,OverallAvg
697851cb82c04511c8aa53e8,Abhi Ghodekar,Teacher,mr,Myelin Model School,Myelin Cbse Primary & Secondary School,m942e,5,1.00,25.0,6,1.20,30.0,9,1.80,45.0,6,1.50,37.5,1.38
696dc548c6f1e9689723af89,Neha Test,Leader,en,Deccan Education Society,D.E.S. SECONDARY SCHOOL,M004,12,2.40,60.0,11,2.20,55.0,11,2.20,55.0,8,2.00,50.0,2.20
```

---

## 15. Implementation Checklist

- [ ] Create `GET /api/v1/diagnostics/baseline/teacher` endpoint
- [ ] Create `GET /api/v1/diagnostics/baseline/leader` endpoint
- [ ] Implement `format` query param (`json`/`csv`) and `Accept` header negotiation
- [ ] Implement filtering: `branchCode`, `language`, `submittedAfter`, `submittedBefore`
- [ ] Build branchCode lookup via `Diagnostic` collection (not in `SchoolBranches`)
- [ ] Implement scoring: `score = 4 - parseInt(selectedOption)`
- [ ] Implement area extraction: regex `/^([AB]\d)/` on `questionMetadata.description`
- [ ] Handle missing users (FullName = "Unknown")
- [ ] Handle missing branch info gracefully
- [ ] Only include `isSubmitted: true` attempts
- [ ] Include `meta` block in JSON response with area definitions
- [ ] CSV: quote fields containing commas
- [ ] Validate response counts match expected totals (609 teacher, 67 leader)
- [ ] Add unit tests for scoring formula and area extraction
- [ ] Add integration test with known attempt → expected output
