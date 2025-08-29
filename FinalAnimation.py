from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.base import SpeechService
import numpy as np
import os, glob, subprocess

# ------------------------ STYLE / CONSTANTS ------------------------
config.frame_rate = 30
config.background_color = "#0e1a25"
AXIS_COLOR  = "#D9D9D9"
GRID_COLOR  = "#6b7a86"
TEXT_COLOR  = WHITE
ACCENT_X    = "#8F3931"  # vertical (x-axis reflection cue)
ACCENT_Y    = "#49A88F"  # horizontal (y-axis reflection cue)
ACCENT_C    = "#a9dc76"  # final/vertical shift cue
POINT_START = "#26b6da"
POINT_FINAL = "#a9dc76"

# ------------------------ UTILITIES ------------------------
def callout_box(mobj: Mobject, pad=0.18, stroke=1.0, alpha=0.18):
    """Soft translucent halo behind text without blocking grid."""
    bg = RoundedRectangle(corner_radius=0.16, stroke_width=stroke,
                          stroke_color=WHITE, fill_color=BLACK, fill_opacity=alpha)
    # size to content
    bg.set(width=mobj.width + 2*pad, height=mobj.height + 2*pad)
    g = VGroup(bg, mobj)
    g.set_z_index(3)
    return g

def right_column_layout(scene, *mobjects, col_center=3.8, top_y=3.2, vgap=0.3):
    """Stack objects in the cleared right margin, no opaque panel."""
    y = top_y
    placed = []
    for m in mobjects:
        g = callout_box(m)
        g.move_to([col_center, y - g.height/2, 0])
        y -= g.height + vgap
        placed.append(g)
    return VGroup(*placed)

def pulse(mobj, color, rt=0.35):
    return AnimationGroup(
        mobj.animate.set_color(color),
        Wait(rt*0.5),
        mobj.animate.set_color(TEXT_COLOR),
        lag_ratio=0.0, run_time=rt
    )

# ------------------------ VO LINES (concise) ------------------------
VO = {
    "theory": (
        "We start with the mapping from function to points: "
        "g of x equals a, times f of k times x minus d, plus c. "
        "That induces x prime equals x over k plus d, and y prime equals a y plus c. "
        "Inside controls horizontal motion in x. Outside controls vertical motion in y. "
        "Negative a reflects across the x–axis; negative k reflects across the y–axis."
    ),
    "plane": "Now let us work on the coordinate plane.",
    "start": "Our given point on f is one, negative two.",
    "y_reflect": "First, reflect across the y–axis; negate x, hold y.",
    "left_shift": "Next, translate left by one; subtract one from x.",
    "x_reflect": "Then, reflect across the x–axis; negate y, hold x.",
    "up_shift": "Finally, translate up by three; add three to y.",
    "wrap": "The image is negative two, five."
}

# ------------------------ OPTIONAL: Piper service (disabled by default) ------------------------
USE_PIPER = False

class PiperService(SpeechService):
    def __init__(self, piper_path: str, model_path: str, speaker=None, tempo=1.0, **kw):
        super().__init__(**kw); self.piper_path=piper_path; self.model_path=model_path
        self.speaker=speaker; self.tempo=float(tempo)
        self.ffmpeg_path=os.path.join(os.path.dirname(piper_path),"ffmpeg","bin","ffmpeg.exe")

    def _ffargs(self):
        t=self.tempo
        if abs(t-1.0)<1e-3: return []
        if 0.5<=t<=2.0: return ["-af", f"atempo={t}"]
        a=max(0.01,min(4.0,t))**0.5; return ["-af", f"atempo={a},atempo={a}"]

    def generate_from_text(self, text, cache_dir=None, path=None):
        cache_dir=cache_dir or self.cache_dir; os.makedirs(cache_dir, exist_ok=True)
        stem=self.get_audio_basename({"input_text":text, "model":self.model_path})
        wav=os.path.join(cache_dir, stem+".wav"); mp3=os.path.join(cache_dir, stem+".mp3")
        cmd=[self.piper_path,"--model",self.model_path,"--output_file",wav]
        if self.speaker is not None: cmd+=["--speaker",str(self.speaker)]
        pr=subprocess.run(cmd, input=text.encode("utf-8"), capture_output=True)
        if pr.returncode!=0: raise RuntimeError("Piper failed.")
        if os.path.exists(mp3): os.remove(mp3)
        pr2=subprocess.run([self.ffmpeg_path,"-y","-v","error","-i",wav]+self._ffargs()+["-acodec","libmp3lame","-b:a","192k",mp3], capture_output=True)
        if pr2.returncode!=0 or not os.path.exists(mp3): raise RuntimeError("ffmpeg failed.")
        return {"path": mp3, "original_audio": os.path.basename(mp3), "input_data":{"input_text":text}}

# ------------------------ SCENE ------------------------
class FinalAnimation(VoiceoverScene, Scene):
    def setup(self):
        if USE_PIPER:
            rt = os.path.join(os.path.dirname(__file__), "piper_runtime")
            exe = os.path.join(rt,"piper.exe")
            models = sorted(glob.glob(os.path.join(rt,"*.onnx")))
            if models: self.set_speech_service(PiperService(exe, models[0], tempo=1.0))

        # Left axes restricted to [-4,4] in x per request
        self.axes = Axes(
            x_range=[-4,4,1], y_range=[-4,7,1],
            x_length=7.0, y_length=6.0,
            axis_config={"color":AXIS_COLOR, "stroke_width":2}
        ).to_edge(LEFT, buff=0.8)
        self.grid = NumberPlane(
            x_range=[-4,4,1], y_range=[-4,7,1],
            x_length=7.0, y_length=6.0,
            background_line_style={"stroke_color":GRID_COLOR,"stroke_width":1,"stroke_opacity":0.5},
            axis_config={"stroke_width":0},
        ).move_to(self.axes)

        # Right-column anchor (reserved margin)
        self.right_center_x = 3.6
        self.right_top_y    = 3.2

        # Common math snippets with isolations for coloring
        self.gx_base = MathTex(
            "g(x)","=","-","f","(","-","x","-","1",")","+","3",
            substrings_to_isolate=["-x-1","-","3","x","1","+","-x","-1"]
        ).set_color(TEXT_COLOR).scale(0.9)
        self.map_base = MathTex(
            "x'","=","{x \\over k}","+","d",",","\\;","y'","=","a","y","+","c",
            substrings_to_isolate=["{x \\over k}","d","a","y","+","c"]
        ).set_color(TEXT_COLOR).scale(0.9)

    # ---------------- WHITEBOARD INTRO (isolated) ----------------
    def whiteboard_intro(self):
        board = RoundedRectangle(corner_radius=0.4, width=12.6, height=7.2,
                                 fill_opacity=1, fill_color="#e6e9ee", stroke_color="#1f2b36", stroke_width=4)
        board.to_edge(DOWN, buff=0.05).set_z_index(0)

        title = Tex("Transformation Map (Function $\\to$ Points)").scale(1.1).set_color(BLACK)
        g = MathTex("g(x)=a\\,f\\big(k(x-d)\\big)+c").set_color(BLACK).scale(1.1)
        mapping = MathTex("x'={x\\over k}+d\\,,\\quad y'=a\\,y+c").set_color(BLACK).scale(1.05)
        bullets = VGroup(
            Tex("Inside $\\Rightarrow$ horizontal, acts on $x$").set_color(BLACK),
            Tex("Outside $\\Rightarrow$ vertical, acts on $y$").set_color(BLACK),
            Tex("$a<0$: reflect across $x$–axis,\\quad $k<0$: reflect across $y$–axis").set_color(BLACK)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)

        group = VGroup(title,g,mapping,bullets).arrange(DOWN, buff=0.45).move_to(board.get_center()+UP*0.2)
        # CHECKPOINT-10: fit within board
        group.scale_to_fit_width(board.width*0.84)

        # — Write theory
        self.add(board)
        with self.voiceover(text=VO["theory"]) if USE_PIPER else nullcontext():
            self.play(FadeIn(title, shift=UP*0.1), run_time=0.35)
            self.play(Write(g), run_time=0.9)
            self.play(Write(mapping), run_time=0.8)
            self.play(LaggedStart(*[Write(b) for b in bullets], lag_ratio=0.15), run_time=1.0)
            self.wait(0.2)

        # — Natural eraser (mask) → remove ONLY the three bullets (keep title+lines)
        # FM-1 mitigation: use a DARK mask to avoid lightening the navy background.
        # Build a local dark layer covering the bullets; animate a rounded "eraser" cutout along a hand-like path.
        dark_layer = Rectangle(width=board.width*0.88, height=bullets.height+0.6,
                               fill_color=board.get_fill_color(), fill_opacity=1.0, stroke_width=0)
        dark_layer.move_to(bullets)

        cutout = RoundedRectangle(corner_radius=0.18, width=2.2, height=0.8,
                                  fill_color=config.background_color, fill_opacity=1.0, stroke_width=0).move_to(bullets)
        dark_group = VGroup(dark_layer, cutout).set_z_index(2)

        # Updater: keep a "hole" where cutout is (simulate wipe)
        def maintain_hole(m: VGroup):
            # replace dark layer fill with background, then re-add hole for compositing illusion
            dark_layer.set_fill(board.get_fill_color(), opacity=1.0)
            cutout.set_fill(config.background_color, opacity=1.0)

        dark_group.add_updater(lambda m, dt=0: maintain_hole(m))  # FM-2 safe; cleared later
        self.add(dark_group)

        # hand-like bezier path across bullets
        path = VMobject().set_points_smoothly([
            bullets.get_left()+LEFT*0.5+UP*0.25,
            bullets.get_left()+UP*0.15,
            bullets.get_center()+RIGHT*0.2,
            bullets.get_right()+RIGHT*0.2+DOWN*0.15
        ])
        # Move cutout along path while fading out bullets under it
        def move_wipe(alpha):
            cutout.move_to(path.point_from_proportion(alpha))
            for b in bullets: b.set_opacity(max(0.0, 1.0-3.0*alpha))

        self.play(UpdateFromAlphaFunc(cutout, move_wipe), run_time=1.1)
        dark_group.clear_updaters(); self.remove(dark_group)

        # Write the PROBLEM on the same board immediately after the wipe (CHECKPOINT-3)
        problem = Tex("Problem:").set_color(BLACK).scale(1.0).to_edge(LEFT)
        gx_problem = MathTex("g(x)=-\\,f(-x-1)+3").set_color(BLACK).scale(1.0)
        given = MathTex("\\text{Given on }f:(1,-2)").set_color(BLACK).scale(0.95)

        prob_group = VGroup(problem, gx_problem, given).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        prob_group.next_to(mapping, DOWN, buff=0.6).align_to(mapping, LEFT)
        prob_group.scale_to_fit_width(board.width*0.8)  # CHECKPOINT-10 bounds
        with self.voiceover(text="Our problem uses g of x equals negative f of minus x minus one, plus three; with the point one, negative two on f.") if USE_PIPER else nullcontext():
            self.play(Write(prob_group), run_time=0.9)
            self.wait(0.2)

        # Fade out entire board BEFORE showing the grid (CHECKPOINT-1)
        self.play(FadeOut(VGroup(board, title, g, mapping, bullets, prob_group), run_time=0.7))

    # ---------------- MAIN ----------------
    def construct(self):
        # 1) Whiteboard (theory + problem then fade)
        self.whiteboard_intro()

        # 2) Stage: graph on left, right notes column (CHECKPOINT-4)
        with self.voiceover(text=VO["plane"]) if USE_PIPER else nullcontext():
            self.play(FadeIn(self.grid, self.axes), run_time=0.6)

        # Initial point and label
        p = Dot(self.axes.c2p(1,-2), color=POINT_START, radius=0.09)
        p_lbl = MathTex("(1,-2)").scale(0.9).next_to(p, DR, buff=0.18).set_z_index(3)
        with self.voiceover(text=VO["start"]) if USE_PIPER else nullcontext():
            self.play(FadeIn(p, scale=0.6), Write(p_lbl), run_time=0.7)

        # Right column: gx, mapping, given (recreate in white-on-dark)
        gx = self.gx_base.copy()
        mapping = self.map_base.copy()
        given = MathTex("(1,-2)\\ \\text{on }f").scale(0.9).set_color(TEXT_COLOR)
        right = right_column_layout(self, gx, mapping, given,
                                    col_center=self.right_center_x, top_y=self.right_top_y)
        self.play(FadeIn(right, shift=UP*0.1), run_time=0.6)

        # Helper: color maps (CHECKPOINT-7; avoid playing set_color_by_tex directly)
        def colored_gx_inside():
            gx2 = self.gx_base.copy()
            gx2.set_color_by_tex_to_color_map({"-x-1": ACCENT_Y})
            gx2.move_to(gx)
            return gx2
        def colored_map_k():
            m2 = self.map_base.copy()
            m2.set_color_by_tex_to_color_map({"{x \\over k}": ACCENT_Y})
            m2.move_to(mapping)
            return m2
        def colored_map_d():
            m2 = self.map_base.copy()
            m2.set_color_by_tex_to_color_map({"d": ACCENT_Y})
            m2.move_to(mapping)
            return m2
        def colored_map_a():
            m2 = self.map_base.copy()
            m2.set_color_by_tex_to_color_map({"a": ACCENT_X})
            m2.move_to(mapping); return m2
        def colored_map_c():
            m2 = self.map_base.copy()
            m2.set_color_by_tex_to_color_map({"c": ACCENT_C})
            m2.move_to(mapping); return m2

        # 3) Reflect across y-axis (POINT ONLY; grid static per CHECKPOINT-5)
        with self.voiceover(text=VO["y_reflect"]) if USE_PIPER else nullcontext():
            self.play(Transform(gx, colored_gx_inside()), Transform(mapping, colored_map_k()), run_time=0.35)
            new_xy = (-1, -2)
            self.play(
                p.animate.move_to(self.axes.c2p(*new_xy)),
                Transform(p_lbl, MathTex("(-1,-2)").scale(0.9).next_to(self.axes.c2p(*new_xy), DL, buff=0.18)),
                pulse(self.axes.get_y_axis(), ACCENT_Y, rt=0.5),
                run_time=0.9
            )
            # restore mapping color
            self.play(Transform(mapping, self.map_base.copy().move_to(mapping)), run_time=0.25)

        # 4) Shift left by 1 (subtract one from x)
        with self.voiceover(text=VO["left_shift"]) if USE_PIPER else nullcontext():
            self.play(Transform(mapping, colored_map_d()), run_time=0.35)
            new_xy = (-2, -2)
            self.play(
                p.animate.move_to(self.axes.c2p(*new_xy)),
                Transform(p_lbl, MathTex("(-2,-2)").scale(0.9).next_to(self.axes.c2p(*new_xy), DL, buff=0.18)),
                run_time=0.9
            )
            self.play(Transform(mapping, self.map_base.copy().move_to(mapping)), run_time=0.25)

        # 5) Reflect across x-axis (POINT ONLY)
        with self.voiceover(text=VO["x_reflect"]) if USE_PIPER else nullcontext():
            self.play(Transform(mapping, colored_map_a()), run_time=0.35)
            new_xy = (-2, 2)
            self.play(
                p.animate.move_to(self.axes.c2p(*new_xy)),
                Transform(p_lbl, MathTex("(-2,2)").scale(0.9).next_to(self.axes.c2p(*new_xy), UL, buff=0.18)),
                pulse(self.axes.get_x_axis(), ACCENT_X, rt=0.5),
                run_time=0.9
            )
            self.play(Transform(mapping, self.map_base.copy().move_to(mapping)), run_time=0.25)

        # 6) Shift up by 3
        with self.voiceover(text=VO["up_shift"]) if USE_PIPER else nullcontext():
            self.play(Transform(mapping, colored_map_c()), run_time=0.35)
            new_xy = (-2, 5)
            self.play(
                p.animate.move_to(self.axes.c2p(*new_xy)),
                Transform(p_lbl, MathTex("(-2,5)").scale(0.9).next_to(self.axes.c2p(*new_xy), UL, buff=0.18)),
                p.animate.set_color(POINT_FINAL),
                run_time=1.0
            )

        # 7) Wrap-up
        with self.voiceover(text=VO["wrap"]) if USE_PIPER else nullcontext():
            self.play(
                Indicate(p_lbl, color=POINT_FINAL, scale_factor=1.05),
                run_time=0.8
            )
            self.wait(0.2)

# --------------- DEBUG toggle (does nothing unless you set DEBUG=True) ---------------
DEBUG = False
if DEBUG:
    np.random.seed(0)
