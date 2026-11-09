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
_extensions/lecturekit/   the engine's Quarto extension, vendored once for all projects: lecturekit 0.4.0, the commit
                          requirements.txt pins; the build fails when it differs from the installed package's copy
template/                 the project convention: lk new 0.3.0's scaffold plus sources/, SESSION.md and expo.yaml
<project>/                one folder per project: a lecturekit project with the method's files
requirements.txt          the engine, pinned by commit: lecturekit[review,figures,clips,manim8] @ ...@81c4a66
tools/check_meta.py       expo.yaml against the engines: budgets, clip names, manim8 kinds, the vendored extension
tools/check_clips.py      every manim8 clip in an index against the manifest of the job that made it
tools/vendor_extension.py replaces the shared extension with the installed engine's (after moving the pin)
tools/gallery.py          assembles the gallery (index.html with a card per project) from expo.yaml files
tools/projects.py         lists projects for the continuous build (by preset, and those with clips)
.github/workflows/        the continuous build: clips, then every deck in its presets, the checks, the gallery
PLAN.md                   what this repository is for, and the topics
```

Each project is a Quarto project of its own: `slides.qmd`, `_quarto.yml`, `_brand.yml` (and the dark preset),
`make_assets.py` for the figures, `anim/` for kit clips, `assets/`, `references.bib`, `STORYBOARD.md`, `PLAN.md`,
`FACTS.md`, `MANIFEST.md`, `README.md`, and three files the expo adds: `sources/`, `SESSION.md` and `expo.yaml`. A
project with manim8 clips has a manim8 workspace in `clips/` (`lk new --manim8`): its styles, bridged from the
project's brands, and a family whose render environment is pinned by its `uv.lock`.

There is one engine for the whole expo, not one per project: `requirements.txt` pins the package and
`_extensions/lecturekit` at the root is its extension, to which every project's `_extensions` is a link. A project
taken out of the expo gets its own copy:

```sh
cp -r drift-diffusion ~/my-lecture       # the copied _extensions is a link to nothing
lk new --vendor-only ~/my-lecture        # replaces the link with a copy of the installed engine's extension
lk build ~/my-lecture
```

with the engine of `requirements.txt` installed. A workspace in `clips/` goes along unchanged: its family takes
manim8 from GitHub at a fixed commit.

## Build

Python 3.12 (manim8 needs it), Quarto 1.11 and a TeX distribution with XeLaTeX as for the engine
([INSTALL.md](https://github.com/tknapen/lecturekit/blob/81c4a66f3571fb03c54e1817f7366141907929b5/docs/INSTALL.md)), and for the clips the Cairo and
Pango headers and ffmpeg (`libcairo2-dev libpango1.0-dev pkg-config ffmpeg` on Debian and Ubuntu).

```sh
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt            # lecturekit 0.4.0 with Manim, manim8 0.1.0a0 (and uv) and Playwright
playwright install chromium
python tools/check_meta.py                 # the metadata, and the vendored extension against the installed one
lk clips divisive-normalization            # its manim8 clip: syncs the family environment once, then renders
python tools/check_clips.py                # each manim8 clip in an index against its job's manifest
lk build signal-detection                  # _build/slides-live.html, _build/slides-study.pdf, the plan against the budget
lk build signal-detection --profile dark   # _build-dark/, for a project whose expo.yaml declares dark
lk review shoot signal-detection/_build/slides-live.html --sheet
python tools/gallery.py                    # _gallery/index.html
```

`uv pip install -r requirements.txt` works as well.

Moving the engine: change the commit in `requirements.txt`, install it, run `python tools/vendor_extension.py`, build
every project, and commit the two together. `lk build` refuses an extension whose version differs from the
package's in the major or (while the major is 0) the minor number, and `tools/check_meta.py` refuses any byte of
difference.

## Continuous build

`.github/workflows/build.yml` runs on pushes to `main` and `claude/**` and on pull requests, with the pinned engine:

- clips: lk clips for every project with clips (and `--mode dark` where `expo.yaml` declares dark), each failure
  failing the job, then `tools/check_clips.py` against the manifests; the fresh clips go on to the build;
- build: `tools/check_meta.py`, then each project in each preset it declares (`paper`, and `dark` where declared):
  `lk build`, and `lk review overflow`, `contrast`, `shoot`, `measure` and `frags`, every one of them gating; then
  the gallery, which is published to Pages from `main`.

Every Monday, and when run by hand, the same jobs install lecturekit's `main` branch in place of the pinned commit, so that
an engine change that breaks a deck is seen here before it is released. That run reports the vendored extension's
drift from `main` as a warning, builds with `main`'s own copy, and publishes nothing.

## Add a project

1. `cp -r template <folder>` (the `_extensions` link stays valid), or `lk new <folder> --title "..." --budget
   <minutes>`, then `rm -r <folder>/_extensions && ln -s ../_extensions <folder>/_extensions` and copy `sources/`,
   `SESSION.md` and `expo.yaml` from `template/`.
2. Put the sources in `sources/` (or links and digitised values) and write `STORYBOARD.md` by hand.
3. Build the plan, the simulations, the figures, the clips and the slides as the engine's
   [WORKFLOW.md](https://github.com/tknapen/lecturekit/blob/81c4a66f3571fb03c54e1817f7366141907929b5/docs/WORKFLOW.md) describes, keeping `SESSION.md`
   as you go. For manim8 clips, `lk new --manim8 <folder>` makes `clips/` a workspace.
4. `lk build`, the review rounds, `FACTS.md` and `MANIFEST.md`; fill `expo.yaml` (title, minutes equal to the
   deck's budget, device, clip names as slugs, manim8 kinds by their registry names) and run
   `python tools/check_meta.py`.
5. Open a pull request; the continuous build renders every project's clips, builds every deck and the gallery.

## Status

- Five project skeletons on the 0.3.0 scaffold, their storyboards still to be written: signal detection theory,
  drift diffusion, divisive normalization, MRI from spins to k-space, and a talk from the 2025 Nature paper. Each
  builds as the scaffold deck, with the budget of its `expo.yaml`, until its storyboard, plan and figures replace
  it.
- Signal detection declares the dark preset, and the continuous build builds and checks it in both.
- Divisive normalization has the first manim8 workspace, with one clip: manim8's `divisive_normalization` example,
  rendered by `lk clips` in the continuous build and committed as the fallback. It is on no slide: its equation is
  the example's schematic, and it is replaced, with the lecturer's sign-off, before the clip is used.
- Not yet built: the gallery's clip previews (they wait for `lk clips --preview`, which lecturekit does not have),
  its filters, the clip reel and the reader (PLAN.md).

## Licences

Code (tools, workflows) under MIT (`LICENSE`); the content of the projects under CC BY 4.0, each with its author;
the vendored extension and fonts under the licences stated in the engine's `NOTICE.md`. Sources are included only
when their licence allows it.
