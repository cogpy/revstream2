# {{ROUTINE_TITLE}} — Rolling State (single source of iteration continuity)

**Scope:** {{SCOPE}} | **Last iteration:** {{DATE}} ({{SESSION_OR_RUN_ID}})
{{STATUS_MARKER}}: ACTIVE

**Contract:** every iteration reads THIS file first and rewrites it LAST. Keep it under
~120 lines. Do not re-read session history or the full corpus — deep references are linked
below; load one only when the step you have chosen requires it.

**Runner:** `{{WORKFLOW_PATH}}`, fresh session per run. Fires on: daily {{CRON_HUMAN}} ·
manual `workflow_dispatch` (with `force` to override a COMPLETE marker) · push to `main`
touching {{TRIGGER_PATHS_HUMAN}} (the gate relays a human push into the dispatch below, so
it still iterates within a minute) · `repository_dispatch` type `{{DISPATCH_TYPE}}` (fire
externally with no commit when an input arrives by another channel).
{{SIBLING_ROUTINE_LINE — if another workflow works the same gaps, name it and its state file here; delete otherwise}}

**Every commit this routine makes MUST contain the marker `{{MARKER}}`** — the gate uses it
to skip pushes the routine itself produced. Omitting it causes an infinite trigger loop.

The routine **self-terminates** when the `{{STATUS_MARKER}}` line above reads `COMPLETE`;
set that when every gap closes, or to pause. Preserve that line verbatim on every rewrite.

## Grip (current)

| Deliverable | Grip | One-line status |
|---|---|---|
| {{DELIVERABLE_1}} | {{SCORE}} | {{STATUS}} |
| {{DELIVERABLE_2}} | {{SCORE}} | {{STATUS}} |

## Gaps (all require a NEW INPUT — never re-search; corpus exhausted by enumeration, see {{CLOSURE_DOC}})

| # | Gap | Unblocks when (must be observable by the routine) | Holder |
|---|---|---|---|
| 1 | {{GAP}} | {{FILE_APPEARS / ENV_VAR_SET / ...}} — if credential-gated, ALSO keep an unchecked item in the "Credential-gated retrieval" section below | {{PARTY}} |
| 2 | {{GAP}} | {{...}} | {{PARTY}} |

## Credential-gated retrieval (gate 1 ONLY — never worked as a verification item; delete this section if no gap is credential-gated)

- [ ] {{"retrieve <what> 0 of N" — keep unchecked and update the count each tranche; tick only when nothing remains. The runner's gate keeps scheduled runs alive while any `- [ ]` exists anywhere in this file, so this line is what keeps the routine awake for retrieval. Gate 3 must skip it: when the secrets are unset this item simply waits.}}

## Verification queue (gate 3 — work when gates 1 and 2 are closed; one item per iteration; held primaries only, never a re-search; must not contradict the standing rules)

- [ ] {{ITEM — a verification against primaries, or analysis of held-but-unanalysed material}}
- [ ] {{ITEM}}

## Standing rules (each traces to a retracted finding — non-negotiable; origins in {{RULES_DOC}})

0. Anything already marked verified / passed / summarised is NEVER re-verified. The verification queue holds only checks against held primaries that were never done.
1. Negative findings ("X never happened") → re-run against per-document PRIMARIES, never an index/aggregate.
2. Extract metadata that doesn't chain with neighbours → re-read the source document.
3. Cite evidence by content identity (hash / message ID / decoded content), never analyst filename.
4. Declare a corpus exhausted only after mechanical enumeration.
5. Floors get one-sided `+x%` sensitivity, never `±x%`.
6. Derived / reconstructed data is a map to sources, not a source; never cite it directly.
7. Corrections at source, superseded text retained. Commit + push + draft PR every substantive iteration.
{{ADD_DOMAIN_RULES_HERE — each with a retraction behind it}}

## Deep references (load only when needed)

`{{CLOSURE_DOC}}` (gap detail + exhaustion evidence) · `{{REQUEST_SCHEDULE_DOC}}` (per-holder
requests) · `{{RULES_DOC}}` (standing rules with origins) · {{OTHER_REFS}}

## Iteration log (keep last 5 only)

| Date | Did | Result |
|---|---|---|
| {{DATE}} | Converted investigation to routine | State file + runner established; gaps enumerated |
