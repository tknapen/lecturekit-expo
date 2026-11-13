# Four pRF clips to re-render in the site's light and dark themes

For the agent that builds animations for the website. Each folder is one clip as a manim8 (SciAnim Studio)
project seed: `animation.yaml` (what the clip must show; schema 1.0, validated with manim8 0.1.0a0),
`references/brief.md` (the same in prose), `data/` (every number the clip draws) and `references/` (the
original scene's source and its last frame).

| Folder | Clip | Original on the site | Length |
| --- | --- | --- | --- |
| `stimulus_to_bold` | From stimulus to predicted BOLD signal | a04-stim-bold | 12 s |
| `model_as_chain` | The model as a chain of stages | a02-model-box | 15.5 s |
| `grid_and_fit` | Grid search and refinement of a pRF fit | a04b-fit-2 | 20 s |
| `fields_to_map` | From fitted receptive fields to a map | map (lecture of 18 November 2026) | 18 s |

## What exists and what does not

The originals were hand-written Manim scenes, not manim8 projects: there is no storyboard to reuse. The scene
source is in each `references/original_scene.py`. It imports helpers that are not in this bundle (`kit`,
`VisualField`, `TracePanel`, `Frame`, `label`, and for the chain `l2model`), so read it for positions, sizes
and timing; do not try to run it. Scene units there: a 16 by 9 frame with the origin at the centre. The
renders already on the site are the reference for motion.

The storyboard is yours to write (`create_storyboard` proposals). Where the component registry has no fit
(the gear and box glyphs, the bar in the visual field, the sheet of squares), use `kind: custom` with a named
builder and flag it for review.

## Themes

- Render every clip twice, under the site's light style and its dark style:
  `scianim render <project> --profile final --style <name@version>`. The `style:` in each `animation.yaml`
  (`tomas_scientific@0.5.1`) is a placeholder that validates; replace it with the site's light style.
- Colour by palette role only, never a hex value in a storyboard or a builder. The roles each clip uses are
  listed under `direction.prefer` in its `animation.yaml`. The page colour is the style's `background`.
- A fill that was a tint of a colour in the original becomes the matching `*_soft` role, so that it does not
  turn grey on a dark page.
- Geometry, timing and frame count are identical in both themes, so the page can swap one video for the other.
  Check every checkpoint under both styles before a final render: thin strokes and small text first.
- Deliver `<id>.light.mp4` and `<id>.dark.mp4`, each with a poster of its last frame.

## Rules

- Draw only what `data/` holds. Three clips are simulations and one (`grid_and_fit`) shows a measured voxel;
  the `citation` of each source says which, and the labels in the clip must agree.
- No titles or captions inside the clips beyond the labels the briefs name; the page carries the rest.
- `fields_to_map` has one hold for lecturing, at 12.9 s (`extensions.lecturekit.stops`). The website does not
  need it; keep the rest there.

## Ask the owner before deciding

- The names and versions of the site's light and dark styles, if they are not obvious from the workspace.
- Whether 1920 by 1080 is the size the site wants (the originals were cropped to their content afterwards).
- Any change to a number, a label that makes a claim, or the order of events.
