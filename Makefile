# Myelin NEP Readiness — Dashboard & Report Generation
#
# Usage:
#   make dashboards       — regenerate all HTML dashboards
#   make reports          — regenerate CSV/XLSX reports
#   make all              — regenerate everything
#   make clean            — remove generated output
#
# Prerequisites:
#   pip install -r requirements.txt
#   Node.js (for extraction scripts that run against MongoDB)

PYTHON  := python3
OUT_D   := output/dashboards
OUT_R   := output/reports
OUT_I   := output/images
SCRIPTS := scripts/dashboards
SRC     := src

.PHONY: all dashboards reports clean help

all: dashboards reports

# ── Dashboards ────────────────────────────────────────────

dashboards: \
	$(OUT_D)/01_baseline_dashboard.html \
	$(OUT_D)/02_daily_progress_dashboard.html \
	$(OUT_D)/03_comment_sentiment_dashboard.html \
	$(OUT_D)/04_task_mapping_dashboard.html \
	$(OUT_D)/05_intent_depth_dashboard.html \
	$(OUT_D)/06_sri_dashboard.html \
	$(OUT_D)/07_mathangle_dashboard.html \
	$(OUT_D)/08_mathangle_methodology.html

$(OUT_D)/01_baseline_dashboard.html:
	$(PYTHON) $(SCRIPTS)/build_html_dashboard.py

$(OUT_D)/02_daily_progress_dashboard.html:
	$(PYTHON) $(SCRIPTS)/build_daily_progress_dashboard.py

$(OUT_D)/03_comment_sentiment_dashboard.html:
	$(PYTHON) $(SCRIPTS)/build_comment_sentiment_dashboard.py

$(OUT_D)/04_task_mapping_dashboard.html:
	$(PYTHON) $(SCRIPTS)/build_task_mapping_dashboard.py

$(OUT_D)/05_intent_depth_dashboard.html:
	$(PYTHON) $(SCRIPTS)/build_intent_depth_dashboard.py

$(OUT_D)/06_sri_dashboard.html:
	$(PYTHON) $(SRC)/compute_sri_scores.py

$(OUT_D)/07_mathangle_dashboard.html:
	$(PYTHON) $(SCRIPTS)/mathangle_html_dashboard.py

$(OUT_D)/08_mathangle_methodology.html:
	$(PYTHON) $(SCRIPTS)/mathangle_dashboard.py

# ── Reports ───────────────────────────────────────────────

reports: \
	$(OUT_R)/SRI_All_Constructs_Data.xlsx \
	$(OUT_R)/micro_intervention_report.csv

$(OUT_R)/SRI_All_Constructs_Data.xlsx:
	$(PYTHON) $(SCRIPTS)/build_sri_workbook.py

$(OUT_R)/micro_intervention_report.csv:
	node scripts/util/micro_intervention_report.js

# ── Utilities ─────────────────────────────────────────────

clean:
	rm -f $(OUT_D)/*.html $(OUT_R)/*.csv $(OUT_R)/*.xlsx $(OUT_R)/*.json $(OUT_I)/*.png

help:
	@echo "Targets: all, dashboards, reports, clean"
	@echo "See Makefile header for details."
