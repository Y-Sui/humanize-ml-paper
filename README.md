# humanize-ml-paper

**An agent skill for writing ML conference papers (ICLR, NeurIPS, ICML) in the style of human-written papers.**

English | [中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-SKILL.md-2A4E8F)](https://agentskills.io)
[![Blog post](https://img.shields.io/badge/Blog-The%20Art%20of%20Writing-2A4E8F)](https://lehengthu.github.io/blog/2026/paper-skill-ai-detection/)

<a href="https://lehengthu.github.io/blog/2026/paper-skill-ai-detection/"><img src="media/demo.gif" width="800" alt="Opening film of the blog post: an agent writes a draft page and revises it with the skill's style sheet"></a>

We distilled the writing practices of human-written papers that follow academic conventions into a workflow, rules, a phrase bank and checking tools. An agent equipped with the skill can write fluent, logical prose with a lower AI detection rate and can even write a complete conference paper in one run.

The full study is the blog post [The Art of Writing: Agents with Well-Curated Skills Can Cheat AI Detectors](https://lehengthu.github.io/blog/2026/paper-skill-ai-detection/). You can also watch the [37-second film](media/demo.mp4).

## Results

<img src="media/result-en.png" width="760" alt="Share of text that Pangram 4.1 labels AI on four papers: 94% without the skill, 29% with the skill, 29% for the human-written text">

- **Text generated with the skill is less likely to be detected by Pangram.** We simulate the writing process from a draft to a finished text. On four papers, Pangram labels 94% of the text that Claude Opus 5.5 writes without the skill as AI, compared with 29% with the skill, the same as the human-written text.
- **The text follows academic conventions.** The skill's checker finds 6 habits of machine-written drafts in the text generated with the skill, compared with 75 without it.
- **One prompt, one complete paper.** Given a single prompt, an agent with the skill chose an idea, ran the experiments and typeset an ICML 2027 submission alone in about 82 minutes.
- **The skill does not replace your thinking.** If the content is AI-generated to begin with, revising it with AI cannot correct it: papers written from a topic alone stay at 100% AI. A complete one-shot paper reads as human but is still labeled AI because of its length.

> [!CAUTION]
> **Scope:** the texts that pass the detector are mostly short ones written from a human draft. Text generated directly by AI, or a long paper, is still likely to be labeled AI.

## Advanced usage: one prompt, one complete paper

The skill can also take an agent from an idea to a typeset submission. Given one prompt, Claude Opus 5.5 with the skill wrote [SourceStein](examples/sourcestein-icml2027/), a 14-page ICML 2027 submission, in a single run of 209 turns and about 82 minutes, including 37 minutes of its own experiments on a CPU-only Mac. Nobody edited the paper.

<a href="examples/sourcestein-icml2027/"><img src="examples/sourcestein-icml2027/preview/pages.jpg" alt="All 14 pages of SourceStein, the paper written in one run"></a>

[Read the paper](examples/sourcestein-icml2027/SourceStein.pdf) · [The prompt](examples/sourcestein-icml2027/prompt.md) · [Source, code and results](examples/sourcestein-icml2027/source/)

> [!CAUTION]
> **Risk:** for a complete generation, although the writing reads as human, it is still labeled AI because of its length.

## Install

**Claude Code** (plugin marketplace):

```
/plugin marketplace add LehengTHU/humanize-ml-paper
/plugin install humanize-ml-paper@humanize-ml-paper
```

**Other agents** (Codex, Cursor, Gemini CLI and others that read `SKILL.md`):

```bash
npx skills add LehengTHU/humanize-ml-paper
# or, with the GitHub CLI
gh skill install LehengTHU/humanize-ml-paper humanize-ml-paper
```

**Manual:**

```bash
git clone https://github.com/LehengTHU/humanize-ml-paper
cp -r humanize-ml-paper/skills/humanize-ml-paper ~/.claude/skills/
```

The skill needs Python 3.8+ for its checker and a LaTeX engine ([tectonic](https://tectonic-typesetting.github.io) is the smallest) to build papers. After a manual install, `bash ~/.claude/skills/humanize-ml-paper/scripts/check_env.sh` reports anything missing and builds a one-page test PDF. The full setup is in [`skills/humanize-ml-paper/README.md`](skills/humanize-ml-paper/README.md).

## Usage

Ask in plain language; the skill triggers on paper-writing tasks. For example:

- "Turn my method notes and results in `notes.md` into a full ICLR paper."
- "Rewrite the introduction in `chapters/1_introduction.tex` in this style."
- "Make the main result table from `results.csv`, with empty cells for the missing runs."
- "Plan the page budget for an ICML submission and tell me what goes to the appendix."
- "Review my draft against the style checklist."

The checker also runs on its own: `python3 skills/humanize-ml-paper/scripts/check_paper.py <paper_dir> --stage submission`.

## Optional drawing sub-skills

The default drawing workflows remain the bundled Matplotlib plot style and TikZ diagram tools. Two optional adapters provide access to external drawing skills without changing the paper-writing conventions:

| Option | Best suited to | Adapter | External skill |
|---|---|---|---|
| FigGenie | Architecture, method, mechanism and teaser diagrams; editable SVG and PowerPoint | [FigGenie adapter](skills/humanize-ml-paper/subskills/humanize-figgenie/SKILL.md) | [Sleepy-Avacado/FigGenie-paper-diagram-skill](https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill) |
| figures4papers | Matplotlib result plots and multi-panel comparisons in the figures4papers style | [figures4papers adapter](skills/humanize-ml-paper/subskills/humanize-figures4papers/SKILL.md) | [ChenLiu-1996/figures4papers](https://github.com/ChenLiu-1996/figures4papers) |

Examples:

- "Use FigGenie to draw the method overview from `chapters/3_methodology.tex`; deliver SVG, PDF and a preview."
- "Use figures4papers for the ablation plot in `results/ablation.csv`; export PDF and PNG."
- "Use the default TikZ workflow for this diagram."

The adapters use an existing installation or checkout of the external skill. If it is missing, follow that repository's installation instructions before using the adapter; the full external repositories and their dependencies are not bundled here. FigGenie needs Python and headless Chromium; PowerPoint export has additional optional dependencies. figures4papers uses Python and Matplotlib. Each adapter links the upstream instructions and records the revision reviewed for this integration.

External projects retain their own licenses: FigGenie's code and documentation are MIT, with separately licensed fonts and third-party figure assets; figures4papers is CC BY-NC 4.0. See the external repositories for their license and attribution files.

## What is inside

| Path | Contents |
|---|---|
| `SKILL.md` | The workflow from a proposal to a finished paper, in eight steps, and the style checklist |
| `references/` | Venue limits and page budgets, paper types, structure, prose rules, the argument chain of the Introduction, concepts, math, experiments, figures and tables, LaTeX conventions, annotated examples |
| `assets/lexicon/` | The phrase bank: 1,272 expressions taken from the papers, each with its counts and a tier (core, occasional, retired, reference only, banned) |
| `tools/` | `ps.py` looks up how often a phrase occurs, from a shipped index of word-sequence counts that holds no sentences; `build_corpus.py` and `ngrams.py` build the same from your own papers |
| `scripts/check_paper.py` | Word budgets, the page limit, required statements, sentence shape and the 27 habits of machine-written drafts, with line numbers |
| `templates/` | ICLR and NeurIPS (one column) and ICML (two column) LaTeX projects, table templates, a plot style and a TikZ diagram style |

## Responsible use

- A draft that passes a detector is still an LLM draft. Venues such as ICLR require you to disclose any use of an LLM, and this applies to papers written with this skill.
- Detector scores should not decide authorship.
- What the paper says and how it argues are still for you to decide. Read and revise everything the agent writes.

## Citation

```bibtex
@misc{sheng2026paperskill,
  title        = {The Art of Writing: Agents with Well-Curated Skills Can Cheat AI Detectors},
  author       = {Sheng, Leheng and Zhang, An and Wang, Xiang},
  year         = {2026},
  howpublished = {Blog post},
  url          = {https://lehengthu.github.io/blog/2026/paper-skill-ai-detection/}
}
```

## Acknowledgement

I thank my advisors Xiang Wang and An Zhang for permission to distill the papers, the early users for their feedback, and my girlfriend Xieyang Zhao for her support and help with the design of the blog.

## License

[MIT](LICENSE)
