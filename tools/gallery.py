#!/usr/bin/env python3
"""Assemble the expo's gallery from the projects' expo.yaml files and their built outputs.

    python tools/gallery.py                 # writes _gallery/index.html and copies each project's _build and sheet
    python tools/gallery.py --out site      # another output directory

A project is a directory with an `expo.yaml` beside a `_quarto.yml`. For each, the gallery card shows the title,
the minutes, the field, the deck type, the teaching device it demonstrates, the manim8 kinds it uses, the clips in
its index, the sources, and links to the live deck and the study PDF of each preset it was built in (`_build`, and
`_build-dark` for the dark preset), the contact sheets (`review/shots`, `review/shots-dark`) and SESSION.md. A
project whose paper build is missing says "not built yet". No dependency beyond PyYAML.
"""

from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

CSS = """
:root{--ink:#202B33;--muted:#566573;--hairline:#C8C3BA;--paper:#F3F2EE;--concept:#175B8E;--anchor:#006C65}
body{margin:0;font:17px/1.45 "TeX Gyre Heros",Helvetica,Arial,sans-serif;color:var(--ink);background:var(--paper)}
header{padding:48px 56px 24px}
h1{font:400 40px/1.1 "TeX Gyre Pagella",Palatino,serif;text-transform:uppercase;letter-spacing:.02em;margin:0 0 12px}
header p{max-width:60em;color:var(--muted);margin:0}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:24px;padding:24px 56px 64px}
.card{background:#fff;border:1px solid var(--hairline);border-radius:6px;padding:20px 22px;display:flex;flex-direction:column;gap:8px}
.eyebrow{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--anchor)}
.card h2{font:400 24px/1.15 "TeX Gyre Pagella",Palatino,serif;text-transform:uppercase;letter-spacing:.02em;margin:0}
.meta{color:var(--muted);font-size:14px}
.device{border-left:3px solid var(--concept);padding-left:10px}
.links a{margin-right:14px;color:var(--concept);text-decoration:none}
.links span{color:var(--hairline);margin-right:14px}
.sources{font-size:13px;color:var(--muted)}
.sources li{margin:2px 0}
footer{padding:0 56px 48px;color:var(--muted);font-size:14px}
"""


def projects() -> list[tuple[Path, dict]]:
    out = []
    for yml in sorted(ROOT.glob("*/expo.yaml")):
        if (yml.parent / "_quarto.yml").exists() and yml.parent.name != "template":
            out.append((yml.parent, yaml.safe_load(yml.read_text(encoding="utf-8")) or {}))
    return out


def card(project: Path, meta: dict, out: Path) -> str:
    name = project.name
    dest = out / name
    if dest.exists():
        shutil.rmtree(dest)                       # no stale outputs of an earlier run
    links = []
    for build, sub, label in ((project / "_build", "", ""), (project / "_build-dark", "dark/", " (dark)")):
        if (build / "slides-live.html").exists():
            shutil.copytree(build, dest / sub, dirs_exist_ok=True)
            links.append(f'<a href="{name}/{sub}slides-live.html">live deck{label}</a>')
        if (build / "slides-study.pdf").exists():
            links.append(f'<a href="{name}/{sub}slides-study.pdf">study PDF{label}</a>')
    for shots, label in (("shots", ""), ("shots-dark", " (dark)")):
        sheet = project / "review" / shots / "sheet.png"
        if sheet.exists():
            dest.mkdir(parents=True, exist_ok=True)
            target = f"sheet{'-dark' if label else ''}.png"
            shutil.copy2(sheet, dest / target)
            links.append(f'<a href="{name}/{target}">contact sheet{label}</a>')
    session = project / "SESSION.md"
    if session.exists():
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(session, dest / "SESSION.md")
        links.append(f'<a href="{name}/SESSION.md">session</a>')
    built = (project / "_build" / "slides-live.html").exists()
    e = html.escape
    kinds = ", ".join(meta.get("manim8_kinds", []) or [])
    sources = "".join(f"<li>{e(str(s))}</li>" for s in meta.get("sources", []) or [])
    status = "" if built else '<span>not built yet</span>'
    rendered = rendered_clips(project)
    clips = f'<div class="meta">clips rendered: {e(", ".join(rendered))}</div>' if rendered else ""
    return f"""
<article class="card">
  <div class="eyebrow">{e(str(meta.get('deck', 'lecture')))} · {e(str(meta.get('field', '')))}</div>
  <h2>{e(str(meta.get('title', name)))}</h2>
  <div class="meta">{e(str(meta.get('minutes', '?')))} minutes · {e(str(meta.get('author', '')))}{(' · manim8: ' + e(kinds)) if kinds else ''}</div>
  <div class="device">{e(str(meta.get('device', '')))}</div>
  {clips}
  <div class="links">{status}{' '.join(links)}</div>
  <ul class="sources">{sources}</ul>
</article>"""


def rendered_clips(project: Path) -> list[str]:
    """The clips in the project's index (assets/clips/clips.json), by name."""
    index = project / "assets" / "clips" / "clips.json"
    if not index.exists():
        return []
    try:
        return sorted(json.loads(index.read_text(encoding="utf-8")))
    except ValueError:
        return []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "_gallery")
    a = ap.parse_args()
    out = a.out
    out.mkdir(parents=True, exist_ok=True)
    cards = [card(p, m, out) for p, m in projects()]
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>lecturekit expo</title>
<meta name="viewport" content="width=device-width, initial-scale=1"><style>{CSS}</style></head>
<body>
<header>
  <h1>lecturekit expo</h1>
  <p>Complete lecture projects built on lecturekit, each from a small set of source documents, each showing one
  teaching device done well, each with its clips made for it. Every project carries its storyboard, plan, checked
  facts, manifest and the prompts of the session that built it. Content CC BY 4.0.</p>
</header>
<main>{''.join(cards) or '<p>No projects yet.</p>'}</main>
<footer>Built with <a href="https://github.com/tknapen/lecturekit">lecturekit</a> and
<a href="https://github.com/tknapen/manim8">manim8</a>. The plan of this expo is
<a href="https://github.com/tknapen/lecturekit-expo/blob/main/PLAN.md">PLAN.md</a> in its repository.</footer>
</body></html>
"""
    (out / "index.html").write_text(page, encoding="utf-8")
    print(f"{len(cards)} project card(s) in {out / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
