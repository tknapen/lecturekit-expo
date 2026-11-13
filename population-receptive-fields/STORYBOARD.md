# Storyboard: Population receptive fields, from stimulus to map

The lecturer's intent, in the lecturer's voice, before any slide exists. This deck started from four clips, not from
a storyboard: the lecturer uploaded them as manim8 seeds (13 November 2026, `SESSION.md`) with their briefs. What
follows is drafted from those briefs for the lecturer to rewrite; the words of each brief are the lecturer's.

## What the time is for

Fifteen minutes in which the room sees the whole pRF method move: a stimulus becomes a predicted time course, the
model is a chain of stages with parameters on some of them, a fit finds one voxel's field, and fits voxel by voxel
make a map that nobody put in.

## The arc

The forward model first: one voxel, one run, one cursor. Then the model opened into its stages, so the parameters
have a place. Then the inverse: fitting one measured voxel by grid search and refinement. Last, many fits side by
side: a map appears.

## What moves on each slide

| Slide | Clip | What moves | What the room should see |
| --- | --- | --- | --- |
| Stimulus and pRF predict BOLD | `stimulus_to_bold`, 12 s | One cursor runs through a 300 s bar run at constant speed. The bar crosses the visual field, the predicted neural and BOLD traces are drawn up to the cursor, a dot rides each. | The neural trace rises at each crossing of the pRF; the BOLD trace follows about 5 s later, smoother, with an undershoot in every blank. |
| A model is a chain of stages | `model_as_chain`, 15.5 s | The modelling loop (parameters, stimulus, model, prediction on data) shrinks to the top; the model box opens into seven stages; a copy of theta splits into four tags; a pulse runs from stimulus to BOLD; the prediction is drawn over the data. | The model is a chain, and the fitted parameters belong to four of its stages. |
| Grid search, then refinement | `grid_and_fit`, 20 s | A candidate field hops over a grid (4 slowly, 48 quickly, the best so far kept as a dashed outline), lands on the best grid point, then slides in eleven steps to the optimum, its prediction laid on one measured voxel with R squared read out. | A fit is a search: the prediction that matches the measurement best gives the field. |
| A map from independent fits | `fields_to_map`, 18 s | 690 voxels are fitted one after another across a sheet of cortex; each adds a dot at its fitted centre and colours its square by eccentricity; after a rest everything is recoloured by polar angle. | Bands appear although no fit knows its neighbours: the map comes out of the fits. |

## What must be on screen

The four clips, each alone under its title. The one hold for lecturing is on the complete eccentricity map (12.9 s),
where the room predicts how the bands will run when the colour changes to direction from fixation.

## Credit and lineage

The clips are the lecturer's, rebuilt in manim8 from the hand-written Manim scenes of the Coimbra pRF workshop and the
lecture of 18 November 2026. Three clips show simulations (prfmodel; one synthetic panel); one shows a measured voxel
of prfmodel's example dataset 7t-aot-visual (Knapen 2026, figshare, CC BY 4.0).

## Constraints

Fifteen minutes, a talk; the audience knows what fMRI and a voxel are. The clips are 1280 by 720 at 30 fps, in the
deck's paper and dark presets.
