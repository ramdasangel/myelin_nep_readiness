# Smart Adaptive Online Assessment — Technical Documentation

**Module:** Student Online Assessment (Adaptive Engine)
**Platform:** Myelin Education Platform
**Date:** 2026-02-20
**Source:** `docs/smart_adaptive_specs`
**Status:** Production (live as of 2026-02-19)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Collections](#2-collections)
3. [APIs](#3-apis)
4. [Adaptive Algorithm](#4-adaptive-algorithm)
5. [Data Structures](#5-data-structures)
6. [Question Flow & Lifecycle](#6-question-flow--lifecycle)
7. [Scoring & Level Progression](#7-scoring--level-progression)
8. [Subtopic Architecture](#8-subtopic-architecture)
9. [Result Object — Full Schema](#9-result-object--full-schema)
10. [Worked Example](#10-worked-example)
11. [Key Observations & Edge Cases](#11-key-observations--edge-cases)
12. [Integration Points](#12-integration-points)

---

## 1. Overview

The Smart Adaptive Online Assessment is a **student-facing, real-time adaptive testing system** that adjusts question difficulty per subtopic based on a student's running performance. Unlike the NEP readiness diagnostics (fixed questionnaire for teachers/leaders), this module targets **students** and dynamically selects questions from a question bank.

### Key Characteristics

| Attribute | Value |
|-----------|-------|
| **Target users** | Students |
| **Question format** | MCQ (4 options, single correct) |
| **Adaptation level** | Per subtopic within a subject |
| **Difficulty levels** | L0 (easiest) → L1 → L2 → L3 (hardest) |
| **Time constraint** | Configurable per question (default 60 seconds) |
| **Subjects** | Multi-subject (Hindi, English, Maths, etc.) |
| **Test types** | Adaptive, Diagnostics, Scholarship, Chapter-wise |
| **Real-time saving** | Each answer saved immediately via API |

### How It Differs From NEP Readiness Diagnostics

| Dimension | NEP Readiness Diagnostic | Smart Adaptive Test |
|-----------|-------------------------|---------------------|
| **Who takes it** | Teachers / Leaders | Students |
| **Question set** | Fixed (setCode-based) | Dynamic (adaptive engine) |
| **Difficulty** | Single level | L0–L3 per subtopic |
| **Response format** | Likert scale (SA/A/D/SD) | MCQ (single correct answer) |
| **Collections** | DiagnosticAttempt, DiagnosticQuestion | OnlineAssesmentStudentResult, OnlineAssesmentQuestions |
| **Scoring** | Area-based (FP1–FP5) | Subtopic-level with level tracking |

---

## 2. Collections

### 2.1 `OnlineAssesment`

Test definition / configuration collection.

| Field (inferred) | Type | Description |
|-------------------|------|-------------|
| `_id` | ObjectId | Test identifier (referenced as `OnlineAssesmentID` in results) |
| `Subject` | String | Subject name (e.g., "Hindi", "English") |
| `TestType` | String | "adaptive", "diagnostics", "scholarship", "chapter-wise" |
| `TotalTimePerQuestion` | Number | Seconds allowed per question |
| `SubTopics` | Array | List of subtopics included in this test |
| `ClassID` | ObjectId | Target class/grade |
| `BranchID` | ObjectId | School branch |
| `IsActive` | Boolean | Whether test is currently available |

### 2.2 `OnlineAssesmentQuestions`

Question bank. Each question belongs to a subtopic and has a difficulty level.

| Field (inferred) | Type | Description |
|-------------------|------|-------------|
| `_id` | ObjectId | Question identifier |
| `Question` | String | Question text |
| `Options` | Array | 4 MCQ options `[{ Option: String, Check: 0/1 }]` |
| `ActualAnswer` | String | Correct answer text |
| `Marks` | Number | Points for correct answer (typically 1) |
| `IsMcqFlag` | Number | 1 = MCQ format |
| `SubTopic` | String | Subtopic this question belongs to |
| `Level` | String | Difficulty level: "L0", "L1", "L2", "L3" |
| `Subject` | String | Subject |
| `AttachmentPath` | Array | Optional file attachments |

### 2.3 `OnlineAssesmentStudentResult`

Per-student, per-test attempt record. Contains the full adaptive session state and every question answered.

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | Result record ID |
| `OnlineAssesmentID` | ObjectId | Reference to `OnlineAssesment` |
| `StudentID` | ObjectId | Student who took the test |
| `BranchID` | ObjectId | School branch |
| `ClassID` | ObjectId | Class/grade |
| `Subject` | String | Subject tested |
| `EnterDate` | Date | When student started the test |
| `SubmitDate` | Date | When student submitted/finished |
| `createdAt` | Date | Record creation timestamp |
| `updatedAt` | Date | Last update timestamp |
| `SaveFlag` | Number | 1 = test saved |
| `SubmitFlag` | Number | 1 = test submitted |
| `SubmitMarksFlag` | Number | 0 = marks not finalized externally |
| `TotalObtainedMarks` | Number | Total correct answers |
| `TotalTestMarks` | Number/null | Max possible marks (null = dynamic/adaptive) |
| `TotalTimePerQuestion` | Number | Seconds per question (60) |
| `TimeLeft` | Number | Time remaining at submission (negative = exceeded) |
| `GroupID` | ObjectId/null | Optional grouping |
| `IsTestSubmitOnPortal` | Boolean | Whether submitted via web portal |
| `subTopics` | Array | **Adaptive state**: per-subtopic level and progression |
| `AssesmentResult` | Array | **Full question-by-question results** |

---

## 3. APIs

### 3.1 `GetTestTypesOfOnlineAssesment`

**Purpose:** Returns available test types for the student.

**Response (inferred):**
```json
{
  "TestTypes": [
    { "type": "adaptive", "label": "Smart Adaptive Test" },
    { "type": "diagnostics", "label": "Diagnostic Test" },
    { "type": "scholarship", "label": "Scholarship Test" },
    { "type": "chapterwise", "label": "Chapter-wise Test" }
  ]
}
```

**UI flow:** Student sees test type selection screen. Choosing "adaptive" enters the smart adaptive flow.

---

### 3.2 `GetOnlineAssesmentListByFilter`

**Purpose:** Returns available tests filtered by subject (and optionally class, branch).

**Input (inferred):**
```json
{
  "Subject": "Hindi",
  "ClassID": "5cd17817a2b82d31999dac1e",
  "BranchID": "5cd17817a2b82d31999dac12"
}
```

**Response (inferred):**
```json
{
  "assessments": [
    {
      "_id": "6996f1600753576a914c1a9f",
      "Subject": "Hindi",
      "SubTopics": ["Tenses", "Singular–Plural", "Verbs", ...],
      "TotalTimePerQuestion": 60,
      "TestType": "adaptive"
    }
  ]
}
```

**UI flow:** Student selects a subject → sees list of available adaptive tests → picks one to start.

---

### 3.3 `saveAndGetQuestionForSmartAdaptiveOnlineAssessment`

**Purpose:** The **core adaptive engine API**. Dual function:
1. **Saves** the student's answer to the current question
2. **Returns** the next question based on adaptive logic

**This is the heart of the adaptive system.** Called on every question interaction.

**Input (inferred):**
```json
{
  "OnlineAssesmentID": "6996f1600753576a914c1a9f",
  "StudentID": "5fdc4836521df02dea6b68af",
  "QuestionID": "6996f1c2f11c0425b86e55e8",
  "Answer": "tomorrow",
  "SelectedOption": { "Option": "tomorrow", "Check": 1 },
  "TimeTaken": 45
}
```

**Response (inferred):**
```json
{
  "nextQuestion": {
    "_id": "6996f1c2f11c0425b86e55ea",
    "Question": "What tense is used in...",
    "Options": [...],
    "SubTopic": "Tenses",
    "Level": "L0"
  },
  "currentSubTopic": "Tenses",
  "currentLevel": "L0",
  "questionNumber": 2,
  "totalAnswered": 1,
  "isLastQuestion": false
}
```

**Adaptive decision logic (per call):**
1. Evaluate the answer just submitted
2. Update the running subtopic state (level, sequenceNo)
3. Decide: advance level in current subtopic, move to next subtopic, or end test
4. Select the next question from the question bank matching the decided subtopic + level
5. Return the next question to the client

---

## 4. Adaptive Algorithm

### 4.1 Core Concept

The test adapts **independently per subtopic**. Each subtopic has its own difficulty trajectory:

```
                     ┌─────┐
                     │ L3  │  ← Hardest (analytical/application)
                     └──┬──┘
                        │ correct streak
                     ┌──┴──┐
                     │ L2  │  ← Hard (reasoning)
                     └──┬──┘
                        │ correct streak
                     ┌──┴──┐
                     │ L1  │  ← Medium (understanding)
                     └──┬──┘
                        │ correct streak
                     ┌──┴──┐
                     │ L0  │  ← Easy (recall/recognition)
                     └─────┘
                     START HERE
```

### 4.2 Level Definitions

| Level | Difficulty | Cognitive Demand | Example (Singular-Plural) |
|-------|-----------|-----------------|---------------------------|
| **L0** | Easy | Recall / Recognition | "What is the plural of mouse?" |
| **L1** | Medium | Understanding | "Which noun does not change in plural form?" |
| **L2** | Hard | Reasoning / Analysis | "Why don't we add -s to 'sheep'?" |
| **L3** | Hardest | Application / Evaluation | "Find the incorrect plural in this sentence" |

### 4.3 Progression Rules (inferred from data)

```
For each subtopic:
  1. Start at L0
  2. Serve questions at current level
  3. IF student answers correctly:
       → Advance to next level (L0→L1→L2→L3)
       → Serve questions at new level
       → sequenceNo increments
  4. IF student answers incorrectly:
       → Stay at current level OR stop progression
       → sequenceNo increments
  5. STOP when:
       → Student reaches L3 and answers (ceiling found)
       → Student fails at current level (floor found)
       → Maximum questions per subtopic reached
  6. Move to next subtopic
```

### 4.4 Question Allocation Pattern (observed)

| Outcome | Questions Served | Final Level | sequenceNo |
|---------|-----------------|-------------|------------|
| Student fails at L0 | 2–3 (minimum) | L0 | 3 |
| Student progresses partially | 4–6 | L1–L2 | 5–8 |
| Student reaches ceiling | 6–8+ | L2–L3 | 8 |

**Key insight:** Stronger areas get more questions (to find the ceiling), weaker areas get fewer (floor identified quickly).

---

## 5. Data Structures

### 5.1 `subTopics` Array (Adaptive State Tracker)

Stored in `OnlineAssesmentStudentResult.subTopics`. Tracks the adaptive progression per subtopic.

```json
{
  "subtopic": "Singular–Plural",
  "sequenceNo": 8,
  "level": "L2"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `subtopic` | String | Subtopic name |
| `sequenceNo` | Number | Position reached in the subtopic's question sequence. Higher = more questions served / deeper probing |
| `level` | String | Highest difficulty level reached: "L0", "L1", "L2", "L3" |

**Interpretation guide:**

| sequenceNo | level | Meaning |
|-----------|-------|---------|
| 3 | L0 | Weak — student didn't advance beyond entry level |
| 5 | L1 | Basic — passed L0, partially through L1 |
| 8 | L2 | Competent — reached reasoning level |
| 8 | L3 | Strong — reached highest difficulty |

### 5.2 `AssesmentResult` Array (Question-by-Question Detail)

Each element represents one question answered by the student.

```json
{
  "_id": { "$oid": "6996f1c2f11c0425b86e55e8" },
  "Question": "Which word signals future tense?",
  "Options": [
    { "Check": 0, "_id": null, "Option": "yesterday" },
    { "Check": 0, "_id": null, "Option": "now" },
    { "Check": 0, "_id": null, "Option": "already" },
    { "Check": 0, "_id": null, "Option": "tomorrow" }
  ],
  "Answer": "",
  "ActualAnswer": "tomorrow",
  "ObtainedMarks": 0,
  "Marks": 1,
  "IsMcqFlag": 1,
  "AttachmentPath": [],
  "File": [],
  "EditedFile": [],
  "userOptionSequence": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | Question ID (references `OnlineAssesmentQuestions`) |
| `Question` | String | Question text |
| `Options[]` | Array | 4 options with `Option` (text) and `Check` (0=not selected, 1=selected by student) |
| `Answer` | String | Student's selected answer text (empty if skipped/timed out) |
| `ActualAnswer` | String | The correct answer |
| `ObtainedMarks` | Number | 1 = correct, 0 = wrong |
| `Marks` | Number | Maximum marks for this question |
| `IsMcqFlag` | Number | 1 = MCQ type |
| `AttachmentPath` | Array | Question attachments (images, audio) |
| `File` | Array | Uploaded files (for non-MCQ) |
| `EditedFile` | Array | Modified file submissions |
| `userOptionSequence` | Array | Order in which student viewed/toggled options |

---

## 6. Question Flow & Lifecycle

### 6.1 Complete User Journey

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        STUDENT TEST JOURNEY                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────────────┐    │
│  │ Select   │──►│ Select   │──►│ Start    │──►│ Adaptive Question    │    │
│  │ Test Type│   │ Subject  │   │ Test     │   │ Loop                 │    │
│  └──────────┘   └──────────┘   └──────────┘   │                      │    │
│  GetTestTypes   GetByFilter                    │  ┌──────────────┐   │    │
│                                                │  │ Show Question│   │    │
│                                                │  └──────┬───────┘   │    │
│                                                │         │           │    │
│                                                │         ▼           │    │
│                                                │  ┌──────────────┐   │    │
│                                                │  │ Student      │   │    │
│                                                │  │ Answers      │   │    │
│                                                │  └──────┬───────┘   │    │
│                                                │         │           │    │
│                                                │         ▼           │    │
│                                                │  ┌──────────────┐   │    │
│                                                │  │ saveAndGet   │   │    │
│                                                │  │ Question API │   │    │
│                                                │  └──────┬───────┘   │    │
│                                                │         │           │    │
│                                                │    ┌────┴────┐      │    │
│                                                │    │ Adaptive │      │    │
│                                                │    │ Decision │      │    │
│                                                │    └────┬────┘      │    │
│                                                │         │           │    │
│                                                │    More questions?   │    │
│                                                │    YES ──► loop back│    │
│                                                │    NO  ──► ┌──────┐ │    │
│                                                │            │Submit│ │    │
│                                                │            └──────┘ │    │
│                                                └──────────────────────┘    │
│                                                                             │
│                                           ▼                                 │
│                                  ┌────────────────┐                         │
│                                  │ Result Screen  │                         │
│                                  │ Score + Level  │                         │
│                                  │ per Subtopic   │                         │
│                                  └────────────────┘                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Per-Question Lifecycle

```
Student sees question
        │
        ▼
Selects an option (or timer expires)
        │
        ▼
Client calls saveAndGetQuestionForSmartAdaptiveOnlineAssessment
        │
        ├─► Server saves answer to AssesmentResult[]
        ├─► Server evaluates: correct or incorrect?
        ├─► Server updates subTopics[] (level, sequenceNo)
        ├─► Server decides next subtopic + level
        ├─► Server picks next question from OnlineAssesmentQuestions
        │
        ▼
Returns next question to client (or signals test complete)
```

### 6.3 State Flags

| Flag | Value | Meaning |
|------|-------|---------|
| `SaveFlag = 0` | | Test not yet saved (in progress) |
| `SaveFlag = 1` | | Test saved (at least one answer recorded) |
| `SubmitFlag = 0` | | Test not yet submitted |
| `SubmitFlag = 1` | | Test submitted (final) |
| `SubmitMarksFlag = 0` | | Marks not externally verified |
| `SubmitMarksFlag = 1` | | Marks verified/published |

---

## 7. Scoring & Level Progression

### 7.1 Scoring Rules

| Rule | Detail |
|------|--------|
| Each question | 1 mark (all equal weight) |
| Correct answer | `ObtainedMarks = 1` when `Answer == ActualAnswer` |
| Wrong answer | `ObtainedMarks = 0` |
| Skipped/Timeout | `Answer = ""`, `ObtainedMarks = 0`, no option has `Check: 1` |
| Total score | `TotalObtainedMarks = sum(AssesmentResult[].ObtainedMarks)` |
| Max marks | `TotalTestMarks = null` for adaptive (dynamic total) |

### 7.2 Answer Detection

A student's answer is determined by:
- `Answer` field: text of the selected option
- `Options[].Check`: `1` on the selected option, `0` on others
- If `Answer = ""` and all `Check = 0`: question was skipped or timed out

### 7.3 Level Interpretation for Reporting

| Level Reached | Student Ability Band | Suggested Label |
|---------------|---------------------|-----------------|
| **L0** | Below basic | Needs significant support |
| **L1** | Basic | Developing understanding |
| **L2** | Proficient | Competent with reasoning |
| **L3** | Advanced | Strong application skills |

---

## 8. Subtopic Architecture

### 8.1 Subtopics Per Subject (example: Hindi)

From the sample result, Hindi is tested across 7 subtopics:

| # | Subtopic | Topic Category | Sample Question |
|---|----------|---------------|-----------------|
| 1 | Tenses | Grammar — Verb tenses | "Which word signals future tense?" |
| 2 | Singular–Plural | Grammar — Nouns | "What is the plural of 'mouse'?" |
| 3 | Verbs | Grammar — Verb usage | "What is the correct verb in: He ___ to school" |
| 4 | Types of Sentences | Grammar — Sentence structure | "Which sentence is asking something?" |
| 5 | Conjunctions | Grammar — Connectors | "Choose the correct use of 'although'" |
| 6 | Pronouns | Grammar — Pronouns | "Which one is a pronoun?" |
| 7 | Prepositions | Grammar — Prepositions | "Choose the correct preposition" |

### 8.2 Question Ordering Within the Test

Questions are grouped by subtopic and served sequentially. The system cycles through subtopics in order:

```
Subtopic 1 (Tenses)         → 2-3 questions at L0
Subtopic 2 (Singular-Plural) → 2-4+ questions, level advances if correct
Subtopic 3 (Verbs)          → 2-3 questions at L0
...
Subtopic 7 (Prepositions)   → 2-3 questions at L0
```

### 8.3 Questions Per Subtopic (estimated ranges)

| Student Performance | Questions Served | Levels Touched |
|--------------------|-----------------|----------------|
| All wrong at L0 | 2–3 | L0 only |
| Some correct at L0 | 3–4 | L0, L1 |
| Correct through L1 | 5–6 | L0, L1, L2 |
| Correct through L2 | 6–8 | L0, L1, L2, L3 |

---

## 9. Result Object — Full Schema

```json
{
  "_id": ObjectId,

  // ── Context ──
  "OnlineAssesmentID": ObjectId,       // Links to OnlineAssesment
  "StudentID": ObjectId,               // Links to student
  "BranchID": ObjectId,                // School branch
  "ClassID": ObjectId,                 // Class/grade
  "GroupID": ObjectId | null,          // Optional grouping
  "Subject": String,                   // "Hindi", "English", etc.

  // ── Timestamps ──
  "EnterDate": Date,                   // Test start time
  "SubmitDate": Date,                  // Test end time
  "createdAt": Date,                   // Record creation
  "updatedAt": Date,                   // Last modification

  // ── Status Flags ──
  "SaveFlag": 0 | 1,                  // Test saved
  "SubmitFlag": 0 | 1,                // Test submitted
  "SubmitMarksFlag": 0 | 1,           // Marks verified
  "IsTestSubmitOnPortal": Boolean,     // Submitted via web portal

  // ── Scoring ──
  "TotalObtainedMarks": Number,        // Total correct answers
  "TotalTestMarks": Number | null,     // Max marks (null = adaptive)
  "TotalTimePerQuestion": Number,      // Seconds per question
  "TimeLeft": Number,                  // Seconds remaining (negative = over time)

  // ── Adaptive State ──
  "subTopics": [
    {
      "subtopic": String,              // Subtopic name
      "sequenceNo": Number,            // Progression depth reached
      "level": String                  // "L0" | "L1" | "L2" | "L3"
    }
  ],

  // ── Question Results ──
  "AssesmentResult": [
    {
      "_id": ObjectId,                 // Question ID
      "Question": String,              // Question text
      "Options": [
        {
          "Option": String,            // Option text
          "Check": 0 | 1,             // 1 = selected by student
          "_id": null
        }
      ],
      "Answer": String,               // Student's answer (empty if skipped)
      "ActualAnswer": String,          // Correct answer
      "ObtainedMarks": 0 | 1,         // Correct = 1
      "Marks": Number,                // Max marks for question
      "IsMcqFlag": 0 | 1,            // 1 = MCQ
      "AttachmentPath": Array,         // Question attachments
      "File": Array,                   // Uploaded files
      "EditedFile": Array,             // Modified submissions
      "userOptionSequence": Array      // Option interaction order
    }
  ]
}
```

---

## 10. Worked Example

### 10.1 Sample Test: Hindi Adaptive (2026-02-19)

**Student:** ID `5fdc4836521df02dea6b68af`
**Test:** ID `6996f1600753576a914c1a9f`
**Duration:** ~2.5 minutes (11:39:10 → 11:41:37)
**Total Score:** 3 / 18 (16.7%)

### 10.2 Per-Subtopic Breakdown

| # | Subtopic | Qs | Correct | Wrong | Level | sequenceNo | Assessment |
|---|----------|----|---------|-------|-------|------------|------------|
| 1 | Tenses | 2 | 0 | 2 | L0 | 3 | Weak — couldn't identify tense signals |
| 2 | Singular–Plural | 4 | 2 | 2 | L2 | 8 | Competent — knew "mice", spotted "childs" error |
| 3 | Verbs | 2 | 0 | 2 | L0 | 3 | Weak — confused tenses in verb selection |
| 4 | Types of Sentences | 2 | 0 | 2 | L0 | 3 | Weak — confused questions with commands |
| 5 | Conjunctions | 2 | 0 | 2 | L0 | 3 | Weak — couldn't use "although" correctly |
| 6 | Pronouns | 4 | 1 | 3 | L3 | 8 | Mixed — identified pronouns but failed usage |
| 7 | Prepositions | 2 | 0 | 2 | L0 | 3 | Weak — wrong prepositions selected |
| **Total** | | **18** | **3** | **15** | | | |

### 10.3 Question-by-Question Detail

**Subtopic: Tenses (L0, 0/2)**

| Q# | Question | Student Answer | Correct Answer | Result |
|----|----------|---------------|----------------|--------|
| 1 | "Which word signals future tense?" | _(skipped/timeout)_ | tomorrow | Wrong |
| 2 | "What tense is used in 'I have eaten lunch'?" | Present simple | Present perfect | Wrong |

**Subtopic: Singular–Plural (L2, 2/4)**

| Q# | Question | Student Answer | Correct Answer | Result |
|----|----------|---------------|----------------|--------|
| 3 | "What is the plural of 'mouse'?" | mice | mice | Correct |
| 4 | "Which noun does not change in plural form?" | dish | deer | Wrong |
| 5 | "Why don't we add -s to 'sheep'?" | It already sounds plural | It's irregular and doesn't change | Wrong |
| 6 | "Which plural form is used incorrectly: 'The women and childs are dancing'" | childs | childs | Correct |

**Subtopic: Verbs (L0, 0/2)**

| Q# | Question | Student Answer | Correct Answer | Result |
|----|----------|---------------|----------------|--------|
| 7 | "What is the correct verb: He ___ to school every day" | went | goes | Wrong |
| 8 | "Which sentence uses a better verb?" | She went fast. | She ran fast. | Wrong |

**Subtopic: Types of Sentences (L0, 0/2)**

| Q# | Question | Student Answer | Correct Answer | Result |
|----|----------|---------------|----------------|--------|
| 9 | "Which sentence is asking something?" | Sit down. | What time is it? | Wrong |
| 10 | "Choose the sentence that shows a command" | Are you okay? | Stop shouting. | Wrong |

**Subtopic: Conjunctions (L0, 0/2)**

| Q# | Question | Student Answer | Correct Answer | Result |
|----|----------|---------------|----------------|--------|
| 11 | "Choose the correct use of 'although'" | Although played, raining we. | Although it was raining, we played. | Wrong |
| 12 | "Which sentence uses the conjunction incorrectly?" | He played and danced. | She was sad so cried. | Wrong |

**Subtopic: Pronouns (L3, 1/4)**

| Q# | Question | Student Answer | Correct Answer | Result |
|----|----------|---------------|----------------|--------|
| 13 | "Which one is a pronoun?" | Him | Him | Correct |
| 14 | "Which word can replace 'Ravi': ___ is tired" | It | He | Wrong |
| 15 | "Find the correct sentence" | Her is going. | I am a student. | Wrong |
| 16 | "Fill in the blank: Can you help ___?" | they | me | Wrong |

**Subtopic: Prepositions (L0, 0/2)**

| Q# | Question | Student Answer | Correct Answer | Result |
|----|----------|---------------|----------------|--------|
| 17 | "The bird flew ___ the sky" | over | in | Wrong |
| 18 | "The gift is ___ the table" | at | behind | Wrong |

### 10.4 Adaptive Behavior Observed

```
Tenses:          L0 ──X── (failed) → STOP after 2 Qs
Singular-Plural: L0 ──✓──► L1 ──► L2 (advanced) → 4 Qs
Verbs:           L0 ──X── (failed) → STOP after 2 Qs
Sentences:       L0 ──X── (failed) → STOP after 2 Qs
Conjunctions:    L0 ──X── (failed) → STOP after 2 Qs
Pronouns:        L0 ──✓──► L1 ──► L2 ──► L3 (advanced) → 4 Qs
Prepositions:    L0 ──X── (failed) → STOP after 2 Qs
```

---

## 11. Key Observations & Edge Cases

### 11.1 Observations

| # | Observation | Detail |
|---|-------------|--------|
| 1 | **`TotalTestMarks` is null** | Adaptive tests don't have a fixed max — total questions vary per student |
| 2 | **`TimeLeft` is negative (-894)** | Student exceeded allotted time. System still accepted answers |
| 3 | **Subtopics with same sequenceNo but different levels** | Pronouns reached L3 with 1/4 correct; Singular-Plural reached L2 with 2/4 — level progression may factor in which questions were correct (early vs late) |
| 4 | **Subject field says "Hindi" but questions are in English** | Questions are about English grammar concepts; the subject classification may refer to the curriculum context |
| 5 | **No explicit subtopic field in AssesmentResult** | Question-to-subtopic mapping must be derived from question IDs in `OnlineAssesmentQuestions` collection |
| 6 | **Options order may be randomized** | `userOptionSequence` array exists to track interaction order |

### 11.2 Edge Cases

| Case | Behavior |
|------|----------|
| Student skips a question | `Answer = ""`, all `Options[].Check = 0`, `ObtainedMarks = 0` |
| Timer expires on a question | Same as skip — treated as wrong |
| Student exits mid-test | `SaveFlag = 1`, `SubmitFlag = 0` — partial result preserved |
| All subtopics at L0 | Minimum ~14 questions (2 per subtopic × 7) |
| All subtopics at L3 | Maximum ~28+ questions (4+ per subtopic × 7) |
| Re-attempt same test | New `OnlineAssesmentStudentResult` document created |

---

## 12. Integration Points

### 12.1 Data Dependencies

```
OnlineAssesment (test config)
       │
       ├──► OnlineAssesmentQuestions (question bank)
       │         └── Filtered by Subject + SubTopic + Level
       │
       └──► OnlineAssesmentStudentResult (per attempt)
                  ├── subTopics[] (adaptive state)
                  └── AssesmentResult[] (full Q&A log)
```

### 12.2 Related Collections (from existing NEP platform)

| Collection | Relationship |
|------------|-------------|
| `UserTemp` / Students collection | `StudentID` links to student profile |
| `SchoolBranches` | `BranchID` links to school branch |
| Classes collection | `ClassID` links to grade/section |

### 12.3 Potential Dashboard Metrics

| Metric | Source | Formula |
|--------|--------|---------|
| Overall score | `TotalObtainedMarks / len(AssesmentResult)` | Percentage correct |
| Per-subtopic level | `subTopics[].level` | L0–L3 band |
| Time management | `EnterDate` → `SubmitDate` | Duration + `TimeLeft` |
| Strongest subtopics | `subTopics` where `level` = L2/L3 | Filter + sort |
| Weakest subtopics | `subTopics` where `level` = L0 | Filter + sort |
| Class-level heatmap | Aggregate `subTopics[].level` across students | Subtopic × Level matrix |
| Question difficulty | Aggregate `ObtainedMarks` per question `_id` | % students correct |
