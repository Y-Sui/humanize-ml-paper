#!/usr/bin/env python3
"""render_diagram.py -- build TikZ diagram sources into a printed-size vector PDF and a PNG preview.

Usage:
    python3 render_diagram.py FIG.tex [FIG2.tex ...] [--out-dir DIR] [--dpi 300] [--check]
                              [--engine auto|tectonic|latexmk|pdflatex]

Each FIG.tex is a standalone document that loads housediagram.sty (templates/; copy it next to the
source or leave it in the skill). For every source the script
  1. compiles it in a temporary folder (tectonic if installed, else latexmk, else pdflatex) with
     templates/ on the search path;
  2. stops on LaTeX errors and lists the warnings that change the output (missing characters, overfull
     boxes, font substitutions, undefined references);
  3. checks the PDF: page width against the '% target-width-in: W' line of the source (the figure is
     drawn at its printed width, so it must be included unscaled), no Type 3 fonts, no raster images;
  4. writes OUT/FIG.pdf and OUT/FIG.png (white background, --dpi, default 300) with PyMuPDF;
  5. with --check, prints the clean-palette metrics of colour_stats.py (figures_tables.md section 5.1).
Exit status 1 if any source fails to build or breaks a hard check (Type 3 fonts, width off by > 3 %).
Open the PNG after every build and look at it: the checks catch broken files, not ugly ones.

Needs a LaTeX engine and PyMuPDF (python3 -m pip install --user pymupdf); without PyMuPDF the PNG
falls back to pdftoppm when it is installed.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.normpath(os.path.join(HERE, "..", "templates"))
WIDTH_TOL = 0.03

_WARN = re.compile(r"Missing character|Overfull \\[hv]box|Font shape .* (?:undefined|not available)|"
                   r"Font Warning|Reference .* undefined|There were undefined references|LaTeX Warning|"
                   r"Package (?!shellesc)\S+ Warning")


def _engine(choice):
    if choice != "auto":
        if not shutil.which(choice):
            sys.exit(f"render_diagram: {choice} not found on PATH")
        return choice
    for e in ("tectonic", "latexmk", "pdflatex"):
        if shutil.which(e):
            return e
    sys.exit("render_diagram: no LaTeX engine found (install tectonic or TeX Live; README.md 'Setup')")


def _compile(src, engine, tmp):
    stem = os.path.splitext(os.path.basename(src))[0]
    cwd = os.path.dirname(os.path.abspath(src))
    env = dict(os.environ)
    if engine == "tectonic":
        cmd = ["tectonic", "-X", "compile", "--keep-logs", "--outdir", tmp, "-Z", f"search-path={TEMPLATES}",
               os.path.abspath(src)]
    else:
        # the empty last entry keeps kpathsea's default trees even when TEXINPUTS is already set
        env["TEXINPUTS"] = os.pathsep.join([cwd, TEMPLATES, env.get("TEXINPUTS", "").strip(os.pathsep), ""])
        if engine == "latexmk":
            cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", f"-outdir={tmp}",
                   os.path.abspath(src)]
        else:
            cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={tmp}",
                   os.path.abspath(src)]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    log_path = os.path.join(tmp, stem + ".log")
    if engine == "pdflatex" and p.returncode == 0 and "Rerun" in open(log_path, errors="replace").read():
        p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    log = open(log_path, errors="replace").read() if os.path.isfile(log_path) else ""
    out = p.stdout + "\n" + p.stderr + "\n" + log
    pdf = os.path.join(tmp, stem + ".pdf")
    if p.returncode != 0 or not os.path.isfile(pdf):
        tail = "\n".join([ln for ln in out.splitlines() if ln.strip()][-25:])
        return None, [f"build failed ({engine}, exit {p.returncode}):\n{tail}"], time.time() - t0
    warns = sorted({ln.strip() for ln in out.splitlines() if _WARN.search(ln)})
    return pdf, warns, time.time() - t0


def _target_width(src):
    m = re.search(r"^%\s*target-width-in:\s*([0-9.]+)", open(src, errors="replace").read(), re.M)
    return float(m.group(1)) if m else None


def _import_pymupdf():
    try:
        import pymupdf
        return pymupdf
    except ImportError:
        try:
            import fitz
            return fitz
        except ImportError:
            return None


def _png(pdf, png, dpi):
    pm = _import_pymupdf()
    if pm is not None:
        doc = pm.open(pdf)
        doc[0].get_pixmap(dpi=dpi, alpha=False).save(png)
        return True
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-singlefile", pdf, png[:-4]], check=True)
        return True
    return False


def _pdf_facts(pdf):
    pm = _import_pymupdf()
    if pm is None:
        return None
    doc = pm.open(pdf)
    page = doc[0]
    fonts = page.get_fonts(full=True)
    return {"w_in": page.rect.width / 72.0, "h_in": page.rect.height / 72.0,
            "type3": [f[3] or f[4] for f in fonts if f[2] == "Type3"],
            "images": len(page.get_images(full=True)), "pages": doc.page_count,
            "kb": os.path.getsize(pdf) / 1024.0}


def _geometry_warnings(pdf):
    """Detect text words intersecting stroked line segments (wrapped chips, colliding arrow labels)."""
    pm = _import_pymupdf()
    if pm is None:
        return []
    doc = pm.open(pdf)
    page = doc[0]
    words = page.get_text("words")
    draws = page.get_drawings()
    hits = []
    for d in draws:
        if d.get("color") is None:
            continue
        for w in words:
            wb = pm.Rect(w[0] + 0.4, w[1] + 0.4, w[2] - 0.4, w[3] - 0.4)
            if wb.is_empty:
                continue
            for it in d["items"]:
                if it[0] == "l":
                    p1, p2 = it[1], it[2]
                    seg = pm.Rect(
                        min(p1.x, p2.x) - 0.6,
                        min(p1.y, p2.y) - 0.6,
                        max(p1.x, p2.x) + 0.6,
                        max(p1.y, p2.y) + 0.6,
                    )
                    if wb.intersects(seg):
                        hits.append(w[4])
                        break
    if not hits:
        return []
    sample = ", ".join(repr(t) for t in list(dict.fromkeys(hits))[:5])
    return [f"geometry: {len(hits)} text-stroke intersection(s) near {sample} (inspect the PNG for overlaps)"]


def render(src, out_dir, dpi, check, engine):
    stem = os.path.splitext(os.path.basename(src))[0]
    hard = []
    with tempfile.TemporaryDirectory() as tmp:
        pdf, warns, secs = _compile(src, engine, tmp)
        if pdf is None:
            print(f"[FAIL] {src}\n{warns[0]}")
            return False
        os.makedirs(out_dir, exist_ok=True)
        out_pdf = os.path.join(out_dir, stem + ".pdf")
        shutil.copyfile(pdf, out_pdf)
    out_png = os.path.join(out_dir, stem + ".png")
    have_png = _png(out_pdf, out_png, dpi)
    facts = _pdf_facts(out_pdf)
    head = f"[ok]   {stem}: built in {secs:.1f} s with {engine}"
    if facts:
        head += f"; {facts['w_in']:.2f} x {facts['h_in']:.2f} in, {facts['kb']:.0f} KB"
        target = _target_width(src)
        if target:
            off = facts["w_in"] / target - 1
            head += f" (target width {target:.2f} in, {off:+.1%})"
            if abs(off) > WIDTH_TOL:
                hard.append(f"width {facts['w_in']:.2f} in is {off:+.1%} off the target {target:.2f} in: "
                            "change the gaps or box widths, never scale the figure")
        if facts["type3"]:
            hard.append(f"Type 3 fonts in the PDF ({', '.join(facts['type3'])}): venues reject them")
        if facts["images"]:
            warns.append(f"{facts['images']} raster image(s) in the PDF: a diagram should be pure vector")
        if facts["pages"] != 1:
            warns.append(f"{facts['pages']} pages: a diagram source must produce exactly one page")
    if check:
        warns.extend(_geometry_warnings(out_pdf))
    print(head)
    print(f"       -> {out_pdf}" + (f"\n       -> {out_png} ({dpi} dpi)" if have_png else
                                     "\n       (no PNG: install PyMuPDF with python3 -m pip install --user pymupdf)"))
    for w in warns:
        print(f"       warning: {w}")
    for h in hard:
        print(f"       ERROR: {h}")
    if check and have_png:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        sys.dont_write_bytecode = True       # keep the skill folder free of __pycache__
        import colour_stats
        print("       " + colour_stats.line(stem + ".png", colour_stats.load_png(out_png)).strip()
              + "   (targets: white >= 0.72, earthy <= 0.05, mean-sat 0.25-0.75, hue-families <= 3,"
              " +1 for semantic teal / coral)")
    return not hard


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out-dir", help="output folder (default: next to each source)")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--check", action="store_true", help="also print the clean-palette metrics")
    ap.add_argument("--engine", default="auto", choices=["auto", "tectonic", "latexmk", "pdflatex"])
    a = ap.parse_args()
    engine = _engine(a.engine)
    ok = True
    for src in a.sources:
        out_dir = a.out_dir or os.path.dirname(os.path.abspath(src))
        ok &= render(src, out_dir, a.dpi, a.check, engine)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
