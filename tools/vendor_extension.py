#!/usr/bin/env python3
"""Replace the expo's shared copy of the engine's Quarto extension with the installed lecturekit's.

    python tools/vendor_extension.py            # _extensions/lecturekit := the installed package's extension
    python tools/vendor_extension.py --check    # only report whether the two differ (exit 1 if they do)

The expo vendors the extension once, at `_extensions/lecturekit`, and every project's `_extensions` is a link to
`../_extensions`. `lk new --vendor-only --force <project>` would give one project its own copy instead (lecturekit
0.3 turns the link into a real directory and leaves the shared copy alone), so the shared copy is upgraded here.
Run it after moving the pin in requirements.txt and installing it; `tools/check_meta.py` then reports no drift.
The installed copy is found with lecturekit's own `lecturekit.project.extension_source()`.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDORED = ROOT / "_extensions" / "lecturekit"
IGNORE = ("__pycache__", "*.pyc", ".DS_Store")


def installed_extension() -> Path:
    try:
        from lecturekit.project import extension_source
    except ImportError as exc:
        raise SystemExit(f"lecturekit is not importable ({exc}); install requirements.txt first") from None
    return extension_source()


def differences(a: Path, b: Path) -> list[str]:
    """Paths (relative to the copies) that are missing from one side or differ byte for byte."""
    out: list[str] = []

    def walk(cmp: filecmp.dircmp, rel: Path) -> None:
        for name in cmp.left_only:
            if not _ignored(name):
                out.append(f"only in the vendored copy: {rel / name}")
        for name in cmp.right_only:
            if not _ignored(name):
                out.append(f"only in the installed copy: {rel / name}")
        for name in cmp.common_files:
            if not filecmp.cmp(Path(cmp.left) / name, Path(cmp.right) / name, shallow=False):
                out.append(f"differs: {rel / name}")
        for name in cmp.funny_files:
            out.append(f"cannot compare: {rel / name}")
        for name, sub in sorted(cmp.subdirs.items()):
            if not _ignored(name):
                walk(sub, rel / name)

    if not a.is_dir():
        return [f"no vendored copy at {a}"]
    walk(filecmp.dircmp(a, b, ignore=[]), Path("."))
    return sorted(out)


def _ignored(name: str) -> bool:
    from fnmatch import fnmatch
    return any(fnmatch(name, pattern) for pattern in IGNORE)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report the differences only; exit 1 when there are any")
    a = ap.parse_args(argv)
    source = installed_extension()
    diff = differences(VENDORED, source)
    if a.check:
        for line in diff:
            print(f"  {line}")
        print(f"{len(diff)} difference(s) between {VENDORED.relative_to(ROOT)} and {source}")
        return 1 if diff else 0
    if not diff:
        print(f"{VENDORED.relative_to(ROOT)} already equals {source}")
        return 0
    if VENDORED.is_symlink():
        raise SystemExit(f"{VENDORED} is a link; the expo's shared copy is a real directory")
    if VENDORED.exists():
        shutil.rmtree(VENDORED)
    shutil.copytree(source, VENDORED, ignore=shutil.ignore_patterns(*IGNORE))
    print(f"{VENDORED.relative_to(ROOT)} replaced by {source} ({len(diff)} difference(s) before)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
