# -*- coding: utf-8 -*-
# ==============================================================================
# --- ACTIVE ---
# [CHECKPOINT-A | STATUS: Active | Title: Determinism & Consistency | Must-Preserve: random.seed(7), config settings | Notes: Ensures reproducible output.]
# [CHECKPOINT-B | STATUS: Active | Title: Regression Guard & Debugging | Must-Preserve: DEBUG flag, _guard_* functions | Notes: Core infrastructure for testing and validation.]
# [CHECKPOINT-D | STATUS: Active | Title: Whiteboard Component | Must-Preserve: Dynamic sizing, z-index layering, elegant text dissolve | Notes: Governs the entire whiteboard intro sequence.]
# [CHECKPOINT-E | STATUS: Active | Title: Layout & Readability | Must-Preserve: Static grid, responsive right column, caption below graph, robust text updates | Notes: Umbrella for all visual layout, now using robust text updates.]
# [CHECKPOINT-F | STATUS: Active | Title: Piper Voiceover Service | Must-Preserve: PiperService class, ffmpeg command, USE_PIPER flag | Notes: Manages all text-to-speech functionality.]
# [CHECKPOINT-G | STATUS: Active | Title: Animation Pacing & Aesthetics | Must-Preserve: narr_time(), smoothed final path | Notes: Governs the timing and visual flow of the animation.]
# [CHECKPOINT-H | STATUS: Active | Title: Robust UI Positioning | Must-Preserve: caption_placeholder logic | Notes: Ensures UI elements like the caption have stable, predictable positions.]
# ==============================================================================
# --- ARCHIVE ---
# [CHECKPOINT-C | STATUS: Superseded (2025-08-29) | Notes: Merged into C-E.]
# [CHECKPOINT-1 | STATUS: Superseded (2025-08-29) | Notes: Merged into C-D.]
# [CHECKPOINT-9 | STATUS: Superseded (2025-08-29) | Notes: Merged into C-D.]
# [CHECKPOINT-13 | STATUS: Superseded (2025-08-29) | Notes: Merged into C-D.]
# [CHECKPOINT-15 | STATUS: Superseded (2025-08-29) | Notes: Merged into C-D.]
# [CHECKPOINT-16 | STATUS: Archived Hotfix (2025-08-29) | Notes: Merged into C-D.]
# [CHECKPOINT-2 | STATUS: Superseded (2025-08-29) | Notes: Merged into C-E.]
# [CHECKPOINT-4 | STATUS: Superseded (2025-08-29) | Notes: Merged into C-E.]
# [CHECKPOINT-17 | STATUS: Superseded (2025-08-29) | Notes: Merged into C-E.]
# [CHECKPOINT-18 | STATUS: Superseded (2025-08-29) | Notes: Merged into C-E.]
# [CHECKPOINT-19 | STATUS: Superseded (2025-08-29) | Notes: Merged into C-E.]
# [CHECKPOINT-21 | STATUS: Superseded (2025-08-29) | Notes: Merged into C-E.]
# [CHECKPOINT-22 | STATUS: Superseded (2025-08-29) | Notes: Merged into C-E.]
# [CHECKPOINT-23 | STATUS: Superseded (2025-08-29) | Notes: Merged into C-E.]
# [CHECKPOINT-24 | STATUS: Superseded (2025-08-29) | Notes: Merged into C-E.]
# [CHECKPOINT-5 | STATUS: Deprecated (2025-08-29)]
# [CHECKPOINT-8 | STATUS: Deprecated (2025-08-29)]
# [CHECKPOINT-12 | STATUS: Archived Hotfix (2025-08-29) | Notes: Merged into C-F.]
# [CHECKPOINT-14 | STATUS: Archived Hotfix (2025-08-29) | Notes: Merged into C-F.]
# ==============================================================================

from __future__ import annotations
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.base import SpeechService
import os, subprocess, glob, numpy as np, random
from contextlib import nullcontext

# =============================
# Debug Harness (CHECKPOINT-B)
# =============================
DEBUG = False

def _guard_label_readable(label, min_px=28):
    """Ensures a label's rendered height is above a minimum pixel threshold."""
    assert label.height * 1080 >= min_px, f"[GUARD] Too small: {label}"

def _guard_no_lingering_updaters(mobj):
    """Checks that a mobject has no updaters attached after an animation."""
    assert len(mobj.updaters) == 0, f"[GUARD] Lingering updaters: {mobj}"

def _set_determinism():
    """Sets global seeds and configuration for reproducible animations."""
    from manim.utils.random import seed
    seed(42)
    config.frame_rate = 30
    config.pixel_height = 1080
    config.pixel_width = 1920

if DEBUG:
    _set_determinism()

# =============================
# Globals / Config (CHECKPOINT-A)
# =============================
USE_PIPER = True
random.seed(7)
config.quality = "example_quality"
config.frame_rate = 30
config.background_color = "#0e1a25"  # deep slate

# Palette
START_COLOR = "#29ABCA"
PATH_COLOR  = "#9CDCEB"
FINAL_COLOR = "#a9dc76"
AXIS_COLOR  = "#E6E6E6"
GRID_COLOR  = "#6d7a86"
Y_AXIS_GLOW = "#49A88F"
X_AXIS_GLOW = "#8F3931"
TEXT_COLOR  = WHITE

# =============================
# Voice & pacing helpers (CHECKPOINT-G)
# =============================
VOICE_TEMPO = 1.00
BASE_PAD    = 0.35
HOLD_PAD    = 0.50

def narr_time(tr, min_rt=0.9, cap=2.2, extra=BASE_PAD):
    """Tie motion to speech without dragging visuals."""
    d = getattr(tr, "duration", 0.0)
    return max(min_rt, min(d + extra, cap))

# =============================
# Piper SpeechService (CHECKPOINT-F)
# =============================
class PiperService(SpeechService):
    """Uses piper.exe to synthesize WAV, then converts to MP3 via bundled ffmpeg."""
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
        if abs(t - 1.0) < 1e-3: return []
        if 0.5 <= t <= 2.0: return ["-af", f"atempo={t}"]
        import math
        a = math.sqrt(max(0.01, min(4.0, t)))
        return ["-af", f"atempo={a},atempo={a}"]

    def generate_from_text(self, text: str, cache_dir: str | None = None, path: str | None = None) -> dict:
        cache_dir = cache_dir or self.cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        stem = self.get_audio_basename({"input_text": text, "model": self.model_path})
        wav_path = os.path.join(cache_dir, stem + ".wav")
        mp3_path = os.path.join(cache_dir, stem + ".mp3")

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

        if os.path.exists(mp3_path): os.remove(mp3_path)
        
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
# Voiceover Content
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
# Utilities (CHECKPOINT-E)
# =============================
def whiteboard(
    width: float, height: float, rect_pad: float = 0.55
) -> tuple[RoundedRectangle, RoundedRectangle]:
    """Large white board with border."""
    board = RoundedRectangle(
        width=width, height=height, corner_radius=0.4,
        stroke_width=3, color=GREY_B, fill_color=WHITE, fill_opacity=1,
    )
    frame = RoundedRectangle(corner_radius=0.4, stroke_width=5, color=GREY_E)
    frame.match_width(board).match_height(board).move_to(board)
    return board, frame

def safe_color_by_tex(m: Mobject, tokens: list[str], color: ManimColor) -> Mobject:
    r"""Highlight using Manim (not LaTeX \color)."""
    for t in tokens:
        try:
            m.set_color_by_tex(t, color)
        except Exception: pass
    return m

def note_stack(*items: Mobject) -> VGroup:
    """Stacks items vertically with left alignment and airy spacing."""
    group = VGroup()
    for item in items:
        group.add(item.copy().scale(0.95))
    group.arrange(DOWN, aligned_edge=LEFT, buff=0.7)
    return group

# =============================
# Scene
# =============================
class FinalAnimation(VoiceoverScene, Scene):
    LEFT_W  = 6.2

    def setup(self):
        if USE_PIPER:
            base_dir  = os.path.dirname(__file__)
            rt        = os.path.join(base_dir, "piper_runtime")
            piper_exe = os.path.join(rt, "piper.exe")
            models = sorted(glob.glob(os.path.join(rt, "*.onnx")))
            if not models:
                raise FileNotFoundError("Place a Piper voice model .onnx in piper_runtime")
            self.set_speech_service(PiperService(piper_exe, models[0], tempo=VOICE_TEMPO))

        # --- Graph (CHECKPOINT-E)
        self.axes = Axes(
            x_range=[-4, 4, 1], y_range=[-4, 7, 1], x_length=self.LEFT_W, y_length=6.3,
            axis_config={"color": AXIS_COLOR, "stroke_width": 2}
        )
        self.grid = NumberPlane(
            x_range=[-4, 4, 1], y_range=[-4, 7, 1], x_length=self.LEFT_W, y_length=6.3,
            background_line_style={"stroke_color": GRID_COLOR, "stroke_width": 1, "stroke_opacity": 0.45}
        )
        self.coords = self.axes.add_coordinates(font_size=24, num_decimal_places=0)
        self.graph_group = VGroup(self.grid, self.axes, self.coords).to_edge(LEFT, buff=0.5).set_z_index(1)

    # --- Whiteboard Sequence (CHECKPOINT-D)
    def whiteboard_intro(self):
        title  = Tex(r"\textbf{Transformation Map (Function $\to$ Points)}", font_size=56, color=BLACK)
        g_eq   = MathTex(r"g(x)=a\,f\!\big(k(x-d)\big)+c", color=BLACK).scale(1.2)
        mapping= MathTex(r"x'=\frac{x}{k}+d,\quad y'=a\,y+c", color=BLACK).scale(1.1)
        
        bullets= VGroup(
            Tex(r"Inside $\Rightarrow$ horizontal, acts on $x$", color=BLACK),
            Tex(r"Outside $\Rightarrow$ vertical, acts on $y$", color=BLACK),
            Tex(r"$a<0 \Rightarrow$ reflect across $x$-axis", color=BLACK),
            Tex(r"$k<0 \Rightarrow$ reflect across $y$-axis", color=BLACK),
        ).scale(0.9).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        
        theory_content = VGroup(title, g_eq, mapping, bullets).arrange(DOWN, buff=0.5)

        board_width = config.frame_width - 2 * 0.55
        board_height = theory_content.height + 1.2
        board, frame = whiteboard(width=board_width, height=board_height)

        whiteboard_group = VGroup(board, frame, theory_content).to_edge(UP, buff=0.35).set_z_index(5)

        with self.voiceover(text=VO["theory"]) if USE_PIPER else nullcontext() as tr:
            self.play(FadeIn(board, shift=UP*0.1), Create(frame), run_time=0.6)
            self.play(Write(title), run_time=0.5)
            self.play(LaggedStart(Write(g_eq), Write(mapping), lag_ratio=0.25), run_time=1.0)
            rt = narr_time(tr, min_rt=1.2, cap=3.2) if USE_PIPER else 1.2
            self.play(LaggedStart(*[Write(b) for b in bullets], lag_ratio=0.2), run_time=rt)
            self.wait(0.3)

        self.play(
            FadeOut(bullets, scale=0.8, target_position=mapping),
            run_time=1.0
        )
        
        problem = VGroup(
            Tex(r"\textbf{Problem:}", color=BLACK), MathTex(r"g(x)=-\,f(-x-1)+3", color=BLACK),
            Tex(r"Given point on $f$: $(1,-2)$", color=BLACK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28).next_to(mapping, DOWN, buff=0.55).align_to(g_eq, LEFT).set_z_index(6)

        with self.voiceover(text=VO["announce_problem"]) if USE_PIPER else nullcontext() as tr:
            rt = narr_time(tr, min_rt=1.0, cap=2.6) if USE_PIPER else 1.0
            self.play(Write(problem), run_time=rt)

        self.play(FadeOut(VGroup(problem, title, g_eq, mapping, frame, board)), run_time=0.6)

    # --- Main Animation Sequence
    def construct(self):
        self.whiteboard_intro()

        with self.voiceover(text=VO["plane"]) if USE_PIPER else nullcontext() as tr:
            rt = narr_time(tr, min_rt=0.8, cap=1.2) if USE_PIPER else 0.8
            self.play(FadeIn(self.graph_group, shift=UP*0.1), run_time=rt)

        gx      = MathTex(r"g(x)=-\,f(-x-1)+3", color=TEXT_COLOR)
        mapping = MathTex(r"x'=\frac{x}{k}+d,\;\;y'=a\,y+c", color=TEXT_COLOR)
        given   = MathTex(r"(1,-2)\ \text{ on }f", color=TEXT_COLOR)
        
        right_column = note_stack(gx, mapping, given)
        right_edge_x, left_edge_x = config.frame_width / 2, self.graph_group.get_right()[0]
        center_x = left_edge_x + (right_edge_x - left_edge_x) / 2
        right_column.move_to([center_x, 0, 0]).align_to(self.axes, UP)
        self.play(FadeIn(right_column, shift=UP*0.1), run_time=0.6)

        # FIX: Create a stable placeholder for the caption's position. (CHECKPOINT-H)
        caption_placeholder = Mobject()
        caption_placeholder.next_to(self.graph_group, DOWN, buff=0.25)
        caption = Tex("").move_to(caption_placeholder)
        self.add(caption)

        with self.voiceover(text=VO["start"]) if USE_PIPER else nullcontext() as tr:
            point = Dot(self.axes.c2p(1, -2), color=START_COLOR, radius=0.09)
            label = MathTex(r"(1,-2)", color=TEXT_COLOR).scale(0.9).next_to(point, DR, buff=0.18)
            rt = narr_time(tr) if USE_PIPER else 0.9
            self.play(FadeIn(point, scale=0.5), Write(label), run_time=rt)
        self.wait(HOLD_PAD)

        # Robust text update functions
        def update_text(old_mobj, new_text_str, position_mobj, **kwargs):
            text_color = kwargs.pop('color', TEXT_COLOR)
            new_mobj = MathTex(new_text_str, color=text_color, **kwargs).scale(0.9)
            new_mobj.next_to(position_mobj, UL, buff=0.18)
            self.play(FadeOut(old_mobj, scale=0.5), FadeIn(new_mobj, scale=1.5))
            return new_mobj

        def update_caption_text(new_text_str):
            new_caption = Tex(new_text_str, color=TEXT_COLOR)
            max_width = self.graph_group.width - 0.5
            if new_caption.width > max_width:
                new_caption.set_width(max_width)
            # FIX: Move to the stable placeholder's position. (CHECKPOINT-H)
            new_caption.move_to(caption_placeholder)
            self.play(FadeOut(caption), FadeIn(new_caption))
            return new_caption

        # Animation sequence
        with self.voiceover(text=VO["y_reflect"]) if USE_PIPER else nullcontext() as tr:
            caption = update_caption_text("Reflect across the $y$-axis")
            target = self.axes.c2p(-1, -2)
            label = update_text(label, r"(-1,-2)", Dot(target))
            self.play(point.animate.move_to(target), run_time=narr_time(tr, cap=1.8))
        self.wait(HOLD_PAD*0.8)

        with self.voiceover(text=VO["left_shift"]) if USE_PIPER else nullcontext() as tr:
            caption = update_caption_text("Translate left by $1$")
            target = self.axes.c2p(-2, -2)
            shift_vec = self.axes.c2p(-1,0) - self.axes.c2p(0,0)
            label = update_text(label, r"(-2,-2)", Dot(target))
            self.play(point.animate.shift(shift_vec), run_time=narr_time(tr, cap=1.6))
        self.wait(HOLD_PAD*0.8)

        with self.voiceover(text=VO["x_reflect"]) if USE_PIPER else nullcontext() as tr:
            caption = update_caption_text("Reflect across the $x$-axis")
            target = self.axes.c2p(-2, 2)
            label = update_text(label, r"(-2,2)", Dot(target))
            self.play(point.animate.move_to(target), run_time=narr_time(tr, cap=1.8))
        self.wait(HOLD_PAD*0.8)

        with self.voiceover(text=VO["up_shift"]) if USE_PIPER else nullcontext() as tr:
            caption = update_caption_text("Translate up by $3$")
            target = self.axes.c2p(-2, 5)
            shift_vec = self.axes.c2p(0,3) - self.axes.c2p(0,0)
            label = update_text(label, r"(-2,5)", Dot(target), color=FINAL_COLOR)
            label.scale(1.1)
            self.play(point.animate.shift(shift_vec), run_time=narr_time(tr, cap=1.8))
            self.play(point.animate.set_color(FINAL_COLOR), run_time=0.25)
        self.wait(HOLD_PAD)

        with self.voiceover(text=VO["wrap"]) if USE_PIPER else nullcontext() as tr:
            caption = update_caption_text(r"Result: $(-2,\,5)$")
            pts = [self.axes.c2p(1,-2), self.axes.c2p(-1,-2), self.axes.c2p(-2,-2), self.axes.c2p(-2,2), self.axes.c2p(-2,5)]
            path = VMobject(color=PATH_COLOR, stroke_width=3.5).set_points_smoothly(pts)
            dots = VGroup(*[Dot(p, radius=0.06, color=PATH_COLOR) for p in pts]).set_z_index(3)
            dots[0].set_color(START_COLOR)
            dots[-1].set_color(FINAL_COLOR).scale(1.3)
            rt = narr_time(tr, min_rt=1.2, cap=2.4, extra=0.5) if USE_PIPER else 1.2
            self.play(Create(path), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.15), run_time=rt)
        self.wait(0.7)