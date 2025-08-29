# -*- coding: utf-8 -*-
# See active checkpoints at the very top of this file.

from __future__ import annotations
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.base import SpeechService
import os, subprocess, glob, numpy as np, random

# =============================
# Globals / Config
# =============================
random.seed(7)  # CHECKPOINT-10
config.quality = "example_quality"
config.frame_rate = 30  # CHECKPOINT-10
config.background_color = "#0e1a25"  # deep slate

# Palette
START_COLOR = "#29ABCA"
PATH_COLOR  = "#9CDCEB"
FINAL_COLOR = "#a9dc76"
AXIS_COLOR  = "#E6E6E6"
GRID_COLOR  = "#6d7a86"
Y_AXIS_GLOW = "#49A88F"  # inside (horizontal) cues
X_AXIS_GLOW = "#8F3931"  # outside (vertical) cues
TEXT_COLOR  = WHITE

# =============================
# Voice & pacing helpers
# =============================
VOICE_TEMPO = 1.00
BASE_PAD    = 0.35
HOLD_PAD    = 0.50

def narr_time(tr, min_rt=0.9, cap=2.2, extra=BASE_PAD):
    """Tie motion to speech without dragging visuals. (CHECKPOINT-3)"""
    d = getattr(tr, "duration", 0.0)
    return max(min_rt, min(d + extra, cap))

# =============================
# Piper SpeechService
# =============================
class PiperService(SpeechService):
    """
    Uses piper.exe to synthesize WAV, then converts to MP3 via bundled ffmpeg.
    (CHECKPOINT-6)
    """
    def __init__(self, piper_path: str, model_path: str, speaker: int | None = None, tempo: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.piper_path = piper_path
        self.model_path = model_path
        self.speaker    = speaker
        self.tempo      = float(tempo)

        if not os.path.exists(self.piper_path):
            raise FileNotFoundError(f"Piper EXE not found: {self.piper_path}")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Piper model not found: {self.model_path}")

        base_dir = os.path.dirname(self.piper_path)
        self.ffmpeg_path = os.path.join(base_dir, "ffmpeg", "bin", "ffmpeg.exe")
        if not os.path.exists(self.ffmpeg_path):
            raise FileNotFoundError("ffmpeg.exe not found at piper_runtime\\ffmpeg\\bin\\ffmpeg.exe")

    def _ffmpeg_atempo_args(self):
        t = self.tempo
        if abs(t - 1.0) < 1e-3:
            return []
        if 0.5 <= t <= 2.0:
            return ["-af", f"atempo={t}"]
        import math
        a = math.sqrt(max(0.01, min(4.0, t)))
        return ["-af", f"atempo={a},atempo={a}"]

    def generate_from_text(self, text: str, cache_dir: str | None = None, path: str | None = None) -> dict:
        cache_dir = cache_dir or self.cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        stem = self.get_audio_basename({"input_text": text, "model": self.model_path})
        wav_path = os.path.join(cache_dir, stem + ".wav")
        mp3_path = os.path.join(cache_dir, stem + ".mp3")

        # 1) Synthesize WAV with Piper
        cmd = [self.piper_path, "--model", self.model_path, "--output_file", wav_path]
        if self.speaker is not None:
            cmd += ["--speaker", str(self.speaker)]
        proc = subprocess.run(cmd, input=text.encode("utf-8"), capture_output=True)
        if proc.returncode != 0:
            raise RuntimeError(
                f"Piper failed (exit {proc.returncode}).\n"
                f"Cmd: {' '.join(cmd)}\nSTDOUT:\n{proc.stdout.decode(errors='ignore')}\n"
                f"STDERR:\n{proc.stderr.decode(errors='ignore')}\n"
                "If you see 0xC0000135, install the MSVC 2015–2022 Redistributable (x64 & x86)."
            )

        # 2) WAV -> MP3 for accurate duration
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
        ff = [self.ffmpeg_path, "-y", "-v", "error", "-i", wav_path] + self._ffmpeg_atempo_args() + \
             ["-acodec", "libmp3lame", "-b:a", "192k", mp3_path]
        proc2 = subprocess.run(ff, capture_output=True)
        if proc2.returncode != 0 or not os.path.exists(mp3_path):
            raise RuntimeError(
                "ffmpeg failed converting WAV->MP3.\n"
                f"STDOUT:\n{proc2.stdout.decode(errors='ignore')}\n"
                f"STDERR:\n{proc2.stderr.decode(errors='ignore')}"
            )

        rel_mp3 = os.path.relpath(mp3_path, cache_dir).replace("\\", "/")
        return {"path": mp3_path, "original_audio": rel_mp3, "input_data": {"input_text": text}}

# =============================
# Teacher-style VO text
# =============================
VO = {
    "theory": (
        "Here is the transformation framework. "
        "For a new function g of x equals a times f of k times x minus d, plus c, "
        "the point mapping is x prime equals x over k plus d, and y prime equals a y plus c. "
        "Inside changes act horizontally on x; outside changes act vertically on y. "
        "A negative a reflects across the x axis, and a negative k reflects across the y axis."
    ),
    "announce_problem": (
        "Now, the problem. We are given g of x equals negative f of minus x minus one, plus three, "
        "and the point one, negative two lies on the graph of f. We will find its image under g."
    ),
    "plane": "Let us move to the coordinate plane and track the image step by step.",
    "start": "We begin at the point one, negative two on f.",
    "y_reflect": "First, reflect across the y axis. The x coordinate changes sign; y is unchanged.",
    "left_shift": "Next, translate one unit to the left. Only the x coordinate decreases by one.",
    "x_reflect": "Now, reflect across the x axis. The y coordinate changes sign; x is unchanged.",
    "up_shift": "Finally, translate upward by three units. Only the y coordinate increases by three.",
    "wrap": "Collecting all steps, the resulting point is negative two, five."
}

# =============================
# Utilities (layout & highlighting)
# =============================
def whiteboard(rect_pad=0.55) -> tuple[RoundedRectangle, RoundedRectangle]:
    """Large white board with border. (CHECKPOINT-1,9)"""
    board = RoundedRectangle(corner_radius=0.4, stroke_width=3, color=GREY_B, fill_color=WHITE, fill_opacity=1)
    board.set_width(config.frame_width - 2*rect_pad)
    board.set_height(config.frame_height - 1.2)
    board.to_edge(UP, buff=0.35)
    frame = RoundedRectangle(corner_radius=0.4, stroke_width=5, color=GREY_E)
    frame.match_width(board).match_height(board).move_to(board)
    return board, frame

def safe_color_by_tex(m: Mobject, tokens: list[str], color: ManimColor) -> Mobject:
    """Highlight using Manim (not LaTeX \color). (CHECKPOINT-7)"""
    for t in tokens:
        try:
            m.set_color_by_tex(t, color)
        except Exception:
            pass
    return m

def note_stack(x_right: float, top_y: float, *items: Mobject) -> VGroup:
    """Right-column stack with airy spacing; no background panel. (CHECKPOINT-2,4)"""
    y = top_y
    blocks = []
    for it in items:
        it = it.copy().scale(0.9)
        it.move_to([x_right, y, 0]).align_to([x_right, y, 0], LEFT)
        it.set_z_index(3)
        pad = 0.16
        rr = RoundedRectangle(corner_radius=0.14, stroke_width=1.2, color=GREY_E)
        rr.set_width(it.width + 2*pad)
        rr.set_height(it.height + 2*pad)
        rr.move_to(it)
        group = VGroup(rr, it)
        blocks.append(group)
        y -= (it.height + 0.5)
    return VGroup(*blocks)

# =============================
# Scene
# =============================
class FinalAnimation(VoiceoverScene, Scene):
    LEFT_W  = 6.2   # reserved width for the plane
    RIGHT_X = 2.7   # x coord where notes are placed (screen coords)
    TOP_Y   = 2.8

    def setup(self):
        # --- Voice
        base_dir  = os.path.dirname(__file__)
        rt        = os.path.join(base_dir, "piper_runtime")
        piper_exe = os.path.join(rt, "piper.exe")
        models = sorted(glob.glob(os.path.join(rt, "*.onnx")))
        if not models:
            raise FileNotFoundError("Place a Piper voice model .onnx in piper_runtime")
        self.set_speech_service(PiperService(piper_exe, models[0], tempo=VOICE_TEMPO))

        # --- Graph (left column)
        self.axes = Axes(
            x_range=[-4, 4, 1],  # CHECKPOINT-2: x-range fixed
            y_range=[-4, 7, 1],
            x_length=self.LEFT_W,
            y_length=6.3,
            axis_config={"color": AXIS_COLOR, "stroke_width": 2}
        )
        self.grid = NumberPlane(
            x_range=[-4, 4, 1], y_range=[-4, 7, 1],
            x_length=self.LEFT_W, y_length=6.3,
            background_line_style={
                "stroke_color": GRID_COLOR,
                "stroke_width": 1,
                "stroke_opacity": 0.45,
            }
        )
        self.coords = self.axes.add_coordinates(font_size=24, num_decimal_places=0)
        self.graph_group = VGroup(self.grid, self.axes, self.coords).to_edge(LEFT, buff=0.5)
        self.graph_group.set_z_index(1)

    # ---------------- Whiteboard (its own clean segment) ----------------
    def whiteboard_intro(self):
        board, frame = whiteboard(rect_pad=0.55)
        title  = Tex(r"\textbf{Transformation Map (Function $\to$ Points)}", font_size=56, color=BLACK).next_to(board.get_top(), DOWN, buff=0.6)
        g_eq   = MathTex(r"g(x)=a\,f\!\big(k(x-d)\big)+c", color=BLACK).scale(1.2).next_to(title, DOWN, buff=0.65)
        mapping= MathTex(r"x'=\frac{x}{k}+d,\quad y'=a\,y+c", color=BLACK).scale(1.1).next_to(g_eq, DOWN, buff=0.6)
        bullets= VGroup(
            Tex(r"Inside $\Rightarrow$ horizontal, acts on $x$", color=BLACK),
            Tex(r"Outside $\Rightarrow$ vertical, acts on $y$", color=BLACK),
            Tex(r"$a<0$: reflect across $x$-axis,\;\; $k<0$: reflect across $y$-axis", color=BLACK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28).next_to(mapping, DOWN, buff=0.55).align_to(g_eq, LEFT)

        board_grp = VGroup(board, frame, title, g_eq, mapping, bullets).set_z_index(5)

        # Enter board
        with self.voiceover(text=VO["theory"]) as tr:
            self.play(FadeIn(board, shift=UP*0.1), Create(frame), run_time=0.6)
            self.play(Write(title), run_time=0.5)
            self.play(LaggedStart(Write(g_eq), Write(mapping), lag_ratio=0.25), run_time=1.0)
            self.play(LaggedStart(*[Write(b) for b in bullets], lag_ratio=0.2), run_time=narr_time(tr, min_rt=1.2, cap=3.2))
            self.wait(0.3)

        # Erase ONLY the theory bullets with a natural hand-wave; keep title + equations
        eraser = RoundedRectangle(width=2.6, height=1.0, corner_radius=0.2,
                                  fill_color=WHITE, fill_opacity=1.0, stroke_width=0).set_z_index(6)

        # Path across the bullet area (serpentine)
        path = VMobject()
        p_right = bullets.get_right() + RIGHT*0.2
        p_left  = bullets.get_left()  + LEFT*0.2
        path.set_points_as_corners([p_right, p_left, p_right + UP*0.6, p_left + UP*0.6, p_right + UP*1.2])

        # Fade bullets by alpha while moving eraser along path (FIX: remove alpha-parameter updater)
        def fade_bullets(mob, alpha):
            for b in bullets:
                b.set_opacity(max(0.0, 1.0 - 1.6*alpha))

        self.add(eraser)
        self.play(
            MoveAlongPath(eraser, path),
            UpdateFromAlphaFunc(bullets, fade_bullets),
            run_time=1.3
        )
        self.remove(eraser)
        self.play(FadeOut(bullets), run_time=0.3)

        # State the concrete problem after erase (still on whiteboard)
        problem = VGroup(
            Tex(r"\textbf{Problem:}", color=BLACK),
            MathTex(r"g(x)=-\,f(-x-1)+3", color=BLACK),
            Tex(r"Given point on $f$: $(1,-2)$", color=BLACK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28).next_to(mapping, DOWN, buff=0.55).align_to(g_eq, LEFT)

        with self.voiceover(text=VO["announce_problem"]) as tr:
            self.play(Write(problem), run_time=narr_time(tr, min_rt=1.0, cap=2.6))

        # Clean exit of board
        self.play(FadeOut(VGroup(problem, title, g_eq, mapping, frame, board)), run_time=0.6)

    # ---------------- Main construct ----------------
    def construct(self):
        # 1) Whiteboard segment
        self.whiteboard_intro()

        # 2) Stage: graph on left, notes on right
        with self.voiceover(text=VO["plane"]) as tr:
            self.play(FadeIn(self.graph_group, shift=UP*0.1), run_time=narr_time(tr, min_rt=0.8, cap=1.2))

        # Right notes (no background panel; clean callouts) (CHECKPOINT-2)
        gx      = MathTex(r"g(x)=-\,f(-x-1)+3", color=TEXT_COLOR).scale(0.95)
        mapping = MathTex(r"x'=\frac{x}{k}+d,\;\;y'=a\,y+c", color=TEXT_COLOR).scale(0.9)
        given   = MathTex(r"(1,-2)\ \text{ on }f", color=TEXT_COLOR).scale(0.9)
        right_column = note_stack(2.7, 2.8, gx, mapping, given)
        self.play(FadeIn(right_column, shift=UP*0.1), run_time=0.6)

        # Top caption for steps
        caption = Tex("", color=TEXT_COLOR).to_edge(UP, buff=0.35).set_z_index(4)
        self.add(caption)

        # Start point
        with self.voiceover(text=VO["start"]) as tr:
            point = Dot(self.axes.c2p(1, -2), color=START_COLOR, radius=0.09)
            label = MathTex(r"(1,-2)", color=TEXT_COLOR).scale(0.9).next_to(point, DR, buff=0.18)
            self.play(FadeIn(point, scale=0.5), Write(label), run_time=narr_time(tr))
        self.wait(HOLD_PAD)

        # Helpers to recolor tokens safely (CHECKPOINT-7)
        def recolor_gx(tokens: list[str], color: ManimColor):
            temp = gx.copy()
            safe_color_by_tex(temp, tokens, color)
            self.play(Transform(gx, temp), run_time=0.35)

        def recolor_map(tokens: list[str], color: ManimColor):
            temp = mapping.copy()
            safe_color_by_tex(temp, tokens, color)
            self.play(Transform(mapping, temp), run_time=0.35)

        # 3) Reflect across y-axis
        with self.voiceover(text=VO["y_reflect"]) as tr:
            self.play(Transform(caption, Tex("Reflect across the $y$-axis", color=TEXT_COLOR).move_to(caption)), run_time=0.3)
            recolor_gx(["-x-1", "-x", "(-x-1)"], Y_AXIS_GLOW)
            self.grid.save_state()
            y_reflect = np.array([[-1, 0], [0, 1]])
            target = self.axes.c2p(-1, -2)
            new_lab = MathTex(r"(-1,-2)", color=TEXT_COLOR).scale(0.9).next_to(target, DL, buff=0.18)
            self.play(
                ApplyMatrix(y_reflect, self.grid),
                point.animate.move_to(target),
                Transform(label, new_lab),
                run_time=narr_time(tr, cap=1.8)
            )
            recolor_gx(["-x-1", "-x", "(-x-1)"], TEXT_COLOR)
        self.grid.restore()
        self.wait(HOLD_PAD*0.8)

        # 4) Shift left by 1
        with self.voiceover(text=VO["left_shift"]) as tr:
            self.play(Transform(caption, Tex("Translate left by $1$", color=TEXT_COLOR).move_to(caption)), run_time=0.3)
            recolor_map(["+d", "d"], Y_AXIS_GLOW)
            shift_vec = self.axes.c2p(-1,0) - self.axes.c2p(0,0)
            target = self.axes.c2p(-2, -2)
            new_lab = MathTex(r"(-2,-2)", color=TEXT_COLOR).scale(0.9).next_to(target, DL, buff=0.18)
            self.play(point.animate.shift(shift_vec), Transform(label, new_lab), run_time=narr_time(tr, cap=1.6))
            recolor_map(["+d", "d"], TEXT_COLOR)
        self.wait(HOLD_PAD*0.8)

        # 5) Reflect across x-axis
        with self.voiceover(text=VO["x_reflect"]) as tr:
            self.play(Transform(caption, Tex("Reflect across the $x$-axis", color=TEXT_COLOR).move_to(caption)), run_time=0.3)
            recolor_map(["a"], X_AXIS_GLOW)
            self.grid.save_state()
            x_reflect = np.array([[1, 0], [0, -1]])
            target = self.axes.c2p(-2, 2)
            new_lab = MathTex(r"(-2,2)", color=TEXT_COLOR).scale(0.9).next_to(target, UL, buff=0.18)
            self.play(
                ApplyMatrix(x_reflect, self.grid),
                point.animate.move_to(target),
                Transform(label, new_lab),
                run_time=narr_time(tr, cap=1.8)
            )
            recolor_map(["a"], TEXT_COLOR)
        self.grid.restore()
        self.wait(HOLD_PAD*0.8)

        # 6) Shift up by 3
        with self.voiceover(text=VO["up_shift"]) as tr:
            self.play(Transform(caption, Tex("Translate up by $3$", color=TEXT_COLOR).move_to(caption)), run_time=0.3)
            recolor_map(["+c", "c"], FINAL_COLOR)
            shift_vec = self.axes.c2p(0,3) - self.axes.c2p(0,0)
            target = self.axes.c2p(-2, 5)
            new_lab = MathTex(r"(-2,5)", color=FINAL_COLOR).scale(1.0).next_to(target, UL, buff=0.2)
            self.play(point.animate.shift(shift_vec), Transform(label, new_lab), run_time=narr_time(tr, cap=1.8))
            self.play(point.animate.set_color(FINAL_COLOR), run_time=0.25)
            recolor_map(["+c", "c"], TEXT_COLOR)
        self.wait(HOLD_PAD)

        # 7) Wrap-up
        with self.voiceover(text=VO["wrap"]) as tr:
            self.play(Transform(caption, Tex(r"Result: $(-2,\,5)$", color=FINAL_COLOR).move_to(caption)), run_time=0.4)
            pts = [self.axes.c2p(1,-2), self.axes.c2p(-1,-2), self.axes.c2p(-2,-2), self.axes.c2p(-2,2), self.axes.c2p(-2,5)]
            path = VMobject(color=PATH_COLOR, stroke_width=3).set_points_as_corners(pts)
            dots = VGroup(*[Dot(p, radius=0.06, color=PATH_COLOR) for p in pts]).set_z_index(3)
            dots[0].set_color(START_COLOR)
            dots[-1].set_color(FINAL_COLOR).scale(1.3)
            self.play(Create(path), LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.15),
                      run_time=narr_time(tr, min_rt=1.2, cap=2.4, extra=0.5))
        self.wait(0.7)
