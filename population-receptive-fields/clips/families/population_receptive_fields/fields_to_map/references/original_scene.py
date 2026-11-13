"""Clip: the map falls out. Left, the right half of the visual field (radius 6.5 deg); right, a model sheet of early
visual cortex, one square per voxel (sims/run.py, `map`: 690 synthetic voxels simulated and fitted with prfmodel).

Beats (what the viewer should take from each):
  1. Voxels are fitted one after another, in the order they lie on the sheet from one edge to the other. Each fit puts
     a dot at the voxel's fitted pRF centre in the field and colours the voxel's square by the centre's eccentricity:
     the colour bands on the sheet were not put there, they come out of the fits.
  2. The same fits, coloured by polar angle: the bands now run the other way across the sheet.
No title or caption in the clip: the slide carries the claim. Colours are brand tokens mixed along a ramp.
"""
from kit import *

M = json.loads((DATA / 'map.json').read_text())
U, V = np.array(M['u']), np.array(M['v']); FX, FY = np.array(M['fx']), np.array(M['fy']); STEP = M['step']
ECC = np.hypot(FX, FY); ANG = np.degrees(np.arctan2(FY, np.maximum(FX, 1e-6)))
RAMP_ECC = (CAVEAT, EXAMPLE, TEAL, BLUE); RAMP_ANG = (ORANGE, PURPLE, TEAL)


def ramp(stops, t):
    t = min(max(float(t), 0.0), 1.0) * (len(stops) - 1); i = min(int(t), len(stops) - 2)
    return interpolate_color(ManimColor(stops[i]), ManimColor(stops[i + 1]), t - i)


class MapFallsOut(Scene):
    def construct(self):
        # the field (right half), radius 6.5 deg drawn as 2.8 units
        c = np.array([-6.3, -0.1, 0]); rf = 2.8; kf = rf / 6.5
        arc = Arc(radius=rf, start_angle=-PI / 2, angle=PI, color=HAIR, stroke_width=2).move_arc_center_to(c)
        mer = Line(c + rf * DOWN, c + rf * UP, color=HAIR, stroke_width=2)
        fix = VGroup(Line(c + 0.1 * LEFT, c + 0.1 * RIGHT, color=MUTED, stroke_width=2), Line(c + 0.1 * DOWN, c + 0.1 * UP, color=MUTED, stroke_width=2))
        self.add(arc, mer, fix, label('the visual field: fitted pRF centres', 22, MUTED).move_to([-4.6, 3.2, 0]))
        # the sheet
        sc = 5.6 / (V.max() - V.min() + STEP); s0 = np.array([3.9 - (U.max() - U.min()) * sc / 2, -0.1, 0])
        pos = [s0 + np.array([(u - U.min()) * sc, v * sc, 0]) for u, v in zip(U, V)]
        self.add(label('a sheet of cortex: one square per voxel', 22, MUTED).move_to([3.9, 3.2, 0]))
        order = np.argsort(U + 0.02 * V)
        squares = [Square(side_length=STEP * sc * 0.94, stroke_width=0, fill_color=ramp(RAMP_ECC, ECC[i] / 6.5), fill_opacity=1).move_to(pos[i]) for i in order]
        dots = [Dot(c + np.array([FX[i] * kf, FY[i] * kf, 0]), radius=0.05, color=ramp(RAMP_ECC, ECC[i] / 6.5)) for i in order]
        key = label('colour: distance from fixation', 24, INK).move_to([-0.9, -3.3, 0]); self.add(key)
        self.wait(0.6)
        self.play(LaggedStart(*[AnimationGroup(FadeIn(s, scale=0.3), FadeIn(d, scale=0.3)) for s, d in zip(squares, dots)], lag_ratio=0.012), run_time=11, rate_func=linear)
        self.wait(1.0); checkpoint(self, 'eccentricity', label='coloured by eccentricity', rest=0.6)
        key2 = label('colour: direction from fixation', 22, INK).move_to(key)
        self.play(*[s.animate.set_fill(ramp(RAMP_ANG, (90 - ANG[i]) / 180)) for s, i in zip(squares, order)],
                  *[d.animate.set_color(ramp(RAMP_ANG, (90 - ANG[i]) / 180)) for d, i in zip(dots, order)], Transform(key, key2), run_time=2.5)
        self.wait(2.5)
