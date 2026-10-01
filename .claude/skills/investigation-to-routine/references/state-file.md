# The state file — single source of continuity

The state file is the entire memory of the routine. Every iteration reads it first and
rewrites it last. Nothing else — not session history, not the corpus, not a memory system
— is consulted for orientation. This is a deliberate constraint, and it's what makes the
routine's context cost flat no matter how many iterations run.

Use `assets/STATE_TEMPLATE.md` as the skeleton. This document explains what each section
is for and why the constraints are set where they are.

## The two contracts

**Read first, rewrite last.** An iteration's first action is reading this file; its final
action is rewriting it. Everything in between is one unit of work. The rewrite is not
optional — an iteration that does work but doesn't update the state file has effectively
not happened, because the next iteration won't know.

**≤ 120 lines, always.** The cap is load-bearing. A state file that grows becomes a second
investigation log, and the context problem the routine was built to solve returns
through the back door. Trim the iteration log to the last five entries; move anything
longer into a referenced document and link it. If you find yourself needing more than
120 lines, that's a signal that something in the file is history, not state.

## Anatomy

### Header block

```text
# <Routine name> — Rolling State
**Scope:** <case / project> | **Last iteration:** <date> (<session or run id>)
<STATUS_MARKER>: ACTIVE
```

The status marker line must be preserved **verbatim** on every rewrite — the runner's
gate greps for it. When it reads `COMPLETE` the routine goes dormant. Put it on its own
line near the top so it's impossible to miss and trivial to grep.

### Contract paragraph

Three or four sentences telling the reader what to read (this file, recent commit log)
and — more importantly — what *not* to read (the project's investigation history, the
full corpus). Name the runner file and its triggers. State the commit-tag requirement
for the loop guard. This paragraph is the thing that stops a capable fresh session from
"getting up to speed" by re-reading everything, which is exactly the behaviour the
routine exists to prevent.

If a sibling routine exists on the same work, name it here with its state file, so the
two can cross-reference instead of colliding.

### Grip / progress table

| Deliverable | Grip | One-line status |
|---|---|---|

One row per thing the work must ultimately deliver, with a coarse score (0–1 or a
category) and a one-line status. This is the routine's dashboard — the first thing a
human glances at. Keep status lines to one line; if a row needs a paragraph, that
paragraph belongs in a referenced document.

### Gap table

| # | Gap | Unblocks when | Holder |
|---|---|---|---|

The heart of the file. Each row is an input the routine is waiting for. Two rules that
make this table work:

- **Unblocks when** must be observable by the routine: a file in a path, an env var set,
  a document in an uploads folder. "When the counterparty responds" is not observable;
  "when a statement PDF for account N lands in `evidence/`" is.
- **Holder** is whoever has to *act* for the input to exist — a vendor, a bank, a team,
  or the project owner (who must unzip an archive, file an email, or set a secret). It is
  never the routine itself. If the routine could close the gap by searching, it isn't a
  gap — it's unfinished investigation, and the file's contract paragraph should be sending
  the reader to the exhaustion proof instead.

Number the rows and refer to them by number in the runner prompt ("gaps 2–7") so the
prompt doesn't have to be edited when the table's wording changes.

### Verification queue

A checklist of things worth doing when *every* gap is blocked, one per iteration. These
are not searches of exhausted corpora — they're verifications against primaries, analyses
of held-but-unanalysed material, or re-checks that become due when a dependency changes.
Tick items off in place; don't delete them, so the history of what was checked stays
visible within the line budget.

### Standing rules

The distilled rules from `references/epistemic-rules.md`, adapted to your domain, each
one line. Number them. These are non-negotiable for the routine and the prompt should
say so — but the *reason* they're non-negotiable is that each traces to a retraction, and
the reference document holds those origins so the state file can stay short.

### Deep references

A single paragraph of file paths, each with a two-or-three-word purpose. The rule for
this section: the routine loads a reference only when the step it has chosen requires
it. Listing them here is what lets the contract paragraph say "don't read the corpus"
without leaving the reader stranded.

### Iteration log

| Date | Did | Result |
|---|---|---|

Last five entries only. Older entries are in git history if anyone needs them. A no-op
iteration gets one line — "no-op — blocked on gaps 1–7" — so the log shows the routine is
alive without the file growing.

## What goes wrong

**The file drifts into a narrative.** Someone adds a paragraph of context "so the next
session understands". Then another. Within a month it's 400 lines and every iteration
pays for it. Hold the line at 120; put context in a referenced doc.

**Gap rows with unobservable unblock conditions.** The routine can't act on "when the bank
replies", so the gap never moves and the routine never notices when it should. Rewrite
the condition as something the routine can check.

**The status marker gets reworded.** A rewrite changes `STATUS: ACTIVE` to `Status —
active` and the gate's grep stops matching. Preserve it verbatim; say so in the contract
paragraph; say so again in the runner prompt.

**Standing rules without origins.** They read as arbitrary and get skipped under
pressure. Keep the one-line form in the state file but make sure the reference document
carries the retraction each rule came from.
