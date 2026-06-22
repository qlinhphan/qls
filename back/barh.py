import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def barhs(sign, scores):

    fig, ax = plt.subplots(figsize=(8, 4))

    bars = ax.barh(sign, scores, color='skyblue')

    for bar in bars:
        x, y = bar.get_xy()
        width = bar.get_width()
        height = bar.get_height()

        bar.remove()

        rounded_bar = FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.02,rounding_size=0.15",
            facecolor="cornflowerblue",
            edgecolor="none"
        )
        ax.add_patch(rounded_bar)

    ax.set_xlim(0, max(scores) * 1.1)
    ax.set_xlabel("sign")
    ax.set_ylabel("scores")
    ax.set_title("--- Score for test ---")
    ax.grid(axis='x', linestyle='--', alpha=0.3)

    plt.tight_layout()
    # plt.show()
    ax.get_figure().savefig("report/view_semantic_sign.png", bbox_inches="tight")

if __name__ == "__main__":
    sign = ["dh1", 'dh2']
    scores = [1, 2]
    barhs(sign, scores)