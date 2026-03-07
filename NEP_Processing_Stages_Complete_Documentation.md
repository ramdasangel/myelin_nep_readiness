# Project Kshitij (क्षितिज) — NEP-2020 Readiness: Complete Stage-by-Stage Documentation

**Project Owner:** Myelin
**Partner:** Deccan Education Society (DES)
**Scale:** 50+ DES schools, ~200 teachers
**Classification:** Strictly Confidential — Internal Use Only
**Document Status:** Consolidated Reference | All Stages

---

## Table of Contents

1. [Project Overview & Philosophy](#1-project-overview--philosophy)
2. [Readiness Framework](#2-readiness-framework)
3. [Stage 1 — Leadership & Teacher Orientation (Baseline)](#3-stage-1--leadership--teacher-orientation-baseline)
4. [Stage 2 — Classroom Practice Depth Baseline](#4-stage-2--classroom-practice-depth-baseline)
5. [Stage 3 — Teacher Cognitive Capacity Baseline](#5-stage-3--teacher-cognitive-capacity-baseline)
6. [Stage 4 — School Enablement & Systems Baseline](#6-stage-4--school-enablement--systems-baseline)
7. [Stage 5 — Micro-Intervention 1 & Practice Logging](#7-stage-5--micro-intervention-1--practice-logging)
8. [Stage 6 — Post-Practice Deep Diagnostic & Teacher Selection](#8-stage-6--post-practice-deep-diagnostic--teacher-selection)
9. [Stage 7 — Student Cognitive & Competency Signals](#9-stage-7--student-cognitive--competency-signals)
10. [Stage 8 — Mid-Line Self-Assessment & Champion Selection](#10-stage-8--mid-line-self-assessment--champion-selection)
11. [Stage 9 — Micro-Intervention 2 & Synthesis](#11-stage-9--micro-intervention-2--synthesis)
12. [Composite Readiness Index (SRI) Design](#12-composite-readiness-index-sri-design)
13. [Dashboard Architecture & Regeneration](#13-dashboard-architecture--regeneration)
14. [API Specifications](#14-api-specifications)
15. [Database Schema (ERD)](#15-database-schema-erd)
16. [Week-by-Week Execution Timeline](#16-week-by-week-execution-timeline)
17. [Pending Work & Action Items](#17-pending-work--action-items)

---

## 1. Project Overview & Philosophy

### 1.1 What is Project Kshitij?

Project Kshitij is designed to **measure and build NEP-2020 readiness as a layered, evolving reality** — not a single score. The project observes intent, capacity, context, action, validation, and early impact, then converts that understanding into a **living NEP-2020 Playbook**.

**Duration:** 12-week collaborative academic and research initiative
**Kicked off:** 19 January 2026

### 1.2 Core Philosophy

- No single tool gives readiness
- Readiness emerges from **intersections, sequences, and trajectories**
- Trust-based reflection is preferred over surveillance
- The playbook is **derived, not pre-designed**

**Critical Framing:** Orientation ≠ Enactment ≠ Readiness ≠ Impact

### 1.3 Project Outcomes

**For DES:**
- School-wise 100-point NEP Readiness Index
- Teacher maturity insights (via Teacher Diagnostic)
- Category-wise gaps and action priorities
- Evidence from real classroom interventions
- A research-backed NEP model for state-scale replication

**For Myelin:**
- Validation of teacher maturity (TEMM) and readiness framework
- Cluster-level data on teacher cognitive and computational capabilities
- Intervention effectiveness insights
- A replicable model for larger networks

---

## 2. Readiness Framework

### 2.1 Six Readiness Dimensions

| Layer | What It Captures |
|-------|------------------|
| Orientation | Intent and belief alignment with NEP principles |
| Classroom Practice | How NEP values translate into daily teaching |
| Teacher Cognitive Capacity | Reasoning, diagnosis, design, and decision-making ability |
| School Enablement & Systems | Institutional support structures |
| Parent Collaboration | Teacher-parent partnership quality |
| Student Learning Signals | Early competency and cognitive indicators |

### 2.2 Five Foundational Principles (FP1–FP5)

| FP | Principle | What It Means |
|----|-----------|---------------|
| FP-1 | Every Child is Unique | Recognising diversity in learners' pace, interests, abilities, and contexts. Ethically strong but operationally demanding. Often believed in before it is designed for. |
| FP-2 | Holistic & Experiential Learning | Learning beyond rote memorisation. Connecting concepts to lived experiences. The most intuitive entry point into NEP thinking. |
| FP-3 | Reflective Practitioner | Teachers regularly reflecting on instructional choices. Internally practiced but externally fragile. Reflection often exists in the mind, not in the system. |
| FP-4 | Assessment for Learning | Using assessment to understand learning gaps, not just rank students. Structurally disruptive — challenges exam, reporting, and time-table logics. |
| FP-5 | Collaboration & Community | Teachers collaborating with peers, parents as partners, community as learning resource. Structurally dependent — rarely emerges through individual effort alone. |

### 2.3 Practice Depth Bands (D1–D4)

| Band | Label | Classroom Meaning |
|------|-------|-------------------|
| D1 | Procedural | Rule-based, default, surface action |
| D2 | Responsive | Adjusts based on situation |
| D3 | Diagnostic | Uses evidence to decide next steps |
| D4 | Adaptive | Intentionally redesigns practice |

NEP-2020 readiness depends on **depth progression, not adoption**. Movement from D1/D2 toward D3/D4 indicates increasing capacity for learner self-direction.

### 2.4 15-Step Execution Framework

```
PHASE 1 — BASELINE COLLECTION
  i.   Leadership & Teacher Orientation
  ii.  Classroom Practice Depth
  iii. Teacher Cognitive Capacity (Baseline)
  iv.  School Enablement & Systems

PHASE 2 — INTERVENTION & PRACTICE
  v.   Micro-Intervention 1 (FP-Focused)
  vi.  Practice Logging & Reflection (3 Weeks)
  vii. Teacher Cognitive Capacity (Post/Deep Diagnostic)

PHASE 3 — VALIDATION & SELECTION
  viii. Selection of High-Cognition Teachers
  ix.   Student Cognitive & Competency Signals (Sample)
  x.    Teacher–Parent Collaboration
  xi.   Teacher Self-Observed Mid-Line Assessment

PHASE 4 — SYNTHESIS & PLAYBOOK
  xii.  Selection of Champion Teachers
  xiii. Micro-Intervention 2 (Teachers Only)
  xiv.  Composite Readiness Index
  xv.   NEP-2020 Playbook (Actionable, Co-Created)
```

---

## 3. Stage 1 — Leadership & Teacher Orientation (Baseline)

**Phase:** 1 | **Weeks:** 1–2 (19–28 Jan)
**Who:** School Heads / Academic Leaders + All Teachers
**SRI Construct:** Intent Readiness (Weight: 20/100)

### 3.1 Purpose

Captures the **natural attention and belief orientation** of leaders and teachers across FP1–FP5. This is the orientation layer — it reveals intent and priority, **not behaviour**.

### 3.2 School Leader NEP Readiness Survey

**Instrument:** 15 scenario-based questions + 5 Foundational Anchor questions
**Output:** FP Orientation (FP1–FP5) — No depth band (orientation only)

#### FP Orientation Key for Leaders

| Code | Principle | Core Question Leader Is Asking |
|------|-----------|-------------------------------|
| FP-1 | Every Child is Unique | "How is each learner experiencing learning?" |
| FP-2 | Holistic & Experiential Learning | "Is learning meaningful beyond textbooks?" |
| FP-3 | Teacher as Reflective Practitioner | "What is the teacher thinking, trying, learning?" |
| FP-4 | Assessment for Learning | "What does evidence tell us about learning gaps?" |
| FP-5 | Collaboration & Community | "Who else is part of the learning ecosystem?" |

#### Rubric Levels

| Level | Label | Description |
|-------|-------|-------------|
| Level 1 | NEP-Aligned | Diagnostic, learner-centered, system-aware responses |
| Level 2 | Partially Aligned | Responsive, partial awareness — on the path |
| Level 3 | Traditional | Compliance-focused, procedural, or surface-level responses |

#### Foundational Anchor Questions (Sample)

**FA1.** When a class shows uneven learning progress, what is your first response as a school leader?
- A → FP2 | B → FP1 | C → FP4 | D → FP5

**FA2.** When you visit a classroom, what makes you feel that learning is happening well?
- A → FP2 | B → FP3 | C → FP1 | D → FP4

**FA3.** What would you prioritise most if you had time for one school improvement initiative?
- A → FP4 | B → FP3 | C → FP2 | D → FP5

#### Section Questions — Leaders (Q1–Q15)

| Section | Focus Area | NEP Principle | Level 1 Answer |
|---------|-----------|---------------|----------------|
| Q1–Q3 | Each Child is Unique | FP-1 | C, C, C |
| Q4–Q6 | Diagnosing Learning Levels | FP-4 | C, D, C |
| Q7–Q9 | Competency-Based Learning | FP-2 | C, B/C, C |
| Q10–Q12 | Teacher Upskilling | FP-3 | B/C, C, C |
| Q13–Q15 | Parent-Teacher Collaboration | FP-5 | C, C, C |

**Design Note:** FP-1 dominates Level 1 answers for school leaders — NEP-aligned leadership should naturally orient toward learner-centered observation.

### 3.3 Teacher NEP Readiness Survey

**Instrument:** 15 multiple-choice questions + 5 situation-based questions
**Output:** FP Orientation (FP1–FP5) + Practice Depth Band (D1–D4)
**Languages:** English and Marathi

#### Section Questions — Teachers (Q1–Q15)

| Section | Focus Area | NEP Principle |
|---------|-----------|---------------|
| Q1–Q3 | Each Child is Unique | FP-1 |
| Q4–Q6 | Diagnosing Learning Levels | FP-4 |
| Q7–Q9 | Competency-Based Learning | FP-2 |
| Q10–Q12 | Teacher Upskilling (Reflective Practitioner) | FP-3 |
| Q13–Q15 | Parent–Teacher Collaboration | FP-5 |

#### Sample Question with FP + Depth Mapping

**Q1.** When two students learn at very different speeds, what do you usually do?

| Option | Text | FP | Depth | Rubric Level |
|--------|------|----|-------|-------------|
| A | Continue teaching at the same pace for everyone | FP-2 | D1 | Level 3 |
| B | Give extra homework to the slower learner | FP-1 | D1 | Level 3 |
| C | Provide varied support so both can progress | FP-1 | D3 | Level 1 |
| D | Ask the faster learner to help the slower one | FP-5 | D2 | Level 2 |

#### Situation-Based Questions (SQ1–SQ5)

| SQ | Scenario | Measures |
|----|----------|----------|
| SQ1 | Student consistently makes same Maths mistake | Diagnosing Learning Levels — formative assessment preference |
| SQ2 | Belief about ability ("Some children are naturally better") | FP-1 — Growth vs fixed mindset |
| SQ3 | Class finished chapter but can't apply concept to real life | FP-2 — Application vs recall orientation |
| SQ4 | Last time strategy was changed because something wasn't working | FP-3 — Actual professional adaptiveness |
| SQ5 | When parents ask what they can do to support learning at home | FP-5 — Actual vs ideal parent collaboration |

#### Quick Scoring Reference

| Question | Level 1 (Best) | Level 2 (Partial) | Level 3 (Traditional) |
|----------|----------------|--------------------|-----------------------|
| Q1 | C | D | A, B |
| Q2 | B | C | A, D |
| Q3 | C | B | A, D |
| Q4 | B | C, D | A |
| Q5 | C | B, D | A |
| Q6 | D | C | A, B |
| Q7 | C | — | A, B, D |
| Q8 | B | — | A, C, D |
| Q9 | C | — | A, B, D |
| Q10 | D | B, C | A |
| Q11 | D | B, C | A |
| Q12 | D | B, C | A |
| Q13 | D | B, C | A |
| Q14 | D | C | A, B |
| Q15 | D | C | A, B |

### 3.4 FP Scoring Logic

**FP Score Calculation:** For each respondent:
1. Map each question response (A/B/C/D) to its corresponding FP
2. Count total selections per FP
3. Result: Five FP scores (FP1–FP5), each ranging 0–15

**Interpretation Guide:**
- 12–15: Strong alignment with this philosophy
- 8–11: Moderate alignment
- 4–7: Developing alignment
- 0–3: Limited alignment — needs focused development

### 3.5 FP Mapping Format (CSV)

Two detailed CSV files track per-response FP classification:
- `school_leaders_detailed_fp_mapping.csv` (20 rows, 36 columns)
- `teachers_detailed_fp_mapping.csv` (80 rows, 36 columns)

**Column structure per file:**
```
Column 1:     user_id
Columns 2–31: Q{n}_response, Q{n}_FP (for Q1 through Q15)
Columns 32–36: FP1, FP2, FP3, FP4, FP5 (total counts)
```

**Key rule:** FP1 + FP2 + FP3 + FP4 + FP5 = 15 (total questions)

**Sample L01 Profile:**
```
Q1: C → FP1  | Q2: A → FP3  | Q3: C → FP1  | Q4: B → FP4
Q5: D → FP1  | Q6: D → FP1  | Q7: D → FP3  | Q8: A → FP2
...
Summary: FP1=4, FP2=5, FP3=3, FP4=2, FP5=1
Dominant Lens: FP2 | Blind Spot: FP5
```

### 3.6 Question Sets in Production

| SetCode | Audience | Language | Responses |
|---------|----------|----------|-----------|
| 1234 | Teachers | English | 2,671 |
| 7890 | Leaders | English | 391 |
| 103 | Teachers | Marathi | 10,945 |
| 104 | Leaders | Marathi | 1,349 |

---

## 4. Stage 2 — Classroom Practice Depth Baseline

**Phase:** 1 | **Weeks:** 2 (26 Jan–1 Feb)
**Who:** All Teachers
**SRI Construct:** Practice Readiness (Weight: 25/100)

### 4.1 Purpose

Captures **how NEP values are enacted in daily practice**. The Practice Depth survey maps teacher responses to both an FP orientation and a depth band (D1–D4).

### 4.2 Practice Depth Bands

| Band | Label | Classroom Meaning |
|------|-------|-------------------|
| D1 | Procedural | Rule-based, default, surface action |
| D2 | Responsive | Adjusts based on situation |
| D3 | Diagnostic | Uses evidence to decide next steps |
| D4 | Adaptive | Intentionally redesigns practice |

### 4.3 DA-FP Index (Depth-Adjusted FP Index)

Normalised to 0–1 scale:
- 0.25–0.40 → Procedural dominance
- 0.40–0.60 → Responsive / early diagnostic
- 0.60–0.80 → Diagnostic strength
- > 0.80 → Adaptive practice (rare, aspirational)

### 4.4 Observability Constraints

- FP1-D1 and FP1-D4 are not directly observable (by design)
- FP2-D4 is not observable (would require evidence of adaptive redesign)
- These are intentional design decisions, not instrument gaps

### 4.5 Dashboard Outputs for Practice Depth

- **Primary:** FP × Practice Depth Distribution Heatmap (cohort-level)
- **Secondary:** DA-FP Index per FP (0–1 scale)
- **Narrative:** One-line insight per FP (e.g., "High intent, low depth")

---

## 5. Stage 3 — Teacher Cognitive Capacity Baseline

**Phase:** 1 | **Weeks:** 2 (7–8 Feb)
**Who:** All Teachers
**SRI Construct:** Capacity Readiness (Weight: 20/100)

### 5.1 Purpose

Captures **how teachers reason, diagnose, design, and decide**. Teacher cognitive capacity is the limiting reagent for diagnostic and adaptive practice.

### 5.2 Task Group C — What It Measures

- How teachers reason
- How teachers diagnose student gaps
- How teachers design instructional responses
- How teachers make classroom decisions

### 5.3 Index Contribution

- High-leverage teacher identification
- Cognitive diversity mapping across clusters
- Prerequisite for Micro-Intervention 2 selection

### 5.4 Smart Adaptive Online Assessment (Student-Level)

For **students**, the platform runs a Smart Adaptive Test with the following characteristics:

| Attribute | Value |
|-----------|-------|
| Target users | Students |
| Question format | MCQ (4 options, single correct) |
| Adaptation level | Per subtopic within a subject |
| Difficulty levels | L0 (easiest) → L1 → L2 → L3 (hardest) |
| Time constraint | Configurable per question (default 60 seconds) |
| Subjects | Multi-subject (Hindi, English, Maths, etc.) |

#### Adaptive Algorithm

```
For each subtopic:
  1. Start at L0
  2. IF correct → advance level (L0→L1→L2→L3)
  3. IF incorrect → stay at current level or stop
  4. STOP when ceiling or floor found, or max questions reached
  5. Move to next subtopic
```

#### Level Definitions

| Level | Difficulty | Cognitive Demand |
|-------|-----------|-----------------|
| L0 | Easy | Recall / Recognition |
| L1 | Medium | Understanding |
| L2 | Hard | Reasoning / Analysis |
| L3 | Hardest | Application / Evaluation |

#### Scoring

| Rule | Detail |
|------|--------|
| Each question | 1 mark |
| Correct answer | ObtainedMarks = 1 |
| Wrong/skipped | ObtainedMarks = 0 |
| Total | Sum of all ObtainedMarks |

---

## 6. Stage 4 — School Enablement & Systems Baseline

**Phase:** 1 | **Weeks:** 2 (26 Jan–1 Feb)
**Who:** Teachers (experience lens) + Leaders (structure lens)
**SRI Construct:** System Readiness (Weight: 20/100)
**Question Sets:** base001 (Teacher EN), base002 (Leader EN), base003 (Teacher MR), base004 (Leader MR)

### 6.1 Interpretive Stack

```
Orientation → Practice Depth → Practice Diagnostics (this stage)
```

Practice Diagnostics explain **why** observed practice depth looks the way it does. They are the system-reality layer — never read in isolation.

### 6.2 Scoring & Banding

**Per-Question Scoring:**
| Response | Score |
|----------|-------|
| Strongly Agree | 4 |
| Agree | 3 |
| Disagree | 2 |
| Strongly Disagree | 1 |

**Formula:** `score = 4 - parseInt(selectedOption)` (selectedOption is 0-indexed)

**Area-Level Banding:**
| Band | Mean Score Range | Label |
|------|-----------------|-------|
| Band 1 | 1.0 – 1.99 | Weak enablement |
| Band 2 | 2.0 – 2.99 | Partial enablement |
| Band 3 | 3.0 – 3.49 | Adequate enablement |
| Band 4 | 3.5 – 4.0 | Strong enablement |

**API Readiness Bands:**
| Band | Average Score Range | Interpretation |
|------|-------------------|----------------|
| Strong | >= 3.50 | Systems strongly support this area |
| Moderate | 2.50 – 3.49 | Partial enablement; some gaps exist |
| Developing | 1.50 – 2.49 | Significant gaps; needs attention |
| Limited | < 1.50 | Minimal enablement; urgent action needed |

### 6.3 Teacher Lens (Areas A1–A4)

#### Area A1: Continuous Learning Diagnostics
**FP Link:** FP-4 (Assessment for Learning)

| Sub-Area | Question |
|----------|----------|
| A1.1 Access | You have access to simple tools or formats to understand students' learning levels |
| A1.2 Usability | These tools help you clearly identify what students are struggling with |
| A1.3 Follow-through | You get time or support to act on diagnostic insights |
| A1.4 Collective Use | Diagnostic insights are discussed with other teachers (meetings / Peer Learning Circles) |
| A1.5 Student Clarity | Students are informed about what they are working towards based on diagnostics |

**SET Canonical Reading Examples:**
| Depth Observation | + A1 Signal | → Reading |
|---|---|---|
| Low FP-4 depth | A1 Access ↓, Usability ↓ | Teachers value assessment but lack usable tools |
| Low FP-4 depth | A1 Follow-through ↓ | Diagnostic info exists, but no time/support to act |
| FP-4 stalls at D2 | A1 Collective Use ↓ | Assessment remains individual — no peer sense-making |

#### Area A2: Teacher Development & Growth Support
**FP Link:** FP-3 (Reflective Practitioner)

| Sub-Area | Question |
|----------|----------|
| A2.1 Structure | You have a clear plan or pathway for your professional growth aligned to NEP |
| A2.2 Safety | You have safe spaces to discuss classroom challenges openly |
| A2.3 Peer Learning | You have opportunities to learn from other teachers regularly |
| A2.4 Experimentation | You are encouraged to try new approaches without fear of evaluation |
| A2.5 Growth Culture | Teacher growth is discussed beyond annual reviews |

#### Area A3: HPC Teacher Enablement
**FP Link:** FP-4 + FP-1

| Sub-Area | Question |
|----------|----------|
| A3.1 Understanding | You clearly understand what to observe beyond marks for HPC |
| A3.2 Clarity | HPC indicators are clearly explained and documented |
| A3.3 Time | You get time to record and reflect on HPC inputs |
| A3.4 Use | HPC discussions are used to guide learning conversations |
| A3.5 Student Role | Students are involved in reflecting on their own progress |

#### Area A4: Parent & Community Support
**FP Link:** FP-5 (Collaboration & Community)

| Sub-Area | Question |
|----------|----------|
| A4.1 Communication | You feel supported in communicating learning progress to parents |
| A4.2 Guidance | You receive clear guidance on how to engage parents meaningfully |
| A4.3 Facilitation | Community interactions are facilitated by the school (not left to you alone) |
| A4.4 Recognition | Efforts to involve parents or community are recognised |

**Teacher Lens Total: 19 scored questions + 1 open reflection**

### 6.4 Leadership Lens (Areas B1–B5)

#### Area B1: NEP Governance & Ownership
**FP Link:** Cross-FP governance backbone

| Sub-Area | Question |
|----------|----------|
| B1.1 Ownership | You have a clearly identified role or team responsible for NEP implementation |
| B1.2 Translation | NEP priorities are translated into term-wise focus areas |
| B1.3 Distribution | Responsibility for NEP implementation is shared across the school |

#### Area B2: Data-Informed Decision Culture
**FP Link:** FP-4 (Assessment for Learning)

| Sub-Area | Question |
|----------|----------|
| B2.1 Review | You review learning diagnostic insights at leadership level |
| B2.2 Decisions | Academic decisions are influenced by learning trends |
| B2.3 Support | Teachers are supported when data suggests changes are needed |

#### Area B3: Teacher Development Culture (Leadership View)
**FP Link:** FP-3 + FP-5
**Note:** B3 is the leadership mirror of Teacher Area A2. Divergence signals perception gaps.

| Sub-Area | Question |
|----------|----------|
| B3.1 Peer Learning Circles | You have regular and purposeful teacher reflection forums |
| B3.2 Safety | Teachers are encouraged to share challenges without fear |
| B3.3 Experimentation | Experimentation is protected and valued by leadership |

**Cross-Read: B3 vs. Teacher A2**
| B3 (Leader View) | A2 (Teacher View) | Reading |
|---|---|---|
| High | High | Validated — growth culture is real |
| High | Low | Perception gap — leaders think safe; teachers disagree |
| Low | High | Informal support exists despite no formal structures |
| Low | Low | Confirmed gap — no growth culture either side |

#### Area B4: HPC & Reporting Culture
**FP Link:** FP-4 + FP-1
**Note:** B4 is the leadership mirror of Teacher Area A3.

| Sub-Area | Question |
|----------|----------|
| B4.1 Purpose | HPC is discussed as a learning narrative, not just reporting |
| B4.2 Parent Clarity | Parents are oriented to what HPC represents |
| B4.3 Teacher Support | Teachers are supported in shifting beyond marks-based reporting |

#### Area B5: Parent & Community Partnerships
**FP Link:** FP-5 (Collaboration & Community)
**Note:** B5 is the leadership mirror of Teacher Area A4.

| Sub-Area | Question |
|----------|----------|
| B5.1 Strategy | You have a school-level approach to parent engagement |
| B5.2 Activation | Community resources are identified and used intentionally |
| B5.3 Feedback | Parent feedback is used to improve learning processes |

**Leadership Lens Total: 15 scored questions + 1 open reflection**
**Grand Total Stage 4: 34 scored questions + 2 open reflections**

### 6.5 The Five Gap Types (Emergent from Cross-Reading)

| Gap Type | How to Detect | What It Means |
|----------|---------------|---------------|
| Tool Gap | A1 low + High FP-4 orientation | Intent exists, tools don't |
| Culture Gap | A2 Safety/Experimentation low + FP-3 stalls at D1 | Environment blocks growth |
| Comprehension Gap | A3 Understanding/Clarity low + Low FP-4 depth | HPC is form-filling, not formative |
| Structural Gap | A4 Facilitation low + Low FP-5 depth | Collaboration desired but unsupported |
| Translation Gap | All areas high + Depth still D1–D2 | System enabled but practice hasn't shifted |

### 6.6 API Endpoints for Stage 4

```
GET /api/v1/diagnostics/baseline/teacher
GET /api/v1/diagnostics/baseline/leader
```

**Common Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| format | string | json or csv |
| branchCode | string | Filter by branch (e.g. M001) |
| language | string | en, mr, or both |
| submittedAfter | ISO date | Filter by date |
| submittedBefore | ISO date | Filter by date |

**Current Production Data Volumes:**
| Metric | Value |
|--------|-------|
| Teacher submitted attempts | 609 (base001: 249, base003: 360) |
| Leader submitted attempts | 67 (base002: 25, base004: 42) |
| Total DES branches | 37 (M001–M038) |

### 6.7 SET — Structured Explanation of Translation

SET is a disciplined reading grammar — not a score, variable, or model. It explains how intent translates into practice under real school conditions.

**Interpretive Stacking Order:**
```
Orientation → Practice Depth → Practice Diagnostics (areas)
```

- Diagnostics **explain** depth; they do not define orientation
- They should never be read in isolation

**Signal Sets:**
- Signal Set 1: Orientation Alignment × Practice Depth (Where intent is shared, where enactment lags)
- Signal Set 2: Practice Depth × Practice Diagnostic Areas (Why observed depth looks the way it does)

---

## 7. Stage 5 — Micro-Intervention 1 & Practice Logging

**Phase:** 2 | **Weeks:** 3–6 (2 Feb–29 Feb)
**Who:** All Teachers
**SRI Construct:** Practice Trajectory Signals (pending instrument & UX)

### 7.1 Micro-Intervention 1 Workshops

**Rationale:** Teachers can meaningfully shift only 1–2 Foundational Principles at a time.

| Workshop | FP Focus | Participants | Core Focus |
|----------|----------|--------------|------------|
| A | FP-1 (Every Child is Unique) | Teachers + Leaders | Seeing learner diversity diagnostically |
| B | FP-2 (Holistic & Experiential) | Teachers | Redesigning learning tasks |
| C | FP-3 (Reflective Practitioner) | Teachers + Academic Leaders | Reflection, safety, adaptivity |
| D | FP-4 or FP-5 | Leaders + Select Teachers | Systems, assessment, collaboration |

### 7.2 The 12 Micro-Intervention Tasks

| Code | Task Name | FP | Depth | Description |
|------|-----------|----|-------|-------------|
| T01 | Notice One Learner | FP-1 | D1→D2 | Pick one student today and notice how they engage (not marks) |
| T02 | One Adjustment | FP-1 | D2→D3 | Make one small adjustment (pace, example, grouping) for a learner |
| T03 | Change One Example | FP-2 | D1→D2 | Replace one textbook example with a real-life/contextual one |
| T04 | Ask a Why/How | FP-2 | D2→D3 | Ask at least one "why" or "how" question during teaching |
| T05 | End-of-Class Reflection | FP-3 | D1→D2 | At end of class, mentally note one thing that worked / didn't |
| T06 | Try One Small Change | FP-3 | D2→D3 | Try one change in the next class based on your reflection |
| T07 | Quick Check | FP-4 | D1→D2 | Ask 2–3 students to explain an answer in their own words |
| T08 | Spot One Pattern | FP-4 | D2→D3 | Notice one common mistake or misunderstanding today |
| T09 | Teacher Touchpoint | FP-5 | D1→D2 | Share one classroom moment with another teacher |
| T10 | Parent Signal | FP-5 | D1→D2 | Share one positive learning observation with a parent (informal) |
| T11 | Student Voice | FP-1 | Cross-FP | Ask one student: "What helped you learn today?" |
| T12 | Pause & Name | FP-4 | Cross-FP | Pause once and name what students are doing well in learning |

**Tasks by FP:**
| FP | Task IDs |
|----|----------|
| FP-1: Every Child is Unique | T01, T02, T11 |
| FP-2: Holistic & Experiential Learning | T03, T04 |
| FP-3: Reflective Practitioner | T05, T06 |
| FP-4: Assessment for Learning | T07, T08, T12 |
| FP-5: Collaboration & Community | T09, T10 |

**Bilingual support:** All tasks available in English and Marathi.

### 7.3 Practice Logging System (PRD)

**Module:** Teacher Intervention Choice Selection & Daily Logging
**Duration:** 21-day practice window (Feb 9–29)

#### Design Principles
- Trust-based reflection over surveillance
- Minimal friction (~10 min/day)
- Bilingual (English/Marathi toggle)
- Mobile-friendly, PWA for offline support

#### Screen 1: Intervention Choice Selection

| Requirement | Priority |
|-------------|----------|
| Display all 12 tasks grouped by FP | Must |
| Teacher selects minimum 3, maximum 5 tasks | Must |
| Show running count of selected tasks | Must |
| Validate selection before submission | Must |
| Allow modification at any time during 21 days | Must |
| Save selection with timestamp | Must |

**Data captured:** Teacher ID, Selected task IDs (array of 3–5), Selection timestamp, Modification history

#### Screen 2: Daily Logging

| Requirement | Priority |
|-------------|----------|
| Show only selected interventions (3–5 tasks) | Must |
| Show current date prominently | Must |
| Checkbox to mark "Done today" per task | Must |
| Optional comment field (max 280 chars) | Must |
| Allow logging for current day only (no backdating) | Must |
| Auto-save on checkbox change | Should |

**Data captured per log:** Teacher ID, Date, Task ID, Completed (boolean), Comment (optional), Timestamp

#### Screen 3: Progress Dashboard

| Requirement | Priority |
|-------------|----------|
| Tabular view: Tasks as rows, Dates 1–21 as columns | Must |
| Cell states: Done / Not done / Future | Must |
| Completion % per task | Should |
| Overall completion % | Should |
| Hover/click on cell shows comment | Should |
| Horizontal scroll on smaller screens | Must |

**Cell visual states:**
- Green filled checkbox — Done, with comment
- Green outline checkbox — Done, no comment
- Empty checkbox — Not done (past date)
- Gray checkbox — Future date (not yet loggable)

#### Key Metrics

| Metric | Formula |
|--------|---------|
| Completion Rate | totalChecked / (totalChecked + totalUnchecked) × 100 |
| Consistency | daysLogged / min(daysSinceMapping, 21) × 100 |
| Comment Rate | totalComments / totalLogEntries × 100 |

#### Success Criteria

| Metric | Target |
|--------|--------|
| Teacher adoption | 80% of workshop participants select tasks |
| Logging consistency | 60% teachers log at least 15 of 21 days |
| Comment engagement | 30% of log entries include comments |
| System uptime | 99.5% during logging period |

### 7.4 Data Collections for Stage 5

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| `UserTaskMapping` | Task selections | userTempId, SelectedTasks[], createdAt |
| `UserDailyProgress` | Daily logs | UserTempId, SubmitDate, TasksProgress[{taskId, isChecked, comment}] |
| `MicroInterventionTasks` | Task definitions | taskCode, label (en/mr), description, FP, depth |

**Task ID Series (MongoDB ObjectIds):**

| Task | Series A (697b1e2c...) | Series B (697b1e3b...) |
|------|------------------------|------------------------|
| T01 | 697b1e2cc01f188423ea7e0f | 697b1e3bc671c89acb64125a |
| T02 | 697b1e2cc01f188423ea7e10 | 697b1e3bc671c89acb64125b |
| T03 | 697b1e2cc01f188423ea7e11 | 697b1e3bc671c89acb64125c |
| T12 | 697b1e2cc01f188423ea7e1a | 697b1e3bc671c89acb641265 |

Both series are actively used in production data.

### 7.5 Current Production Statistics (as of 2026-02-18)

| Metric | Value |
|--------|-------|
| Total mapped users (DES) | 124 (updated to 169 as of Mar 2026) |
| Active users (>=1 log) | 119 (96%) |
| Zero-log users | 5 (4%) |
| Total task-log entries | 2,994 |
| Avg days logged (active) | 5.7 |
| Global completion rate | ~88% |
| Global comment rate | ~11% |
| Teachers | ~85 |
| Leaders | ~39 |

---

## 8. Stage 6 — Post-Practice Deep Diagnostic & Teacher Selection

**Phase:** 3 | **Week:** 7 (1–7 Mar)
**Who:** All Teachers
**SRI Construct:** Capacity Readiness (post-baseline comparison)

### 8.1 Purpose

After the 21-day practice window, a **deep cognitive diagnostic** is administered to measure how teacher thinking has evolved. This enables:
- Pre/post cognitive capacity comparison
- High-cognition teacher identification
- Selection inputs for Micro-Intervention 2

### 8.2 Selection Criteria for High-Cognition Teachers

1. Post-reflection cognitive capacity score
2. Practice consistency (% of 21 days logged)
3. Parent collaboration maturity
4. Self-observed readiness and articulation

---

## 9. Stage 7 — Student Cognitive & Competency Signals

**Phase:** 3 | **Week:** 8 (8–14 Mar)
**Who:** One sample class per selected high-cognition teacher
**SRI Construct:** Ecosystem Readiness — Early Impact Signals (Weight: part of 15/100)

### 9.1 Purpose

Sample-based student diagnostics to capture **early competency and cognitive indicators**. These are downstream signals — informative but not over-weighted in the SRI.

### 9.2 Smart Adaptive Test — Full Flow

```
Student selects test type
       |
       v
Student selects subject
       |
       v
Adaptive Question Loop:
  → Show Question
  → Student answers (or timer expires)
  → saveAndGetQuestionForSmartAdaptiveOnlineAssessment API called
  → Server: save answer, evaluate, update subtopic state, select next question
  → Returns next question (or signals complete)
       |
       v
Result Screen: Score + Level per Subtopic
```

### 9.3 Key API

**`saveAndGetQuestionForSmartAdaptiveOnlineAssessment`** — Core adaptive engine:
1. Saves student's answer to current question
2. Returns next question based on adaptive logic

### 9.4 Result Schema (OnlineAssesmentStudentResult)

| Field | Description |
|-------|-------------|
| `subTopics[]` | Adaptive state: {subtopic, sequenceNo, level} per subtopic |
| `AssesmentResult[]` | Full question-by-question: {Question, Options, Answer, ActualAnswer, ObtainedMarks} |
| `TotalObtainedMarks` | Total correct answers |
| `TotalTestMarks` | null for adaptive (dynamic total) |

### 9.5 Worked Example (Hindi Adaptive, 2026-02-19)

| Subtopic | Questions | Correct | Level | Assessment |
|----------|-----------|---------|-------|------------|
| Tenses | 2 | 0 | L0 | Weak |
| Singular–Plural | 4 | 2 | L2 | Competent |
| Verbs | 2 | 0 | L0 | Weak |
| Types of Sentences | 2 | 0 | L0 | Weak |
| Conjunctions | 2 | 0 | L0 | Weak |
| Pronouns | 4 | 1 | L3 | Mixed |
| Prepositions | 2 | 0 | L0 | Weak |
| **Total** | **18** | **3** | | **16.7%** |

---

## 10. Stage 8 — Mid-Line Self-Assessment & Champion Selection

**Phase:** 3 | **Weeks:** 9–10 (15–28 Mar)

### 10.1 Teacher Self-Observed Mid-Line Assessment (Week 9)

**Status:** Instrument design pending

**Purpose:** Meta-signal — teacher's own readiness assessment after 6+ weeks of practice. Captures:
- Perceived change in practice
- Confidence in NEP principles
- Self-identified barriers and enablers

### 10.2 Champion Teacher Selection (Week 10: 22–28 Mar)

Selection based on:
1. Post-reflection cognitive capacity
2. Practice consistency (21-day log)
3. Parent collaboration maturity
4. Self-observed readiness and articulation quality

---

## 11. Stage 9 — Micro-Intervention 2 & Synthesis

**Phase:** 4 | **Weeks:** 10–12 (22 Mar–11 Apr)

### 11.1 Micro-Intervention 2 (Champion Teachers Only)

**Purpose:** Sense-making and prioritisation, not training.

**Focus Areas:**
- Value vs effort mapping of NEP practices
- Identifying high-leverage interventions
- Articulating real constraints and enablers
- Co-creating inputs for NEP-2020 Playbook

### 11.2 Composite Readiness Index (Week 11–12)

Integrates all signal types into a 100-point school-level index.

### 11.3 NEP-2020 Playbook (Week 11–12)

- FP-specific
- Role-specific (Teacher / Leader)
- Context-sensitive (school realities, not ideal conditions)
- Teacher-co-created
- Execution-tested

---

## 12. Composite Readiness Index (SRI) Design

### 12.1 Design Philosophy

- Structured synthesis of signals, **not a test score**
- No single instrument dominates
- No early signal is over-weighted
- **Trajectory matters more than absolute values**
- Contradictions are informative, not errors

### 12.2 Critical Guardrail

> *"If this number goes up by 10%, what real change does it represent in classrooms?"*
> If the answer isn't obvious → the scoring is wrong.

### 12.3 Seven Signal Types

| # | Signal Type | Status |
|---|-------------|--------|
| 1 | Orientation signals (Leader & Teacher FP attention) | Done |
| 2 | Practice depth signals (D1–D4 across FPs) | Done |
| 3 | Teacher cognitive capacity (Baseline + Post) | Done |
| 4 | System enablement signals (Teacher + Leader lenses) | Done |
| 5 | Practice trajectory signals (Reflection consistency) | Pending (instrument & UX) |
| 6 | Validation signals (Parent collaboration) | Pending (HPC API integration) |
| 7 | Early impact signals (Student cognitive sample) | Done (UX engineering pending) |
| 8 | Teacher self-observed readiness (meta-signal) | Pending |

### 12.4 Two-Layer Scoring Approach

**Layer 1: Signal Normalisation** (No judgment yet)

| Signal | Normalised As |
|--------|---------------|
| Orientation | Attention density |
| Practice | Depth distribution |
| Cognition | Capacity band |
| Reflection | Consistency index |
| Parent | Experience alignment |
| Student | Cognitive demand exposure |

**Layer 2: Readiness Constructs**

| Construct | Weight | Contributing Signals |
|-----------|--------|---------------------|
| Intent Readiness | 20 | Leader + Teacher orientation |
| Practice Readiness | 25 | Practice depth + reflection |
| Capacity Readiness | 20 | Teacher cognition (pre/post) |
| System Readiness | 20 | Enablement & leadership routines |
| Ecosystem Readiness | 15 | Parent + student signals |

No single construct exceeds 25 — avoids domination and false precision.

### 12.5 Scoring Bands

Use bands, not points:

| Band | Meaning |
|------|---------|
| Emerging | Very early readiness signals |
| Developing | Consistent but not yet embedded |
| Anchoring | Embedded in practice, not yet systemic |
| Transforming | Systemic, self-sustaining readiness |

### 12.6 Design Guardrails

- No single signal dominates
- Early signals are not over-weighted
- Trajectory matters more than absolute values
- Contradictions are treated as insight, not error
- False precision and ranking temptation are avoided

---

## 13. Dashboard Architecture & Regeneration

### 13.1 Task Mapping Dashboard

**File:** `output/task_mapping_dashboard.html`
**PRD:** `docs/PRD_task_mapping_dashboard_regeneration.md`
**Primary question:** Who selected what?

#### Architecture

```
Prod MongoDB (13.200.74.24)
       |  SCP/SSH
       v
Local Machine:
  output/micro_intervention_report.csv
       |
  scripts/build_task_mapping_dashboard.py
       |
       v
output/task_mapping_dashboard.html
```

#### Regeneration Steps

**Step 1:** Refresh `micro_intervention_report.csv` from prod:
```bash
scp -i ~/.ssh/myelin_pilot_key.pem scripts/micro_intervention_report.js ec2-user@13.200.74.24:~/myelin_stat_ro/
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  "mongosh --port 27017 -u Shridhar -p 'ShriDhar@Myelin' \
   --authenticationDatabase pdea_pilot pdea_pilot \
   --quiet ~/myelin_stat_ro/micro_intervention_report.js \
   > ~/myelin_stat_ro/micro_intervention_report.csv"
scp -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24:~/myelin_stat_ro/micro_intervention_report.csv output/micro_intervention_report.csv
```

**Step 2:** (If new users) Update `MAPPING_DATES` dictionary in builder
**Step 3:** Build:
```bash
python3 scripts/build_task_mapping_dashboard.py
```

#### Dashboard Contents (7 charts)

| Chart | Type | Description |
|-------|------|-------------|
| Task Adoption | Horizontal bar | User count per task T01–T12 |
| FP Coverage | Vertical bar | Total task selections per FP |
| Depth Intent Distribution | Doughnut | D1→D2 / D2→D3 / Cross-FP |
| Tasks Chosen per User | Bar | Distribution of selection count |
| Role Distribution | Doughnut | Teacher vs Leader vs Unknown |
| Enrollment Timeline | Bar + line | New enrollments per day + cumulative |
| FP Radar | Radar | Users covering each FP |

**KPI Row (6 metrics):** Total Users Enrolled, Users Who Logged >=1 Day, Avg Tasks/User, Teachers, Leaders, Zero Logs

### 13.2 Daily Progress Dashboard

**File:** `output/daily_progress_dashboard.html`
**PRD:** `docs/PRD_daily_progress_dashboard_regeneration.md`
**Primary question:** Who is practicing daily?

#### Architecture

```
Prod MongoDB
   |
   v (SCP/SSH)
assets/myelin_stat_ro/daily_progress_full.csv
output/micro_intervention_report.csv
   |
   v
scripts/build_daily_progress_dashboard.py
   |
   v
output/daily_progress_dashboard.html
```

#### Regeneration Steps

**Step 1:** Extract `daily_progress_full.csv` from prod:
```bash
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  "mongosh --port 27017 -u Shridhar -p 'ShriDhar@Myelin' \
   --authenticationDatabase pdea_pilot pdea_pilot \
   --quiet ~/myelin_stat_ro/extract_daily_progress_full.js \
   > ~/myelin_stat_ro/daily_progress_full.csv"
scp -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24:~/myelin_stat_ro/daily_progress_full.csv assets/myelin_stat_ro/daily_progress_full.csv
```

**Step 2:** (Conditional) Refresh `micro_intervention_report.csv` if new users enrolled
**Step 3:** Update hardcoded `today` date in builder (line 198):
```python
today = date(2026, 2, 18)  # Update to current date
```
**Step 4:** Build:
```bash
python3 scripts/build_daily_progress_dashboard.py
```

#### Dashboard Contents (8 charts)

| Chart | Type | Description |
|-------|------|-------------|
| Daily Activity Timeline | Stacked bar + line | Checked vs unchecked entries per day |
| Task Completion Rate | Horizontal bar | Completion % for each task T01–T12 |
| FP Mapped vs Logged | Grouped bar | Users mapped vs users who logged per FP |
| Depth Intent vs Logs | Grouped bar | D-level selections vs checked/unchecked logs |
| Consistency Distribution | Bar | Users by consistency band |
| Tasks Mapped vs Days Logged | Scatter | Correlation: Teacher vs Leader |
| FP Completion Rate | Radar | Completion % across 5 FPs |
| Role Comparison | Metric cards | Teacher vs Leader side-by-side stats |

**KPI Row (8 metrics):** Total Users, Active (>=1 Log), Zero Logs, Avg Days (Active), Completion Rate, Comment Rate, Avg Consistency, Total Log Entries

#### Known Limitations & Recommendations

| # | Issue | Recommendation |
|---|-------|----------------|
| 1 | Hardcoded `today` date (line 198) | Replace with `date.today()` |
| 2 | Hardcoded `MAPPING_DATES` dictionary (~120 entries) | Extract dynamically from `UserTaskMapping.CreatedAt` |
| 3 | Hardcoded header date text | Replace with `Data through {today.isoformat()}` |
| 4 | School filter hardcoded to "Deccan Education Society" | Add `--school` CLI argument |

### 13.3 Baseline Dashboard (Stage 4.3)

**File:** `baseline_dashboard.html`
**Tabs:** Teacher Lens (A1–A4) + Leadership Lens (B1–B5)

Data consumed via:
1. **Embedded data** — JSON arrays baked into HTML at build time
2. **File upload** — user uploads `.csv` or `.json`
3. **Paste import** — user pastes CSV or JSON text

---

## 14. API Specifications

### 14.1 Assessment APIs

```
POST /api/assessment/submit
GET  /api/assessment/results/{user_id}
GET  /api/assessment/cohort/{school_id}
GET  /api/analytics/fp-distribution
GET  /api/analytics/recommendations/{user_id}
GET  /api/questions/{user_type}
```

### 14.2 Practice Diagnostics Baseline APIs

```
GET /api/v1/diagnostics/baseline/teacher
GET /api/v1/diagnostics/baseline/leader
```

**Response Format:** JSON (default) or CSV via `?format=csv` or `Accept: text/csv`

**Teacher JSON Response Structure:**
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
      "UserId": "...",
      "FullName": "...",
      "Role": "Teacher",
      "Language": "mr",
      "School": "...",
      "Branch": "...",
      "BranchCode": "M001",
      "A1_Score": 15, "A1_Avg": 3.00, "A1_Pct": 75.0,
      "A2_Score": 14, "A2_Avg": 2.80, "A2_Pct": 70.0,
      "A3_Score": 16, "A3_Avg": 3.20, "A3_Pct": 80.0,
      "A4_Score": 11, "A4_Avg": 2.75, "A4_Pct": 68.75,
      "OverallAvg": 2.94
    }
  ]
}
```

### 14.3 Smart Adaptive Test APIs

```
GET  /api  GetTestTypesOfOnlineAssesment
GET  /api  GetOnlineAssesmentListByFilter
POST /api  saveAndGetQuestionForSmartAdaptiveOnlineAssessment
```

**`saveAndGetQuestionForSmartAdaptiveOnlineAssessment`** — Dual function:
1. Saves the student's current answer
2. Returns the next adaptive question

### 14.4 Action Recommendations Engine

Based on FP scores, system generates targeted interventions:

| Condition | Recommendation |
|-----------|---------------|
| FP1 < 5 | "Focus on differentiated instruction training" |
| FP2 < 6 | "Introduce experiential learning workshops" |
| FP3 < 4 | "Establish peer reflection circles" |
| FP4 < 5 | "Train on formative assessment techniques" |
| FP5 < 3 | "Design parent engagement programs" |

---

## 15. Database Schema (ERD)

### 15.1 Organization Structure

| Collection | Records | Description |
|------------|---------|-------------|
| Schools | 33 | Parent organization/school entities |
| SchoolBranches | 234 | Individual school branches |

### 15.2 People

| Collection | Records | Description |
|------------|---------|-------------|
| Users (UserTemp) | 3,056 | All user accounts (teachers, leaders, admins) |
| Teachers | 16,123 | Teacher-specific records with subject mappings |
| Students | 89,351 | Student records |

### 15.3 Kshitij Assessment Collections

| Collection | Records | Description |
|------------|---------|-------------|
| DiagnosticQuestionSet | 12 | Question set definitions |
| DiagnosticQuestion | 191 | Individual questions |
| DiagnosticAttempt | 1,308 | User attempts on question sets |
| QuestionResponse | 27,823 | Individual question responses |

### 15.4 Intervention Collections

| Collection | Records | Description |
|------------|---------|-------------|
| MicroInterventionTasks | 12 | Intervention task definitions (T01–T12) |
| UserTaskMapping | ~169 | User-task selections |
| UserDailyProgress | ~2,994 entries | Daily practice logs |

### 15.5 Entity Relationships

| Parent Collection | Child Collection | Relationship | Join Field |
|-------------------|------------------|--------------|------------|
| Schools | SchoolBranches | 1:Many | SchoolID |
| SchoolBranches | Users | 1:Many | BranchID |
| Users | DiagnosticAttempt | 1:Many | userId |
| DiagnosticQuestionSet | DiagnosticQuestion | 1:Many | questionSetId |
| DiagnosticAttempt | QuestionResponse | 1:Many | attemptId |
| MicroInterventionTasks | UserTaskMapping | 1:Many | taskId |
| Users | UserTaskMapping | 1:Many | userId |
| UserTaskMapping | UserDailyProgress | 1:Many | taskMappingId |

### 15.6 Key Query Patterns

**Get submitted baseline attempts (Teacher):**
```javascript
db.DiagnosticAttempt.find({
  setCode: { $in: ["base001", "base003"] },
  isSubmitted: true
})
```

**Build branchId → branchCode map:**
```javascript
const branchCodeMap = {};
db.Diagnostic.find({}, { branchId: 1, branchCode: 1 }).forEach(d => {
  if (d.branchId && d.branchCode) {
    branchCodeMap[d.branchId.toString()] = d.branchCode;
  }
});
```

**Note:** `SchoolBranches` does NOT have a `BranchCode` field. Branch codes must be derived from the `Diagnostic` collection. Branch codes follow `M001`–`M038` for DES schools.

### 15.7 Response Object Structure (DiagnosticAttempt)

```json
{
  "questionId": "ObjectId",
  "selectedOption": "0",
  "questionMetadata": {
    "goal": "Access",
    "description": "A1. Continuous learning diagnostics"
  },
  "options": [
    { "text": "Strongly Agree" },
    { "text": "Agree" },
    { "text": "Disagree" },
    { "text": "Strongly Disagree" }
  ]
}
```

**Area extraction:** Parse `questionMetadata.description` with regex `/^([AB]\d)/` to get area code.

---

## 16. Week-by-Week Execution Timeline

| Week | Dates | Phase | Key Activities |
|------|-------|-------|----------------|
| 1 | 19–25 Jan | Orientation & Baseline | Project kick-off, NEP orientation, Leadership & Teacher baseline (FP1–FP5) |
| 2 | 26 Jan–1 Feb | Practice & Cognitive Baselines | Classroom Practice Depth (D1–D4), Teacher Cognitive baseline, School Enablement surveys |
| 3 | 2–8 Feb | Micro-Intervention 1 | 4 cluster-level workshops (1–2 FPs each) |
| 4–6 | 9–29 Feb | Practice Logging | 3-week trust-based practice logging (~10 min/day), Parent Collaboration survey |
| 7 | 1–7 Mar | Post-Practice Diagnostic | Deep cognitive diagnostic, High-cognition teacher selection |
| 8 | 8–14 Mar | Student Signals | Sample-based student diagnostics (one class per selected teacher) |
| 9 | 15–21 Mar | Mid-Line Assessment | Teacher self-observed readiness assessment |
| 10 | 22–28 Mar | Champion Selection | Champion teacher selection, Micro-Intervention 2 |
| 11–12 | 29 Mar–11 Apr | Synthesis | Composite Readiness Index, NEP-2020 Playbook v1 |

### Fixed Milestone Dates

| Milestone | Date |
|-----------|------|
| Project Kick-off | 19 Jan |
| Leader Orientation Diagnostics | 19–21 Jan |
| Teacher Orientation Diagnostics | 22 Jan |
| Teacher Practice Diagnostics | 27–28 Jan |
| Micro-Intervention 1 (Offline) | 2–6 Feb |
| Cognitive Diagnostics (All Teachers) | 7–8 Feb |
| Practice Logging Period Begins | 9 Feb |
| Student Diagnostics (Sample) | 9–14 Feb |
| Mid-line Reflection | ~20 Feb |
| Selection for Micro-Intervention 2 | 18–19 Feb |
| Post-Practice Deep Diagnostic | 1–7 Mar |
| Student Signals | 8–14 Mar |
| Champion Selection + MI-2 | 22–28 Mar |
| Composite Readiness Index + Playbook v1 | 29 Mar–11 Apr |

---

## 17. Pending Work & Action Items

### 17.1 Blocking / Urgent

| # | Item | Owner(s) | Status |
|---|------|----------|--------|
| 1 | Practice Trajectory Signals — instrument design + UX engineering | Manoj, Swati, Neha, Sonal | Pending |
| 2 | Validation Signals — HPC API integration for parent collaboration | Manoj, Swati, Neha, Sonal | Pending |
| 3 | Early Impact Signals — UX engineering (discussed with Harshad, Chetan) | Engineering team | UX pending |
| 4 | Teacher Self-Observed Readiness — meta-signal instrument design | Manoj, Swati, Neha, Sonal | Pending |

### 17.2 Dashboard Improvements

| # | Improvement | Impact |
|---|-------------|--------|
| 1 | Replace hardcoded `today` with `date.today()` in daily progress builder | Eliminates manual date editing each run |
| 2 | Dynamically extract `MAPPING_DATES` from `UserTaskMapping.CreatedAt` | Supports new users without manual dict updates |
| 3 | Make header date dynamic | Consistent date display |
| 4 | Single-command regeneration script (`./regenerate.sh`) | One-command pipeline |
| 5 | Add `--school` CLI argument | Removes hardcoded DES filter |
| 6 | Add data validation / row-count sanity checks | Catches extraction/transfer errors early |

### 17.3 Open Design Questions

| # | Question | Source |
|---|----------|--------|
| 1 | Should there be push notifications/reminders for daily logging? | PRD |
| 2 | Should teachers see peer comparison (gamification)? | PRD |
| 3 | Integration with HPC (Holistic Progress Card) system? | PRD |
| 4 | Admin dashboard requirements for school coordinators? | PRD |

### 17.4 API Implementation Checklist (Stage 4)

- [ ] Create `GET /api/v1/diagnostics/baseline/teacher` endpoint
- [ ] Create `GET /api/v1/diagnostics/baseline/leader` endpoint
- [ ] Implement `format` query param (json/csv) and Accept header negotiation
- [ ] Implement filtering: `branchCode`, `language`, `submittedAfter`, `submittedBefore`
- [ ] Build branchCode lookup via `Diagnostic` collection
- [ ] Implement scoring: `score = 4 - parseInt(selectedOption)`
- [ ] Implement area extraction: regex `/^([AB]\d)/` on `questionMetadata.description`
- [ ] Handle missing users (FullName = "Unknown")
- [ ] Only include `isSubmitted: true` attempts
- [ ] Validate response counts (609 teacher, 67 leader)

---

## Appendix: Key Patterns & Themes Across All Stages

### Pattern 1: "Orientation ≠ Enactment" — The Intent-Practice Gap
This is the single most repeated insight. Nearly every stage warns against equating what educators *believe* with what they *do*.

### Pattern 2: Trust-Based, Non-Punitive Design
Every instrument is deliberately non-judgmental:
- Practice logging is binary and simple ("Done / Didn't get time")
- Assessments are framed as "baselines" and "reflections", never evaluations
- Micro-tasks are described as "practice noticing" — "This is not homework for teachers"

### Pattern 3: Bilingual Parity as a First-Class Requirement
English and Marathi versions exist for every instrument — not as translations but as parallel documents.

### Pattern 4: Layered Signal Architecture (No Single Score)
The project explicitly resists reducing readiness to a single number:
- 7+ signal types feeding into 5 readiness constructs
- Two-layer scoring (normalise first, construct second)
- Contradictions are treated as insight, not error

### Pattern 5: System vs. Individual Attribution
Multiple stages distinguish between what teachers can control vs. what the system constrains:
- Practice Diagnostics separate "teacher lens" (A1–A4) from "leadership lens" (B1–B5)
- FP-5 is described as "structurally dependent" — not something to blame individuals for
- SET reads low depth as system friction, not teacher resistance

---

*Consolidated by: Myelin NEP Readiness Team*
*Sources: All documentation files in DES-Kshitij-Existing Docs/, DES-Project-kshitij/, docs/, assets/myelin_stat_ro/*
*Classification: Strictly Confidential — Internal Use Only*
*All intellectual property belongs to Myelin.*