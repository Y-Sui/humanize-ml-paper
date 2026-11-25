"""plot_style.py -- the house matplotlib look for data plots.

Hex values were pixel-sampled from the published figures this style was distilled from
(see references/figures_tables.md sections 3-4; evidence labels as defined in SKILL.md).
Conventions encoded here:
  * one PNG per panel at 600 dpi [current]; panels are assembled in LaTeX with subfigure,
    never with plt.subplots(1, n) [all];
  * bold Times everywhere: ticks 16 pt, axis labels 18 pt, legend 14 pt [most];
  * four-sided box [all]; dashed y-only grid #D3D3D3 [current]; #595959 spines at 2.2 pt and
    inward ticks are one variant [some] (black spines are the other);
  * two colour families: saturated = ours / "with", pale tint of the same hue = baseline / "without" [all];
    option [some]: when a figure carries two metric families, the metric picks the hue
    (performance = pink, cost = blue);
  * no titles on plots (the LaTeX subcaption is the title); unit in parentheses [all]; label case
    must be consistent within a paper: Title Case ("Coverage Score (%)") or sentence case
    ("Filtering time (min)") [some each];
  * ICML asks for vector plots where possible: save() writes PNG + PDF, include the PDF there.

Usage:
    import plot_style as ps
    ps.apply()
    fig, ax = ps.new_figure("square")
    ps.raw_and_smoothed(ax, steps, val_acc, ps.PALETTE["blue"], "X")
    ps.save(fig, "figures/exp/dynamics/val_acc")   # writes .png (600 dpi) and .pdf

Worked examples on invented data: assets/make_assets.py (renders assets/plots/*.png).
"""
from __future__ import annotations

import glob
import os

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.transforms import Bbox

# --------------------------------------------------------------------------- palette
PALETTE = {
    # blue family: ours / main series (saturated) vs baseline / w/o (tint)
    "blue": "#649CD8", "blue_light": "#BFD8EF", "blue_text": "#527FD4",
    # pink family: second metric family (e.g., performance when blue = cost)
    "pink": "#FF85A1", "pink_light": "#FFDAE2", "pink_text": "#F1667E",
    # neutrals
    "base_gray": "#A5A5A5",     # plain baseline curve
    "spine": "#595959",         # box, ticks, legend edge
    "grid": "#D3D3D3",          # dashed y-grid (variant: #CFCFCF)
    "sep": "#696969",           # dashed separator before the "Avg" group
    "sep_blue": "#5799C6",      # same, blue variant
    "hatch_edge": "#464646",    # dark hatch edge (hatched variant bars)
    # ordered sweep of ONE hyperparameter, light -> dark; the chosen default is darkest [some]
    "sweep_khaki": ["#DCD4BE", "#BAAE8B", "#8C8064"],
    # categorical without hue: grayscale + hatches "//", "xx", "\\\\" [some]
    "gray3": ["#D6D6D6", "#595959", "#999999"],
}
# Diagram colours (clean palette; see references/figures_tables.md sections 3 and 5 and
# templates/housediagram.sty). White boxes, colour in saturated OUTLINES, black text; not used by plots.
DIAGRAM = {
    "input_box": "#594E54", "panel_bg": "#F6F6F6", "frame": "#595959", "ink": "#1F1F1F",
    "accent_a": "#DB687B", "accent_b": "#143973", "aux_path": "#FFB84D",   # rose / navy outlines; amber = dashed score arrows only
    "success": "#67AB9F", "failure": "#EA6B66",                             # semantic correct / incorrect only
    "box_fill": "#FFFFFF", "trainable_edge": "#DB687B", "frozen_edge": "#143973",
    "item_fill": "#FFFFFF", "item_edge": "#595959",
    "state_fill": "#E3EAF5", "state_edge": "#143973",                       # the one highlighted object, if any
}
# Earlier "ours" colour [older]: warm red #D64F38 / #E56F5E. Use blue for new figures.

# Figure sizes in inches. Printed tick labels should come out at ~7 pt:
# font_pt = 7 * figure_width_in / printed_width_in  (with 16 pt ticks in the source).
#   "wide" (7.7 in)    -> \columnwidth (ICML, 3.25 in) or 0.59\textwidth (NeurIPS/ICLR, 5.5 in text)
#   "square" (3.75 in) -> 0.49\columnwidth or 0.29\textwidth; also each half of a
#                         wrapfigure{r}{0.52\textwidth} pair (NeurIPS space saver)
#   (0.45 / 0.25\textwidth, used earlier, print ~5 pt ticks: too small)
SIZES = {"square": (3.75, 3.47), "wide": (7.72, 3.72), "wide_bar": (8.52, 4.12), "strip": (9.72, 3.92)}

_TIMES = "Times New Roman"
HOUSE_RC = {
    "font.family": "serif",
    "font.serif": [_TIMES, "Times", "Nimbus Roman", "TeX Gyre Termes", "DejaVu Serif"],
    "font.weight": "bold", "font.size": 16,
    "axes.labelweight": "bold", "axes.titleweight": "bold",
    "axes.labelsize": 18, "axes.titlesize": 18,
    "xtick.labelsize": 16, "ytick.labelsize": 16, "legend.fontsize": 14,
    "mathtext.fontset": "custom",
    "mathtext.rm": _TIMES + ":bold", "mathtext.it": _TIMES + ":italic:bold", "mathtext.bf": _TIMES + ":bold",
    "axes.linewidth": 2.2, "axes.edgecolor": PALETTE["spine"],
    "axes.spines.top": True, "axes.spines.right": True,
    "axes.grid": True, "axes.grid.axis": "y", "axes.axisbelow": True,
    "grid.color": PALETTE["grid"], "grid.linestyle": "--", "grid.linewidth": 1.2,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.color": PALETTE["spine"], "ytick.color": PALETTE["spine"],       # tick marks match the spines
    "xtick.labelcolor": "black", "ytick.labelcolor": "black",
    "xtick.major.size": 6, "ytick.major.size": 6, "xtick.major.width": 2.0, "ytick.major.width": 2.0,
    "xtick.minor.visible": False, "ytick.minor.visible": False,
    "lines.linewidth": 2.6, "lines.markersize": 9, "hatch.linewidth": 1.0,
    "legend.frameon": True, "legend.fancybox": True,
    "legend.edgecolor": PALETTE["spine"], "legend.framealpha": 0.8,
    "legend.borderpad": 0.4, "legend.handlelength": 2.0,
    "figure.facecolor": "white",
    "savefig.dpi": 600, "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
    "pdf.fonttype": 42, "ps.fonttype": 42,
}
RC_OLDER_DELTA = {  # [older] look: black 3.5 pt box, grid on both axes, thicker lines
    "axes.edgecolor": "black", "axes.linewidth": 3.5, "axes.grid.axis": "both",
    "grid.color": "#BFBFBF", "grid.linewidth": 2.0, "xtick.direction": "out", "ytick.direction": "out",
    "lines.linewidth": 4.0, "lines.markersize": 12, "legend.edgecolor": "0.8",
    "xtick.color": "black", "ytick.color": "black",
}


def set_palette(**overrides: str) -> None:
    """Override palette entries in place, e.g. set_palette(blue="#4C72B0", blue_light="#C6D4EA").

    The house hex values are a default, not a requirement: keep the roles (saturated = ours,
    tint of the same hue = baseline) and change the hues if your group or venue uses its own."""
    unknown = set(overrides) - set(PALETTE)
    if unknown:
        raise KeyError(f"unknown palette keys: {sorted(unknown)}")
    PALETTE.update(overrides)


def _register_termes_fallback() -> bool:
    """Register TeX Gyre Termes (Times clone from TeX Live) when Times New Roman is not installed."""
    global _TIMES
    existing = {f.name for f in font_manager.fontManager.ttflist}
    if _TIMES in existing:
        return True
    if "TeX Gyre Termes" in existing:
        _TIMES = "TeX Gyre Termes"
        return True
    candidates = [
        "/usr/local/texlive/*/texmf-dist/fonts/opentype/public/tex-gyre/texgyretermes-*.otf",
        "/usr/share/texlive/texmf-dist/fonts/opentype/public/tex-gyre/texgyretermes-*.otf",
        "/usr/share/fonts/**/texgyretermes-*.otf",
    ]
    found = []
    for pat in candidates:
        found.extend(glob.glob(pat, recursive=True))
    if not found:
        return False
    for fp in sorted(set(found)):
        font_manager.fontManager.addfont(fp)
    _TIMES = "TeX Gyre Termes"
    return True


def apply(era: str = "current") -> None:
    """Install the rcParams. era="older" reproduces the earlier look (only to match an older paper)."""
    has_times = _register_termes_fallback()
    mpl.rcParams.update(HOUSE_RC)
    if _TIMES == "TeX Gyre Termes":
        mpl.rcParams.update({
            "font.serif": ["TeX Gyre Termes", "Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"],
            "mathtext.rm": "TeX Gyre Termes:bold",
            "mathtext.it": "TeX Gyre Termes:italic:bold",
            "mathtext.bf": "TeX Gyre Termes:bold",
        })
    mpl.rcParams.update({"axes.edgecolor": PALETTE["spine"], "grid.color": PALETTE["grid"],
                         "legend.edgecolor": PALETTE["spine"], "xtick.color": PALETTE["spine"],
                         "ytick.color": PALETTE["spine"]})   # honour set_palette()
    if era == "older":
        mpl.rcParams.update(RC_OLDER_DELTA)
    if not has_times:
        # A silent fallback to DejaVu Serif is a known accident in published bar charts. Do not ship that.
        print("[plot_style] WARNING: Times New Roman not found; matplotlib will fall back to another "
              "serif. Install Times New Roman (or TeX Gyre Termes) before exporting final figures.")


def new_figure(size: str = "wide"):
    """One figure = one panel (panels are combined in LaTeX with subfigure)."""
    return plt.subplots(figsize=SIZES[size])


def new_fixed_panel(canvas_wh: tuple[float, float], ax_rect: list[float]):
    """Create a panel with fixed canvas size `(W, H)` inches and explicit axes `[x0, y0, w, h]`.

    Use identical `canvas_wh` and congruent `(w, h, y0)` across paired LaTeX subfigures so
    spines, font scaling, and subcaptions align exactly (avoiding `bbox_inches="tight"` drift).
    """
    fig = plt.figure(figsize=canvas_wh, facecolor="white")
    ax = fig.add_axes(ax_rect)
    return fig, ax


def save(fig, path: str, formats=("png", "pdf"), close: bool = True) -> list[str]:
    """Save `fig` as <path>.png (600 dpi) and <path>.pdf; returns the written paths.

    `path` may include or omit an extension; directories are created. Keep superseded versions
    in a sibling *_old/ folder instead of overwriting [most].
    """
    root, ext = os.path.splitext(path)
    if ext.lower() in {".png", ".pdf", ".svg", ".jpg"}:
        path = root
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    written = []
    for fmt in formats:
        out = f"{path}.{fmt}"
        fig.savefig(out, format=fmt, dpi=600 if fmt in {"png", "jpg"} else None)
        written.append(out)
    if close:
        plt.close(fig)
    return written


def save_fixed(
    fig,
    ax,
    path: str,
    canvas_wh: tuple[float, float],
    *,
    leg=None,
    extra_axes: tuple = (),
    formats=("png", "pdf"),
    close: bool = True,
    check_bounds: bool = True,
) -> list[str]:
    """Verify outside-legend clearance and zero border clipping, then save exact `canvas_wh` files."""
    if check_bounds:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        fig_bbox = fig.bbox
        ab = ax.get_window_extent(renderer)
        bboxes = [ab]
        if leg is not None:
            lb = leg.get_window_extent(renderer)
            if lb.overlaps(ab):
                raise ValueError(f"{path}: legend overlaps axes box (gap_px={lb.y0 - ab.y1:.1f})")
            bboxes.append(lb)
        for a in (ax, *extra_axes):
            for lbl in (a.xaxis.label, a.yaxis.label):
                if lbl.get_visible() and lbl.get_text().strip():
                    bboxes.append(lbl.get_window_extent(renderer))
            xlo, xhi = sorted(a.get_xlim())
            ylo, yhi = sorted(a.get_ylim())
            for tk, pos in zip(a.get_xticklabels(), a.get_xticks()):
                if xlo - 1e-9 <= pos <= xhi + 1e-9 and tk.get_visible() and tk.get_text().strip():
                    bboxes.append(tk.get_window_extent(renderer))
            for tk, pos in zip(a.get_yticklabels(), a.get_yticks()):
                if ylo - 1e-9 <= pos <= yhi + 1e-9 and tk.get_visible() and tk.get_text().strip():
                    bboxes.append(tk.get_window_extent(renderer))
        union = Bbox.union(bboxes)
        margins = (
            union.x0 - fig_bbox.x0,
            union.y0 - fig_bbox.y0,
            fig_bbox.x1 - union.x1,
            fig_bbox.y1 - union.y1,
        )
        if min(margins) < 1.0:
            raise ValueError(
                f"{path}: content clips fixed canvas {canvas_wh}; margins_px(L,B,R,T)={[round(m, 1) for m in margins]}"
            )
    root, ext = os.path.splitext(path)
    if ext.lower() in {".png", ".pdf", ".svg", ".jpg"}:
        path = root
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    fixed_bbox = Bbox([[0.0, 0.0], [canvas_wh[0], canvas_wh[1]]])
    written = []
    for fmt in formats:
        out = f"{path}.{fmt}"
        fig.savefig(
            out,
            format=fmt,
            dpi=600 if fmt in {"png", "jpg"} else None,
            bbox_inches=fixed_bbox,
            pad_inches=0.0,
        )
        written.append(out)
    if close:
        plt.close(fig)
    return written


def legend(ax, loc="best", ncol=1, frame_lw=1.5, handles=None, labels=None, **kw):
    """Legend inside the axes in the emptiest corner, bold entries, thin rounded frame [most];
    pass frameon=False on a compact square dynamics panel [some]."""
    args = (handles, labels) if handles is not None else ()
    leg = ax.legend(*args, loc=loc, ncol=ncol,
                    prop={"weight": "bold", "size": mpl.rcParams["legend.fontsize"]}, **kw)
    leg.get_frame().set_linewidth(frame_lw)
    return leg


def legend_above(ax, ncol=3, **kw):
    """Grouped bars with >= 3 series: legend above the axes [some]."""
    return legend(ax, loc="lower center", ncol=ncol, bbox_to_anchor=(0.5, 1.02), **kw)


def legend_outside_top(
    ax,
    *,
    ncol: int = 2,
    size: float = 9.2,
    y_anchor: float = 1.05,
    x_anchor: float = 0.5,
    handles=None,
    labels=None,
    frame_lw: float = 1.2,
    **kw,
):
    """Compact bold legend placed strictly above the top spine so zero plot area is covered."""
    args = (handles, labels) if handles is not None else ()
    defaults = dict(
        handlelength=1.25,
        handletextpad=0.35,
        borderpad=0.25,
        labelspacing=0.22,
        columnspacing=0.60,
        framealpha=0.95,
    )
    defaults.update(kw)
    leg = ax.legend(
        *args,
        loc="lower center",
        bbox_to_anchor=(x_anchor, y_anchor),
        ncol=ncol,
        prop={"weight": "bold", "size": size},
        **defaults,
    )
    if leg.get_frame() is not None:
        leg.get_frame().set_linewidth(frame_lw)
        leg.get_frame().set_edgecolor(PALETTE["spine"])
    return leg


def color_yaxis(ax, color):
    """Twin-axis convention: label and ticks take the text shade of their series [some]."""
    ax.yaxis.label.set_color(color)
    ax.tick_params(axis="y", labelcolor=color)


def value_labels(ax, bars, fmt="{:.2f}", size=10):
    """Bold 2-decimal value labels above bars [current]."""
    for b in bars:
        h = b.get_height()
        ax.annotate(fmt.format(h), (b.get_x() + b.get_width() / 2, h), xytext=(0, 2),
                    textcoords="offset points", ha="center", va="bottom", fontsize=size, fontweight="bold")


def avg_separator(ax, x, color=None):
    """Dashed vertical line before the right-most "Avg" group [current]."""
    ax.axvline(x, ls="--", lw=2, color=color or PALETTE["sep"], zorder=0.5)


def raw_and_smoothed(ax, x, y, color, label, w=5):
    """Thin translucent raw curve under a thick trailing rolling mean [current]. Say so in the caption.
    The mean starts at x[0] (the first w - 1 points average what is available), so no curve starts late."""
    x, y = np.asarray(x), np.asarray(y, dtype=float)
    ax.plot(x, y, color=color, lw=0.9, alpha=0.16)
    w = max(1, min(w, len(y)))
    cs = np.cumsum(np.insert(y, 0, 0.0))
    sm = np.concatenate([cs[1:w] / np.arange(1, w), (cs[w:] - cs[:-w]) / w])
    ax.plot(x, sm, color=color, lw=2.6, label=label)


def hatched_bars(ax, x, h, width, color, hatch="///", dark_edge=None, **kw):
    """Hatches separate conditions without adding hues (white hatch [most]; dark-edged hatch [some]).
    dark_edge=None picks it from the fill: a white hatch vanishes on a pale tint, so pale fills get the
    dark #464646 edge and hatch."""
    if dark_edge is None:
        r, g, b = mpl.colors.to_rgb(color)
        dark_edge = 0.299 * r + 0.587 * g + 0.114 * b > 0.75
    edge = PALETTE["hatch_edge"] if dark_edge else "white"
    return ax.bar(x, h, width, color=color, hatch=hatch, edgecolor=edge,
                  linewidth=1.0 if dark_edge else 0.0, **kw)


# ------------------------------------------------------------------ demo (dummy data, layout only)
if __name__ == "__main__":
    apply()
    P = PALETTE
    xs = np.arange(5)
    fig, ax = new_figure("wide")
    ax2 = ax.twinx()
    ax2.bar(xs - .18, [5, 9, 16, 24, 31], .36, color=P["blue_light"], label="Baseline (Time)")
    ax2.bar(xs + .18, [7, 9, 11, 12, 13], .36, color=P["blue"], label="X (Time)")
    ax.plot(xs, [71, 74, 76, 77, 78], "-o", color=P["pink_light"], label="Baseline (Acc.)")
    ax.plot(xs, [73, 77, 80, 82, 83], "-o", color=P["pink"], label="X (Acc.)")
    ax.set_zorder(ax2.get_zorder() + 1)
    ax.patch.set_visible(False)
    ax2.grid(False)
    ax.set_ylim(0, 100)
    ax2.set_ylim(0, 50)
    ax.set_xticks(xs)
    ax.set_xticklabels(["10", "25", "50", "75", "100"])
    ax.set_xlabel("Share of pool scored (%)")
    ax.set_ylabel("Accuracy (%)")
    ax2.set_ylabel("Filtering time (min)")
    color_yaxis(ax, P["pink_text"])
    color_yaxis(ax2, P["blue_text"])
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    legend(ax, loc="center left", bbox_to_anchor=(0.015, 0.44), handles=h1 + h2, labels=l1 + l2)
    print(save(fig, "demo_cost_quality"))
