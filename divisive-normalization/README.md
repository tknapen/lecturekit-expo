# Divisive normalization

A lecturekit project: one `slides.qmd`, a live deck and a study PDF.

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

## Log

- 2026-11-08: project created with `lk new` (lecturekit 0.2.0).
- 2026-11-09: brought to the lecturekit 0.3.0 scaffold: the budget is 25 minutes as in `expo.yaml` (it was the
  scaffold's 45), the plan's total and the placeholder figure's name (`example.tex`) are right, and `.gitignore`
  covers the Beamer auxiliaries and a manim8 workspace's renders. The deck is still the scaffold.
- 2026-11-09: `clips/` is a manim8 workspace (`lk new --manim8`): the bridged paper and dark styles, a family
  environment pinned to manim8 commit bad3ae1 (`uv.lock`), and one project, `divisive_normalization_intro`,
  copied from manim8's example at 1280 by 720 and 30 fps in `lecturekit_paper@0.1.0`. `lk clips` renders it
  into `assets/clips` (18 s, four checkpoints, still `rebalanced`). It is on no slide: its equation is the
  example's schematic, and replacing it is the lecturer's decision (the project's README says what is needed).
