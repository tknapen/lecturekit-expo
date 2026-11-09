#!/usr/bin/env python3
"""List the expo's projects, one per line, for the continuous build's loops.

    python tools/projects.py                 # every project (a directory with expo.yaml and _quarto.yml), not template/
    python tools/projects.py --preset dark   # those whose expo.yaml declares the dark preset
    python tools/projects.py --clips         # those with clips to render: a manim8 workspace (clips/) or kit scenes
                                             # (anim/clip_*.py)
    python tools/projects.py --presets       # "<project> <preset>" for every preset each project declares
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def projects() -> list[tuple[Path, dict]]:
    out = []
    for yml in sorted(ROOT.glob("*/expo.yaml")):
        p = yml.parent
        if p.name == "template" or not (p / "_quarto.yml").exists():
            continue
        out.append((p, yaml.safe_load(yml.read_text(encoding="utf-8")) or {}))
    return out


def has_clips(p: Path) -> bool:
    return (p / "clips" / "workspace.yaml").exists() or any((p / "anim").glob("clip_*.py"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preset", choices=["paper", "dark"], help="only projects that declare this preset")
    ap.add_argument("--clips", action="store_true", help="only projects with clips to render")
    ap.add_argument("--presets", action="store_true", help="print '<project> <preset>' per declared preset")
    a = ap.parse_args(argv)
    for p, meta in projects():
        presets = [str(x) for x in meta.get("presets") or ["paper"]]
        if a.preset and a.preset not in presets:
            continue
        if a.clips and not has_clips(p):
            continue
        if a.presets:
            for preset in presets:
                print(f"{p.name} {preset}")
        else:
            print(p.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
