# Population receptive fields, from stimulus to map

A lecturekit project: one `slides.qmd`, a live deck and a study PDF. A fifteen-minute talk in four clips, each the
lecturer's own, rebuilt in manim8 from a seed: the forward model, the model as a chain of stages, a fit of one
measured voxel, and a map that appears from independent fits.

```bash
lk build            # both outputs into _build/, timing plan on the terminal
lk build --to live  # the live deck only
lk build --profile dark
lk review shoot _build/slides-live.html
lk review measure _build/slides-live.html
lk clips            # anim/clip_*.py on the Manim kit and the manim8 projects in clips/, into assets/clips
lk clips --mode dark   # the dark preset's clips, into assets/clips/dark
```

Method: `STORYBOARD.md` (intent) → `PLAN.md` (slides and minutes) →
`sims/` (what the figures show) → `make_assets.py` (figures from numbers) →
`slides.qmd` → review rounds → `FACTS.md` and `MANIFEST.md` → this file as the log.

## The tour

| # | Slide | Clip | What it shows | Data |
| --- | --- | --- | --- | --- |
| 1 | the title slide | | | |
| 2 | Stimulus and pRF predict BOLD | `stimulus_to_bold`, 12 s | a bar sweeps over one pRF; the predicted neural and BOLD responses are drawn by one cursor | simulated with prfmodel |
| 3 | A model is a chain of stages | `model_as_chain`, 15.5 s | the modelling loop opens its model into seven stages; theta lands on four; a pulse runs to BOLD | synthetic |
| 4 | Grid search, then refinement | `grid_and_fit`, 20 s | a candidate field hops over a grid, the best is kept, then refined to the optimum | one measured voxel (7t-aot-visual, CC BY 4.0) |
| 5 | A map from independent fits | `fields_to_map`, 18 s | 690 voxels fitted one by one colour a sheet of cortex; bands appear; recoloured, they run the other way | simulated |
| 6 | References | | prfmodel; 7t-aot-visual | |

Where things are:

- `clips/`: the manim8 workspace. `styles/` holds the bridged `lecturekit_paper` and `lecturekit_dark` (0.1.0);
  `families/population_receptive_fields/` is one family, whose render environment (manim8 `bad3ae1`, Manim 0.22) is
  pinned by its `uv.lock`, with four projects. Each project has the lecturer's seed (`animation.yaml`, `data/`,
  `references/`), its `storyboard.yaml` (written only through the proposals in `proposals/applied/`), its builders in
  `code/` (with the generated `scene_<id>.py`), and a `README.md` with the rung, the evidence for it and what is left
  for the lecturer.
- `assets/clips/` and `assets/clips/dark/`: the rendered clips, stills and `clips.json` of each preset, committed.
- `sources/prf-clips/`: the bundle's README and the four briefs.
- `anim/` holds no clip: no clip needed a kit scene.

Reproduce, from the expo's root with its engine installed:

```bash
lk clips population-receptive-fields && lk clips population-receptive-fields --mode dark
python tools/check_clips.py population-receptive-fields
lk build population-receptive-fields --strict && lk build population-receptive-fields --profile dark --strict
```

## Log

- 2026-11-13: project created with `lk new` (lecturekit 0.4.0).
- 2026-11-13: the lecturer's four pRF clip seeds became four manim8 projects in one family, each rendered at 1280 by
  720 and 30 fps under `lecturekit_paper@0.1.0` and `lecturekit_dark@0.1.0`. All four reached rung R5: `kind: custom`
  builders in each project's `code/` for what the registry cannot draw (the bar in the field, the glyphs and boxes,
  the candidate field, the sheet of squares, the ramps), moved by registered `vary_parameter` actions through the
  parametric route (a `ParametricComponent` whose parameters a zero-window data transform declares). No custom
  action, pinned scene or kit scene. Every hard scientific constraint was checked on the pixels by the clip's builder
  (each project's README).
- 2026-11-13: the deck: a title slide, one slide per clip with its claim as the title (drafts, for the lecturer) and
  its data named in the caption (simulated, synthetic or measured, as the seeds' citations say), and the references
  (prfmodel and 7t-aot-visual only). `lk clips` in both presets (all eight renders cache hits of the builders' final
  jobs), `lk build --strict` in both presets, and the review checks (overflow, contrast, shoot, measure, frags) pass.
- 2026-11-13: not done, the hold. `fields_to_map` has its stop `eccentricity` at 12.9 s (frame 387, `stop: true`,
  39 still frames before it in manim8's manifest), but `lk clips` measures 0 frames of unchanged picture before it in
  both presets, so `lk build` refuses `stops="eccentricity"` and `tools/check_clips.py` reports it (exit 1). The
  cause is the encoding, not the picture: frame 387 starts a new section, which Manim encodes as a fresh H.264
  keyframe at CRF 23, and on this picture of 1380 small coloured marks its re-coding differs from the still frames
  before it by up to 8 grey levels (paper) and 7 (dark) at lecturekit's measuring size, 160 px wide, against a
  tolerance of 6 (calibrated on manim8's `tuning_sweep`, where a fresh keyframe differs by up to 5). Moving the
  recolouring later within the timeline's tolerance (13.6 s and 13.7 s, trial renders) passed in paper and failed in
  dark. The fix belongs in the engine: a rest measure that tolerates a keyframe's re-coding, or a higher encoder
  quality for a clip with stops. Until then the slide plays the clip through, the presenter pauses with Space at
  12.9 s for the prompt (in the notes), and the study PDF prints the stop's frame and the end
  (`study="eccentricity end"`). The continuous build's clips job runs `tools/check_clips.py`, so it fails on this
  stop until the engine accepts it or the lecturer drops the stop.
