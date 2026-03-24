# SRI Implementation Specification

> Based on three instrument PDFs in `docs/requirements/`:
> - `SRI-SystemReadinessInstrument.pdf`
> - `SRI-EcosystemReadinessInstrument.pdf`
> - `SET.pdf`

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SRI — System Readiness Index              │
├──────────────────┬──────────────────┬───────────────────────┤
│  Instrument 1    │  Instrument 2    │  Instrument 3         │
│  System Audit    │  Parent Signal   │  SET                  │
│  (Binary, 0-20)  │  (Likert, 0-7)   │  (Structural)         │
│  ✅ Implemented  │  ⏳ Awaiting data │  ✅ Implemented       │
├──────────────────┼──────────────────┼───────────────────────┤
│  SRI001 (10 Qs)  │  P1-P5 (5 Qs)   │  SET1: Orientation ×  │
│  E1-E5 + R1-R5   │  Likert 5-point  │    Practice Depth     │
│  Principal/VP/AC  │  Parents (anon)  │  SET2: Depth ×        │
│                  │                  │    Diagnostic Areas   │
│                  │                  │  Archetypes: ARCH-01  │
│                  │                  │    through ARCH-06    │
└──────────────────┴──────────────────┴───────────────────────┘
```

---

## Module Structure

```
src/sri/
├── __init__.py                  # Package docstring
├── constants.py                 # All codes, thresholds, banding rules, archetypes
├── system_readiness_audit.py    # Instrument 1: Binary scoring (0-20)
├── parent_validation.py         # Instrument 2: Likert scoring (0-7)
├── set_computation.py           # Instrument 3: SET1 + SET2 + archetypes
└── pipeline.py                  # Orchestrator: loads data → runs all 3 → outputs
```

---

## Instrument 1: System Readiness Audit

**Source:** `SRI-SystemReadinessInstrument.pdf`
**setCode:** `SRI001` | **Questions:** 10 (binary Yes/No) | **Score:** 0-20
**Respondents:** Principal + VP + Academic Coordinator
**DB Status:** 6 submitted attempts in DiagnosticAttempt

### Sections

| Section | Code | Items | Score Range |
|---|---|---|---|
| A: Teacher Enablement | E1-E5 | 5 | 0-10 |
| B: Leadership Routines | R1-R5 | 5 | 0-10 |

### Scoring Formula

```
EnablementIndex = (E1 + E2 + E3 + E4 + E5) / 5
TeacherEnablement(0-10) = 10 × EnablementIndex

RoutineIndex = (R1 + R2 + R3 + R4 + R5) / 5
LeadershipRoutines(0-10) = 10 × RoutineIndex

SystemReadiness(0-20) = TeacherEnablement + LeadershipRoutines
```

### Interpretation Bands

| Score | Band |
|---|---|
| 0-5 | Structural absence |
| 6-10 | Emerging structure |
| 11-15 | Partially institutionalised |
| 16-20 | Operationalised structure |

### Questions (E1-E5: Teacher Enablement)

| Code | Question | Why It Matters |
|---|---|---|
| E1 | Formally scheduled weekly planning period for teachers? | Protected time is precondition for D3/D4 practice |
| E2 | Recurring monthly academic review meeting on teaching quality? | Signals structured pedagogical review |
| E3 | Structured access to student performance insights beyond marks? | Enables diagnostic teaching |
| E4 | Defined mechanism to protect instructional time from admin interruptions? | Reduces friction load |
| E5 | Documented directive encouraging instructional experimentation? | Legitimises adaptive practice |

### Questions (R1-R5: Leadership Routines)

| Code | Question | Why It Matters |
|---|---|---|
| R1 | Structured classroom observation framework aligned to D1-D4? | Links monitoring to practice depth |
| R2 | Defined observation calendar with minimum frequency? | Ensures review consistency |
| R3 | Written feedback after observations using consistent format? | Institutionalises instructional improvement |
| R4 | Documented teacher-level intervention tracking mechanism? | Enables follow-through on improvement |
| R5 | Principal access to consolidated academic review dashboard? | Ensures oversight visibility |

### Branch Aggregation

When multiple respondents (Principal + VP + AC) per branch:
- **Majority vote** per question (Yes if ≥50% say Yes)
- Individual scores also preserved for analysis

---

## Instrument 2: Parent Validation Signal

**Source:** `SRI-EcosystemReadinessInstrument.pdf`
**Status:** ⏳ NOT YET COLLECTED — module ready, awaiting data
**Questions:** 5 (P1-P5) | **Score:** 0-7
**Respondents:** Parents (anonymous, 1 per student)

### Scoring

```
Each response → 0-1:
  Strongly Disagree = 0, Disagree = 0.25, Neutral = 0.5,
  Agree = 0.75, Strongly Agree = 1.0

ParentIndex = mean(P1, P2, P3, P4, P5)
ParentReadiness(0-7) = 7 × ParentIndex
```

### Interpretation Bands

| Score | Band |
|---|---|
| 0-2 | Weak parent alignment |
| 2-4 | Partial visibility |
| 4-6 | Strong communication & trust |
| 6-7 | High ecosystem validation |

### Sampling Rules

- Minimum 30% response rate required
- Responses anonymised
- Single response per student
- Multi-grade coverage
- If response rate < threshold → apply coverage moderation

### Questions

| Code | Question (EN) |
|---|---|
| P1 | I understand what my child is expected to learn beyond examination marks |
| P2 | I receive structured feedback on my child's strengths and areas of improvement |
| P3 | My child is asked to explain reasoning or solve problems in different ways |
| P4 | I trust my child's teacher to make instructional decisions in the best interest of learning |
| P5 | The school provides meaningful academic communication opportunities with parents |

---

## Instrument 3: SET — Structured Explanation of Translation

**Source:** `SET.pdf` (17 pages)
**Nature:** Disciplined reading grammar — NOT a score, variable, or model
**Level:** Cluster / School only — NEVER individual

### SET1: Orientation Alignment × Practice Depth

**Purpose:** Identify WHERE translation gaps exist

#### Inputs

| Input | Source | Type |
|---|---|---|
| leader_fp | Leader Orientation Survey | Categorical (FP1-FP5) |
| teacher_fp | Teacher Orientation Survey | Categorical (FP1-FP5) |
| teacher_depth | Teacher Practice Diagnostics | Ordinal (D1-D4 → 1-4) |

#### Depth Levels

| Level | Meaning |
|---|---|
| D1 | Procedural |
| D2 | Responsive |
| D3 | Diagnostic |
| D4 | Adaptive |

#### Banding Rules

| Measure | Band | Rule |
|---|---|---|
| Orientation strength | High | p ≥ 0.30 |
| | Medium | 0.15 ≤ p < 0.30 |
| | Low | p < 0.15 |
| Practice depth | Low | D < 2.2 |
| | Mid | 2.2 ≤ D < 3.0 |
| | High | D ≥ 3.0 |

#### Alignment States (per FP)

| Condition | State |
|---|---|
| Leader High + Teacher High + Depth Low | `intent_high_translation_low` |
| Teacher High + Leader Low | `teacher_led_intent` |
| Leader High + Teacher Low | `leader_led_intent` |
| Both Low | `low_attention_zone` |
| Both High + Depth High | `intent_translation_aligned` |

#### SET1 Guardrails

- No scoring
- No individual-level outputs
- No causality claims
- SET1 answers WHERE to look deeper, nothing more

---

### SET2: Practice Depth × Diagnostic Areas

**Purpose:** Explain WHY translation looks the way it does

#### Teacher Areas (A1-A4)

| Area | Name | Sub-areas |
|---|---|---|
| A1 | Continuous Learning Diagnostics | Access, Usability, FollowThrough, CollectiveUse, StudentClarity |
| A2 | Teacher Development & Growth | Structure, Safety, PeerLearning, Experimentation, GrowthCulture |
| A3 | Holistic Progress Card Enablement | Understanding, Clarity, Time, Use, StudentRole |
| A4 | Parent & Community Support | Communication, Guidance, Facilitation, Recognition |

#### Leader Areas (B1-B4)

| Area | Name | Sub-areas |
|---|---|---|
| B1 | NEP Governance & Ownership | OwnershipClarity, TranslationToAction, ResponsibilityDistribution |
| B2 | Data-Informed Decision Culture | ReviewPractice, DecisionUse, ChangeSupport |
| B3 | Teacher Development Culture | PLCRegularity, Safety, ExperimentationProtection |
| B4 | HPC & Reporting Culture | PurposeClarity, ParentOrientation, TeacherSupport |

#### Area Banding (same for teacher and leader)

| Band | Rule |
|---|---|
| Low | < 2.5 |
| Mid | 2.5 – 3.2 |
| High | > 3.2 |

#### FP → Diagnostic Area Explainability Links

| FP | Teacher Areas | Leader Areas |
|---|---|---|
| FP1 (Each Child Unique) | A1, A3 | B2, B4 |
| FP2 (Holistic/Experiential) | A3, A2 | B1, B4 |
| FP3 (Reflective Practitioner) | A2 | B3 |
| FP4 (Assessment for Learning) | A1, A3 | B2, B4 |
| FP5 (Collaboration/Community) | A4 | B1, B3 |

#### SET2 Guardrails

- Areas never redefine orientation
- Areas never create scores
- SET2 never runs without depth
- Teacher and Leader SET2 NEVER merge at individual level
- No teacher–leader response comparison
- SET2 remains explanatory, not evaluative

---

### SET Archetypes

Archetypes are sense-making constructs, NOT evaluations.

#### Core Archetypes (ARCH-01 to ARCH-06)

| ID | SET1 State | Teacher (A) | Leader (B) | Interpretation |
|---|---|---|---|---|
| ARCH-01 | intent_high_translation_low | A1↓, A3↓ | B4↓ | Shared intent, but lack of shared language limits translation |
| ARCH-02 | intent_high_translation_low | A2↓ | B3↓ | Teachers reflect but hesitate due to low safety |
| ARCH-03 | teacher_led_intent | A3↓ | B1↓ | Teachers ahead of systems; leadership not yet operational |
| ARCH-04 | leader_led_intent | A1↓ | B2↓ | Leadership intent, but weak diagnostic follow-through |
| ARCH-05 | low_attention_zone | A1↓, A2↓ | B1↓, B3↓ | NEP intent not yet in collective attention |
| ARCH-06 | intent_translation_aligned | A1↑, A2↑ | B2↑, B3↑ | Coherently aligned; focus on sustaining depth |

#### Archetype Detection Rules

- SET1 trigger: `alignment_state == <state>`
- Teacher SET2 trigger: ≥2 A-areas in Low band
- Leader SET2 trigger: ≥1 B-area in Low band
- Assign highest-confidence match (priority-ordered)
- No archetype at individual level
- Archetypes do not imply performance ranking

#### Canonical Sentence Template

```
Given [FP orientation], and observed practice depth at [Dx],
translation is shaped by [Area + specific sub-areas], indicating
that [condition], rather than intent, is the limiting factor.
```

---

## Data Pipeline

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ MongoDB      │     │ scripts/extract/ │     │ src/sri/        │
│              │────▶│                  │────▶│                 │
│ SRI001       │     │ extract_sri_     │     │ pipeline.py     │
│ DiagAttempt  │     │   audit.js       │     │   ├─ Inst 1     │
│ Intent data  │     │ extract_all_     │     │   ├─ Inst 2     │
│ Baseline     │     │   constructs.js  │     │   └─ SET        │
└──────────────┘     └──────────────────┘     └────────┬────────┘
                                                       │
                                              ┌────────▼────────┐
                                              │ output/reports/ │
                                              │ sri_v2_branch_  │
                                              │   scores.csv    │
                                              │ sri_v2_detail   │
                                              │   .json         │
                                              └─────────────────┘
```

### Running the Pipeline

```bash
# 1. Extract SRI audit data from prod
ssh -i $SSH_KEY $PROD_USER@$PROD_HOST \
  'cd ~/myelin_stat_ro && mongosh --port 27017 \
   -u $MONGO_USER -p $MONGO_PASS \
   --authenticationDatabase pdea_pilot pdea_pilot \
   < extract_sri_audit.js > sri_audit_output.txt 2>&1'

# 2. Transfer to local
scp -i $SSH_KEY $PROD_USER@$PROD_HOST:~/myelin_stat_ro/sri_audit_output.txt \
  data/extracted/constructs/sri_audit.jsonl

# 3. Run pipeline
python3 src/sri/pipeline.py
```

---

## Current Data Availability

| Instrument | Data Status | Records |
|---|---|---|
| 1. System Readiness Audit | 6 submitted attempts (SRI001) | Sparse — most branches have 0 |
| 2. Parent Validation | Not yet collected | 0 |
| 3. SET (Orientation) | Full data via intent surveys | ~3,000+ users |
| 3. SET (Practice Depth) | Full data via baseline surveys | ~1,200+ users |
| 3. SET (Diagnostic Areas) | Partial — needs area-level parsing | Depends on extraction |

---

## Key Design Principles (from SET.pdf)

1. **SET is NOT a score** — it is a structured reading grammar
2. **Never individual-level** — all outputs are cluster/school aggregated
3. **Explanatory, not evaluative** — preserves dignity, avoids blame
4. **Teacher and Leader co-exist** — never merged at individual level
5. **Areas explain depth, they do not define orientation**
6. **Archetypes are sense-making constructs, not evaluations**
7. **No causality claims** — SET1 identifies WHERE, SET2 explains WHY

---

*Implementation based on instrument specifications dated 2026-03.*
*Module: `src/sri/` | Pipeline: `src/sri/pipeline.py`*
