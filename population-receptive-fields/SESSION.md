# Session

The prompts of the session that built this deck, in order, with what the lecturer changed by hand after each.
Without this file the project is a deck; with it, it is a reproducible example of the method.

## Round 1: four clips to a talk (13 November 2026)

Prompt, with the upload `prf-clips-specs.zip` attached:

> here are some examples that would look good in the expo site:

The upload: four pRF clips as manim8 project seeds (`stimulus_to_bold`, `model_as_chain`, `grid_and_fit`,
`fields_to_map`), each an `animation.yaml`, its data and its references (the brief, the original hand-written Manim
scene, its last frame), with a README written for a website. The bundle's README and briefs are in
`sources/prf-clips/`; the seeds are the manim8 projects under `clips/families/population_receptive_fields/`.

The prompt above is the lecturer's only message. It names none of the decisions below: they came with the task
that the session's orchestrating workflow gave its agents, not from the lecturer, and the bundle's README lists two
of them (the styles, and whether 1920 by 1080 is the size wanted) under "Ask the owner before deciding". They were
applied as given and are open for the lecturer to confirm:

- A new expo project with a talk deck: one clip per slide, in the order stimulus to BOLD, model as a chain, grid and
  fit, fields to map.
- The clips render at 1280 by 720 and 30 fps (the README asked whether 1920 by 1080 was wanted).
- The two styles are the project's bridged `lecturekit_paper` and `lecturekit_dark` (given as version 0.1.0), not the
  website's. The dark style is now at 0.1.1 (step 4 below).
- The only key-press stop is `fields_to_map`'s hold at 12.9 s (the snapshot named in its `extensions.lecturekit.stops`),
  as a manim8 `stop: true` snapshot; the other clips play through.

How the session went:

1. The project was scaffolded with `lk new --manim8` and the expo's conventions; the seeds went into one family.
2. Four agents, one per clip, wrote each storyboard through manim8 proposals and the custom builders in each
   project's `code/`, checked the hard scientific constraints on the pixels, and rendered both styles
   (`scianim snapshot`, `scianim render`). All four reached rung R5 (builder objects, motion by registered
   `vary_parameter`); each project's README has the evidence.
3. The integrator rendered the clips into the deck (`lk clips`, `lk clips --mode dark`), drafted the slides and the
   planning files, and ran the checks. The hold at 12.9 s could not be put on the slide: lecturekit 0.4.0 measured 0
   frames of unchanged picture before it (README.md, log), so the slide played the clip through.
4. Reviewers checked the clips and the deck against the seeds; a fixer agent made the changes their findings allowed
   without the lecturer and listed the rest (README.md, log; PLAN.md, open items): the dark style's quiet roles
   lifted (`lecturekit_dark@0.1.1`, from `_brand-dark.yml`), the small text of two clips in `secondary_text`, a
   0.1 s reveal in `stimulus_to_bold`, the study PDF's link colour, the captions' citation, two titles redrafted as
   claims, and the records (FACTS.md, expo.yaml, this file).
5. The orchestrating session changed the engine: lecturekit 0.4.1 measures a keyframe's re-coding in a still rest
   as no change of picture, and settles clips on their last frame in `lk review shoot`. The hold went on slide 5
   (`stops="eccentricity" study=strip`), and the checks were run again in both presets (README.md, log).

Changed by hand: nothing yet. Open for the lecturer: the decisions above; the four slide titles (drafts of the
briefs' claims) and the deck's title, which sets on three lines on the paper title page; the hold at 12.9 s, now on slide 5, and the
missed 0 s milestones (README.md, log); the BOLD box's prediction before the pulse in `model_as_chain`; the HRF glyph
of `model_as_chain`, a schematic with no data; the dark style 0.1.1; the dataset's DOI; and the sign-off on each
clip's storyboard proposals and builder code.
