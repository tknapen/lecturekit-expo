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
| 4 | Fits keep the best candidate | `grid_and_fit`, 20 s | a candidate field hops over a grid, the best is kept, then refined to the optimum | one measured voxel (7t-aot-visual, CC BY 4.0) |
| 5 | Independent fits make a map | `fields_to_map`, 18 s | 690 voxels fitted one by one colour a sheet of cortex; bands appear; recoloured, they run the other way | simulated |
| 6 | References | | prfmodel; 7t-aot-visual | |

Where things are:

- `clips/`: the manim8 workspace. `styles/` holds the bridged `lecturekit_paper` (0.1.0) and `lecturekit_dark`
  (0.1.0, and 0.1.1, the newest, which the dark preset renders under);
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
  stop until the engine accepts it, or the lecturer drops the stop and slide 5 changes with it (below).
- 2026-11-13: review, and what it changed. Two entries above say too much. "Every hard scientific constraint was
  checked" does not hold for the timelines' hard milestones at 0 s (tolerance 0: `stimulus_to_bold` `layout`,
  `model_as_chain` `loop`, `grid_and_fit` `layout`, `fields_to_map` `layout`), which no render meets: frame 0 of every
  clip, in both presets, is the empty page, and the layout settles 0.7 to 1.1 s later (in `model_as_chain` the dots
  start at 0.4 s while the loop is half faded in). manim8 bad3ae1 cannot meet them: every object gets a reveal from
  alpha 0 at the scene start (`src/scianim/codegen/generate.py`: `begins = scene.start_seconds if
  obj.reveal_at_seconds is None ...`), and `motion.reveal_seconds` must be greater than 0 (`scianim_core/style.py`:
  `reveal_seconds: float = Field(gt=0)`). This is a deviation from four hard constraints that waits on the lecturer's
  decision. In `stimulus_to_bold`, which reveals nothing later, the project override `motion.reveal_seconds: 0.1`
  (proposal `prop_quick_reveal`, the same under both styles) completes the layout at frame 3; the other three keep
  the style's 0.85 s, on which their later reveals rely (the row's boxes, the headings and the fit line, the key
  line's cross-fade). And "the review checks pass" left out that `lk review shoot` flags the title slide (the title
  sets on three lines on the paper title page) and that `tools/check_clips.py` exits 1 (the hold, above).
- 2026-11-13: the dark preset's quiet roles lifted. Under `lecturekit_dark@0.1.0` the zero lines of
  `stimulus_to_bold` (`grid`, #151515) were 1.15:1 on black and the bar (`neutral`, #2A2A2A) 1.46:1, as were the
  field outlines (`hairline`) of three clips and `model_as_chain`'s stimulus glyph and the stage the pulse is in.
  `_brand-dark.yml` now has `hairline: "#505050"`, and `lk theme . --brand _brand-dark.yml --mode dark --manim8 0.1.1`
  wrote `lecturekit_dark@0.1.1` (dark only; the paper style and the projects' `animation.yaml` are unchanged):
  `neutral` and `hairline` #505050 (2.6:1), `grid` #282828 (1.42:1), `muted` #607C6D (4.6:1). In the dark deck the
  rules and table lines take the same hairline. Not reached: `selection` (#090E13, 1.08:1), the fill of
  `model_as_chain`'s boxes and of the funnel that constraint `loop_stays` names, because the bridge mixes it as 8 per
  cent of `input` over the page in both presets; it needs the bridge (lecturekit) or the lecturer's choice of
  another role.
- 2026-11-13: smaller fixes from the review. Small text in `secondary_text` instead of `muted` (3.07:1 on paper):
  the tick numbers and "time (s)" of `stimulus_to_bold`, and the scale bar's "2°" of `grid_and_fit`, as that clip's
  own tick labels already were. The study PDF's links in `nmInput` (`urlcolor` in `_quarto.yml`): Pandoc's
  `urlcolor={Blue}` came after the engine's and was 2.4:1 on the dark page. The captions cite `prfmodel [-@prfmodel]`,
  so the name is not printed twice. Slides 4 and 5 have claim titles, still drafts: "Fits keep the best candidate"
  and "Independent fits make a map" (they were "Grid search, then refinement" and "A map from independent fits").
  A pending copy of `model_as_chain`'s applied storyboard proposal is removed. FACTS.md: the prfmodel row cites where
  the documentation address is (kickoff's `slides.qmd`), and four claims of the notes have rows. `expo.yaml` says
  where the data and scenes are and that the pause is the presenter's. `SESSION.md` says that the session's
  decisions came with its task, not from the lecturer's prompt. `lk clips` in both presets re-rendered what changed
  (paper: `stimulus_to_bold`, `grid_and_fit`; dark: all four under 0.1.1); geometry, timing and frame counts are the
  same in both presets (360, 465, 600 and 540 frames).
- 2026-11-13: left for the lecturer (PLAN.md, Decisions): the titles; the 0 s milestones; `model_as_chain`'s
  prediction, which the BOLD box shows from 5.5 s and loses in one frame at 9.3 s, as the original scene does,
  where the brief puts it last; `model_as_chain`'s HRF glyph, a canonical two-gamma shape with no data behind it;
  the dark style 0.1.1; and the hold. On the hold, the stop-gap above is incomplete: dropping `stop: true` alone moves
  the failure from `tools/check_clips.py` to `lk build --strict`, because slide 5's `study="eccentricity end"` names a
  stop candidate; the slide must then become `::: {.movie clip="fields_to_map" still="eccentricity" height=4.5cm}`.
  The stop's frame is the outlier, not the frames before it: frame 387 is a fresh keyframe, and in paper the frames
  after it in its own play differ from it by 7 grey levels as well (rest after it: 0; in dark 6, rest 8), while the
  12 frames before it are identical to one another; so splitting the rest into shorter plays would not help. Under
  `lecturekit_dark@0.1.1` the dark measure is unchanged (7 before the stop, rest 0). Until the engine or the lecturer settles it, the continuous build is red on this project
  and the build job (which needs the clips job) is skipped for every project: do not push or merge.
- 2026-11-13: also engine-side: `lk review shoot` captures each slide about 0.1 s after entry, during the clips'
  fade-in, so the contact sheets show the clip slides nearly blank and the posters (`f0000.png`) are the empty page.
  The card links the study PDFs, which show each clip's still.
- 2026-11-13: the hold is on the slide, with lecturekit 0.4.1. Its rest measure now counts two frames as one picture
  when no grey level differs by more than 16 at 160 px (it was 6). Measured across the 143 keyframes that sit in a
  still rest in the expo's and the feature deck's manim8 clips, a keyframe's re-coding differs from the frame before
  it by 1 to 10 levels (10 on this project's maps); where something starts to move on a keyframe the difference was 62
  or more. `lk clips` now records 47 frames of rest before `eccentricity` in paper and 46 in dark (manim8's manifest:
  39 static frames; the other 7 or 8 are the end of the dots' eased arrival, within 16 levels of the stop's frame).
  Slide 5 is `stops="eccentricity" study=strip` with the prompt on the hold; `tools/check_clips.py` passes (8
  entries, 0 problems), and `lk review frags` holds frame 387 in both presets. The continuous build is no longer
  blocked by this project. In the same release `lk review shoot` shoots every clip paused on its last frame, so the
  contact sheets show the clips complete; the posters (`f0000.png`) are still the empty first frame.
- 2026-11-13: correction. `SESSION.md` and `PLAN.md` said the session's decisions came with its task, not from the
  lecturer. Three were the lecturer's answers to the session's questions in its chat (a new project with a deck, one
  clip per slide; only the 12.9 s hold; 1280 by 720). The choice of the bridged styles was the session's.
