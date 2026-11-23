---
name: humanize-figgenie
description: Use the external FigGenie skill for a selected architecture, method, mechanism or teaser diagram, including editable SVG and PowerPoint output, while retaining humanize-ml-paper writing conventions.
---

# Optional FigGenie diagrams

Use this route when FigGenie is selected by name or the requested diagram needs its editable SVG/PowerPoint workflow. The parent skill's native TikZ workflow remains the default. Use the figures4papers sub-skill for numerical result plots.

## External entry and setup

- Repository: [Sleepy-Avacado/FigGenie-paper-diagram-skill](https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill).
- Reviewed revision: `c136a6aeefc6f6fe11fc615a5199cca57be3322a`.
- Entry: [`skills/figgenie-paper-diagram/SKILL.md`](https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill/blob/c136a6aeefc6f6fe11fc615a5199cca57be3322a/skills/figgenie-paper-diagram/SKILL.md).

Use the installed `figgenie-paper-diagram` skill or a complete checkout of that repository. Read its entry and the references needed for the chosen figure. If it is absent, follow the repository's installation instructions; this adapter does not bundle its scripts, fonts or exemplar libraries. Keep its relative paths rooted in its own skill directory.

Rendering and linting require Python and headless Chromium. See the upstream setup for Python packages, optional formula rendering and editable PowerPoint export. Install only the dependencies needed for the selected outputs.

## Integration

1. Read the manuscript material and identify the figure's claim, components, relationships and intended printed width. Use the paper's exact terminology and symbols.
2. Follow FigGenie's brief, spec, exemplar selection and drawing workflow, including its required user checkpoints. Keep source materials with the figure.
3. Render, lint and visually inspect the output using FigGenie's tools. Check the final placement size, labels, arrows and caption against the manuscript and venue requirements.
4. Deliver editable SVG, a vector PDF for LaTeX, a PNG preview and a caption. Add PowerPoint only when requested, following the upstream export checks.

For this figure, FigGenie's visual conventions and checks replace the parent's TikZ-specific styling and renderer checks. Preserve the parent's scientific, terminology, caption and venue requirements. Do not add a second, competing palette or font preset.

The upstream code and documentation use MIT; fonts and third-party figure assets retain their own licenses and credits. Follow the repository's `LICENSE`, `CREDITS.md`, `SOURCES.md` and font license files when reusing material.
