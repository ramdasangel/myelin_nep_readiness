# Regeneration: sri_dashboard.html

**Stage:** SRI (School Readiness Index) Composite Dashboard
**Output:** `output/sri_dashboard.html`
**Generator:** `src/compute_sri_scores.py` (computes data) + manual HTML generation

## Overview

Self-contained HTML dashboard showing the composite School Readiness Index (SRI) across 5 constructs for all 38 DES branches. Includes branch rankings, construct breakdowns, and radar charts.

## SRI Constructs

| Construct | Max Score | Data Source |
|-----------|-----------|-------------|
| C1 — Intent Readiness | 20 | Teacher + Leader intent survey responses |
| C2 — Practice Readiness | 25 | Teacher intent depth analysis (D1-D4) |
| C3 — Capacity Readiness | 20 | MathAngle cognitive probe |
| C4 — System Readiness | 20 | Baseline Stage-2 survey |
| C5 — Ecosystem Readiness | 15 | No data available (set to 0) |
| **SRI Total** | **100** | Weighted composite |

## Prerequisites

- SSH access to prod server
- mongosh credentials (see memory.md)
- Python 3.x with `openpyxl` package (`pip install openpyxl`)

## Data Dependencies

| File | Source | Description |
|------|--------|-------------|
| `assets/myelin_stat_ro/intent_teacher_english_responses.csv` | `extract_all_constructs.js` | C1+C2 teacher intent |
| `assets/myelin_stat_ro/intent_teacher_marathi_responses.csv` | `extract_all_constructs.js` | C1+C2 teacher intent (Marathi) |
| `assets/myelin_stat_ro/intent_leader_english_responses.csv` | `extract_all_constructs.js` | C1 leader intent |
| `assets/myelin_stat_ro/intent_leader_marathi_responses.csv` | `extract_all_constructs.js` | C1 leader intent (Marathi) |
| `assets/myelin_stat_ro/system_readiness_responses_detail.csv` | `extract_all_constructs.js` | C4 system readiness |
| `output/mathangle_master.csv` | `scripts/mathangle_csv_dump.py` | C3 capacity scores |

## Step-by-Step Regeneration

### Step 1: Extract all construct responses from prod

```bash
# SCP the extraction script to prod
scp -i ~/.ssh/myelin_pilot_key.pem \
  scripts/extract_all_constructs.js \
  ec2-user@13.200.74.24:~/myelin_stat_ro/

# Run on prod
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'cd ~/myelin_stat_ro && mongosh --port 27017 -u Shridhar -p "ShriDhar@Myelin" --authenticationDatabase pdea_pilot pdea_pilot < extract_all_constructs.js > constructs_output.txt 2>&1'

# Transfer ALL generated CSVs
for f in intent_teacher_english_responses.csv intent_teacher_marathi_responses.csv \
         intent_leader_english_responses.csv intent_leader_marathi_responses.csv \
         system_readiness_responses_detail.csv; do
  scp -i ~/.ssh/myelin_pilot_key.pem \
    ec2-user@13.200.74.24:~/myelin_stat_ro/$f \
    assets/myelin_stat_ro/
done
```

### Step 2: Generate MathAngle capacity scores

Follow the full pipeline in `07_mathangle_dashboard.md` Steps 1-2 to produce `output/mathangle_master.csv`.

Or if mathangle data is already up to date:
```bash
python3 scripts/mathangle_csv_dump.py
```

### Step 3: Compute SRI scores

```bash
python3 src/compute_sri_scores.py
```

This generates:
- `output/sri_branch_scores.csv` — per-branch SRI breakdown
- `output/sri_dashboard_data.json` — JSON data for the dashboard
- Updates `output/SRI_All_Constructs_Data.xlsx` with SRI Scores sheet

### Step 4: Regenerate the HTML dashboard

The `sri_dashboard.html` has SRI data embedded inline as a `const DATA=[...]` array (line 264). To regenerate:

1. Open `output/sri_dashboard_data.json`
2. Copy the JSON array from the `"main"` key
3. Replace the `const DATA=[...]` array on line 264 of `output/sri_dashboard.html`

**Note:** There is currently no automated script to rebuild the HTML from the JSON. The HTML template was generated once and the data was embedded manually.

### Step 5: Clean up prod temp files

```bash
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'rm -f ~/myelin_stat_ro/extract_all_constructs.js ~/myelin_stat_ro/constructs_output.txt'
```

## Output

- `output/sri_dashboard.html` (~43 KB, self-contained)
- `output/sri_branch_scores.csv` — branch-level SRI breakdown
- `output/sri_dashboard_data.json` — JSON data used in dashboard
- `output/SRI_All_Constructs_Data.xlsx` — Excel workbook with all constructs

## Notes

- C5 (Ecosystem Readiness) is currently not measured — always 0
- SRI_Max is 85 (not 100) because C5=15 is unavailable
- Branch codes M001-M038 derived from Diagnostic collection
