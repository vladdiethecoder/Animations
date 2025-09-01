# PR Checklist — Policy Compliance

This checklist ensures all commits respect the project’s workflow.  
Reviewers should confirm each box before merging.

---

## Gate 0 — Sync
- [ ] `/docs/CHECKPOINTS.md` is in sync with code headers (Active only).
- [ ] Sync plan executed if mismatch was found.

## Planning
- [ ] Request Brief & Parameter Matrix attached.
- [ ] Candidates A/B/C, Second-Thought critique, Decision Matrix, and Pick included.
- [ ] Pass structure defined (Pass 1 = planning only, Pass 2 = implementation).

## Research
- [ ] Sources ≥5 (≥2 forums, ≥1 official), labeled & timestamped, pinned to v0.19.0.
- [ ] Deep Research dossier created if ≥2 attempts failed.

## Documentation
- [ ] `CODEBASEDOCUMENTATION.md` updated or cited for any classes/objects/functions touched.
- [ ] Extended guidelines (`WORKFLOW_EXTENDED.md`) applied where relevant.

## Code & Checkpoints
- [ ] Snippet patch provided (diff/anchor) with clear Instructions Block.
- [ ] Efficiency Gauge reported (lines delta, runtime delta, checkpoint pass rate, regressions, smoothness, compile scope).
- [ ] Rotation check performed — header decluttered as needed.
- [ ] Regression Guard confirms all Active checkpoints preserved.
- [ ] Rollback snippet provided.

## Drift & Overrides
- [ ] Drift Score (%) computed, drift justified if >5%, repaired version provided.
- [ ] Any deviations from hard rules explicitly stated with justification.

---
