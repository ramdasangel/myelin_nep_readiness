# Regeneration: task_mapping_dashboard.html

**Stage:** Stage-5 Micro-Intervention Task Mapping
**Output:** `output/task_mapping_dashboard.html`
**Generator:** `scripts/build_task_mapping_dashboard.py`

## Overview

Self-contained HTML dashboard showing which micro-intervention tasks each DES teacher selected. Includes enrollment timeline, task adoption stats, FP coverage radar, and searchable user table.

## Prerequisites

- SSH access to prod server
- mongosh credentials (see memory.md)
- Python 3.x (stdlib only, no pip dependencies)

## Data Dependencies

| File | Source | Description |
|------|--------|-------------|
| `output/micro_intervention_report.csv` | `scripts/micro_intervention_report.js` | DES user-task selections |
| Hardcoded `MAPPING_DATES` in script | `scripts/extract_mapping_dates_v2.js` | userId to createdAt timestamp mapping |

## Step-by-Step Regeneration

### Step 1: Extract task mapping data from prod

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

### Step 2: Extract mapping timestamps (for new enrollments only)

```bash
# SCP the script to prod
scp -i ~/.ssh/myelin_pilot_key.pem \
  scripts/extract_mapping_dates_v2.js \
  ec2-user@13.200.74.24:~/myelin_stat_ro/

# Run on prod
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'cd ~/myelin_stat_ro && mongosh --port 27017 -u Shridhar -p "ShriDhar@Myelin" --authenticationDatabase pdea_pilot pdea_pilot < extract_mapping_dates_v2.js > mapping_dates.txt 2>&1'

# Transfer output
scp -i ~/.ssh/myelin_pilot_key.pem \
  ec2-user@13.200.74.24:~/myelin_stat_ro/mapping_dates.txt \
  /tmp/mapping_dates.txt
```

### Step 3: Update MAPPING_DATES in the script

Open `scripts/build_task_mapping_dashboard.py` and append any new userId-timestamp entries to the `MAPPING_DATES` dictionary (line ~26). The format is:

```python
'<userTempId>': '<ISO 8601 timestamp>',
```

### Step 4: Build the HTML dashboard

```bash
python3 scripts/build_task_mapping_dashboard.py
```

### Step 5: Clean up prod temp files

```bash
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'rm -f ~/myelin_stat_ro/micro_intervention_report.js ~/myelin_stat_ro/extract_mapping_dates_v2.js ~/myelin_stat_ro/mi_output.txt ~/myelin_stat_ro/mapping_dates.txt'
```

## Output

- `output/task_mapping_dashboard.html` (~100 KB, self-contained)
- Enrollment timeline chart, task adoption bars, FP radar
- Searchable/filterable user table with task selections

## Notes

- The `MAPPING_DATES` dict is hardcoded in the Python script because `UserTaskMapping.createdAt` was not always reliably stored. The extraction script reads the actual MongoDB timestamps.
- 5 userTempIds in UserTaskMapping don't exist in UserTemp (early test records) — these are excluded automatically.
