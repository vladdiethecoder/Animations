# PR Checklist — Policy Compliance

This checklist ensures all contributions respect the project workflow.  
Reviewers must confirm each item before merging.

---

## Gate –1 — Project Acquaintance
- [ ] Parsed `/docs/FILE_INDEX.md` at task start to establish file layout.
- [ ] Confirmed which files are relevant before planning or edits.

## Gate 0 — Sync
- [ ] `/docs/CHECKPOINTS.md` was compared with code headers (Active only).
- [ ] Sync plan executed if mismatch was found (no code changes until resolved).

## Planning (Pass 1 — no code)
- [ ] Request Brief & Parameter Matrix provided.
- [ ] Candidates A/B/C proposed with Second-Thought critique.
- [ ] Decision Matrix with scores + rationale included.
- [ ] Pick justified with switch criteria.
- [ ] Pass breakdown defined (Pass 1 = planning, Pass 2 = implementation).
- [ ] Relevant entries from `CODEBASEDOCUMENTATION.md` cited.
- [ ] Drift Score computed; drift >5% justified + repaired.

## Implementation (Pass 2 — snippet-only edits)
- [ ] Changes delivered as **unified diff** or **anchor-based patch**.
- [ ] Instructions Block included: File(s), Where, Why (Checkpoints/FMs), How to apply, Rollback.
- [ ] Efficiency Gauge reported:
  - Lines changed (+ / -)
  - Runtime delta
  - Checkpoint pass rate
  - Regressions (count + IDs)
  - Smoothness (improved/same/worse)
  - Compile scope (none / single scene / full)
- [ ] Regression Guard confirms all Active checkpoints preserved.
- [ ] Rollback snippet provided.
- [ ] Rotation check performed — header decluttered as needed.

## Research
- [ ] Standard research ≥5 sources (≥2 forums, ≥1 official, ≥2 blogs/tutorials).
- [ ] Sources labeled (Official, Forum, Blog) and timestamped.
- [ ] All guidance pinned to **Manim CE v0.19.0**.
- [ ] Deep Research dossier produced if 2+ failed attempts:
  - ≥8 sources (≥3 forums, ≥2 official)
  - MRE created
  - Experiment matrix run
  - ≥3 strategies compared
  - Patch Plan + Fallback + Rollback
  - Upstream issues/PRs checked
  - Go/No-Go recommendation included.

## Documentation
- [ ] `CODEBASEDOCUMENTATION.md` updated for any new classes/objects/functions used.
- [ ] Extended guidelines (`WORKFLOW_EXTENDED.md`) applied where relevant.
- [ ] References to raw GitHub links from `FILE_INDEX.md` or `RAW_LINKS.md` included if files were touched.

## Drift & Overrides
- [ ] Drift Score (%) reported after planning + implementation.
- [ ] If >5%, drift justified, repaired, and compared (drift vs corrected).
- [ ] Any deviations from hard rules explicitly stated with justification.
- [ ] Quality Override used only when compliance reduced accuracy/clarity, and reason given.

---

✅ Sign-off means: this PR passed all gates, preserved checkpoints, controlled drift, updated docs, and delivered snippet-only edits tied to v0.19.0.
