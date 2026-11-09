#!/usr/bin/env python3
"""Check the expo's metadata against the engines it describes.

    python tools/check_meta.py                          # every project, PLAN.md and the vendored extension
    python tools/check_meta.py --allow-extension-drift  # report a drifted extension as a warning (the weekly build)

Per project (a directory with an `expo.yaml` beside a `_quarto.yml`, template/ included):

- `minutes` equals `budget:` in the front matter of `slides.qmd`;
- every name in `clips` is a slug (lowercase letters, digits and underscores, starting with a letter), the form
  manim8 requires of a project id; every `clip=` in `slides.qmd`, every entry of `assets/clips/clips.json` (and of
  the dark index) and every manim8 project under `clips/families/` is named in `clips` (`-` and `_` are the same,
  as in lecturekit's lookups, so the kit's `bar-bold` is `bar_bold`);
- every name in `manim8_kinds` is a kind in manim8's registry, and every kind a storyboard under `clips/` uses is
  in `manim8_kinds`;
- `presets` holds paper and possibly dark, and a project that declares dark has `_quarto-dark.yml` and
  `_brand-dark.yml`; `deck` is one of the deck types;
- its `_extensions/lecturekit`, whether the shared copy it links to or a copy of its own, is byte for byte the
  installed lecturekit's extension (`lecturekit.project.extension_source()`).

And the kinds column of PLAN.md's topic table names registry kinds only (a note in brackets after a kind is
allowed: `custom (a grid builder)`).

The registry is `scianim_core.components.REGISTRY` when scianim_core is importable (it comes with lecturekit's
manim8 extra); otherwise the list below, which is REGISTRY 0.5.0, with a note saying so. Exit 0 when nothing is an
error, 1 otherwise. Needs PyYAML, and lecturekit for the extension check.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

# manim8's REGISTRY 0.5.0 (packages/scianim_core/src/scianim_core/components.py), for when scianim_core is not
# installed. When it is, the real registry is used, and a difference from this list is reported as a note.
VENDORED_REGISTRY_VERSION = "0.5.0"
VENDORED_KINDS = frozenset({
    "text_caption", "scientific_plot", "function_plot", "surface_plot", "function_image", "equation_block",
    "equation_label", "comparison_plot", "caption_with_citation", "schematic_population", "receptive_field_glyph",
    "network_graph", "sphere", "custom",
})

SLUG = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
DECKS = {"talk", "lecture", "kickoff", "tutorial", "seminar"}
PRESETS = {"paper", "dark"}
REQUIRED = ("title", "minutes", "field", "deck", "sources", "device", "clips", "manim8_kinds", "presets", "author",
            "licence")
CLIP_ATTR = re.compile(r"""\bclip\s*=\s*(?:"([^"]+)"|'([^']+)'|([^\s}"']+))""")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warning(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")

    def note(self, msg: str) -> None:
        self.notes.append(msg)


def norm(name: str) -> str:
    return str(name).strip().lower().replace("-", "_")


def registry(report: Report) -> frozenset[str]:
    try:
        from scianim_core.components import REGISTRY, REGISTRY_VERSION
    except ImportError:
        report.note(f"scianim_core is not importable; kinds are checked against the vendored list of manim8's "
                    f"REGISTRY {VENDORED_REGISTRY_VERSION} in tools/check_meta.py")
        return VENDORED_KINDS
    kinds = frozenset(REGISTRY)
    if kinds != VENDORED_KINDS or REGISTRY_VERSION != VENDORED_REGISTRY_VERSION:
        added = ", ".join(sorted(kinds - VENDORED_KINDS)) or "none"
        removed = ", ".join(sorted(VENDORED_KINDS - kinds)) or "none"
        report.note(f"manim8's REGISTRY is {REGISTRY_VERSION} (added: {added}; removed: {removed}); the vendored "
                    f"list in tools/check_meta.py is {VENDORED_REGISTRY_VERSION}: update it")
    report.note(f"kinds checked against manim8's REGISTRY {REGISTRY_VERSION} ({len(kinds)} kinds)")
    return kinds


def projects() -> list[Path]:
    return sorted(p.parent for p in ROOT.glob("*/expo.yaml") if (p.parent / "_quarto.yml").exists())


def front_matter(qmd: Path) -> dict:
    text = qmd.read_text(encoding="utf-8")
    m = re.match(r"---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


SKIP_DIRS = {"renders", "revisions", "code", "proposals", "feedback", "node_modules", "__pycache__"}


def manim8_projects(project: Path) -> list[Path]:
    """The manim8 projects (a directory with an `animation.yaml`) under the project's `clips/families/`, without
    the copies manim8 keeps of them (revisions, proposals) or its output."""
    import os
    fam = project / "clips" / "families"
    found = []
    for dirpath, dirnames, filenames in os.walk(fam):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        if "animation.yaml" in filenames:
            found.append(Path(dirpath))
    return found


def storyboard_kinds(clip_dir: Path) -> set[str]:
    sb = clip_dir / "storyboard.yaml"
    if not sb.exists():
        return set()
    data = yaml.safe_load(sb.read_text(encoding="utf-8")) or {}
    return {str(o.get("kind")) for s in data.get("scenes") or [] for o in s.get("objects") or [] if o.get("kind")}


def index_names(project: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for rel in ("assets/clips/clips.json", "assets/clips/dark/clips.json"):
        p = project / rel
        if p.exists():
            try:
                out[rel] = list(json.loads(p.read_text(encoding="utf-8")))
            except ValueError as exc:
                out[rel] = []
                raise ValueError(f"{rel} is not JSON: {exc}") from None
    return out


def check_project(project: Path, kinds: frozenset[str], report: Report) -> None:
    where = project.name
    meta = yaml.safe_load((project / "expo.yaml").read_text(encoding="utf-8")) or {}
    for key in REQUIRED:
        if key not in meta:
            report.error(where, f"expo.yaml has no `{key}`")

    minutes = meta.get("minutes")
    budget = front_matter(project / "slides.qmd").get("budget") if (project / "slides.qmd").exists() else None
    if not isinstance(minutes, int) or minutes <= 0:
        report.error(where, f"expo.yaml minutes is {minutes!r}, not a positive whole number")
    elif budget is None:
        report.error(where, "slides.qmd has no `budget:` in its front matter")
    elif budget != minutes:
        report.error(where, f"expo.yaml says {minutes} minutes, slides.qmd's budget is {budget}")

    if meta.get("deck") not in DECKS:
        report.error(where, f"deck {meta.get('deck')!r} is not one of {', '.join(sorted(DECKS))}")

    presets = meta.get("presets") or []
    for p in presets:
        if p not in PRESETS:
            report.error(where, f"preset {p!r} is not paper or dark")
    if "paper" not in presets:
        report.error(where, "presets must include paper")
    if "dark" in presets:
        for f in ("_quarto-dark.yml", "_brand-dark.yml"):
            if not (project / f).exists():
                report.error(where, f"declares the dark preset but has no {f}")

    clips = [str(c) for c in meta.get("clips") or []]
    for c in clips:
        if not SLUG.match(c):
            report.error(where, f"clip name {c!r} is not a slug (lowercase letters, digits, underscores)")
    seen: dict[str, str] = {}
    for c in clips:
        if norm(c) in seen:
            report.error(where, f"clips {seen[norm(c)]!r} and {c!r} are the same name")
        seen[norm(c)] = c
    declared = set(seen)

    used = set()
    if (project / "slides.qmd").exists():
        for m in CLIP_ATTR.finditer((project / "slides.qmd").read_text(encoding="utf-8")):
            used.add(next(g for g in m.groups() if g))
    for name in sorted(used):
        if norm(name) not in declared:
            report.error(where, f"slides.qmd plays clip={name!r}, which expo.yaml's clips does not name")
    try:
        indexes = index_names(project)
    except ValueError as exc:
        report.error(where, str(exc))
        indexes = {}
    for rel, names in indexes.items():
        for name in names:
            if norm(name) not in declared:
                report.error(where, f"{rel} holds {name!r}, which expo.yaml's clips does not name")

    listed = [str(k) for k in meta.get("manim8_kinds") or []]
    for k in listed:
        if k not in kinds:
            report.error(where, f"manim8 kind {k!r} is not in manim8's registry")
    if len(set(listed)) != len(listed):
        report.error(where, "manim8_kinds names a kind twice")
    for clip_dir in manim8_projects(project):
        rel = clip_dir.relative_to(project)
        if not SLUG.match(clip_dir.name):
            report.error(where, f"manim8 project {rel} is not a slug")
        if norm(clip_dir.name) not in declared:
            report.error(where, f"manim8 project {rel} is not named in expo.yaml's clips")
        for k in sorted(storyboard_kinds(clip_dir) - set(listed)):
            report.error(where, f"{rel}/storyboard.yaml uses kind {k!r}, which manim8_kinds does not list")

    ext = project / "_extensions"
    if ext.is_symlink():
        target = Path(ext.readlink()).as_posix()
        if target.rstrip("/") != "../_extensions":
            report.warning(where, f"_extensions links to {target}, not to the expo's shared ../_extensions")
    elif ext.is_dir():
        report.warning(where, "_extensions is a copy of its own, not a link to the shared ../_extensions")
    else:
        report.error(where, "has no _extensions")


def check_plan(kinds: frozenset[str], report: Report) -> None:
    plan = ROOT / "PLAN.md"
    rows = [line for line in plan.read_text(encoding="utf-8").splitlines() if line.startswith("| ")]
    header = next((r for r in rows if "| Kinds |" in r), None)
    if header is None:
        report.error("PLAN.md", "the topic table (a `Kinds` column) was not found")
        return
    col = [c.strip() for c in header.strip("|").split("|")].index("Kinds")
    count = 0
    for row in rows[rows.index(header) + 2:]:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) <= col:
            continue
        count += 1
        for token in re.sub(r"\([^)]*\)", "", cells[col]).split(","):
            token = token.strip().strip("`")
            if token and token not in kinds:
                report.error("PLAN.md", f"topic {cells[0]!r} names kind {token!r}, which is not in the registry")
    report.note(f"PLAN.md: {count} topics' kinds checked")


def check_extension(report: Report, allow_drift: bool) -> None:
    try:
        from lecturekit.project import extension_source
    except ImportError as exc:
        report.error("extension", f"lecturekit is not importable ({exc}), so the vendored extension cannot be "
                     "compared with the installed one; install requirements.txt")
        return
    from vendor_extension import differences
    source = extension_source()
    copies = {(ROOT / "_extensions" / "lecturekit").resolve(): "_extensions/lecturekit"}
    for project in projects():
        p = project / "_extensions" / "lecturekit"
        if p.exists():
            copies.setdefault(p.resolve(), f"{project.name}/_extensions/lecturekit")
    for path, label in copies.items():
        diff = differences(path, source)
        if not diff:
            report.note(f"{label} is byte for byte the installed lecturekit's extension ({source})")
            continue
        msg = (f"differs from the installed lecturekit's extension ({source}) in {len(diff)} file(s): "
               + "; ".join(diff[:6]) + (" ..." if len(diff) > 6 else "")
               + ". Re-vendor with `python tools/vendor_extension.py`")
        (report.warning if allow_drift else report.error)(label, msg)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--allow-extension-drift", action="store_true",
                    help="report a vendored extension that differs from the installed one as a warning")
    a = ap.parse_args(argv)
    report = Report()
    kinds = registry(report)
    found = projects()
    for project in found:
        check_project(project, kinds, report)
    report.note(f"{len(found)} project(s) checked: {', '.join(p.name for p in found)}")
    check_plan(kinds, report)
    check_extension(report, a.allow_extension_drift)
    for n in report.notes:
        print(f"note: {n}")
    for w in report.warnings:
        print(f"warning: {w}")
    for e in report.errors:
        print(f"error: {e}")
    print(f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
