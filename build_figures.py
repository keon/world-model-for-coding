"""Generate the two figures embedded in paper.pdf.

Outputs:
  fig_timeline.{pdf,png} - 12-year arc with three parallel lineages
  fig_taxonomy.{pdf,png} - survey structure tree

Usage: python3 build_figures.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
from matplotlib.lines import Line2D

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial Unicode MS", "DejaVu Sans", "Helvetica", "Arial"],
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

LANE_COLORS = {
    "Neural execution":   {"dot": "#1f5aa0", "band": "#eef3f9", "label": "#1f5aa0"},
    "World models / RL":  {"dot": "#b03030", "band": "#fbeded", "label": "#b03030"},
    "Code LLMs":          {"dot": "#1f7a3a", "band": "#ecf4ee", "label": "#1f7a3a"},
}


def timeline():
    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor("white")

    lanes = ["Neural execution", "World models / RL", "Code LLMs"]
    lane_y = {l: i * 2.4 for i, l in enumerate(reversed(lanes))}

    for l, y in lane_y.items():
        c = LANE_COLORS[l]
        ax.axhspan(y - 0.95, y + 0.95, color=c["band"], zorder=0)
        ax.plot([2013.5, 2026.5], [y, y], color="#cccccc", linewidth=0.6,
                linestyle="--", zorder=0.5)
        ax.text(2013.4, y, l, fontsize=11, fontweight="bold",
                color=c["label"], ha="right", va="center")

    # Year axis
    for yr in range(2014, 2027):
        ax.axvline(yr, color="#e4e4e4", linewidth=0.5, zorder=0)
    ax.set_xticks(range(2014, 2027))
    ax.set_xticklabels(range(2014, 2027), fontsize=10, color="#333")
    ax.tick_params(axis="x", colors="#aaa", length=4)

    events = {
        "Neural execution": [
            (2014.0, "Learning to Execute", "above"),
            (2015.0, "Neural Programmer-Interpreters", "below"),
            (2017.0, "Dynamic Neural Program Embedding", "above"),
            (2019.0, "Neural Code Fusion", "below"),
            (2020.0, "IPA-GNN", "above"),
        ],
        "World models / RL": [
            (2018.0, "Ha & Schmidhuber\nWorld Models", "below"),
            (2023.4, "RAP", "above"),
            (2024.5, "Generating CWMs\nvia MCTS ◆", "below"),
            (2024.95, "WebDreamer ◆", "above"),
            (2025.3, "CoLA ◆", "below"),
            (2025.85, "CWM ◆◆", "above"),
            (2026.2, "Debugging CWMs", "below"),
        ],
        "Code LLMs": [
            (2021.0, "Codex /\nScratchpads", "above"),
            (2022.5, "CodeRL", "below"),
            (2023.6, "CodeExecutor /\nTRACED", "above"),
            (2023.95, "SWE-bench", "below"),
            (2024.3, "CodeAct /\nSWE-agent", "above"),
            (2024.65, "NExT /\nSemCoder", "below"),
            (2024.95, "RLEF", "above"),
            (2025.15, "DeepSeek-R1", "below"),
            (2025.4, "SWE-RL", "above"),
            (2025.75, "ATLAS / CLEVER", "below"),
            (2026.2, "Industrial CWM,\nARC executable WMs", "above"),
        ],
    }

    for lane, items in events.items():
        c = LANE_COLORS[lane]
        y_lane = lane_y[lane]
        for x, label, side in items:
            ax.plot(x, y_lane, "o", color=c["dot"], markersize=8,
                    markeredgecolor="white", markeredgewidth=1.2, zorder=4)
            offset = 0.55 if side == "above" else -0.55
            ax.plot([x, x], [y_lane, y_lane + offset * 0.7],
                    color=c["dot"], linewidth=0.8, zorder=3)
            ax.text(x, y_lane + offset, label,
                    fontsize=8, ha="center",
                    va="bottom" if side == "above" else "top",
                    color="#1a1a1a",
                    bbox=dict(boxstyle="round,pad=0.2",
                              facecolor="white",
                              edgecolor=c["dot"],
                              linewidth=0.6))

    # Bottom legend
    ax.text(2014, -2.0,
            "◆ first paper to use \"world model\" / \"Dreamer\" in the contribution name",
            fontsize=9, color="#555")
    ax.text(2014, -2.5,
            "◆◆ CWM — the named open-weights artifact",
            fontsize=9, color="#555")

    ax.set_xlim(2013.2, 2026.7)
    ax.set_ylim(-3.2, max(lane_y.values()) + 1.6)
    ax.set_yticks([])
    ax.set_title("Twelve-Year Arc of Code World Models (2014 – 2026)",
                 fontsize=15, fontweight="bold", pad=18, color="#1a1a1a")
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#bbb")
    ax.spines["bottom"].set_linewidth(0.8)

    plt.tight_layout()
    for ext in ("pdf", "png"):
        plt.savefig(f"fig_timeline.{ext}", bbox_inches="tight", dpi=220,
                    facecolor=fig.get_facecolor())
    plt.close()


def taxonomy():
    fig, ax = plt.subplots(figsize=(11, 8))
    fig.patch.set_facecolor("white")

    def box(x, y, w, h, text, fc, ec, fontsize=10, weight="normal",
            text_color="#1a1a1a"):
        ax.add_patch(FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            fc=fc, ec=ec, linewidth=1.4, zorder=3))
        ax.text(x, y, text, ha="center", va="center",
                fontsize=fontsize, fontweight=weight, color=text_color)

    def arrow(x1, y1, x2, y2):
        ax.plot([x1, x2], [y1, y2], color="#9a9a9a",
                linewidth=1.2, zorder=1, solid_capstyle="round")

    # Root
    box(7, 9.3, 5.6, 0.85, "World Models for Coding",
        fc="#2c4a82", ec="#162a52", fontsize=14, weight="bold",
        text_color="white")
    ax.text(7, 8.65, "184 papers · this survey",
            ha="center", fontsize=9, color="#666", style="italic")

    # Three primary lanes (modeling axes)
    lanes = [
        ("Modeling Code",   1.8,  "#d8efd6", "#3a8a3a"),
        ("Modeling Agents", 7.0,  "#f8dcdc", "#a04040"),
        ("Modeling Tasks", 12.2,  "#fbe9c2", "#a07840"),
    ]
    for label, x, fc, ec in lanes:
        box(x, 7.4, 3.6, 0.75, label, fc=fc, ec=ec,
            fontsize=11, weight="bold")
        arrow(7, 8.85, x, 7.78)

    # Sub-nodes for each lane
    sub = {
        "Modeling Code": [
            ("§6 Foundations",         0.2),
            ("§7 Trace pretraining",   1.8),
            ("§7 CWM lineage",         3.4),
        ],
        "Modeling Agents": [
            ("§8 Web / OS / SWE",      5.4),
            ("§9 Execution-grounded RL", 7.0),
            ("§10 Planning & search",  8.6),
        ],
        "Modeling Tasks": [
            ("§13 Reasoning + memory", 10.6),
            ("§14 Verifier + probing", 12.2),
            ("§14 Safety",             13.8),
        ],
    }
    fc_per = {"Modeling Code": "#eefae9", "Modeling Agents": "#fdf2f2",
              "Modeling Tasks": "#fff5e0"}
    ec_per = {"Modeling Code": "#3a8a3a", "Modeling Agents": "#a04040",
              "Modeling Tasks": "#a07840"}
    base_x = {"Modeling Code": 1.8, "Modeling Agents": 7.0, "Modeling Tasks": 12.2}

    for lane, items in sub.items():
        for label, x in items:
            box(x, 5.9, 1.5, 0.55, label,
                fc=fc_per[lane], ec=ec_per[lane], fontsize=8)
            arrow(base_x[lane], 7.02, x, 6.17)

    # Cross-cutting bridge
    box(7, 4.6, 10.5, 0.7,
        "§11   JEPA · Dreamer · latent-action gap   (cross-cutting bridge)",
        fc="#ece2fc", ec="#5c4296", fontsize=11, weight="bold")
    for x in [1.8, 7.0, 12.2]:
        arrow(x, 5.62, x, 4.95)

    # Synthesis cascade
    box(7, 3.4, 10.5, 0.6,
        "§12   Specialized domains   (diffusion · decompilation · hardware/RTL · ARC · self-play)",
        fc="#e1f6fa", ec="#3a8c9a", fontsize=9.5)
    box(7, 2.3, 10.5, 0.6,
        "§15 – 16   Benchmarks · Empirical landscape   (protocol-stratified tables)",
        fc="#f3f3f3", ec="#777", fontsize=9.5)
    box(7, 1.2, 10.5, 0.6,
        "§17   Critical perspectives   (seven theses)",
        fc="#fde8e8", ec="#a04040", fontsize=10, weight="bold")
    box(7, 0.1, 10.5, 0.6,
        "§18   Open problems         |        §19   Conclusion",
        fc="#f3f3f3", ec="#777", fontsize=9.5)
    for y1, y2 in [(4.25, 3.7), (3.1, 2.6), (2.0, 1.5), (0.9, 0.4)]:
        arrow(7, y1, 7, y2)

    ax.set_xlim(-1.0, 15.0)
    ax.set_ylim(-0.5, 10.5)
    ax.axis("off")
    ax.set_title("Survey Structure: A Taxonomy of World Models for Coding",
                 fontsize=14, fontweight="bold", pad=10, color="#1a1a1a")

    plt.tight_layout()
    for ext in ("pdf", "png"):
        plt.savefig(f"fig_taxonomy.{ext}", bbox_inches="tight", dpi=220,
                    facecolor=fig.get_facecolor())
    plt.close()


if __name__ == "__main__":
    timeline()
    taxonomy()
    print("wrote fig_timeline.{pdf,png} and fig_taxonomy.{pdf,png}")
