---
name: humanize-figures4papers
description: Use the external figures4papers scientific-figure-making skill for selected Matplotlib result plots and multi-panel comparisons in its publication style, while retaining humanize-ml-paper writing conventions.
---

# Optional figures4papers result plots

Use this route when the user selects figures4papers or asks for the look of one of its demos. The parent's bundled Matplotlib style remains the default. Use the FigGenie sub-skill for architecture and mechanism diagrams.

## External entry and setup

- Repository: [ChenLiu-1996/figures4papers](https://github.com/ChenLiu-1996/figures4papers).
- Reviewed revision: `daa2833f03878454cb9b6ad3f9ecb68acad36ade`.
- Entry: [`scientific-figure-making/SKILL.md`](https://github.com/ChenLiu-1996/figures4papers/blob/daa2833f03878454cb9b6ad3f9ecb68acad36ade/scientific-figure-making/SKILL.md).

Use the installed `scientific-figure-making` skill or a checkout of figures4papers. Read its entry, then load only the relevant API, design, pattern or tutorial reference. Its `references/demos.md` links the canonical `figure_*` projects. If a demo is needed, retrieve that project's source; do not assume the adapter contains the external examples or plotting functions.

If the external skill is absent, follow the repository's installation instructions. Run plots with Python, Matplotlib and the packages required by the selected example. Resolve external file paths relative to that checkout.

## Integration

1. Identify the comparison, input result file, metric direction, units, uncertainty and printed figure size. Use measured values; retain missing results as missing.
2. Choose the appropriate chart and closest demo for bars, curves, scatter plots, heatmaps or a multi-panel layout. Adapt it to the paper's data and terminology.
3. Use the external skill's font, palette, layout and export conventions for this figure. Do not also apply the parent's Matplotlib preset.
4. Export a reproducible plotting script, vector PDF and PNG preview, plus SVG if requested and supported. Inspect the outputs at the intended placement size for legibility, clipping, panel alignment and legends.
5. Write the caption using the parent's caption conventions, with the comparison and any uncertainty or axis treatment needed to interpret the figure.

Selection changes figure styling and plotting implementation only. The parent's scientific claims, data provenance, terminology and venue requirements continue to apply. This route covers publication-oriented Matplotlib plots; it does not select interactive dashboards, GIS or unrelated figure workflows.

The external repository is licensed CC BY-NC 4.0. Retain required attribution and license notices when reusing its material; its content is not relicensed under the parent repository's MIT license.
