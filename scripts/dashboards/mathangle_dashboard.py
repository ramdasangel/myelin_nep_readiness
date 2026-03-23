#!/usr/bin/env python3
"""Mathangle Assessment Dashboard — multi-panel visual report."""

import json
import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

INPUT = "/tmp/mathangle_raw.jsonl"
OUT_DIR = Path("/Users/ramdasangel/MyelinMaster/myelin_nep_readiness/output")

# ── colours ──────────────────────────────────────────────────────────
C_PRIMARY = "#2563EB"
C_SECONDARY = "#7C3AED"
C_ACCENT = "#F59E0B"
C_GREEN = "#10B981"
C_RED = "#EF4444"
C_GRAY = "#6B7280"
C_BG = "#F8FAFC"
C_CARD = "#FFFFFF"
TEACHER_CLR = "#3B82F6"
LEADER_CLR = "#8B5CF6"
PALETTE = ["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444", "#06B6D4", "#EC4899", "#84CC16"]

# ── chapter mapping ──────────────────────────────────────────────────
CHAPTER_MAP = {
    "Addition": "Addition &\nSubtraction",
    "बेरीज": "Addition &\nSubtraction",
    "Multiplication": "Multiplication",
    "गुणाकार": "Multiplication",
    "Division": "Division",
    "भागाकार": "Division",
    "Factors & Multiples": "Factors &\nMultiples",
    "विभाज्य आणि विभाजक": "Factors &\nMultiples",
    "Geometry": "Geometry",
    "भूमिती": "Geometry",
    "Measurement": "Measurement",
    "मापन": "Measurement",
    "Money": "Money",
    "पैसे": "Money",
    "Time & Calendar": "Time &\nCalendar",
    "वेळ आणि दिनदर्शिका": "Time &\nCalendar",
}

# Exclude test/demo branches and test users
EXCLUDED_BRANCHES = {"DES Demo", "Myelin Cbse Primary & Secondary School"}

def map_chapter(ch):
    for k, v in CHAPTER_MAP.items():
        if ch.startswith(k):
            return v
    return ch


def load():
    rows = []
    with open(INPUT) as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            rows.append(json.loads(line))
    return rows


def enrich(rows):
    """Add computed fields."""
    for r in rows:
        r["lang"] = "MR" if "मराठी" in r["testName"] else "EN"
        areas = defaultdict(lambda: {"right": 0, "total": 0})
        for ch in r.get("chapterWise", []):
            a = map_chapter(ch["chapter"])
            areas[a]["right"] += ch["right"]
            areas[a]["total"] += ch["total"]
        r["areas"] = {k: round(v["right"]/v["total"]*100, 1) if v["total"] else 0 for k, v in areas.items()}
        r["areas_raw"] = dict(areas)

        cog = {}
        for c in r.get("cognitiveLevel", []):
            cog[c["level"]] = c["pct"]
        r["cog"] = cog

        diff = {}
        for q in r.get("questionLevel", []):
            diff[q["level"]] = round(q["right"]/q["total"]*100, 1) if q["total"] else 0
        r["diff"] = diff
    return rows


# ── helpers ──────────────────────────────────────────────────────────
def bar_label(ax, bars, fmt="{:.0f}%"):
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2, h + 1.2, fmt.format(h),
                    ha="center", va="bottom", fontsize=8, fontweight="bold", color="#374151")


def hbar_label(ax, bars, fmt="{:.0f}%"):
    for bar in bars:
        w = bar.get_width()
        if w > 0:
            ax.text(w + 1.0, bar.get_y() + bar.get_height()/2, fmt.format(w),
                    ha="left", va="center", fontsize=9, fontweight="bold", color="#374151")


def style_ax(ax, title="", ylabel="", xlabel=""):
    ax.set_facecolor(C_CARD)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#E5E7EB")
    ax.spines["bottom"].set_color("#E5E7EB")
    ax.tick_params(colors="#6B7280", labelsize=9)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", color="#1F2937", pad=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9, color=C_GRAY)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=9, color=C_GRAY)


# ════════════════════════════════════════════════════════════════════
def build_dashboard(rows):
    teachers = [r for r in rows if r["role"] == "Teacher"]
    leaders = [r for r in rows if r["role"] == "Leader"]

    fig = plt.figure(figsize=(24, 30), facecolor=C_BG, dpi=150)
    gs = gridspec.GridSpec(5, 4, figure=fig, hspace=0.38, wspace=0.35,
                           left=0.06, right=0.96, top=0.93, bottom=0.03)

    # ── Title banner ─────────────────────────────────────────────────
    fig.text(0.50, 0.97, "MATHANGLE ASSESSMENT DASHBOARD",
             ha="center", va="center", fontsize=22, fontweight="bold", color="#1E3A5F",
             family="sans-serif")
    fig.text(0.50, 0.955, f"109 Responses  •  75 Teachers  •  34 Leaders  •  Adaptive Maths Assessment  •  Feb 2026",
             ha="center", va="center", fontsize=11, color=C_GRAY)

    # ═══════════════════ ROW 1 ═══════════════════════════════════════

    # 1A — Score Distribution Histogram
    ax1 = fig.add_subplot(gs[0, 0:2])
    style_ax(ax1, "Score Distribution (%)", ylabel="Number of Respondents")
    t_pcts = [r["percentage"] for r in teachers]
    l_pcts = [r["percentage"] for r in leaders]
    bins = np.arange(0, 110, 10)
    ax1.hist(t_pcts, bins=bins, alpha=0.7, label=f"Teachers (n={len(teachers)})", color=TEACHER_CLR, edgecolor="white")
    ax1.hist(l_pcts, bins=bins, alpha=0.6, label=f"Leaders (n={len(leaders)})", color=LEADER_CLR, edgecolor="white")
    ax1.axvline(np.mean(t_pcts), color=TEACHER_CLR, ls="--", lw=1.5, label=f"Teacher avg: {np.mean(t_pcts):.1f}%")
    ax1.axvline(np.mean(l_pcts), color=LEADER_CLR, ls="--", lw=1.5, label=f"Leader avg: {np.mean(l_pcts):.1f}%")
    ax1.legend(fontsize=8, loc="upper left", framealpha=0.9)
    ax1.set_xlabel("Score (%)", fontsize=9, color=C_GRAY)

    # 1B — KPI Cards as a subplot
    ax_kpi = fig.add_subplot(gs[0, 2:4])
    ax_kpi.set_facecolor(C_BG)
    ax_kpi.axis("off")

    all_pcts = [r["percentage"] for r in rows]
    kpis = [
        ("Overall Average", f"{np.mean(all_pcts):.1f}%", C_PRIMARY),
        ("Teacher Average", f"{np.mean(t_pcts):.1f}%", TEACHER_CLR),
        ("Leader Average", f"{np.mean(l_pcts):.1f}%", LEADER_CLR),
        ("Highest Score", f"{max(all_pcts):.1f}%", C_GREEN),
        ("Lowest Score", f"{min(all_pcts):.1f}%", C_RED),
        ("Median Score", f"{np.median(all_pcts):.1f}%", C_ACCENT),
    ]
    for i, (label, value, clr) in enumerate(kpis):
        col = i % 3
        row_ = i // 3
        x = 0.05 + col * 0.33
        y = 0.72 - row_ * 0.45
        ax_kpi.add_patch(plt.Rectangle((x, y - 0.12), 0.28, 0.34,
                         transform=ax_kpi.transAxes, facecolor=C_CARD,
                         edgecolor="#E5E7EB", linewidth=1.5, zorder=2,
                         clip_on=False))
        ax_kpi.text(x + 0.14, y + 0.12, value, transform=ax_kpi.transAxes,
                    ha="center", va="center", fontsize=20, fontweight="bold", color=clr, zorder=3)
        ax_kpi.text(x + 0.14, y - 0.03, label, transform=ax_kpi.transAxes,
                    ha="center", va="center", fontsize=9, color=C_GRAY, zorder=3)

    # ═══════════════════ ROW 2 ═══════════════════════════════════════

    # 2A — Competency Area: Teacher vs Leader (grouped bar)
    ax2 = fig.add_subplot(gs[1, 0:3])
    style_ax(ax2, "Competency Area Performance — Teachers vs Leaders", ylabel="Accuracy (%)")

    area_order = ["Multiplication", "Money", "Factors &\nMultiples", "Division",
                  "Measurement", "Addition &\nSubtraction", "Time &\nCalendar", "Geometry"]

    def area_avg(group, area):
        right = sum(r["areas_raw"].get(area, {}).get("right", 0) for r in group)
        total = sum(r["areas_raw"].get(area, {}).get("total", 0) for r in group)
        return round(right / total * 100, 1) if total else 0

    x = np.arange(len(area_order))
    w = 0.35
    t_vals = [area_avg(teachers, a) for a in area_order]
    l_vals = [area_avg(leaders, a) for a in area_order]
    bars_t = ax2.bar(x - w/2, t_vals, w, label="Teachers", color=TEACHER_CLR, edgecolor="white", zorder=3)
    bars_l = ax2.bar(x + w/2, l_vals, w, label="Leaders", color=LEADER_CLR, edgecolor="white", zorder=3)
    bar_label(ax2, bars_t)
    bar_label(ax2, bars_l)
    ax2.set_xticks(x)
    ax2.set_xticklabels(area_order, fontsize=9)
    ax2.set_ylim(0, 110)
    ax2.axhline(50, color="#E5E7EB", ls="--", lw=1, zorder=1)
    ax2.legend(fontsize=9, loc="upper right")
    ax2.yaxis.grid(True, alpha=0.3, color="#E5E7EB")

    # 2B — Cognitive Levels (Bloom's Taxonomy)
    ax3 = fig.add_subplot(gs[1, 3])
    style_ax(ax3, "Bloom's Taxonomy\nCognitive Levels", ylabel="Accuracy (%)")
    cog_order = ["Understand", "Apply", "Analyze", "Evaluate"]
    cog_colors = ["#10B981", "#3B82F6", "#F59E0B", "#EF4444"]

    def cog_avg(group, level):
        right = sum(r.get("cognitiveLevel", [{}]).__class__ and 0 for r in group)  # placeholder
        # Recalculate from raw
        r_sum = 0
        t_sum = 0
        for p in group:
            for c in p.get("cognitiveLevel", []):
                if c["level"] == level:
                    r_sum += c["right"]
                    t_sum += c["total"]
        return round(r_sum / t_sum * 100, 1) if t_sum else 0

    all_cog = [cog_avg(rows, c) for c in cog_order]
    bars_c = ax3.bar(range(len(cog_order)), all_cog, color=cog_colors, edgecolor="white", zorder=3)
    bar_label(ax3, bars_c)
    ax3.set_xticks(range(len(cog_order)))
    ax3.set_xticklabels(cog_order, fontsize=8, rotation=25, ha="right")
    ax3.set_ylim(0, 100)
    ax3.yaxis.grid(True, alpha=0.3, color="#E5E7EB")

    # ═══════════════════ ROW 3 ═══════════════════════════════════════

    # 3A — Branch-wise average scores (horizontal bar)
    ax4 = fig.add_subplot(gs[2, 0:2])
    style_ax(ax4, "Branch-wise Average Score", xlabel="Average Score (%)")

    branch_data = defaultdict(list)
    for r in rows:
        branch_data[r["branchName"]].append(r["percentage"])

    # Sort by average
    branch_sorted = sorted(branch_data.items(), key=lambda x: np.mean(x[1]), reverse=False)
    branch_names = [b[0][:40] for b in branch_sorted]
    branch_avgs = [np.mean(b[1]) for b in branch_sorted]
    branch_counts = [len(b[1]) for b in branch_sorted]
    colors_branch = [C_GREEN if v >= 60 else C_ACCENT if v >= 40 else C_RED for v in branch_avgs]

    y_pos = np.arange(len(branch_names))
    bars_br = ax4.barh(y_pos, branch_avgs, color=colors_branch, edgecolor="white", height=0.7, zorder=3)
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(branch_names, fontsize=7)
    ax4.set_xlim(0, 110)
    ax4.axvline(50, color="#9CA3AF", ls="--", lw=1, zorder=1)
    for i, (v, n) in enumerate(zip(branch_avgs, branch_counts)):
        ax4.text(v + 1.5, i, f"{v:.0f}% (n={n})", va="center", fontsize=7, color="#374151", fontweight="bold")

    # 3B — Difficulty Level Performance
    ax5 = fig.add_subplot(gs[2, 2])
    style_ax(ax5, "Performance by\nDifficulty Level")

    diff_levels = [1, 2, 3]
    diff_labels = ["Level 1\n(Easy)", "Level 2\n(Medium)", "Level 3\n(Hard)"]
    diff_colors = [C_GREEN, C_ACCENT, C_RED]

    def diff_avg(group, level):
        r_sum = 0
        t_sum = 0
        for p in group:
            for q in p.get("questionLevel", []):
                if q["level"] == level:
                    r_sum += q["right"]
                    t_sum += q["total"]
        return round(r_sum / t_sum * 100, 1) if t_sum else 0

    diff_vals = [diff_avg(rows, d) for d in diff_levels]
    bars_d = ax5.bar(range(len(diff_levels)), diff_vals, color=diff_colors, edgecolor="white", zorder=3)
    bar_label(ax5, bars_d)
    ax5.set_xticks(range(len(diff_levels)))
    ax5.set_xticklabels(diff_labels, fontsize=8)
    ax5.set_ylim(0, 100)
    ax5.set_ylabel("Accuracy (%)", fontsize=9, color=C_GRAY)
    ax5.yaxis.grid(True, alpha=0.3, color="#E5E7EB")

    # 3C — Language split
    ax6 = fig.add_subplot(gs[2, 3])
    style_ax(ax6, "Language Distribution\n& Performance")
    en = [r for r in rows if r["lang"] == "EN"]
    mr = [r for r in rows if r["lang"] == "MR"]
    lang_labels = [f"English\n(n={len(en)})", f"Marathi\n(n={len(mr)})"]
    lang_avgs = [np.mean([r["percentage"] for r in en]), np.mean([r["percentage"] for r in mr])]
    bars_lang = ax6.bar(range(2), lang_avgs, color=[C_PRIMARY, C_ACCENT], edgecolor="white", width=0.6, zorder=3)
    bar_label(ax6, bars_lang)
    ax6.set_xticks(range(2))
    ax6.set_xticklabels(lang_labels, fontsize=9)
    ax6.set_ylim(0, 100)
    ax6.set_ylabel("Avg Score (%)", fontsize=9, color=C_GRAY)
    ax6.yaxis.grid(True, alpha=0.3, color="#E5E7EB")

    # ═══════════════════ ROW 4 ═══════════════════════════════════════

    # 4A — Top 15 performers table
    ax_top = fig.add_subplot(gs[3, 0:2])
    ax_top.axis("off")
    style_ax(ax_top)
    ax_top.set_title("Top 15 Performers", fontsize=12, fontweight="bold", color="#1F2937", pad=10)

    sorted_all = sorted(rows, key=lambda x: x["percentage"], reverse=True)
    top15 = sorted_all[:15]

    col_labels = ["Rank", "Name", "Role", "Branch", "Score", "%"]
    table_data = []
    for i, p in enumerate(top15, 1):
        table_data.append([
            str(i),
            f'{p["firstName"]} {p["lastName"]}'.strip(),
            p["role"],
            p["branchName"][:30],
            f'{p["totalObtained"]}/{p["totalMarks"]}',
            f'{p["percentage"]:.1f}%',
        ])

    tbl = ax_top.table(cellText=table_data, colLabels=col_labels, loc="center",
                       cellLoc="left", colWidths=[0.06, 0.22, 0.10, 0.35, 0.10, 0.10])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor("#E5E7EB")
        if row == 0:
            cell.set_facecolor(C_PRIMARY)
            cell.set_text_props(color="white", fontweight="bold")
            cell.set_height(0.05)
        else:
            cell.set_facecolor("#F9FAFB" if row % 2 == 0 else C_CARD)
            cell.set_height(0.045)
            if col == 5:
                pct_val = float(table_data[row-1][5].replace("%", ""))
                if pct_val >= 80:
                    cell.set_text_props(color=C_GREEN, fontweight="bold")
                elif pct_val >= 50:
                    cell.set_text_props(color=C_PRIMARY, fontweight="bold")

    # 4B — Bottom 15 performers table
    ax_bot = fig.add_subplot(gs[3, 2:4])
    ax_bot.axis("off")
    style_ax(ax_bot)
    ax_bot.set_title("Bottom 15 Performers", fontsize=12, fontweight="bold", color="#1F2937", pad=10)

    bot15 = sorted_all[-15:]
    table_data2 = []
    for i, p in enumerate(bot15, len(sorted_all) - 14):
        table_data2.append([
            str(i),
            f'{p["firstName"]} {p["lastName"]}'.strip(),
            p["role"],
            p["branchName"][:30],
            f'{p["totalObtained"]}/{p["totalMarks"]}',
            f'{p["percentage"]:.1f}%',
        ])

    tbl2 = ax_bot.table(cellText=table_data2, colLabels=col_labels, loc="center",
                        cellLoc="left", colWidths=[0.06, 0.22, 0.10, 0.35, 0.10, 0.10])
    tbl2.auto_set_font_size(False)
    tbl2.set_fontsize(8)
    for (row, col), cell in tbl2.get_celld().items():
        cell.set_edgecolor("#E5E7EB")
        if row == 0:
            cell.set_facecolor(C_RED)
            cell.set_text_props(color="white", fontweight="bold")
            cell.set_height(0.05)
        else:
            cell.set_facecolor("#FEF2F2" if row % 2 == 0 else C_CARD)
            cell.set_height(0.045)
            if col == 5:
                pct_val = float(table_data2[row-1][5].replace("%", ""))
                if pct_val < 25:
                    cell.set_text_props(color=C_RED, fontweight="bold")

    # ═══════════════════ ROW 5 ═══════════════════════════════════════

    # 5A — Competency Heatmap by Branch (top 12 branches by count)
    ax_heat = fig.add_subplot(gs[4, 0:3])
    style_ax(ax_heat, "Competency Heatmap by Branch (avg %)")

    area_order_clean = ["Multiplication", "Money", "Factors &\nMultiples", "Division",
                        "Measurement", "Addition &\nSubtraction", "Time &\nCalendar", "Geometry"]

    # Get branches sorted by response count
    branch_counts_map = defaultdict(int)
    for r in rows:
        branch_counts_map[r["branchName"]] += 1
    top_branches = sorted(branch_counts_map.items(), key=lambda x: x[1], reverse=True)[:14]
    top_branch_names = [b[0] for b in top_branches]

    heat_data = []
    for br in top_branch_names:
        br_rows = [r for r in rows if r["branchName"] == br]
        row_data = []
        for area in area_order_clean:
            right = sum(r["areas_raw"].get(area, {}).get("right", 0) for r in br_rows)
            total = sum(r["areas_raw"].get(area, {}).get("total", 0) for r in br_rows)
            row_data.append(round(right / total * 100, 1) if total else 0)
        heat_data.append(row_data)

    heat_arr = np.array(heat_data)
    im = ax_heat.imshow(heat_arr, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)

    ax_heat.set_xticks(range(len(area_order_clean)))
    ax_heat.set_xticklabels(area_order_clean, fontsize=8, rotation=30, ha="right")
    branch_labels = [f"{b[:32]} (n={branch_counts_map[b]})" for b in top_branch_names]
    ax_heat.set_yticks(range(len(branch_labels)))
    ax_heat.set_yticklabels(branch_labels, fontsize=7)

    # Annotate cells
    for i in range(len(top_branch_names)):
        for j in range(len(area_order_clean)):
            val = heat_arr[i, j]
            color = "white" if val < 35 or val > 80 else "#1F2937"
            ax_heat.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=8,
                        fontweight="bold", color=color)

    cbar = plt.colorbar(im, ax=ax_heat, shrink=0.6, pad=0.02)
    cbar.set_label("Accuracy %", fontsize=9, color=C_GRAY)

    # 5B — Radar chart for Teacher vs Leader
    ax_radar = fig.add_subplot(gs[4, 3], polar=True)
    ax_radar.set_facecolor(C_CARD)
    ax_radar.set_title("Teacher vs Leader\nCompetency Profile", fontsize=11,
                       fontweight="bold", color="#1F2937", pad=20)

    radar_areas = ["Multiplication", "Money", "Factors &\nMultiples", "Division",
                   "Measurement", "Add &\nSub", "Time &\nCal", "Geometry"]
    radar_areas_lookup = ["Multiplication", "Money", "Factors &\nMultiples", "Division",
                          "Measurement", "Addition &\nSubtraction", "Time &\nCalendar", "Geometry"]

    angles = np.linspace(0, 2 * np.pi, len(radar_areas), endpoint=False).tolist()
    angles += angles[:1]

    t_radar = [area_avg(teachers, a) for a in radar_areas_lookup]
    t_radar += t_radar[:1]
    l_radar = [area_avg(leaders, a) for a in radar_areas_lookup]
    l_radar += l_radar[:1]

    ax_radar.plot(angles, t_radar, "o-", color=TEACHER_CLR, linewidth=2, markersize=5, label="Teachers")
    ax_radar.fill(angles, t_radar, alpha=0.15, color=TEACHER_CLR)
    ax_radar.plot(angles, l_radar, "s-", color=LEADER_CLR, linewidth=2, markersize=5, label="Leaders")
    ax_radar.fill(angles, l_radar, alpha=0.15, color=LEADER_CLR)

    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels(radar_areas, fontsize=7)
    ax_radar.set_ylim(0, 100)
    ax_radar.set_rticks([25, 50, 75, 100])
    ax_radar.tick_params(axis="y", labelsize=7)
    ax_radar.legend(fontsize=8, loc="lower right", bbox_to_anchor=(1.3, -0.1))
    ax_radar.grid(color="#E5E7EB", alpha=0.5)

    # ── Save ─────────────────────────────────────────────────────────
    out_path = OUT_DIR / "mathangle_assessment_dashboard.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Dashboard saved → {out_path}")
    return out_path


if __name__ == "__main__":
    rows = load()
    rows = [r for r in rows if r.get("branchName", "") not in EXCLUDED_BRANCHES
            and (r.get("lastName", "") or "").strip().lower() != "test"]
    print(f"Loaded {len(rows)} records (after exclusions)")
    rows = enrich(rows)
    build_dashboard(rows)
