"""
Stage 4.3 Practice Diagnostics - Enablement & Systems Baseline
Generates two separate dashboards:
  1. Teacher Lens (Areas A1-A4) - base001 + base003 merged
  2. Leader Lens (Areas B1-B5) - base002 + base004 merged

Response scale: Strongly Agree(4) / Agree(3) / Disagree(2) / Strongly Disagree(1)
"""

import json
import os
import numpy as np
from collections import defaultdict

# Try matplotlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap

# ── Config ──────────────────────────────────────────────────────────────────
AREA_LABELS = {
    # Teacher Lens
    "A1": "Continuous Learning\nDiagnostics",
    "A2": "Teacher Development\n& Growth Support",
    "A3": "HPC Teacher\nEnablement",
    "A4": "Parent & Community\nSupport",
    # Leader Lens
    "B1": "NEP Governance\n& Ownership",
    "B2": "Data-Informed\nDecision Culture",
    "B3": "Teacher Development\nCulture",
    "B4": "HPC & Reporting\nCulture",
    "B5": "Parent & Community\nPartnerships",
}

AREA_GOALS = {
    "A1": ["Access", "Usability", "Follow-through", "Collective Use", "Student Clarity"],
    "A2": ["Structure", "Safety", "Peer Learning", "Experimentation", "Growth Culture"],
    "A3": ["Understanding", "Clarity", "Time", "Use", "Student Role"],
    "A4": ["Communication", "Guidance", "Facilitation", "Recognition"],
    "B1": ["Ownership", "Translation", "Distribution"],
    "B2": ["Review", "Decisions", "Support"],
    "B3": ["Peer Learning Circles", "Safety", "Experimentation"],
    "B4": ["Purpose", "Parent Clarity", "Teacher Support"],
    "B5": ["Strategy", "Activation", "Feedback"],
}

TEACHER_AREAS = ["A1", "A2", "A3", "A4"]
LEADER_AREAS = ["B1", "B2", "B3", "B4", "B5"]

# Colors
C_PRIMARY = "#1a365d"
C_ACCENT = "#2b6cb0"
C_GREEN = "#38a169"
C_AMBER = "#d69e2e"
C_RED = "#e53e3e"
C_LIGHT = "#ebf4ff"
C_BG = "#f7fafc"

SCORE_COLORS = ["#e53e3e", "#ed8936", "#d69e2e", "#38a169"]
SCORE_CMAP = LinearSegmentedColormap.from_list("score", ["#e53e3e", "#ed8936", "#ecc94b", "#38a169"], N=256)


def load_data(path):
    with open(path) as f:
        return json.load(f)


def split_data(data):
    teachers = [r for r in data if r["lens"] == "T"]
    leaders = [r for r in data if r["lens"] == "L"]
    return teachers, leaders


def compute_overall_area_stats(records, areas):
    """Compute overall area-level stats across all records."""
    area_scores = {a: [] for a in areas}
    for r in records:
        for a in areas:
            if a in r["areas"]:
                area_scores[a].append(r["areas"][a]["avg"])
    stats = {}
    for a in areas:
        vals = area_scores[a]
        if vals:
            stats[a] = {
                "mean": np.mean(vals),
                "median": np.median(vals),
                "std": np.std(vals),
                "min": np.min(vals),
                "max": np.max(vals),
                "n": len(vals),
                "pct": np.mean(vals) / 4 * 100,
            }
        else:
            stats[a] = {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0, "n": 0, "pct": 0}
    return stats


def compute_branch_area_matrix(records, areas):
    """Compute area averages per branch."""
    branch_data = defaultdict(lambda: {a: [] for a in areas})
    branch_names = {}
    for r in records:
        bc = r.get("bc", "")
        if not bc:
            continue
        branch_names[bc] = r.get("branch", bc)
        for a in areas:
            if a in r["areas"]:
                branch_data[bc][a].append(r["areas"][a]["avg"])

    matrix = {}
    for bc in sorted(branch_data.keys()):
        matrix[bc] = {"name": branch_names.get(bc, bc), "n": 0}
        for a in areas:
            vals = branch_data[bc][a]
            matrix[bc][a] = np.mean(vals) if vals else 0
            matrix[bc]["n"] = max(matrix[bc]["n"], len(vals))
    return matrix


def compute_score_distribution(records, areas):
    """Count Strongly Agree/Agree/Disagree/Strongly Disagree per area."""
    dist = {a: {"SA": 0, "A": 0, "D": 0, "SD": 0, "total": 0} for a in areas}
    for r in records:
        for a in areas:
            if a in r["areas"]:
                s = r["areas"][a]
                # Approximate from avg: avg=4->SA, avg=3->A, avg=2->D, avg=1->SD
                # More accurate: use total and count to infer
                avg = s["avg"]
                if avg >= 3.5:
                    dist[a]["SA"] += 1
                elif avg >= 2.5:
                    dist[a]["A"] += 1
                elif avg >= 1.5:
                    dist[a]["D"] += 1
                else:
                    dist[a]["SD"] += 1
                dist[a]["total"] += 1
    return dist


def score_band(avg):
    if avg >= 3.5:
        return "Strong", C_GREEN
    elif avg >= 2.5:
        return "Moderate", C_AMBER
    elif avg >= 1.5:
        return "Developing", "#ed8936"
    else:
        return "Limited", C_RED


# ── Dashboard Generator ─────────────────────────────────────────────────────
def generate_dashboard(records, areas, lens_label, output_path):
    """Generate a complete dashboard PNG for one lens."""
    if not records:
        print(f"  No records for {lens_label}, skipping.")
        return

    overall = compute_overall_area_stats(records, areas)
    branch_matrix = compute_branch_area_matrix(records, areas)
    dist = compute_score_distribution(records, areas)

    n_branches = len(branch_matrix)
    n_users = len(records)

    # Figure layout
    fig = plt.figure(figsize=(22, 28), facecolor=C_BG, dpi=150)
    gs = gridspec.GridSpec(5, 2, figure=fig, hspace=0.35, wspace=0.25,
                           left=0.06, right=0.96, top=0.94, bottom=0.03)

    # ── Title ────────────────────────────────────────────────────────────
    fig.suptitle(
        f"Stage 4.3 Practice Diagnostics — {lens_label} Lens\n"
        f"Enablement & Systems Baseline",
        fontsize=22, fontweight="bold", color=C_PRIMARY, y=0.98
    )
    fig.text(0.5, 0.955,
             f"Respondents: {n_users}  |  Branches: {n_branches}  |  "
             f"Scale: Strongly Agree (4) → Strongly Disagree (1)",
             ha="center", fontsize=11, color="#4a5568")

    # ── 1. Area Score Cards (top row, full width) ────────────────────────
    ax_cards = fig.add_subplot(gs[0, :])
    ax_cards.set_xlim(0, len(areas))
    ax_cards.set_ylim(0, 1)
    ax_cards.axis("off")

    card_w = 0.9 / len(areas)
    card_gap = 0.1 / (len(areas) + 1)
    for i, a in enumerate(areas):
        s = overall[a]
        band, color = score_band(s["mean"])
        x = card_gap + i * (card_w + card_gap)

        # Card background
        rect = FancyBboxPatch((x * len(areas), 0.05), card_w * len(areas), 0.85,
                               boxstyle="round,pad=0.05", facecolor="white",
                               edgecolor=color, linewidth=2.5)
        ax_cards.add_patch(rect)

        cx = (x + card_w / 2) * len(areas)
        # Area code
        ax_cards.text(cx, 0.82, a, fontsize=14, fontweight="bold", color=color,
                      ha="center", va="center")
        # Area name
        ax_cards.text(cx, 0.68, AREA_LABELS[a], fontsize=9, color="#4a5568",
                      ha="center", va="center", linespacing=1.2)
        # Score
        ax_cards.text(cx, 0.42, f"{s['mean']:.2f}", fontsize=28, fontweight="bold",
                      color=color, ha="center", va="center")
        # Percentage
        ax_cards.text(cx, 0.24, f"{s['pct']:.0f}%", fontsize=13, color="#718096",
                      ha="center", va="center")
        # Band label
        ax_cards.text(cx, 0.12, band, fontsize=10, fontweight="bold", color=color,
                      ha="center", va="center",
                      bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.12, edgecolor="none"))

    # ── 2. Area Average Bar Chart ────────────────────────────────────────
    ax_bar = fig.add_subplot(gs[1, 0])
    means = [overall[a]["mean"] for a in areas]
    colors = [score_band(m)[1] for m in means]
    bars = ax_bar.barh(areas[::-1], means[::-1], color=[score_band(m)[1] for m in means[::-1]],
                        height=0.6, edgecolor="white", linewidth=0.5)
    ax_bar.set_xlim(0, 4.2)
    ax_bar.set_xlabel("Average Score (out of 4)", fontsize=10)
    ax_bar.set_title("Overall Area Averages", fontsize=13, fontweight="bold", color=C_PRIMARY, pad=10)
    for bar, val in zip(bars, means[::-1]):
        ax_bar.text(val + 0.05, bar.get_y() + bar.get_height() / 2,
                    f"{val:.2f}", va="center", fontsize=11, fontweight="bold", color="#2d3748")
    ax_bar.axvline(x=2.5, color="#a0aec0", linestyle="--", linewidth=0.8, alpha=0.5)
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)
    ax_bar.tick_params(axis="y", labelsize=11)

    # ── 3. Score Distribution (stacked horizontal) ───────────────────────
    ax_dist = fig.add_subplot(gs[1, 1])
    sa_vals, a_vals, d_vals, sd_vals = [], [], [], []
    for a in areas:
        t = dist[a]["total"] or 1
        sa_vals.append(dist[a]["SA"] / t * 100)
        a_vals.append(dist[a]["A"] / t * 100)
        d_vals.append(dist[a]["D"] / t * 100)
        sd_vals.append(dist[a]["SD"] / t * 100)

    y_pos = np.arange(len(areas))
    ax_dist.barh(y_pos, sa_vals, height=0.5, label="Strong (≥3.5)", color=C_GREEN)
    ax_dist.barh(y_pos, a_vals, height=0.5, left=sa_vals, label="Moderate (2.5-3.5)", color=C_AMBER)
    left2 = [sa_vals[i] + a_vals[i] for i in range(len(areas))]
    ax_dist.barh(y_pos, d_vals, height=0.5, left=left2, label="Developing (1.5-2.5)", color="#ed8936")
    left3 = [left2[i] + d_vals[i] for i in range(len(areas))]
    ax_dist.barh(y_pos, sd_vals, height=0.5, left=left3, label="Limited (<1.5)", color=C_RED)
    ax_dist.set_yticks(y_pos)
    ax_dist.set_yticklabels(areas, fontsize=11)
    ax_dist.set_xlim(0, 100)
    ax_dist.set_xlabel("% of respondents", fontsize=10)
    ax_dist.set_title("Score Band Distribution", fontsize=13, fontweight="bold", color=C_PRIMARY, pad=10)
    ax_dist.legend(loc="lower right", fontsize=8, framealpha=0.9)
    ax_dist.spines["top"].set_visible(False)
    ax_dist.spines["right"].set_visible(False)
    ax_dist.invert_yaxis()

    # ── 4. Radar / Spider Chart ──────────────────────────────────────────
    ax_radar = fig.add_subplot(gs[2, 0], projection="polar")
    angles = np.linspace(0, 2 * np.pi, len(areas), endpoint=False).tolist()
    values = [overall[a]["mean"] for a in areas]
    values += values[:1]
    angles += angles[:1]
    ax_radar.fill(angles, values, color=C_ACCENT, alpha=0.2)
    ax_radar.plot(angles, values, color=C_ACCENT, linewidth=2.5, marker="o", markersize=8)
    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels([f"{a}\n{overall[a]['mean']:.2f}" for a in areas], fontsize=10, fontweight="bold")
    ax_radar.set_ylim(0, 4)
    ax_radar.set_yticks([1, 2, 3, 4])
    ax_radar.set_yticklabels(["1", "2", "3", "4"], fontsize=8, color="#a0aec0")
    ax_radar.set_title("Area Profile", fontsize=13, fontweight="bold", color=C_PRIMARY, y=1.08)
    # Reference circle at 2.5
    ref_angles = np.linspace(0, 2 * np.pi, 100)
    ax_radar.plot(ref_angles, [2.5] * 100, color="#a0aec0", linestyle="--", linewidth=0.8, alpha=0.5)

    # ── 5. Box Plot per Area ─────────────────────────────────────────────
    ax_box = fig.add_subplot(gs[2, 1])
    box_data = []
    for a in areas:
        vals = [r["areas"][a]["avg"] for r in records if a in r["areas"]]
        box_data.append(vals)
    bp = ax_box.boxplot(box_data, labels=areas, patch_artist=True, widths=0.5,
                         medianprops=dict(color=C_PRIMARY, linewidth=2))
    for patch, a in zip(bp["boxes"], areas):
        _, color = score_band(overall[a]["mean"])
        patch.set_facecolor(color)
        patch.set_alpha(0.3)
    ax_box.set_ylabel("Average Score", fontsize=10)
    ax_box.set_ylim(0.5, 4.5)
    ax_box.set_title("Score Distribution by Area", fontsize=13, fontweight="bold", color=C_PRIMARY, pad=10)
    ax_box.axhline(y=2.5, color="#a0aec0", linestyle="--", linewidth=0.8, alpha=0.5)
    ax_box.spines["top"].set_visible(False)
    ax_box.spines["right"].set_visible(False)

    # ── 6. Branch Heatmap ────────────────────────────────────────────────
    ax_heat = fig.add_subplot(gs[3, :])
    if branch_matrix:
        # Sort branches by total average score descending
        sorted_branches = sorted(branch_matrix.keys(),
                                  key=lambda bc: np.mean([branch_matrix[bc].get(a, 0) for a in areas]),
                                  reverse=True)
        # Limit to top 30 for readability
        if len(sorted_branches) > 30:
            sorted_branches = sorted_branches[:30]

        heat_data = []
        y_labels = []
        for bc in sorted_branches:
            bm = branch_matrix[bc]
            row = [bm.get(a, 0) for a in areas]
            heat_data.append(row)
            name = bm["name"]
            if len(name) > 50:
                name = name[:47] + "..."
            y_labels.append(f"{name} ({bc}) [n={bm['n']}]")

        heat_arr = np.array(heat_data)
        im = ax_heat.imshow(heat_arr, cmap=SCORE_CMAP, aspect="auto", vmin=1, vmax=4)
        ax_heat.set_xticks(range(len(areas)))
        ax_heat.set_xticklabels(areas, fontsize=11, fontweight="bold")
        ax_heat.set_yticks(range(len(y_labels)))
        ax_heat.set_yticklabels(y_labels, fontsize=7.5)
        ax_heat.set_title(f"Branch × Area Heatmap (top {len(sorted_branches)} branches)",
                           fontsize=13, fontweight="bold", color=C_PRIMARY, pad=10)

        # Annotate cells
        for i in range(len(sorted_branches)):
            for j in range(len(areas)):
                val = heat_arr[i, j]
                txt_color = "white" if val < 2.0 or val > 3.5 else "#2d3748"
                ax_heat.text(j, i, f"{val:.1f}", ha="center", va="center",
                             fontsize=8, fontweight="bold", color=txt_color)

        plt.colorbar(im, ax=ax_heat, shrink=0.6, label="Avg Score (1-4)")
    else:
        ax_heat.text(0.5, 0.5, "No branch data available", ha="center", va="center",
                     fontsize=14, color="#a0aec0")
        ax_heat.axis("off")

    # ── 7. Summary Table ─────────────────────────────────────────────────
    ax_table = fig.add_subplot(gs[4, :])
    ax_table.axis("off")
    ax_table.set_title("Area Summary Statistics", fontsize=13, fontweight="bold",
                        color=C_PRIMARY, pad=10, loc="left")

    table_data = []
    for a in areas:
        s = overall[a]
        band, _ = score_band(s["mean"])
        goals = ", ".join(AREA_GOALS.get(a, []))
        table_data.append([
            a,
            AREA_LABELS[a].replace("\n", " "),
            f"{s['n']}",
            f"{s['mean']:.2f}",
            f"{s['median']:.2f}",
            f"{s['std']:.2f}",
            f"{s['pct']:.0f}%",
            band,
            goals
        ])

    col_labels = ["Area", "Name", "N", "Mean", "Median", "Std Dev", "%", "Band", "Sub-Areas (Goals)"]
    table = ax_table.table(cellText=table_data, colLabels=col_labels,
                            loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1, 1.6)

    # Style header
    for j in range(len(col_labels)):
        cell = table[0, j]
        cell.set_facecolor(C_PRIMARY)
        cell.set_text_props(color="white", fontweight="bold")

    # Style data rows
    for i in range(len(table_data)):
        band_text = table_data[i][7]
        if band_text == "Strong":
            bg = "#f0fff4"
        elif band_text == "Moderate":
            bg = "#fffff0"
        elif band_text == "Developing":
            bg = "#fffaf0"
        else:
            bg = "#fff5f5"
        for j in range(len(col_labels)):
            table[i + 1, j].set_facecolor(bg)

    # Adjust last column width for goals
    for i in range(len(table_data) + 1):
        table[i, 8].set_width(0.25)

    # Save
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close()
    print(f"  Dashboard saved: {output_path}")


def generate_csv_report(records, areas, lens_label, output_path):
    """Generate CSV with per-user area scores."""
    import csv
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["UserId", "FullName", "Role", "Language", "School", "Branch", "BranchCode"]
        for a in areas:
            header.extend([f"{a}_Score", f"{a}_Avg", f"{a}_Pct"])
        header.append("OverallAvg")
        writer.writerow(header)

        for r in records:
            row = [r["uid"], r["name"], r["role"], r["lang"], r["school"], r["branch"], r["bc"]]
            all_avgs = []
            for a in areas:
                if a in r["areas"]:
                    s = r["areas"][a]
                    row.extend([s["s"], s["avg"], s["pct"]])
                    all_avgs.append(s["avg"])
                else:
                    row.extend([0, 0, 0])
            row.append(round(np.mean(all_avgs), 2) if all_avgs else 0)
            writer.writerow(row)
    print(f"  CSV saved: {output_path}")


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "baseline_responses.json")
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    print("Loading data...")
    data = load_data(data_path)
    teachers, leaders = split_data(data)

    print(f"\nTeacher Lens: {len(teachers)} respondents")
    print(f"Leader Lens: {len(leaders)} respondents")

    print("\n── Generating Teacher Lens Dashboard (A1-A4) ──")
    generate_dashboard(teachers, TEACHER_AREAS, "Teacher",
                        os.path.join(output_dir, "baseline_dashboard_teacher.png"))
    generate_csv_report(teachers, TEACHER_AREAS, "Teacher",
                         os.path.join(output_dir, "baseline_scores_teacher.csv"))

    print("\n── Generating Leader Lens Dashboard (B1-B5) ──")
    generate_dashboard(leaders, LEADER_AREAS, "Leader",
                        os.path.join(output_dir, "baseline_dashboard_leader.png"))
    generate_csv_report(leaders, LEADER_AREAS, "Leader",
                         os.path.join(output_dir, "baseline_scores_leader.csv"))

    print("\nDone!")


if __name__ == "__main__":
    main()
