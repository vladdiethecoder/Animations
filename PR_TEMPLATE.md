# PR Checklist — Policy Compliance

## Gate 0 — Sync
- [ ] Read `WORKFLOW.md`, `CHECKPOINTS.md`, `CODEBASEDOCUMENTATION.md`
- [ ] Code header snapshot **matches** `CHECKPOINTS.md (Active)`, or sync plan executed

## Planning Artifacts
- [ ] **Request Brief & Parameter Matrix** attached
- [ ] **Candidates A/B/C**, **Second-Thought critique**, **Decision Matrix**, **Pick** included
- [ ] Smallest **compile scope** defined (static/DEBUG/micro-render)

## Research
- [ ] Sources ≥5 (≥2 forums, ≥1 official), labeled & timestamped; pinned to **v0.19.0**
- [ ] Deep Research **(if triggered)**: ≥8 sources, MRE, experiment matrix, strategies, Patch Plan, Fallback, Rollback, upstream check

## Documentation
- [ ] `CODEBASEDOCUMENTATION.md` updated/cited (new classes/objects/functions)
- [ ] File paths referenced for repo context (if GitHub connector enabled)

## Checkpoints & Regression
- [ ] “**Rotation check performed — header decluttered as needed.**”
- [ ] **Risk & Mitigation Map** (FMs) included
- [ ] **Regression Guard** status per checkpoint
- [ ] **Rollback Snippet** provided

## Patch Delivery
- [ ] Snippet patch (unified diff or anchor-based) with **Instructions Block** (File/Where/Why/How/Rollback)
- [ ] **Efficiency Gauge** reported (lines delta, runtime delta, pass rate, regressions, smoothness, compile scope)

### Notes
- Target stack: **Manim CE v0.19.0**
- No large, unscoped changes; follow **Pass 1 → Pass 2** discipline.
