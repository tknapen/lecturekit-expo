# Brief: from fitted receptive fields to a map

Show that a map of the visual field on cortex is not put in by the analysis: it appears when every voxel is
fitted on its own and coloured by what the fit returned.

Left: the right half of the visual field, out to 6.5 deg, with the vertical meridian and a fixation cross.
Right: a sheet of cortex drawn as a grid of small squares, one per voxel (690).

Motion: voxels are fitted one after another, in order across the sheet. Each fit adds a dot at the voxel's
fitted pRF centre in the field and the voxel's square on the sheet, both in the colour of the centre's distance
from fixation. Bands of colour form across the sheet. After a rest, every square and dot changes to the
colour of the centre's direction from fixation, and the bands now run across the first set. A line of text at
the bottom says which colouring is shown.

`data/voxels.csv` has one row per voxel: its drawing order, its place on the sheet, its fitted centre and
size, and the eccentricity and polar angle of the centre. The voxels are simulated and fitted with prfmodel;
they are not measurements, and the page should say so.
