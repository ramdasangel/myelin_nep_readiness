# Myelin NEP Readiness

Data analysis and dashboard generation for Project Kshitij — a NEP 2020 readiness assessment study covering teachers and school leaders across Maharashtra.

## Project Structure

```
├── data/
│   ├── raw/              # Immutable MongoDB dumps (Feb 2026)
│   ├── extracted/        # Script-produced intermediate CSVs
│   │   ├── baseline/     # Stage-2 baseline survey data (base001–004)
│   │   ├── intent/       # Stage-1 intent/readiness survey data
│   │   ├── constructs/   # SRI all-constructs & system-readiness
│   │   └── mathangle/    # MathAngle online assessment extraction
│   ├── reference/        # Static lookups (branches, question sets)
│   └── processed/        # Cleaned data ready for dashboards
│
├── scripts/
│   ├── extract/          # JS — pull data from MongoDB → data/extracted/
│   ├── parse/            # Python — raw text → structured CSV
│   ├── dashboards/       # Python — generate HTML dashboards + reports
│   └── util/             # Exploratory & one-off scripts
│
├── src/                  # Core reusable modules
│   ├── baseline_dashboard_generator.py
│   ├── compute_sri_scores.py
│   └── nep_dashboard_generator.py
│
├── output/
│   ├── dashboards/       # Numbered HTML dashboards (01–10)
│   ├── reports/          # CSV, XLSX, JSON exports
│   └── images/           # PNG chart images
│
├── docs/
│   ├── project/          # Kshitij project docs, rubrics, Word/PDF sources
│   ├── api/              # Dashboard API specification
│   ├── methodology/      # SRI methodology, adaptive testing docs
│   ├── prd/              # Product requirement docs for dashboards
│   └── regeneration/     # Per-dashboard regeneration guides
│
├── archive/              # Superseded demos & samples (gitignored)
├── Makefile              # Build targets for dashboards & reports
└── requirements.txt      # Python dependencies
```

## Dashboards

| # | Dashboard | Generator |
|---|-----------|-----------|
| 01 | Baseline Survey | `scripts/dashboards/build_html_dashboard.py` |
| 02 | Daily Progress | `scripts/dashboards/build_daily_progress_dashboard.py` |
| 03 | Comment Sentiment | `scripts/dashboards/build_comment_sentiment_dashboard.py` |
| 04 | Task Mapping | `scripts/dashboards/build_task_mapping_dashboard.py` |
| 05 | Intent Depth | `scripts/dashboards/build_intent_depth_dashboard.py` |
| 06 | SRI Constructs | `src/compute_sri_scores.py` |
| 07 | MathAngle | `scripts/dashboards/mathangle_html_dashboard.py` |
| 08 | MathAngle Methodology | `scripts/dashboards/mathangle_dashboard.py` |
| 09 | API Specification (print) | — (static) |
| 10 | C5 Student Dashboard | — (static) |

## Quick Start

```bash
# Install Python dependencies
pip install -r requirements.txt

# Regenerate all dashboards
make dashboards

# Regenerate reports (CSV/XLSX)
make reports

# Regenerate everything
make all
```

## Data Pipeline

1. **Extract** — JS scripts in `scripts/extract/` run against MongoDB on the prod server and produce raw text/CSV files in `data/extracted/`.
2. **Parse** — Python scripts in `scripts/parse/` convert raw extractions into structured CSVs.
3. **Generate** — Python scripts in `scripts/dashboards/` read from `data/` and produce HTML dashboards + CSV/XLSX reports in `output/`.

## Assessment Stages

- **Stage 1 — Intent/Readiness**: Teacher (setCodes: 1234/103) and Leader (7890/104) readiness surveys
- **Stage 2 — Baseline**: Teacher (base001/base003) and Leader (base002/base004) practice diagnostics
- **Stage 3 — Micro-Interventions**: 12 tasks (T01–T12), daily progress logging
- **MathAngle**: Online student assessment (C5 competency)
