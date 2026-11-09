#!/usr/bin/env python3
"""Check every manim8 clip in the expo's clip indexes against the manifest of the job that made it.

    python tools/check_clips.py                          # every project with a clips/ workspace, both presets
    python tools/check_clips.py divisive-normalization   # one project

For each project with a `clips/` workspace, each manim8 entry of `assets/clips/clips.json` (and of
`assets/clips/dark/clips.json` when the project has one) is checked by `tools/check_clip_index.py`: the copied video
is the job's full movie (sha256, size, frame rate, duration, frame count), the revision and the job are the
manifest's, every checkpoint is copied byte for byte and matches its frame, the still is a checkpoint, and nothing
is null. The manifests are under each manim8 project's `renders/`, which are not committed, so run this after
`lk clips` in the same checkout. A project with a workspace but no manim8 entry is an error: its clips were not
rendered.

`tools/check_clip_index.py` is lecturekit's `.github/scripts/check_clip_index.py` at v0.3.0, copied unchanged (the
wheel does not ship it). Exit 0 when every check holds, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_clip_index import check


def workspaces(names: list[str]) -> list[Path]:
    if names:
        return [ROOT / n if not Path(n).is_absolute() else Path(n) for n in names]
    return sorted(p.parent.parent for p in ROOT.glob("*/clips/workspace.yaml")
                  if (p.parent.parent / "expo.yaml").exists())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projects", nargs="*", help="project directories (default: every one with clips/)")
    a = ap.parse_args(argv)
    problems: list[str] = []
    checked = 0
    for project in workspaces(a.projects):
        found = 0
        for mode, rel in (("light", "assets/clips/clips.json"), ("dark", "assets/clips/dark/clips.json")):
            index = project / rel
            if not index.exists():
                continue
            entries = json.loads(index.read_text(encoding="utf-8"))
            for name, entry in sorted(entries.items()):
                if entry.get("producer") != "manim8":
                    continue
                found += 1
                problems += [f"{project.name}: {p}" for p in check(project, name, mode)]
        if not found:
            problems.append(f"{project.name}: has a clips/ workspace but no manim8 clip in its index; run lk clips")
        checked += found
    for p in problems:
        print(f"error: {p}", file=sys.stderr)
    print(f"{checked} manim8 clip entr{'y' if checked == 1 else 'ies'} checked, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
