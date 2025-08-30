# WORKFLOW (Operating Procedure)

This is the **process contract** the assistant must follow. No coding begins until the gates pass.

## Gate 0 — Read & Sync (HARD STOP if not synced)
1) Read: `WORKFLOW.md`, `CHECKPOINTS.md`, `CODEBASEDOCUMENTATION.md`.  
2) Compare code header snapshot to `CHECKPOINTS.md (Active)`.  
3) If mismatch → propose a **sync plan**; get approval; update headers. **No code yet.**

## Pass Structure (Plan before code)
- **Pass 1 — Planning Only**
  - Produce **Request Brief** and **Parameter Matrix**.
  - Cite relevant entries from `CODEBASEDOCUMENTATION.md`.
  - Propose **Candidates A/B/C**, do **Second-Thought** critique, score in **Decision Matrix**, and **pick**.
  - Define smallest **compile scope** to validate (static/DEBUG/micro-render).
  - Ask: *“Is this the correct breakdown?”*  
  - **Do NOT write code**.

- **Pass 2 — Implementation**
  - Apply **Snippet-Only Editing** (unified diff or anchor-based) with an **Instructions Block** and **Rollback**.
  - Validate against **Active Checkpoints** and **Failure Modes**.
  - Report the **Efficiency Gauge**.

> Very large features → decompose into **sub-features** first.

## Snippet-Only Editing Policy
- Prefer patches over full files.
- Always include: File(s) | Where | Why (link Checkpoints/FMs) | How to apply | Rollback.
- Provide **Variant Beam** when not converged (Minimal vs Orthogonal).

## Parametric Scope & Decision Protocol
- **Request Brief:** Objective, Inputs, Assumptions (to verify), Constraints, Non-Goals, Edge Cases (≥3), Acceptance Criteria, Affected Files.
- **Parameter Matrix:** parameter | type | target | limits | notes | success metric.
- **Candidates A/B/C** → **Second-Thought** critique → **Decision Matrix** → **Pick & switch criteria**.

## Research Policy
- **Standard:** ≥5 sources (≥2 forums, ≥1 official, ≥2 blogs/tutorials), label type, timestamp; prefer ≤12 months; pin to **v0.19.0**.
- **Deep Research Trigger:** after **2 failed attempts** or repeated guard failures.
  - **Deep Research Requirements:** ≥8 sources (≥3 forums, ≥2 official), Minimal Reproducible Example, experiment matrix, 3+ strategies, Patch Plan, Fallback, Rollback, upstream issues/PRs, go/no-go.

## Bug Fixing Workflow
- Read **@README.md** first for context.
- Perform discovery + research; report findings **in English** (no code).
- After approval → proceed with snippet patch.

## GitHub Connector (if enabled)
- Allow referencing repo files/paths/README directly in planning/implementation.
- Cite file paths in snippets and documentation capture.

## Response Format (every task)
I) Request Brief & Parameter Matrix  
J) Candidates, Second-Thought, Decision Matrix & Pick  
A) Checkpoint Header (Active + Archive snapshot)  
B) Snippet Patch or Full Script (v0.19.0-compatible)  
C) Regression Guard (checkpoint-by-checkpoint)  
D) Risk & Mitigation Map (FMs)  
E) Self-Test (if DEBUG=True)  
F) Rollback Snippet  
G) Research Section (sources labeled, version-pinned)  
H) Documentation References (`CODEBASEDOCUMENTATION.md`)  
I) Deep Research Dossier (if triggered)
