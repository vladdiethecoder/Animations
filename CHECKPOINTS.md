# CHECKPOINTS (Source of Truth)

Target stack: **Manim CE v0.19.0**  
Scope: Non-compiled guardrails for behavior, style, and invariants.

## Active (keep 5–8 max; never renumber existing IDs)
# [CHECKPOINT-1 | STATUS: Active | Title: Regression Guard | Must-Preserve: preserve prior fixes; minimal-diff edits; rollback ready | Notes: confirm after each change]
# [CHECKPOINT-2 | STATUS: Active | Title: Readability & Accessibility | Must-Preserve: ≥28px labels at 1080p, high contrast, aligned math | Notes: academic style]
# [CHECKPOINT-3 | STATUS: Active | Title: Determinism/Consistency | Must-Preserve: fixed seed; fps/resolution pinned; stable timings | Notes: use _set_determinism()]
# [CHECKPOINT-4 | STATUS: Active | Title: Camera Behavior | Must-Preserve: tasteful zoom/pan; no abrupt jumps | Notes: ties to FM-8]
# [CHECKPOINT-5 | STATUS: Active | Title: Eraser Effect Integrity | Must-Preserve: natural wipe; no background lightening; no jitter | Notes: FM-1]

> Header snapshots in code files **must mirror only the Active list** above.

## Rotation & Archival Policy
- Keep **5–8** Active; merge related items.
- Permanent Active: **C-1 Regression Guard, C-2 Readability, C-3 Determinism**.
- Superseded/Deprecated → move to **Archive** with timestamps and cross-links.
- Each PR must state: *“Rotation check performed — header decluttered as needed.”*

## Failure-Mode Catalog (reference in every change)
- **FM-1:** Eraser artifacts (ghosting/lightening)
- **FM-2:** Lingering updaters
- **FM-3:** Timing regressions
- **FM-4:** Z-order/stacking issues
- **FM-5:** Readability/contrast/font-size
- **FM-6:** API mismatches vs v0.19.0
- **FM-7:** State leakage across scenes
- **FM-8:** Camera motion abruptness

## Version Guard (Manim CE v0.19.0)
- Prefer: `MathTex`, `Text`, `VGroup`, `always_redraw`, `set_z_index`, `rate_functions`.
- Avoid deprecated/removed calls; pin kwargs to 0.19.0.

## Archive (examples)
# [CHECKPOINT-6 | STATUS: Superseded (YYYY-MM-DD) | Title: Old pacing tweak | Notes: merged into C-3 Determinism]
# [CHECKPOINT-7 | STATUS: Deprecated (YYYY-MM-DD) | Title: Temporary hotfix | Notes: obsolete after mask rewrite]
