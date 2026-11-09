# Drift diffusion

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
