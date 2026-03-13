# Regeneration: mathangle_dashboard.html

**Stage:** MathAngle Capacity Assessment Dashboard
**Output:** `output/mathangle_dashboard.html`
**Generator:** `scripts/mathangle_html_dashboard.py`

## Overview

Self-contained HTML dashboard for the MathAngle cognitive assessment. Shows per-student competency profiles, exit level distribution, indecision scoring, and area-wise performance across math domains.

## Prerequisites

- SSH access to prod server
- mongosh credentials (see memory.md)
- Python 3.x (stdlib only, no pip dependencies)

## Data Dependencies

| File | Source | Description |
|------|--------|-------------|
| `/tmp/mathangle_raw.jsonl` | `scripts/extract_capacity_questions.js` | Per-student question-level response data |
| `/tmp/mathangle_exit_levels.jsonl` | `scripts/extract_capacity_questions.js` | Exit level computations per student |
| `/tmp/mathangle_indecision.jsonl` | `scripts/extract_capacity_questions.js` | Indecision index calculations |

## Step-by-Step Regeneration

### Step 1: Extract MathAngle assessment data from prod

```bash
# SCP the extraction script to prod
scp -i ~/.ssh/myelin_pilot_key.pem \
  scripts/extract_capacity_questions.js \
  ec2-user@13.200.74.24:~/myelin_stat_ro/

# Run on prod (generates JSONL files in /tmp/)
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'cd ~/myelin_stat_ro && mongosh --port 27017 -u Shridhar -p "ShriDhar@Myelin" --authenticationDatabase pdea_pilot pdea_pilot < extract_capacity_questions.js > capacity_output.txt 2>&1'

# Transfer JSONL files
scp -i ~/.ssh/myelin_pilot_key.pem \
  ec2-user@13.200.74.24:/tmp/mathangle_raw.jsonl \
  /tmp/mathangle_raw.jsonl

scp -i ~/.ssh/myelin_pilot_key.pem \
  ec2-user@13.200.74.24:/tmp/mathangle_exit_levels.jsonl \
  /tmp/mathangle_exit_levels.jsonl

scp -i ~/.ssh/myelin_pilot_key.pem \
  ec2-user@13.200.74.24:/tmp/mathangle_indecision.jsonl \
  /tmp/mathangle_indecision.jsonl
```

### Step 2: Build the HTML dashboard

```bash
python3 scripts/mathangle_html_dashboard.py
```

### Step 3: (Optional) Generate CSV reports

```bash
# Per-question CSV dump
python3 scripts/mathangle_csv_dump.py

# Ranking report
python3 scripts/mathangle_ranking.py

# PNG dashboard (requires matplotlib)
python3 scripts/mathangle_dashboard.py
```

These produce:
- `output/mathangle_master.csv` — master data with all scores
- `output/mathangle_per_question.csv` — per-question breakdown
- `output/mathangle_branch_summary.csv` — branch-level summary
- `output/mathangle_exit_levels.csv` — exit level per student
- `output/mathangle_ranking.csv` — ranked student list
- `output/mathangle_assessment_dashboard.png` — visual report (matplotlib)

### Step 4: Clean up prod temp files

```bash
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'rm -f ~/myelin_stat_ro/extract_capacity_questions.js ~/myelin_stat_ro/capacity_output.txt /tmp/mathangle_*.jsonl'
```

## Output

- `output/mathangle_dashboard.html` (~136 KB, self-contained)
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

| Level | NEP Stage | Threshold |
|-------|-----------|-----------|
| Below Foundational | Pre-FP | Lowest tier |
| Foundational | FP | Basic competency |
| Preparatory | Preparatory | Intermediate |
| Middle | Middle school | Advanced |

## Notes

- JSONL files are written to `/tmp/` on both prod and local — not persisted
- The `mathangle_html_dashboard.py` script has hardcoded paths to `/tmp/` for input
- Marathi question names are mapped to English equivalents via `CHAPTER_MAP` and `SUBTOPIC_MAP`
