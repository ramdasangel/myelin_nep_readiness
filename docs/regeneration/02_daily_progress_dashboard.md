# Regeneration: daily_progress_dashboard.html

**Stage:** Micro-Intervention Daily Progress
**Output:** `output/daily_progress_dashboard.html`
**Generator:** `scripts/build_daily_progress_dashboard.py`

## Overview

Self-contained HTML dashboard showing daily logging activity for micro-intervention tasks. Includes KPI cards, timeline charts, FP/Depth distribution, and per-user detail tables.

## Prerequisites

- SSH access to prod server
- mongosh credentials (see memory.md)
- Python 3.x (stdlib only, no pip dependencies)

## Data Dependencies

| File | Source | Description |
|------|--------|-------------|
| `output/micro_intervention_report.csv` | `scripts/micro_intervention_report.js` | 133 users, task selections + daily log counts |
| `assets/myelin_stat_ro/daily_progress_full.csv` | `scripts/extract_daily_progress_full.js` | Per-user daily task logs with timestamps |

## Step-by-Step Regeneration

### Step 1: Extract micro-intervention task mappings from prod

```bash
# SCP the script to prod
scp -i ~/.ssh/myelin_pilot_key.pem \
  scripts/micro_intervention_report.js \
  ec2-user@13.200.74.24:~/myelin_stat_ro/

# Run on prod
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'cd ~/myelin_stat_ro && mongosh --port 27017 -u Shridhar -p "ShriDhar@Myelin" --authenticationDatabase pdea_pilot pdea_pilot < micro_intervention_report.js > mi_output.txt 2>&1'

# Transfer the generated CSV
scp -i ~/.ssh/myelin_pilot_key.pem \
  ec2-user@13.200.74.24:~/myelin_stat_ro/micro_intervention_report.csv \
  output/micro_intervention_report.csv
```

### Step 2: Extract daily progress logs from prod

```bash
# SCP the script to prod
scp -i ~/.ssh/myelin_pilot_key.pem \
  scripts/extract_daily_progress_full.js \
  ec2-user@13.200.74.24:~/myelin_stat_ro/

# Run on prod
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'cd ~/myelin_stat_ro && mongosh --port 27017 -u Shridhar -p "ShriDhar@Myelin" --authenticationDatabase pdea_pilot pdea_pilot < extract_daily_progress_full.js > dp_output.txt 2>&1'

# Transfer the generated CSV
scp -i ~/.ssh/myelin_pilot_key.pem \
  ec2-user@13.200.74.24:~/myelin_stat_ro/daily_progress_full.csv \
  assets/myelin_stat_ro/daily_progress_full.csv
```

### Step 3: Build the HTML dashboard

```bash
python3 scripts/build_daily_progress_dashboard.py
```

### Step 4: Clean up prod temp files

```bash
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'rm -f ~/myelin_stat_ro/micro_intervention_report.js ~/myelin_stat_ro/extract_daily_progress_full.js ~/myelin_stat_ro/mi_output.txt ~/myelin_stat_ro/dp_output.txt'
```

## Output

- `output/daily_progress_dashboard.html` (~251 KB, self-contained)
- Aggregates by user: tasks mapped, days logged, completion rate, consistency score

## Task Metadata (T01-T12)

| Code | Label | FP | Depth | Category |
|------|-------|----|-------|----------|
| T01 | Notice One Learner | FP-1 | D1-D2 | entry |
| T02 | One Adjustment | FP-1 | D2-D3 | growth |
| T03 | Change One Example | FP-2 | D1-D2 | entry |
| T04 | Ask a Why/How | FP-2 | D2-D3 | growth |
| T05 | End-of-Class Reflection | FP-3 | D1-D2 | entry |
| T06 | Try One Small Change | FP-3 | D2-D3 | growth |
| T07 | Quick Check | FP-4 | D1-D2 | entry |
| T08 | Spot One Pattern | FP-4 | D2-D3 | growth |
| T09 | Teacher Touchpoint | FP-5 | D1-D2 | entry |
| T10 | Parent Signal | FP-5 | D1-D2 | entry |
| T11 | Student Voice | FP-1 | Cross-FP | cross |
| T12 | Pause & Name | FP-4 | Cross-FP | cross |

## MongoDB Collections Used

- `UserTaskMapping` — userTempId to SelectedTasks array
- `UserDailyProgress` — UserTempId to SubmitDate + TasksProgress
- `UserTemp` — user profiles (firstName, lastName, RoleName)
- `SchoolBranches` — branch info
