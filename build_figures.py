"""Generate the two figures embedded in paper.pdf.

Outputs:
  fig_timeline.{pdf,png} — 12-year arc with three parallel lineages
  fig_taxonomy.{pdf,png} — survey structure tree

Usage: python3 build_figures.py
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def timeline():
    fig, ax = plt.subplots(figsize=(13, 7.5))
    lanes = ["Neural execution", "World models / RL", "Code LLMs"]
    lane_y = {l: i * 1.6 for i, l in enumerate(reversed(lanes))}
    for l, y in lane_y.items():
        ax.axhspan(y - 0.6, y + 0.6, color="#f4f4f4", zorder=0)
        ax.text(2013.6, y, l, fontsize=10, fontweight="bold", ha="right", va="center")
    for yr in range(2014, 2027):
        ax.axvline(yr, color="#d8d8d8", linewidth=0.5, zorder=0)
    ax.set_xticks(list(range(2014, 2027)))
    ax.set_xticklabels(range(2014, 2027), fontsize=9)

    events = {
        "Neural execution": [
            (2014, "Learning to Execute (1410.4615)"),
            (2015, "Neural Programmer-Interpreters"),
            (2017, "Dynamic Neural Program Embedding"),
            (2019, "Neural Code Fusion"),
            (2020, "IPA-GNN (interpreter line stalls)"),
        ],
        "World models / RL": [
            (2018, "Ha & Schmidhuber"),
            (2023.3, "RAP (LLM-as-WM + MCTS)"),
            (2024.4, "Generating CWMs via MCTS ◆"),
            (2024.9, "WebDreamer ◆"),
            (2025.3, "CoLA ◆"),
            (2025.8, "CWM ◆◆"),
            (2026.0, "Debugging CWMs / RWM-Learning"),
        ],
        "Code LLMs": [
            (2021, "Codex / Show Your Work"),
            (2022, "CodeRL"),
            (2023.4, "CodeExecutor / TRACED"),
            (2023.8, "SWE-bench"),
            (2024.2, "CodeAct / SWE-agent"),
            (2024.5, "NExT / SemCoder"),
            (2024.8, "RLEF"),
            (2025.1, "DeepSeek-R1"),
            (2025.2, "SWE-RL"),
            (2025.6, "ATLAS / CLEVER (verifier-grounded)"),
            (2026.3, "Industrial CWM, ARC executable WMs"),
        ],
    }
    colors = {"Neural execution": "#1f77b4", "World models / RL": "#d62728", "Code LLMs": "#2ca02c"}
    for lane, items in events.items():
        y = lane_y[lane]
        for x, label in items:
            ax.plot(x, y, "o", color=colors[lane], markersize=7, zorder=3)
            ax.annotate(label, (x, y), xytext=(0, 8), textcoords="offset points",
                        fontsize=7.5, ha="left", rotation=20, color="#222")

    ax.text(2014, -1.7,
            "◆ first paper to use \"world model\" / \"Dreamer\" in a contribution name.    ◆◆ CWM = named open-weights artifact.",
            fontsize=8, color="#555")
    ax.set_xlim(2013.2, 2026.7)
    ax.set_ylim(-2.2, max(lane_y.values()) + 1.8)
    ax.set_yticks([])
    ax.set_title("Twelve-Year Arc of Code World Models (2014–2026)",
                 fontsize=13, fontweight="bold", pad=15)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#888")
    plt.tight_layout()
    for ext in ("pdf", "png"):
        plt.savefig(f"fig_timeline.{ext}", bbox_inches="tight", dpi=200)
    plt.close()


def taxonomy():
    fig, ax = plt.subplots(figsize=(13, 8))

    def box(x, y, w, h, text, color="#e8eef8", edge="#3a5fa5", fontsize=9, weight="normal"):
        ax.add_patch(FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            fc=color, ec=edge, linewidth=1.3, zorder=2))
        ax.text(x, y, text, ha="center", va="center",
                fontsize=fontsize, fontweight=weight)

    def line(x1, y1, x2, y2):
        ax.plot([x1, x2], [y1, y2], color="#7a7a7a", linewidth=1.2, zorder=1)

    box(6, 9, 4.2, 0.7, "World Models for Coding",
        color="#3a5fa5", edge="#1a3978", fontsize=12, weight="bold")
    ax.text(6, 8.55, "(184 papers · §§6–17)", ha="center", fontsize=8, color="#444")
    for label, x, color in [
        ("Modeling Code", 1.8, "#e8f4e8"),
        ("Modeling Agents", 6.0, "#fde8e8"),
        ("Modeling Tasks", 10.2, "#fff4d6"),
    ]:
        box(x, 7.2, 2.8, 0.65, label, color=color, edge="#666", fontsize=10, weight="bold")
        line(6, 8.65, x, 7.52)

    for items, base_y, edge, fill in [
        ([("§6 Foundations", 0.5), ("§7 Trace pretraining", 1.8), ("§7 CWM lineage", 3.1)], 1.8, "#3a8a3a", "#f4faf4"),
        ([("§8 Web / OS / SWE", 4.7), ("§9 Execution-grounded RL", 6.0), ("§10 Planning & search", 7.3)], 6.0, "#a04040", "#fdf4f4"),
        ([("§13 Reasoning + memory", 8.9), ("§14 Verifier + probing", 10.2), ("§14 Safety", 11.5)], 10.2, "#a08040", "#fffaef"),
    ]:
        for label, x in items:
            box(x, 6.0, 1.2, 0.5, label, color=fill, edge=edge, fontsize=7.5)
            line(base_y, 6.85, x, 6.25)

    box(6, 4.5, 8.0, 0.6,
        "§11 JEPA / Dreamer / latent-action gap  (cross-cutting bridge)",
        color="#f3eaff", edge="#5c4296", fontsize=10, weight="bold")
    for x in [1.8, 6.0, 10.2]:
        line(x, 5.75, x, 4.8)
    box(6, 3.4, 8.0, 0.55,
        "§12 Specialized domains  (diffusion, decompilation, hardware/RTL, ARC, self-play)",
        color="#eefcff", edge="#3a8c9a", fontsize=9)
    box(6, 2.3, 8.0, 0.55,
        "§15–16 Benchmarks · Empirical landscape  (protocol-stratified)",
        color="#f8f8f8", edge="#666", fontsize=9)
    box(6, 1.4, 8.0, 0.55, "§17 Critical perspectives  (seven theses)",
        color="#fff2f2", edge="#a04040", fontsize=9, weight="bold")
    box(6, 0.5, 8.0, 0.55, "§18 Open problems · §19 Conclusion",
        color="#f8f8f8", edge="#666", fontsize=9)
    for y1, y2 in [(4.2, 3.7), (3.1, 2.6), (2.0, 1.7), (1.1, 0.8)]:
        line(6, y1, 6, y2)

    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Taxonomy of World Models for Coding",
                 fontsize=12, fontweight="bold", pad=5)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        plt.savefig(f"fig_taxonomy.{ext}", bbox_inches="tight", dpi=200)
    plt.close()


if __name__ == "__main__":
    timeline()
    taxonomy()
    print("wrote fig_timeline.{pdf,png} and fig_taxonomy.{pdf,png}")
