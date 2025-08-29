# config.py

from manim import *

# =============================
# Global Settings
# =============================
USE_PIPER = True
RANDOM_SEED = 7

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