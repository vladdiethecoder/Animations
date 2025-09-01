# config.py
# [CHECKPOINT-1..5 Active; Mirrors CHECKPOINTS.md]
# Project-wide constants (Manim CE v0.19.0)

from __future__ import annotations
from manim import *

# =============================
# Global Settings
# =============================
USE_PIPER = True
RANDOM_SEED = 7

# ---- Layout anchors (scene coordinates) ----
# WHY: Hard coordinates prevent drift (FM-3, FM-8) vs to_edge()/to_corner() dynamics.
ANCHOR_STEPS = (5.3, -3.0, 0)       # bottom-right area for StepsPanel
ANCHOR_RIGHT_PANE = (5.3, 1.5, 0)   # right-side transform mirror
PANEL_WIDTH = 5.5
PANEL_PADDING = 0.25
LINE_SPACING = 0.5

# ---- Styling ----
FONT_SIZE_MAIN = 36         # >=28px @1080p (Checkpoint-2 Readability)
FONT_SIZE_STEPS = 30
FONT_SIZE_RIGHT = 32

# Highlight style (Checkpoint-2; FM-4 z-order handled in controller)
HIGHLIGHT_COLOR = "#00D1FF"
HIGHLIGHT_STROKE = 4
HIGHLIGHT_FILL_OPACITY = 0.0
HIGHLIGHT_BUFF = 0.08
HIGHLIGHT_Z = 15

# Determinism defaults (Checkpoint-3)
SEED = 7
FPS = 30
RESOLUTION = (1920, 1080)

# Manim global settings (for Manim v0.18.1)
config.quality = "example_quality"
config.frame_rate = 30
config.pixel_height = 1080
config.pixel_width = 1920
config.background_color = "#0e1a25"

# =============================
# Color Palette
# =============================
PALETTE = {
    "start": "#29ABCA",
    "path": "#9CDCEB",
    "final": "#a9dc76",
    "axis": "#E6E6E6",
    "grid": "#6d7a86",
    "text": WHITE,
}

# =============================
# Animation Pacing
# =============================
PACING = {
    "voice_tempo": 1.00,
    "base_pad": 0.35,
    "hold_pad": 0.50,
}

# =============================
# Voiceover Content (VO)
# =============================
VO = {
    "theory_intro": "Here is the transformation map from functions to points...",
    "theory_x":     "First, x prime equals x over k plus d. This comes from the horizontal parameters...",
    "theory_y":     "Next, y prime equals a y plus c. These are the vertical parameters...",
    "theory_bullets": "Inside operations act on x; outside operations act on y; reflections occur when a or k are negative.",
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