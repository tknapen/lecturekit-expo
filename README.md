# lecturekit-expo

Complete lecture projects built on [lecturekit](https://github.com/tknapen/lecturekit), each from a small set of
source documents, each showing one teaching device done well, each with its clips made for it. The engine
repository holds the method and two example decks; this one is where the method is seen at work, many times over.
Every project carries its storyboard, plan, checked facts, manifest, the sources it was built from, and the prompts
of the session that built it, so that a reader can judge the distance from documents to lecture and replay it.

The reasoning behind the expo, the gallery, the catalogue of topics and the first five projects are in
[PLAN.md](PLAN.md).

## Layout

```text
_extensions/lecturekit/   the engine's Quarto extension, vendored once (0.2); every project links to it
template/                 the project convention: an lk new project plus sources/, SESSION.md and expo.yaml
<project>/                one folder per project: a lecturekit project with the method's files
tools/gallery.py          assembles the gallery (index.html with a card per project) from expo.yaml files
.github/workflows/        builds every project in both formats, runs the checks, publishes the gallery to Pages
PLAN.md                   what this repository is for, and the topics
```

Each project is a Quarto project of its own: `slides.qmd`, `_quarto.yml`, `_brand.yml` (and the dark preset),
`make_assets.py` for the figures, `anim/` for the clips, `assets/`, `references.bib`, `STORYBOARD.md`, `PLAN.md`,
`FACTS.md`, `MANIFEST.md`, `README.md`, and three files the expo adds: `sources/`, `SESSION.md` and `expo.yaml`.
`_extensions` in a project is a symlink to the shared copy at the root; a project taken out of the expo copies it
instead (`lk new --vendor-only <dir>`).

## Build

```sh
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt        # the engine from its repository, pinned; playwright for the review tools
playwright install chromium
lk build signal-detection                 # _build/slides-live.html, _build/slides-study.pdf, the plan against the budget
lk review shoot signal-detection/_build/slides-live.html --sheet
python tools/gallery.py                   # _gallery/index.html
```

Quarto and a TeX distribution with XeLaTeX are needed as for the engine (`docs/INSTALL.md` there).

## Add a project

1. Copy `template/` to a new folder, or run `lk new <folder>` and add `sources/`, `SESSION.md` and `expo.yaml`;
   point `_extensions` at the shared copy.
2. Put the sources in `sources/` (or links and digitised values) and write `STORYBOARD.md` by hand.
3. Build the plan, the simulations, the figures, the clips and the slides as `docs/WORKFLOW.md` of the engine
   describes, keeping `SESSION.md` as you go.
4. `lk build`, the review rounds, `FACTS.md` and `MANIFEST.md`; fill `expo.yaml` (title, minutes, device, kinds).
5. Open a pull request; the continuous build renders every project and the gallery.

## Status

Five project skeletons on the scaffold, their storyboards still to be written: signal detection theory, drift
diffusion, divisive normalization, MRI from spins to k-space, and a talk from the 2025 Nature paper. Each builds
as the scaffold deck until its storyboard, plan and figures replace it.

## Licences

Code (tools, workflows) under MIT (`LICENSE`); the content of the projects under CC BY 4.0, each with its author;
the vendored extension and fonts under the licences stated in the engine's `NOTICE.md`. Sources are included only
when their licence allows it.
