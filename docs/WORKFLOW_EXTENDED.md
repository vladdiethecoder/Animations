# WORKFLOW_EXTENDED.md — Soft Guidelines & Best Practices

These are **soft rules**. They guide quality but are not hard guardrails.  
The model may deviate if necessary — but should explain why.

---

## Style & Clarity
- Favor **legibility over cleverness**: simple code, clear naming, minimal nesting.
- Use comments only when they add insight (not to restate obvious things).
- Keep functions focused: one responsibility per method.
- Prefer explicit variable names (avoid single-letter unless math-heavy context).

## Explanations
- Be concise. Prioritize what changed and why, not a long essay.
- Show reasoning when multiple solutions exist, but don’t bloat answers with repetition.
- Only cite research sources when they truly support a decision.

## Collaboration Notes
- Avoid “compliance at all costs.” If breaking a rule improves quality, call it out explicitly.
- Prefer snippets (diffs) but allow full file output if the edit is inseparable.
- Ask for clarification if user input is ambiguous instead of guessing.

## Quality Override Reminder
If sticking to rules would **reduce accuracy, clarity, or usefulness**,  
you may deviate — but always state:
> “Deviation: [rule broken]. Reason: [why better].”

---
