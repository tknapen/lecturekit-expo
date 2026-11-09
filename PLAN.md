# lecturekit-expo: a plan

A parallel repository of complete lecture projects built on lecturekit, each from a small set of source documents,
each showing one teaching device done well, each with its clips made for it. The engine repository stays the method
and two example decks; the expo is where the method is seen at work, many times over, by other people.

## What the expo is for

Four things the engine repository cannot do.

1. It proves the separation. Every project vendors the extension and pins the package (`lecturekit>=0.2,<0.3`) and
   carries no engine code. If a project needs a helper that is not in the engine, it lives in the project's `lib/`
   until a second project wants it; then it moves into the engine with a release. The expo is where that rule is
   exercised.
2. It is the engine's integration test. A change to the filter, the theme or the kit rebuilds a dozen decks in the
   continuous build; a regression that the two example decks do not catch shows up here, with a contact sheet.
3. It tells the story the method claims: from a few source documents (a paper, a chapter, a dataset, a proposal) to
   a lecture with a storyboard, a plan, verified facts, figures from numbers and clips, in a session whose prompts
   are kept. The inputs sit beside the outputs, so a reader can judge the distance travelled.
4. It is the proving ground for manim8. Each project holds its manim8 workspace; each clip that needs a custom
   builder is a candidate for a registered kind; a builder that two projects need is promoted. The expo grows the
   registry and the pattern library from real lectures rather than from demos.

## Shape

```text
lecturekit-expo/
├── README.md                     the gallery's front page is generated; this says what the expo is
├── _gallery/                     tools/gallery.py reads every project's expo.yaml and review sheet into index.html
├── .github/workflows/build.yml   matrix over projects: lk build (both presets where declared), lk review, Pages
├── template/                     the project convention: what lk new writes, plus sources/, SESSION.md, expo.yaml
├── signal-detection/             one folder per project
│   ├── expo.yaml                 title, minutes, field, source documents, teaching device, manim8 kinds used, presets
│   ├── sources/                  the documents the lecture was built from (or links and digitised values)
│   ├── STORYBOARD.md PLAN.md FACTS.md MANIFEST.md README.md   the method's files
│   ├── SESSION.md                the prompts of the session that built it, in order, with what the lecturer changed
│   ├── sims/                     the simulations; summaries land in assets/data
│   ├── make_assets.py anim/ assets/ slides.qmd _quarto.yml _brand.yml references.bib
│   └── clips/                    the manim8 workspace (second release): families/<project>/<clip>/
├── drift-diffusion/
└── ...
```

`expo.yaml` is small and is what the gallery shows:

```yaml
title: Signal detection theory in twenty minutes
minutes: 20
field: perception, methods
deck: lecture                     # talk | lecture | kickoff | tutorial | seminar
sources:
  - Green and Swets 1966, chapter 1 (digitised values; not redistributable)
  - Macmillan and Creelman 2005, chapter 1
device: a quiz that carries its answer; a criterion that slides on a keypress
clips: [criterion_slides, roc_draws]   # slugs: the deck's clip= names and the manim8 project ids
manim8_kinds: [function_plot, scientific_plot, equation_block, text_caption]   # registry ids
presets: [paper, dark]
author: Tomas Knapen
licence: CC BY 4.0
```

The gallery is one page of cards: title and minutes, the field, the teaching device, a five-second preview of the
best clip (a small WebM cut by `lk clips --preview`, to be added), links to the live deck, the study PDF, the contact
sheet and `SESSION.md`, and the sources. Filters by device, field and manim8 kind. A second page, the clip reel, shows
every clip of every project in one grid: that page is the manim8 showcase. A third, the reader, collects the study
PDFs: the student's view of the whole expo.

## Organise by teaching device, not by topic

Another lecturer comes to the expo with a lecture to make, not a topic to find. The useful index is the device:

- predict then reveal: a question, a prediction from the room, the clip that answers it;
- a dial on a parameter driving a model clip, with the static figure as the study equivalent;
- one simulation feeding the figure, the clip and the quiz, so that every number agrees;
- a staged figure that builds in two or three keypresses, identical bounding boxes;
- a worked example one step at a time, numbered in the role colour;
- a quiz or pause slide that carries its answer (live behind a fragment, study in the open);
- a study-only derivation under a live slide that states the result;
- a claim per slide, stated in the title, with the citation in italics on the slide;
- a recorded-lecture variant with pause slides and parts;
- a restyle: the same project in two presets, figures and clips following.

Each project names one primary device in `expo.yaml` and demonstrates it without compromise; it may use others.

## Pairs and variants that make the point

- The same source rendered twice: a 20-minute talk and a 90-minute lecture from one paper, to show how the method
  scales (the plan, the budget, what moves to study-only pages).
- One project in two presets, paper and dark, with the figures and the clips following; the restyle episode on a
  deck that was not built for it.
- A recorded version of one lecture: pause slides, parts, the study PDF as the reader's companion.
- A before-and-after, only for the author's own old decks: the original slides and the rebuilt project side by side.

## Topics

The criteria: one simulation can produce the figure, the clip and the numbers; the dynamic is only clear in motion;
the sources are open or reducible to digitised values; the clips fit manim8's registered kinds (plots, function and
surface plots, function images, equation blocks and labels, captions, schematic populations, receptive-field glyphs,
network graphs, spheres) with at most one custom builder; twenty to thirty minutes for a first entry.

| Project | What moves, and why it must | Sources | Kinds | Device | Min |
| --- | --- | --- | --- | --- | --- |
| Signal detection theory | two distributions, a criterion sliding, the ROC drawn as it moves; d' and bias separate before your eyes | Green and Swets 1966; Macmillan and Creelman 2005 | function_plot, scientific_plot, equation_block, text_caption | quiz with its answer | 20 |
| Drift diffusion | evidence traces reaching bounds, RT distributions piling up, the speed-accuracy trade-off as the bound moves | Ratcliff and McKoon 2008; Ratcliff et al. 2016 | scientific_plot, text_caption | predict then reveal | 25 |
| Divisive normalization | dials on the parameters driving response surfaces; contrast response; attention as gain | Carandini and Heeger 2012; Aqil et al. 2021 (own) | surface_plot, equation_block, function_plot | a dial on a parameter | 25 |
| Tuning curves and population codes | Gaussian tuning, the population vector, noise and Fisher information | Pouget et al. 2000; Dayan and Abbott ch. 3 | schematic_population, function_plot | one simulation for all | 20 |
| Population receptive fields | the kickoff and the workshop lectures, as they are | the Popylar proposal; Dumoulin and Wandell 2008 | receptive_field_glyph, function_plot, surface_plot | the whole method | 15 to 90 |
| Predictive coding | a two-layer network with error units settling; the prediction and the residual over time | Rao and Ballard 1999 | network_graph, scientific_plot | staged figure | 25 |
| Grid and place cells | 2-D firing fields emerging from a trajectory; path integration | Moser, Kropff and Moser 2008 | function_image, scientific_plot | live clip, study still | 20 |
| Bayesian cue combination | prior and likelihood multiplied; the posterior narrows; the weights shift with reliability | Ernst and Banks 2002; Knill and Pouget 2004 | function_plot, equation_block | worked example | 15 |
| Spiking neurons | integrate-and-fire to Hodgkin and Huxley: membrane potential, gating variables, the threshold | Hodgkin and Huxley 1952; Gerstner et al., Neuronal Dynamics (open) | scientific_plot, equation_block | a dial on the input current | 30 |
| Receptive fields and Gabor filters | an image convolved with a Gabor; simple and complex cells; orientation energy | Hubel and Wiesel 1962; Jones and Palmer 1987 | function_image | staged figure | 20 |
| MRI from spins to k-space | precession, the RF pulse, gradients, k-space filling, the Fourier reconstruction | Hornak, The Basics of MRI (open online); Brown et al. 2014 | sphere, function_image, equation_block | predict then reveal | 30 |
| The BOLD response and the GLM | the HRF, convolution, the design matrix, the fit; the bar-and-BOLD clip generalised | Boynton et al. 1996; Poldrack, Mumford and Nichols 2011 | scientific_plot, equation_block | one simulation for all | 25 |
| Diffusion MRI | tensors as ellipsoids, crossing fibres, where tractography fails | Basser et al. 1994; Jones 2010 | surface_plot, sphere | caveat slides | 20 |
| EEG and MEG forward model | a dipole in a sphere, the field map, why inverse problems are ill-posed | Hämäläinen et al. 1993 | sphere, function_image | worked example | 20 |
| Fourier series and transform | a sum of rotating terms drawing a square wave; the frequency domain of an image | any analysis text; Bracewell | function_plot, function_image, equation_block | reveal by term | 20 |
| Linear maps as geometry | a grid deformed by a matrix; eigenvectors standing still; the SVD as rotate-scale-rotate | Strang; 3Blue1Brown as storyboard only (licence note) | custom (a grid builder), equation_block | predict then reveal | 25 |
| Gradient descent on a landscape | a ball on a loss surface; learning rate, momentum, saddles | Goodfellow, Bengio and Courville (open) | surface_plot, function_plot | a dial on the learning rate | 20 |
| Dynamical systems and phase portraits | nullclines, fixed points, a limit cycle; Wilson and Cowan as the neural case | Strogatz; Wilson and Cowan 1972 | custom (a field builder; the kit's nmfield exists), scientific_plot | staged figure | 25 |
| Backpropagation on a tiny network | activations forward, errors backward, weights changing; the loss falling | Rumelhart, Hinton and Williams 1986; Nielsen (open) | network_graph, scientific_plot | worked example | 25 |
| Temporal-difference learning and dopamine | value updates, prediction errors moving back to the cue; the bandit in the room | Schultz, Dayan and Montague 1997; Sutton and Barto (open) | scientific_plot, schematic_population | the room produces data | 25 |
| Entropy and mutual information | areas that split and overlap; the channel; why bits are the unit | Shannon 1948; MacKay (open) | function_plot, equation_block | quiz with its answer | 20 |
| Sampling, resampling and multiple comparisons | sampling distributions forming; a permutation test; the false-positive rate climbing with tests | any open statistics text | scientific_plot | predict then reveal | 20 |
| An epidemic | S, I and R curves as the reproduction number turns; the herd-immunity threshold | Kermack and McKendrick 1927; any open text | scientific_plot | a dial on a parameter | 15 |
| Drift and selection | allele frequencies as random walks; fixation; selection bending the walk | any open population-genetics text | scientific_plot | one simulation for all | 15 |
| Waves and interference | two sources, the pattern on a screen; the double slit | any open physics text | function_image | staged figure | 15 |

The first five, as a set: signal detection (methods, open, plots only), drift diffusion (the pilot exists), divisive
normalization (own work, surfaces and dials), MRI from spins to k-space (the largest effect per minute, spheres and
images), and the Nature paper talk (the researcher's case, episode 9). Two of the author's own, three with open
sources, all twenty to thirty minutes, together most of the registry. Fourier series and gradient descent are the two
to add when manim8 needs a showcase outside neuroscience.

## Per project, the process

1. Put the sources in `sources/` (or their links and the digitised values) and write `STORYBOARD.md` by hand.
2. The assistant proposes `PLAN.md` (claims, roles, minutes, the figure or clip of each slide, the numbers each needs)
   and the simulations in `sims/`; the lecturer edits the plan.
3. Simulations run; summaries land in `assets/data`; `make_assets.py` draws the figures; the clips are briefs to
   manim8 (second release) or scenes on the kit, rendered by `lk clips` into `assets/clips` and `clips.json`.
4. `slides.qmd`, review rounds on the contact sheet and the PDF, `FACTS.md` and `MANIFEST.md`, the README log.
5. `SESSION.md`: the prompts in order and what the lecturer changed by hand. Without it the project is a deck;
   with it, it is a reproducible example of the method.

## Practicalities

- Content under CC BY 4.0, each project with its author. Sources go in only when redistributable; otherwise a link
  and the digitised values, with the method of digitising in `MANIFEST.md`.
- Each project pins its engine range and vendors the extension; the continuous build runs the newest engine against
  every project and the pinned one against each, so a breaking change is seen before a release.
- Each project has its own `_brand.yml`; at least one carries the dark preset too.
- The manim8 workspace per project under `clips/`, styles bridged from `_brand.yml` as versions
  (`styles/<brand>/<version>/style.yaml`), stills from named checkpoints for the study PDF. A custom builder that
  recurs in two projects is proposed to manim8's registry.
- A project's figures and clips are rendered in the continuous build; the committed MP4s are the fallback for the
  Pages site, as in the engine repository.
