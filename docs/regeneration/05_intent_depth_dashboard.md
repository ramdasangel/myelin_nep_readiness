# Regeneration: intent_depth_dashboard.html

**Stage:** Stage-1 Intent Survey — Practice Depth (D1-D4)
**Output:** `output/intent_depth_dashboard.html`
**Generator:** `scripts/build_intent_depth_dashboard.py`

## Overview

Self-contained HTML dashboard showing teacher intent survey depth distribution (D1-D4) across 5 Focus Points. Includes tabbed interface with overview and per-depth teacher ranking tables.

## Depth Levels

| Level | selectedOption | Meaning |
|-------|---------------|---------|
| D1 | 0 | Surface / procedural |
| D2 | 1 | Emerging awareness |
| D3 | 2 | Applied understanding |
| D4 | 3 | Deep / strategic |

## Prerequisites

- SSH access to prod server
- mongosh credentials (see memory.md)
- Python 3.x (stdlib only, no pip dependencies)

## Data Dependencies

| File | Source | Description |
|------|--------|-------------|
| `assets/myelin_stat_ro/intent_teacher_english_responses.csv` | `scripts/extract_all_constructs.js` | English intent responses (setCode 1234) |
| `assets/myelin_stat_ro/intent_teacher_marathi_responses.csv` | `scripts/extract_all_constructs.js` | Marathi intent responses (setCode 103) |

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

# Transfer generated CSVs
scp -i ~/.ssh/myelin_pilot_key.pem \
  ec2-user@13.200.74.24:~/myelin_stat_ro/intent_teacher_english_responses.csv \
  assets/myelin_stat_ro/

scp -i ~/.ssh/myelin_pilot_key.pem \
  ec2-user@13.200.74.24:~/myelin_stat_ro/intent_teacher_marathi_responses.csv \
  assets/myelin_stat_ro/
```

### Step 2: Build the HTML dashboard

```bash
python3 scripts/build_intent_depth_dashboard.py
```

### Step 3: Clean up prod temp files

```bash
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  'rm -f ~/myelin_stat_ro/extract_all_constructs.js ~/myelin_stat_ro/constructs_output.txt'
```

## Output

- `output/intent_depth_dashboard.html` (~148 KB, self-contained)
- Tabbed interface: Overview + D1/D2/D3/D4 tabs
- Per-depth teacher ranking tables with CSV download buttons

## SetCodes Used

| SetCode | Role | Language |
|---------|------|----------|
| 1234 | Teacher | English |
| 103 | Teacher | Marathi |

## Goal to Focus Point Mapping

| Goal (English) | Goal (Marathi) | Focus Point |
|----------------|----------------|-------------|
| Each Child is Unique | - | FP-1 |
| Competency-Based Learning | - | FP-2 |
| Teacher Upskilling | - | FP-3 |
| Diagnosing Learning Levels | अध्ययन स्तरांचे निदान | FP-4 |
| Parent-Teacher Collaboration | पालक - शिक्षक सहयोग | FP-5 |

## Notes

- Marathi goal names are normalised to English equivalents in the script
- Only Teacher role is included (Leader intent is separate)
- Filters to Deccan Education Society only
