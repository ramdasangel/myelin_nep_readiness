# PRD: Daily Progress Dashboard Regeneration

**Document:** PRD-STAGE5-REGEN
**Date:** 2026-02-18
**Owner:** Myelin NEP Readiness Team
**Status:** Active
**Dashboard:** `output/daily_progress_dashboard.html`

---

## 1. Overview

The **Stage 5 — Micro-Intervention Daily Progress Dashboard** is a self-contained HTML file that visualises how 124+ Deccan Education Society (DES) users are engaging with their selected micro-intervention tasks on a daily basis. It must be regenerated periodically (ideally daily during the pilot window) so stakeholders see up-to-date KPIs, charts, and per-user detail.

This document describes the full regeneration pipeline: data sources, extraction steps, build process, hardcoded values that need updating, and known limitations.

---

## 2. Architecture

```
┌────────────────────┐      SCP/SSH       ┌──────────────────────┐
│  Prod MongoDB      │ ◄────────────────► │  Local Machine       │
│  (13.200.74.24)    │   extract script   │                      │
│                    │                    │  assets/myelin_stat_ro/│
│  Collections:      │                    │    daily_progress_    │
│  - UserDailyProgress│                   │    full.csv           │
│  - UserTemp        │                    │                      │
│  - UserTaskMapping │                    │  output/              │
│  - MicroIntervention│                   │    micro_intervention_│
│    Tasks           │                    │    report.csv         │
└────────────────────┘                    │                      │
                                          │  scripts/             │
                                          │    extract_daily_     │
                                          │    progress_full.js   │
                                          │    build_daily_       │
                                          │    progress_          │
                                          │    dashboard.py       │
                                          │                      │
                                          │  output/              │
                                          │    daily_progress_    │
                                          │    dashboard.html     │
                                          └──────────────────────┘
```

### Pipeline Summary

| Step | What | Where | Script |
|------|------|-------|--------|
| 1 | Extract raw daily-progress rows from MongoDB | Prod server | `scripts/extract_daily_progress_full.js` |
| 2 | Transfer CSV to local | SCP | — |
| 3 | Build HTML dashboard from two CSVs | Local Python | `scripts/build_daily_progress_dashboard.py` |

---

## 3. Data Sources

### 3.1 Primary: `UserDailyProgress` (MongoDB → CSV)

| Field | Description |
|-------|-------------|
| `UserTempId` | ObjectId linking to `UserTemp` |
| `SubmitDate` | Date the log was submitted |
| `CreatedAt` | Timestamp of record creation |
| `TasksProgress[]` | Array of `{ taskId, isChecked, comment }` |

**Extraction script:** `scripts/extract_daily_progress_full.js`
**Output CSV columns:** `userId, submitDate, progressCreatedAt, taskId, isChecked, hasComment`
**Output location:** `assets/myelin_stat_ro/daily_progress_full.csv`

### 3.2 Secondary: `micro_intervention_report.csv`

Pre-generated report containing user-task mappings (who selected which tasks).

| Key Fields Used | Description |
|-----------------|-------------|
| `UserId` | ObjectId |
| `FirstName`, `LastName` | User name |
| `Role` | Teacher / Leader |
| `SchoolName` | Filtered to "Deccan Education Society" |
| `BranchName`, `BranchCode` | School branch info |
| `TaskList` | Pipe-delimited task codes (e.g., `T01 - Notice One Learner \| T03 - ...`) |

**Source script:** `scripts/micro_intervention_report.js` (run on prod)
**Location:** `output/micro_intervention_report.csv`

### 3.3 Static: Task Metadata (hardcoded in builder)

12 tasks (T01–T12), each mapped to:
- **FP** (Foundational Principle): FP-1 through FP-5
- **Depth level**: D1→D2 (Entry), D2→D3 (Growth), Cross-FP
- **TaskId → TaskCode mapping**: two MongoDB ObjectId series (prefix `697b1e2c` and `697b1e3b`)

### 3.4 Static: Mapping Dates (hardcoded in builder)

A dictionary of ~120 `userId → mappingDate` entries (lines 48–110 of the builder script). Used to calculate the consistency metric (days logged / days since mapping).

---

## 4. Regeneration Steps

### Step 1: Extract `daily_progress_full.csv` from Prod

```bash
# Upload extraction script to prod
scp -i ~/.ssh/myelin_pilot_key.pem \
  scripts/extract_daily_progress_full.js \
  ec2-user@13.200.74.24:~/myelin_stat_ro/

# Run mongosh extraction
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  "mongosh --port 27017 -u Shridhar -p 'ShriDhar@Myelin' \
   --authenticationDatabase pdea_pilot pdea_pilot \
   --quiet ~/myelin_stat_ro/extract_daily_progress_full.js \
   > ~/myelin_stat_ro/daily_progress_full.csv"

# Download CSV to local
scp -i ~/.ssh/myelin_pilot_key.pem \
  ec2-user@13.200.74.24:~/myelin_stat_ro/daily_progress_full.csv \
  assets/myelin_stat_ro/daily_progress_full.csv

# Cleanup prod temp files
ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  "rm ~/myelin_stat_ro/extract_daily_progress_full.js \
      ~/myelin_stat_ro/daily_progress_full.csv"
```

### Step 2: (Conditional) Refresh `micro_intervention_report.csv`

Only needed if **new users have mapped tasks** since the last build.

```bash
scp -i ~/.ssh/myelin_pilot_key.pem \
  scripts/micro_intervention_report.js \
  ec2-user@13.200.74.24:~/myelin_stat_ro/

ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  "mongosh --port 27017 -u Shridhar -p 'ShriDhar@Myelin' \
   --authenticationDatabase pdea_pilot pdea_pilot \
   --quiet ~/myelin_stat_ro/micro_intervention_report.js \
   > ~/myelin_stat_ro/micro_intervention_report.csv"

scp -i ~/.ssh/myelin_pilot_key.pem \
  ec2-user@13.200.74.24:~/myelin_stat_ro/micro_intervention_report.csv \
  output/micro_intervention_report.csv

ssh -i ~/.ssh/myelin_pilot_key.pem ec2-user@13.200.74.24 \
  "rm ~/myelin_stat_ro/micro_intervention_report.js \
      ~/myelin_stat_ro/micro_intervention_report.csv"
```

### Step 3: Update Hardcoded Values in Builder

Edit `scripts/build_daily_progress_dashboard.py` before running:

| Line | Value | What to Change |
|------|-------|----------------|
| **198** | `today = date(2026, 2, 16)` | Set to the current date (e.g., `date(2026, 2, 18)`) |
| **433** | `Data through 2026-02-16` | Automatically uses f-string — but currently hardcoded as literal text. Should match the date on line 198. |
| **48–110** | `MAPPING_DATES = { ... }` | Add entries for any **new users** who mapped tasks after the last build |

### Step 4: Build the Dashboard

```bash
python3 scripts/build_daily_progress_dashboard.py
```

**Reads:**
- `output/micro_intervention_report.csv`
- `assets/myelin_stat_ro/daily_progress_full.csv`

**Writes:**
- `output/daily_progress_dashboard.html`

**Expected output:**
```
Dashboard written to .../output/daily_progress_dashboard.html (XXkB)
  124 users, 119 active, 2502 log entries
```

### Step 5: Verify

Open `output/daily_progress_dashboard.html` in a browser and confirm:
- Header shows the correct date and updated entry count
- KPI row numbers have changed (total users, active, log entries)
- Daily Activity Timeline chart extends to the latest date
- User detail table reflects new log data

---

## 5. Dashboard Contents

### 5.1 KPI Row (8 metrics)

| KPI | Description |
|-----|-------------|
| Total Users | DES users with task mappings |
| Active (≥1 Log) | Users who submitted at least one daily log |
| Zero Logs | Users who mapped tasks but never logged |
| Avg Days (Active) | Mean days logged among active users |
| Completion Rate | Global checked / (checked + unchecked) |
| Comment Rate | Entries with comments / total entries |
| Avg Consistency | Mean consistency % across active users |
| Total Log Entries | Sum of all task-log rows |

### 5.2 Charts (8 visualizations, Chart.js)

| Chart | Type | Description |
|-------|------|-------------|
| Daily Activity Timeline | Stacked bar + line | Checked vs unchecked entries per day, with active-user overlay |
| Task Completion Rate | Horizontal bar | Completion % for each task T01–T12, colored by FP |
| FP Mapped vs Logged | Grouped bar | Users mapped to each FP vs users who actually logged |
| Depth Intent vs Logs | Grouped bar | D1→D2 / D2→D3 / Cross-FP selections vs checked/unchecked logs |
| Consistency Distribution | Bar | Users bucketed by consistency band (0%, 1-10%, … >50%) |
| Tasks Mapped vs Days Logged | Scatter | Correlation plot, Teacher vs Leader color-coded |
| FP Completion Rate | Radar | Completion % across 5 foundational principles |
| Role Comparison | Metric cards | Teacher vs Leader side-by-side stats |

### 5.3 User Detail Table

Sortable, filterable table with columns: Name, Role, School/Branch, Tasks Mapped, FP tags, Depth tags, Mapping Date, Days Logged, Checked, Unchecked, Comments, Completion%, Consistency%, and per-task Mapped→Logged bars.

**Filters:** text search (name/branch), role dropdown, activity status.

---

## 6. Key Formulas

| Metric | Formula |
|--------|---------|
| **Completion Rate** (per user) | `totalChecked / (totalChecked + totalUnchecked) × 100` |
| **Comment Rate** (per user) | `totalComments / (totalChecked + totalUnchecked) × 100` |
| **Consistency** (per user) | `daysLogged / min(daysSinceMapping, 21) × 100` |
| **Days Available** | `min(today − mappingDate, 21)` — capped at 21 days |

---

## 7. Hardcoded Dependencies & Known Limitations

### 7.1 Hardcoded `today` Date

Line 198: `today = date(2026, 2, 16)`. This must be manually updated each time the dashboard is regenerated. It affects the consistency metric (days available since mapping).

**Recommendation:** Replace with `date.today()` for automatic resolution.

### 7.2 Hardcoded `MAPPING_DATES` Dictionary

Lines 48–110 contain ~120 `userId → date` mappings. If new users start mapping tasks, their entries must be added manually (or the fallback logic on lines 191–194 infers mapping date as one day before their first log).

**Recommendation:** Extract mapping dates from prod dynamically (e.g., from `UserTaskMapping.CreatedAt`).

### 7.3 Hardcoded Header Text

Line 433: `Data through 2026-02-16` is a literal string in the f-string template, not dynamically generated from the `today` variable.

**Recommendation:** Replace with `Data through {today.isoformat()}`.

### 7.4 School Filter

Line 119: Only processes users from `Deccan Education Society`. Other schools are silently dropped.

### 7.5 Task ID Series

Two parallel MongoDB ObjectId series exist for the same 12 tasks (lines 30–45). Both are mapped. If a third series appears, the `TASKID_TO_CODE` dict must be updated.

### 7.6 No Dependency on `micro_intervention_report.js` Changes

If the report script output format changes (column names, delimiter), the builder will break silently.

---

## 8. File Inventory

| File | Type | Role |
|------|------|------|
| `scripts/extract_daily_progress_full.js` | mongosh script | Extracts `UserDailyProgress` → CSV |
| `scripts/micro_intervention_report.js` | mongosh script | Extracts user-task mapping → CSV |
| `scripts/build_daily_progress_dashboard.py` | Python 3 | Reads 2 CSVs, produces HTML |
| `assets/myelin_stat_ro/daily_progress_full.csv` | CSV | Raw daily progress data |
| `output/micro_intervention_report.csv` | CSV | User-task mapping data |
| `output/daily_progress_dashboard.html` | HTML | Final dashboard output |

---

## 9. Prerequisites

- **SSH access** to prod server (`~/.ssh/myelin_pilot_key.pem`)
- **Python 3.8+** with standard library only (no pip dependencies for the builder)
- **mongosh** installed on prod server
- `output/micro_intervention_report.csv` must exist before running the builder

---

## 10. Future Improvements

| # | Improvement | Impact |
|---|-------------|--------|
| 1 | Replace hardcoded `today` with `date.today()` | Eliminates manual date editing |
| 2 | Dynamically extract `MAPPING_DATES` from `UserTaskMapping.CreatedAt` | Supports new users without manual dict updates |
| 3 | Make header date dynamic (`Data through {today}`) | Consistent date display |
| 4 | Single-command regeneration script wrapping Steps 1–4 | One `./regenerate.sh` command for the full pipeline |
| 5 | Add `--school` CLI argument to support multiple schools | Removes hardcoded DES filter |
| 6 | Add data validation / row-count sanity checks | Catches extraction or transfer errors early |
