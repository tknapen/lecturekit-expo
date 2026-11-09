#!/usr/bin/env bash
# Install the engine into .venv with pip: requirements.txt as committed (ENGINE=pinned, the default), or with
# lecturekit's main branch in place of its tag (ENGINE=main: the weekly build, which shows an engine regression
# before a release). Needs Python 3.12 (manim8) and the Cairo and Pango headers (Manim builds against them).
set -euo pipefail
engine="${ENGINE:-pinned}"
python="${PYTHON:-python3}"
req="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/requirements-${engine}.txt"
case "$engine" in
  pinned) cp requirements.txt "$req" ;;
  main)
    sed -E 's#(github\.com/tknapen/lecturekit)@[^ ;]+#\1@main#' requirements.txt > "$req"
    grep -q 'github.com/tknapen/lecturekit@main' "$req" || { echo "no lecturekit pin to replace in requirements.txt" >&2; exit 2; }
    ;;
  *) echo "ENGINE is pinned or main, not '$engine'" >&2; exit 2 ;;
esac
echo "engine: $engine"; grep -v '^#' "$req"
"$python" -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r "$req"
.venv/bin/lk version
.venv/bin/scianim --help > /dev/null
.venv/bin/python -c "import json, importlib.metadata as m; d = m.distribution('lecturekit'); \
print('lecturekit', d.version, 'from', json.loads(d.read_text('direct_url.json') or '{}').get('vcs_info', {}))"
