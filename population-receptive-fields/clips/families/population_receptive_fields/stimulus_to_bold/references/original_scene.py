"""Clip A04 (slide 5): from stimulus to BOLD. Thursday's bar run (300 s: eight sweeps in four directions pairs, a 15 s
blank after every two) at Thursday's voxel, condensed to about 14 s, in three synchronized rows with one cursor: the
stimulus (each sweep a grey band with its direction), the predicted neural response, and the predicted BOLD response,
each on its own scale. On the left the visual field shows the bar at the cursor's time with the pRF outline.

Beats:
  1. The run's stimulus row, the empty neural and BOLD panels, the field with the pRF outline.
  2. The cursor runs through the 300 s: the bar moves in the field, the neural trace follows at once and the BOLD trace
     follows it about 5 s later, through each blank's undershoot. The cursor leaves at the end.
Numbers: sim01.json (part1_thursday_voxel.d0_run: t_s, stimulus.bar_centre_deg and bar_direction_deg per 1-s frame,
frame_kind 0 for blanks; neural (coverage units, max 0.68) and bold (after prfmodel's sum-normalised HRF, max 0.80, min
-0.23)); without the file, anim/l2model.py's run (same schedule, analytic coverage, the same HRF). Storyboard:
STORYBOARD.md slide 5 (A04); PLAN.md slide 5 and clip A04.
"""
from kit import *
import l2model as M

KEYFRAMES = (4.0, 8.0, 12.0)
S1 = M.load('sim01')
X0, Y0, SG = M.VOXEL['x'], M.VOXEL['y'], M.VOXEL['s']
if S1:
    _r = S1['part1_thursday_voxel']['d0_run']; _st = _r['stimulus']
    TS = np.array(_r['t_s'], float); NEU = np.array(_r['neural'], float); BOLD = np.array(_r['bold'], float)
    CEN = [None if c is None else float(c) for c in _st['bar_centre_deg']]
    DIR = [None if d is None else float(d) for d in _st['bar_direction_deg']]
else:
    _sch = M.schedule(); TS = np.arange(len(_sch), dtype=float)
    CEN = [None if s is None else float(s[0]) for s in _sch]; DIR = [None if s is None else float(s[1]) for s in _sch]
    NEU = M.run_cov(); BOLD = M.to_bold(NEU)
T_END = float(TS[-1] + 1)
RUN_T = 13.5                                             # seconds of clip for the whole run


def sweeps():
    """(start, end, direction) of each sweep, in seconds of the run."""
    out, k = [], 0
    while k < len(DIR):
        if DIR[k] is None: k += 1; continue
        j = k
        while j + 1 < len(DIR) and DIR[j + 1] == DIR[k] and CEN[j + 1] is not None and CEN[j + 1] > CEN[j]: j += 1
        out.append((TS[k], TS[j] + 1, DIR[k])); k = j + 1
    return out


def bar_at(t):
    """Bar centre and direction at run time t (the bar moves smoothly between the 1-s frames of a sweep), or None."""
    k = int(np.clip(np.floor(t), 0, len(TS) - 1))
    if CEN[k] is None: return None
    c = CEN[k]
    if k + 1 < len(TS) and CEN[k + 1] is not None and DIR[k + 1] == DIR[k] and CEN[k + 1] > c: c += (CEN[k + 1] - c) * (t - k)
    return c, DIR[k]


class StimBold(Scene):
    def construct(self):
        t = ValueTracker(0.0)
        # the field
        F = VisualField((-6.4, 0.3), 1.45, deg=8.0)
        win = Group(F.outline(HAIR, 3.0).set_z_index(-3), F.prf(X0, Y0, SG, INK, 3.0).set_z_index(1), F.fixation().set_z_index(1))

        def bar():
            b = bar_at(t.get_value())
            return (F.bar(b[0], 2.0, b[1]) if b else F.empty()).set_z_index(-2)
        barm = always_redraw(bar)

        # rows: stimulus strip, neural, BOLD (separate scales), shared time axis
        L, Wd = -3.6, 11.0
        S = Frame(L, 2.75, Wd, 0.8, (0, T_END), (0, 1))
        N = Frame(L, 0.05, Wd, 2.05, (0, T_END), (-0.05, 0.75))
        Bd = Frame(L, -2.85, Wd, 2.3, (0, T_END), (-0.3, 0.9))
        strip = VGroup()
        for a, b, d in sweeps():
            band = Rectangle(width=S(b, 0)[0] - S(a, 0)[0], height=0.8).set_stroke(width=0).set_fill(APERTURE, 1).move_to((S(a, 0.5) + S(b, 0.5)) / 2)
            u = np.array([np.cos(np.radians(d)), np.sin(np.radians(d)), 0])
            arr = Arrow(band.get_center() - u * 0.27, band.get_center() + u * 0.27, buff=0, stroke_width=4, color=INK, tip_length=0.14, max_tip_length_to_length_ratio=0.5)
            strip.add(band, arr)
        rows = VGroup(label('stimulus', 28, INK).next_to(S(0, 0.5), LEFT, buff=0.3),
                      label('neural', 28, INK).rotate(PI / 2).move_to([L - 0.85, N.bottom + N.height / 2, 0]),
                      label('BOLD', 28, INK).rotate(PI / 2).move_to([L - 0.85, Bd.bottom + Bd.height / 2, 0]))
        nax = VGroup(Line(N(0, -0.05), N(0, 0.75)).set_stroke(MUTED, 1.6), Line(N(0, 0), N(T_END, 0)).set_stroke(HAIR, 2),
                     *[label(f'{v:g}', 26, MUTED).next_to(N(0, v), LEFT, buff=0.12) for v in (0, 0.5)])
        bax = VGroup(Line(Bd(0, -0.3), Bd(0, 0.9)).set_stroke(MUTED, 1.6), Line(Bd(0, 0), Bd(T_END, 0)).set_stroke(HAIR, 2),
                     *[label(f'{v:g}', 26, MUTED).next_to(Bd(0, v), LEFT, buff=0.12) for v in (0, 0.5)],
                     Line(Bd(0, -0.3), Bd(T_END, -0.3)).set_stroke(MUTED, 1.6),
                     *[label(f'{v:g}', 26, MUTED).next_to(Bd(v, -0.3), DOWN, buff=0.12) for v in (0, 100, 200, 300)],
                     label('time (s)', 28, MUTED).next_to(Bd(T_END / 2, -0.3), DOWN, buff=0.55))
        TN, TB = TracePanel(N, t), TracePanel(Bd, t)
        neu = TN.series(TS, NEU, GAUSS, 4.0); bold = TB.series(TS, BOLD, GAUSS, 6.0)

        def cursor():
            x = t.get_value()
            return VGroup(Line(S(x, -0.08), Bd(x, -0.3)).set_stroke(MUTED, 2.0, opacity=0.6),
                          Dot(N(x, float(np.interp(x, TS, NEU))), radius=0.075, color=GAUSS),
                          Dot(Bd(x, float(np.interp(x, TS, BOLD))), radius=0.075, color=GAUSS)).set_z_index(3)
        cur = always_redraw(cursor)
        self.add(win, strip, rows, nax, bax)
        self.wait(1.0)
        self.add(barm, neu, bold, cur)
        self.play(t.animate.set_value(T_END - 1e-3), run_time=RUN_T, rate_func=linear)
        self.play(FadeOut(cur), run_time=0.4)
        self.wait(1.2)
