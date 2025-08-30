# CODEBASE DOCUMENTATION CAPTURE

Purpose: A living index of **class/object/function** guidance used in this project, with links and quick context.  
Use: Check during **Pass 1** planning; cite during **Pass 2** implementation.

> Format for each entry:
> ```
> [Name] — [Context/Usage Notes]
> Source Type: Official | Forum | Blog
> Source: <link>
> Verified: YYYY-MM
> Version Notes: (e.g., Manim CE v0.19.0 specifics, kwargs)
> Caveats: (limits, pitfalls)
> Used In: (file paths / scenes)
> ```

## Entries (examples)
- **Text / MathTex** — label rendering, font scaling, stroke/contrast best practices  
  Source Type: Official  
  Source: <link-to-official-docs>  
  Verified: 2025-08  
  Version Notes: v0.19.0 supports …  
  Caveats: ensure height*1080 ≥ 28 for readability  
  Used In: `scenes/labels.py`

- **set_z_index** — controlling overlay order for masks/labels  
  Source Type: Forum  
  Source: <link-to-reddit-or-discourse>  
  Verified: 2025-08  
  Version Notes: works with …  
  Caveats: z-index only within scene render tree  
  Used In: `scenes/eraser_scene.py`

(Add entries as they’re discovered/used; keep duplicates if they add nuance.)

[MathTex.next_to + Axes.p2c] — Quadrant-aware label placement near points to avoid overlap.
Source Type: Blog/Practice
Source: (internal)
Verified: 2025-08
Version Notes: Manim CE v0.19.0; uses p2c() to read data-space for direction choice.
Caveats: Recompute after each point move; ensure ≥28 px via guard.
Used In: FinalAnimation.point_transformation_sequence
