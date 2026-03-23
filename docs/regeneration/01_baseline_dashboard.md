# Regeneration: baseline_dashboard.html

**Stage:** Stage-2 Practice Diagnostics (Baseline Survey)
**Output:** `output/baseline_dashboard.html`
**Generator:** `scripts/build_html_dashboard.py`

## Overview

Self-contained HTML dashboard showing Teacher (A1-A4) and Leader (B1-B5) baseline survey scores with charts, heatmaps, and per-user statistics. Supports CSV/JSON import for updated data.

## Prerequisites

- SSH access to prod server
- mongosh credentials (see memory.md)
- Python 3.x (stdlib only, no pip dependencies)

## Data Dependencies

| File | Source | Description |
|------|--------|-------------|
| `output/baseline_scores_teacher.csv` | `src/baseline_dashboard_generator.py` | Per-user area scores (A1-A4) for 609 teachers |
| `output/baseline_scores_leader.csv` | `src/baseline_dashboard_generator.py` | Per-user area scores (B1-B5) for 67 leaders |

## Step-by-Step Regeneration

### Step 1: Extract baseline responses from prod

```bash
# SCP the extraction script to prod
scp -i $SSH_KEY \
  scripts/extract_baseline_v2.js \
  $PROD_USER@$PROD_HOST:~/myelin_stat_ro/

# Run on prod via SSH
ssh -i $SSH_KEY $PROD_USER@$PROD_HOST \
  'cd ~/myelin_stat_ro && mongosh --port 27017 -u $MONGO_USER -p $MONGO_PASS --authenticationDatabase pdea_pilot pdea_pilot < extract_baseline_v2.js > baseline_output.txt 2>&1'

# Transfer output back
scp -i $SSH_KEY \
  $PROD_USER@$PROD_HOST:~/myelin_stat_ro/baseline_output.txt \
  data/baseline_responses.json
```

### Step 2: Generate per-user area score CSVs

```bash
python3 src/baseline_dashboard_generator.py
```

This reads `data/baseline_responses.json` and writes:
- `output/baseline_scores_teacher.csv`
- `output/baseline_scores_leader.csv`

### Step 3: Build the HTML dashboard

```bash
python3 scripts/build_html_dashboard.py
```

This reads both CSVs and embeds the data as JSON inside the HTML.

### Step 4: Clean up prod temp files

```bash
ssh -i $SSH_KEY $PROD_USER@$PROD_HOST \
  'rm -f ~/myelin_stat_ro/extract_baseline_v2.js ~/myelin_stat_ro/baseline_output.txt'
```

## Output

- `output/baseline_dashboard.html` (~330 KB, self-contained)
- Two tabs: Teacher Baseline (A1-A4) and Leader Baseline (B1-B5)
- Includes Chart.js for visualizations (loaded from CDN)

## SetCodes Used

| SetCode | Role | Language |
|---------|------|----------|
| base001 | Teacher | English |
| base003 | Teacher | Marathi |
| base002 | Leader | English |
| base004 | Leader | Marathi |

## Question Area Mapping

- **Teacher:** A1(5 Qs), A2(5 Qs), A3(5 Qs), A4(4 Qs) — derived from `metadata.description` regex `/^[AB]\d/`
- **Leader:** B1(3 Qs), B2(3 Qs), B3(3 Qs), B4(3 Qs), B5(3 Qs)
