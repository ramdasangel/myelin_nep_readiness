# Regeneration: mathangle_dashboard.html

**Stage:** MathAngle Capacity Assessment Dashboard
**Output:** `output/mathangle_dashboard.html`
**Generator:** `scripts/mathangle_html_dashboard.py`

## Overview

Self-contained HTML dashboard for the MathAngle cognitive assessment. Shows per-student competency profiles, exit level distribution, indecision scoring, and area-wise performance across math domains.

## Prerequisites

- SSH access to prod server
- mongosh credentials (see memory.md)
- Python 3.x (stdlib only for dashboard; matplotlib for PNG)

## Data Pipeline

The MathAngle data lives in the `OnlineAssesmentStudentResult` collection (NOT `DiagnosticAttempt`).
The extraction script generates 3 JSONL files via a two-step process:

1. `scripts/extract_mathangle_jsonl.js` — runs on prod, outputs marker-delimited JSONL to stdout
2. `scripts/parse_mathangle_jsonl.py` — parses the raw output into 3 JSONL files locally

## Data Dependencies

| File | Source | Description |
|------|--------|-------------|
| `/tmp/mathangle_raw.jsonl` | `extract_mathangle_jsonl.js` + `parse_mathangle_jsonl.py` | Per-student scores with chapterWise, cognitiveLevel, questionLevel |
| `/tmp/mathangle_exit_levels.jsonl` | Same pipeline | Per-topic per-level right/total for exit stage derivation |
| `/tmp/mathangle_indecision.jsonl` | Same pipeline | Per-question answer tracking and indecision metrics |

## MongoDB Collections Used

| Collection | Purpose |
|-----------|---------|
| `Diagnostic` | Find Mathangle `onlineAssesmentID` via `setCode` = "Mathangle (English)" or "Mathangle (मराठी)" |
| `OnlineAssesment` | Assessment metadata (TestName, TotalNoOfQuestions) |
| `OnlineAssesmentStudentResult` | Student responses — `AssesmentResult` array with per-question `Options`, `Answer`, `ActualAnswer`, `ObtainedMarks`, `TimeTaken` |
| `DiagnosticQuestion` | Question metadata — `metadata.subtopic`, `metadata.cognitiveLevel`, `metadata.difficultyLevel` |
| `UserTemp` | Student → firstName, lastName, RoleName, selectedBranchId |
| `SchoolBranches` | Branch info (BranchName, School.SchoolName) |

## Step-by-Step Regeneration

### Step 1: Extract MathAngle data from prod

```bash
# SCP the extraction script to prod
scp -i ~/.ssh/myelin_pilot_key.pem \
  scripts/extract_mathangle_jsonl.js \
  ec2-user@13.200.74.24:~/myelin_stat_ro/

# Run on prod
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'cd ~/myelin_stat_ro && mongosh --port 27017 -u Shridhar -p "ShriDhar@Myelin" --authenticationDatabase pdea_pilot pdea_pilot < extract_mathangle_jsonl.js > mathangle_extraction.txt 2>&1'

# Transfer output
scp -i ~/.ssh/myelin_pilot_key.pem \
  ec2-user@13.200.74.24:~/myelin_stat_ro/mathangle_extraction.txt \
  assets/myelin_stat_ro/mathangle_extraction.txt
```

### Step 2: Clean mongosh prompts and parse into JSONL

The raw output contains mongosh connection headers and `pdea_pilot>` prompts. Clean them:

```bash
# Clean the output (strip mongosh prompts and headers)
cat assets/myelin_stat_ro/mathangle_extraction.txt | \
  sed 's/^pdea_pilot> //' | \
  sed 's/^\(\.\.\. \)*//' | \
  sed '/^Current Mongosh/d' | \
  sed '/^Connecting to:/d' | \
  sed '/^Using MongoDB/d' | \
  sed '/^Using Mongosh/d' | \
  sed '/^For mongosh/d' > assets/myelin_stat_ro/mathangle_extraction_clean.txt

# Rename clean version
mv assets/myelin_stat_ro/mathangle_extraction_clean.txt assets/myelin_stat_ro/mathangle_extraction.txt

# Parse into 3 JSONL files
python3 scripts/parse_mathangle_jsonl.py
```

This produces:
- `/tmp/mathangle_raw.jsonl` (111 lines)
- `/tmp/mathangle_exit_levels.jsonl` (111 lines)
- `/tmp/mathangle_indecision.jsonl` (111 lines)

### Step 3: Build the HTML dashboard

```bash
python3 scripts/mathangle_html_dashboard.py
```

### Step 4: (Optional) Generate CSV reports

```bash
# Per-question CSV dump + master CSV
python3 scripts/mathangle_csv_dump.py

# Ranking report
python3 scripts/mathangle_ranking.py

# PNG dashboard (requires matplotlib)
python3 scripts/mathangle_dashboard.py
```

These produce:
- `output/mathangle_master.csv` — 111 rows, 69 columns
- `output/mathangle_per_question.csv` — per-question breakdown
- `output/mathangle_branch_summary.csv` — 29 branches
- `output/mathangle_exit_levels.csv` — exit level per student
- `output/mathangle_ranking.csv` — ranked student list
- `output/mathangle_assessment_dashboard.png` — visual report

### Step 5: Clean up prod temp files

```bash
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'rm -f ~/myelin_stat_ro/extract_mathangle_jsonl.js ~/myelin_stat_ro/mathangle_extraction.txt'
```

## Output

- `output/mathangle_dashboard.html` (~134 KB, self-contained)
- Student profiles, area performance, exit level distribution
- Indecision scoring analysis

## Competency Area Mapping

| Area | Subtopics |
|------|-----------|
| Addition & Subtraction | Addition, Subtraction |
| Multiplication | Multiplication |
| Division | Division |
| Factors & Multiples | LCM, Divisibility Tests |
| Geometry | Types of angles/shapes, Measuring angles |
| Measurement | Length measurement, conversion |
| Money | Currency, operations on money |
| Time & Calendar | Minutes/Hours/Seconds |

## Exit Level Mapping

| Level | NEP Stage | Question Difficulty |
|-------|-----------|---------------------|
| Below Foundational | Pre-FP | Failed all levels |
| Foundational | FP | Passed Level 1 |
| Preparatory | Preparatory | Passed Level 2 |
| Middle | Middle school | Passed Level 3 |

## Key Technical Details

- **Assessment System:** MathAngle uses `OnlineAssesment` / `OnlineAssesmentStudentResult` — NOT `DiagnosticAttempt`
- **SetCodes:** `"Mathangle (English)"` and `"Mathangle (मराठी)"`
- **DiagnosticType:** `COGNITIVE & COMPUTATIONAL THINKING` (312 diagnostics, 78 unique assessments)
- **OnlineAssesmentID:** Stored as ObjectId — must NOT convert to string for MongoDB queries
- **SubmitFlag:** Numeric (1=submitted, 0=not submitted) — NOT boolean
- **111 submitted results** across 121 distinct students (29 branches)
- **11 questions per assessment** (adaptive)
- JSONL files are written to `/tmp/` locally — not persisted in git
- Marathi question names are mapped to English equivalents via `CHAPTER_MAP` and `SUBTOPIC_MAP`
