# Project Structure — Myelin NEP Readiness

> Auto-generated on 2026-03-23. Reflects the reorganized repo layout.

---

## Root Directory

```
myelin_nep_readiness/
├── .gitignore                  # Git ignore rules
├── Makefile                    # Build targets for dashboards & reports
├── README.md                   # Project overview and quick start
├── requirements.txt            # Python dependencies (pandas, matplotlib, etc.)
├── memory.md                   # Local credentials reference (gitignored)
│
├── data/                       # All data files (67 MB)
├── scripts/                    # All scripts organized by purpose (532 KB)
├── src/                        # Core reusable Python modules (76 KB)
├── output/                     # Generated dashboards, reports, images (12 MB)
├── docs/                       # Documentation, specs, PRDs (21 MB)
├── archive/                    # Superseded files — gitignored (32 MB)
└── myelin-react-admin-panel/   # Embedded React app — gitignored
```

---

## data/ — All Data Files (67 MB)

Organized by data lifecycle: raw dumps → extracted intermediates → reference lookups → processed outputs.

```
data/
├── raw/                        # Immutable MongoDB dumps (Feb 2026)
│   ├── 20260201_..._dump1_user_school_branch_questionset_....csv
│   ├── 20260201_..._dump2_user_questionset_attempt_responses_....csv
│   ├── 20260201_..._dump3a_user_taskmapping_....csv
│   ├── 20260201_..._dump3b_user_dailyprogress_taskprogress_....csv
│   ├── baseline_questionsets_dump.csv
│   ├── branch_collection_counts.csv
│   ├── collections_count.csv
│   └── questionset_user_school_branch_dump.csv
│
├── extracted/                  # Script-produced intermediate CSVs
│   ├── baseline/               # Stage-2 baseline survey data
│   │   ├── base001_teacher_english.csv
│   │   ├── base002_leader_english.csv
│   │   ├── base003_teacher_marathi.csv
│   │   └── base004_leader_marathi.csv
│   │
│   ├── intent/                 # Stage-1 intent/readiness survey data
│   │   ├── intent_attempts.csv
│   │   ├── intent_leader_english_attempts.csv
│   │   ├── intent_leader_english_questions.csv
│   │   ├── intent_leader_english_responses.csv
│   │   ├── intent_leader_marathi_attempts.csv
│   │   ├── intent_leader_marathi_questions.csv
│   │   ├── intent_leader_marathi_responses.csv
│   │   ├── intent_questions.csv
│   │   ├── intent_readiness_raw.txt
│   │   ├── intent_responses_detail.csv
│   │   ├── intent_teacher_english_attempts.csv
│   │   ├── intent_teacher_english_questions.csv
│   │   ├── intent_teacher_english_responses.csv
│   │   ├── intent_teacher_marathi_attempts.csv
│   │   ├── intent_teacher_marathi_questions.csv
│   │   └── intent_teacher_marathi_responses.csv
│   │
│   ├── constructs/             # SRI all-constructs & system readiness
│   │   ├── all_constructs_raw.txt
│   │   ├── system_readiness_attempts.csv
│   │   ├── system_readiness_questions.csv
│   │   └── system_readiness_responses_detail.csv
│   │
│   ├── mathangle/              # MathAngle online assessment extraction
│   │   └── mathangle_extraction.txt
│   │
│   ├── comments_full.csv       # Daily progress comments
│   ├── daily_progress_full.csv # Daily progress logging data
│   ├── des_user_task_daily_log_summary.csv
│   ├── micro_intervention_task_report.csv
│   └── user_task_daily_log_summary.csv
│
├── reference/                  # Static lookup tables
│   ├── all_question_sets.csv   # All DiagnosticQuestionSet entries
│   ├── branches_list.json      # SchoolBranches collection dump
│   ├── kshitij_erd.md          # Entity-relationship diagram
│   ├── nep_readiness_summary.txt
│   ├── user_stage_matrix.csv   # User × stage completion matrix
│   └── user_stage2_baseline.csv
│
├── processed/                  # Cleaned data ready for dashboards
│   ├── school_leaders_detailed_fp_mapping.csv
│   └── teachers_detailed_fp_mapping.csv
│
├── questions/                  # Question bank CSVs
│   ├── school_leaders_questions.csv
│   └── teachers_questions.csv
│
├── responses/                  # Sample/uploaded survey responses
│   ├── api_sample_response.json
│   ├── sample_upload_format.json
│   ├── school_a_survey.json
│   ├── school_b_survey.json
│   ├── school_leaders_responses.csv
│   └── teachers_responses.csv
│
└── baseline_responses.json     # Aggregated baseline response data
```

---

## scripts/ — All Scripts (532 KB)

Organized into four categories matching the data pipeline stages.

```
scripts/
├── extract/                    # JS — pull data from MongoDB → data/extracted/
│   ├── extract_all_constructs.js       # SRI constructs + system readiness
│   ├── extract_baseline_v2.js          # Stage-2 baseline responses
│   ├── extract_capacity_questions.js   # Capacity building questions
│   ├── extract_comments.js             # Daily progress comments
│   ├── extract_daily_progress_full.js  # Full daily progress dump
│   ├── extract_intent_readiness.js     # Stage-1 intent/readiness data
│   ├── extract_mapping_dates_v2.js     # Task mapping with dates
│   ├── extract_mathangle_jsonl.js      # MathAngle assessment data
│   └── gen_user_stage_matrix.js        # User × stage matrix
│
├── parse/                      # Python — raw text → structured CSV
│   ├── parse_all_constructs.py         # Parse constructs raw text
│   ├── parse_intent_readiness.py       # Parse intent raw text
│   ├── parse_mathangle_jsonl.py        # Parse MathAngle JSONL
│   └── split_intent_by_setcode.py      # Split intent data by setCode
│
├── dashboards/                 # Python — generate HTML dashboards + reports
│   ├── build_html_dashboard.py             # 01 — Baseline dashboard
│   ├── build_daily_progress_dashboard.py   # 02 — Daily progress
│   ├── build_comment_sentiment_dashboard.py # 03 — Comment sentiment
│   ├── build_task_mapping_dashboard.py     # 04 — Task mapping
│   ├── build_intent_depth_dashboard.py     # 05 — Intent depth
│   ├── build_sri_workbook.py               # 06 — SRI Excel workbook
│   ├── mathangle_html_dashboard.py         # 07 — MathAngle dashboard
│   ├── mathangle_dashboard.py              # 08 — MathAngle methodology
│   ├── mathangle_csv_dump.py               # MathAngle CSV exports
│   └── mathangle_ranking.py                # MathAngle ranking report
│
└── util/                       # Exploratory & one-off scripts
    ├── check_schools_branches.js       # Verify school/branch data
    ├── count_by_branch.js              # Count records per branch
    ├── count_by_branch_fast.js         # Fast branch counts
    ├── explore_baseline_q2.js          # Explore baseline question set
    ├── explore_baseline_questions.js   # Explore baseline questions
    ├── explore_branches.js             # Explore branch data
    ├── explore_diagnostics.js          # Explore diagnostics collection
    ├── gen_functional_steps_pptx.py    # Generate functional steps PPTX
    ├── gen_sri_methodology_docs.py     # Generate SRI methodology docs
    ├── md_to_pdf.py                    # Markdown to PDF converter
    └── micro_intervention_report.js    # Micro-intervention task report
```

---

## src/ — Core Reusable Modules (76 KB)

```
src/
├── baseline_dashboard_generator.py   # Baseline dashboard generation logic
├── compute_sri_scores.py             # SRI score computation + dashboard
└── nep_dashboard_generator.py        # NEP readiness dashboard generator
```

---

## output/ — Generated Artifacts (12 MB)

All files here are produced by scripts. Regenerate with `make all`.

```
output/
├── dashboards/                       # Numbered HTML dashboards
│   ├── 01_baseline_dashboard.html          # Baseline survey results
│   ├── 02_daily_progress_dashboard.html    # Daily progress tracking
│   ├── 03_comment_sentiment_dashboard.html # Comment sentiment analysis
│   ├── 04_task_mapping_dashboard.html      # Task mapping overview
│   ├── 05_intent_depth_dashboard.html      # Intent/readiness depth
│   ├── 06_sri_dashboard.html               # System Readiness Index
│   ├── 07_mathangle_dashboard.html         # MathAngle assessment
│   ├── 08_mathangle_methodology.html       # MathAngle methodology
│   ├── 09_api_specification_print.html     # API spec (printable)
│   └── 10_c5_student_dashboard.html        # C5 student assessment
│
├── reports/                          # CSV, XLSX, JSON exports
│   ├── baseline_scores_leader.csv          # Per-user leader scores
│   ├── baseline_scores_teacher.csv         # Per-user teacher scores
│   ├── mathangle_branch_summary.csv        # MathAngle by branch
│   ├── mathangle_exit_levels.csv           # MathAngle exit levels
│   ├── mathangle_master.csv                # MathAngle master data
│   ├── mathangle_per_question.csv          # MathAngle per question
│   ├── mathangle_ranking.csv               # MathAngle student ranking
│   ├── micro_intervention_report.csv       # 133 users, task selections
│   ├── nep_sharable_exam_data.json         # Shareable exam data export
│   ├── SRI_All_Constructs_Data.xlsx        # Full SRI data workbook
│   ├── sri_branch_scores.csv               # SRI scores by branch
│   └── sri_dashboard_data.json             # SRI dashboard JSON feed
│
└── images/                           # PNG chart images
    ├── baseline_dashboard_leader.png       # Leader baseline chart
    ├── baseline_dashboard_teacher.png      # Teacher baseline chart
    ├── mathangle_assessment_dashboard.png  # MathAngle chart
    └── nep_readiness_dashboard.png         # NEP readiness chart
```

---

## docs/ — Documentation (21 MB)

```
docs/
├── README.md                         # NEP Readiness system documentation
│
├── api/                              # API specifications
│   ├── API_Spec_Baseline_Dashboard.md
│   └── Kshitij_Dashboard_API_Specification.md
│
├── methodology/                      # Research & methodology docs
│   ├── smart_adaptive_specs                  # Adaptive testing specs
│   ├── smart_adaptive_test_documentation.md  # Adaptive test docs
│   ├── SRI_Methodology_Explained.html        # SRI methodology (HTML)
│   └── SRI_Methodology_Explained.pptx        # SRI methodology (PPTX)
│
├── prd/                              # Product requirement documents
│   ├── PRD_daily_progress_dashboard_regeneration.md
│   └── PRD_task_mapping_dashboard_regeneration.md
│
├── project/                          # Kshitij project documents
│   ├── क्षितिज.pdf                           # Project overview (Hindi)
│   ├── DETAILED_FP_MAPPING_FORMAT.md
│   ├── functional_steps_task_mapping_logging.html
│   ├── functional_steps_task_mapping_logging.md
│   ├── functional_steps_task_mapping_logging.pptx
│   ├── Kshitij_Consolidated_Analysis.md
│   ├── Leader_Baseline_Survey_Practice_Diagnostics.md
│   ├── Micro Intervention Tasks.docx
│   ├── MYELIN_DESIGN_SYSTEM.md
│   ├── NEP-2020 readiness assessment-... ProjectPlan.docx.docx
│   ├── NEP-2020-readiness _Assessment -WIP Marathi.docx
│   ├── NEP-2020-SRI-Construct-Design (1).pdf
│   ├── Practice Diagnostics english.docx
│   ├── Practice Diagnostics marathi.docx
│   ├── PRD_Teacher_Intervention_Logging.md
│   ├── Project_Kshitij_Summary.md
│   ├── School Leader's NEP Readiness Questions_Marathi.docx
│   ├── School Leader's NEP Readiness Questions, Rubric.docx
│   ├── School_Leader_NEP_Readiness_Survey_FP_Weights.md
│   ├── screen1_selection.html
│   ├── screen2_logging.html
│   ├── screen3_dashboard.html
│   ├── SET.pdf
│   ├── Teacher_Baseline_Survey_Practice_Diagnostics.md
│   ├── Teacher_NEP_Readiness_Survey_FP_D_Weights.md
│   ├── Teacher's NEP Readiness Questions_Marathi.docx
│   ├── Teacher's NEP Readiness Questions, Rubric.docx
│   ├── Teachers NEP Readiness Questions, Rubric.pdf
│   │
│   └── printed/                      # Print-ready PDF exports
│       ├── क्षितिज.pdf
│       ├── Kshitij Dashboards.pdf
│       ├── Kshitij-FP-Design.pdf
│       ├── Kshitij-InterventionLogingDesign.pdf
│       ├── Kshitij-SignalHirerchicalView-Design.pdf
│       ├── MircoTask and SRI.pdf
│       ├── myelin-NEP Readiness Micro Interventions1.pdf
│       ├── myelin-NEP Readiness Micro Interventions1.pptx
│       ├── NEP-2020 Readiness UX.pdf
│       ├── NEP-2020-SRI-Construct-Design.pdf
│       ├── NEP-2020-SRI-WIP.-V1.pdf
│       ├── School Leaders NEP Readiness-Baseline-Design.pdf
│       ├── SET.pdf
│       └── Teachers NEP Readiness Questions, Rubric.pdf
│
└── regeneration/                     # Per-dashboard regeneration guides
    ├── 01_baseline_dashboard.md
    ├── 02_daily_progress_dashboard.md
    ├── 03_comment_sentiment_dashboard.md
    ├── 04_task_mapping_dashboard.md
    ├── 05_intent_depth_dashboard.md
    ├── 06_sri_dashboard.md
    ├── 07_mathangle_dashboard.md
    ├── 08_mathangle_methodology.md
    ├── 09_api_specification_print.md
    └── 10_c5_student_dashboard.md
```

---

## archive/ — Superseded Files (gitignored, 32 MB)

Old/obsolete files kept locally but excluded from the repository.

```
archive/
├── dashboard_samples/          # Early screenshot samples (Jan 2026)
│   ├── fp_orientation_dashboard.png
│   └── nep_readiness_dashboard.png
│
├── demo/                       # Superseded demo dashboards
│   ├── dashboard.zip
│   ├── INTEGRATION_GUIDE.md
│   ├── myelin_stats_dashboard_20260201.html  (32 MB monolith)
│   ├── nep_dashboard_consolidated.html
│   └── teachers_nep_dashboard.html
│
├── examples/                   # Old sample input files
│   ├── sample_input.json
│   └── sample_input_leaders.json
│
└── web/                        # Standalone dashboard prototype
    └── dashboard.html
```

---

## Data Pipeline Overview

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  MongoDB     │     │ data/raw/   │     │ data/        │     │ output/     │
│  (prod)      │────▶│ data/       │────▶│ extracted/   │────▶│ dashboards/ │
│              │     │ extracted/  │     │              │     │ reports/    │
└─────────────┘     └─────────────┘     └──────────────┘     │ images/     │
                     scripts/extract/    scripts/parse/       └─────────────┘
                     (JS on prod)        (Python local)        scripts/dashboards/
                                                               src/
                                                               (Python local)
```

| Stage | Tool | Input | Output |
|-------|------|-------|--------|
| 1. Extract | `scripts/extract/*.js` (run via mongosh on prod) | MongoDB collections | `data/raw/`, `data/extracted/` |
| 2. Parse | `scripts/parse/*.py` (run locally) | Raw text/JSONL files | Structured CSVs in `data/extracted/` |
| 3. Generate | `scripts/dashboards/*.py`, `src/*.py` (run locally) | `data/extracted/`, `data/reference/` | `output/dashboards/`, `output/reports/`, `output/images/` |

---

## Build Commands

```bash
pip install -r requirements.txt   # Install Python dependencies
make dashboards                   # Regenerate all HTML dashboards
make reports                      # Regenerate CSV/XLSX reports
make all                          # Regenerate everything
make clean                        # Remove all generated output
```
