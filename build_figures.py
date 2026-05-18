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
    fig, ax = plt.subplots(figsize=(11, 5))
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
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor("white")

    ACCENT = "#2c4a82"
    INK = "#1a1a1a"
    MUTED = "#888888"
    RULE = "#dcdcdc"

    # Column headers
    columns = [
        ("Modeling Code",   1.5),
        ("Modeling Agents", 5.0),
        ("Modeling Tasks",  8.5),
    ]
    for label, x in columns:
        ax.text(x, 5.4, label, ha="center", va="center",
                fontsize=11, fontweight="bold", color=ACCENT)
        ax.plot([x - 1.4, x + 1.4], [5.15, 5.15],
                color=ACCENT, linewidth=1.1, solid_capstyle="round")

    # Stack of section labels per column (no boxes, just text)
    items = {
        1.5: [
            ("§6",  "Foundations"),
            ("§7",  "Trace pretraining"),
            ("§7",  "CWM lineage"),
        ],
        5.0: [
            ("§8",  "Web / OS / SWE agents"),
            ("§9",  "Execution-grounded RL"),
            ("§10", "Planning & search"),
        ],
        8.5: [
            ("§13", "Reasoning + memory"),
            ("§14", "Verification + probing"),
            ("§14", "Safety"),
        ],
    }
    for x, rows in items.items():
        y = 4.7
        for tag, name in rows:
            ax.text(x - 1.1, y, tag, ha="right", va="center",
                    fontsize=9, color=MUTED, family="monospace")
            ax.text(x - 0.95, y, name, ha="left", va="center",
                    fontsize=10, color=INK)
            y -= 0.45

    # Horizontal rule
    ax.plot([0.2, 9.8], [2.85, 2.85], color=RULE, linewidth=0.8)

    # Cross-cutting bridge
    ax.text(5.0, 2.55, "§11   JEPA · Dreamer · latent-action gap",
            ha="center", va="center", fontsize=10.5,
            fontweight="bold", color=ACCENT, style="italic")
    ax.text(5.0, 2.2, "(applies across all three columns above)",
            ha="center", va="center", fontsize=8.5, color=MUTED)

    # Horizontal rule
    ax.plot([0.2, 9.8], [1.85, 1.85], color=RULE, linewidth=0.8)

    # Synthesis chapters laid out horizontally
    synth = [
        ("§12",   "Specialized domains",                 1.5, 1.4),
        ("§15-16","Benchmarks · Empirical landscape",    5.0, 1.4),
        ("§17",   "Critical perspectives",               8.5, 1.4),
    ]
    for tag, name, x, y in synth:
        ax.text(x, y, tag, ha="center", va="center",
                fontsize=9, color=MUTED, family="monospace")
        ax.text(x, y - 0.35, name, ha="center", va="center",
                fontsize=10, color=INK)

    # Footer
    ax.text(5.0, 0.25, "§18   Open problems         §19   Conclusion",
            ha="center", va="center", fontsize=9.5, color=INK)

    ax.set_xlim(0, 10)
    ax.set_ylim(-0.2, 6.0)
    ax.axis("off")

    plt.tight_layout()
    for ext in ("pdf", "png"):
        plt.savefig(f"fig_taxonomy.{ext}", bbox_inches="tight", dpi=220,
                    facecolor=fig.get_facecolor())
    plt.close()


if __name__ == "__main__":
    timeline()
    taxonomy()
    print("wrote fig_timeline.{pdf,png} and fig_taxonomy.{pdf,png}")
