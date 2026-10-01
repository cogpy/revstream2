---
name: investigation-to-routine
description: Convert a long-running investigation, audit, migration, review, or research effort — one that has stopped producing findings because everything left depends on inputs from external parties — into a durable, self-terminating scheduled routine driven by a small rolling state file. Use this whenever a multi-session investigation is stalling or looping; whenever someone says work should "keep running", "persist", "run as a routine", "check periodically", "pick up where it left off", or "continue until done"; whenever a session's context has grown so large that continuity is at risk; whenever the remaining work is "wait for X, then act" rather than "search for X"; or whenever a stop-hook / completion check keeps re-firing on a goal that cannot be completed from inside the current environment. Also use it to design the state-file contract and CI workflow for ANY recurring agentic task that must survive across sessions without accumulating context — it is not limited to forensic or legal work.
---

# Investigation → Durable Routine

An interactive investigation and a scheduled routine are different tools for different
phases of the same work. The investigation phase is *search*: the corpus holds answers you
haven't found yet, and each session's context is an asset. The routine phase is *waiting*:
the corpus is exhausted, every remaining gap needs an input someone else holds, and each
session's accumulated context is now a liability — it costs tokens, drifts, and tempts
re-searching ground already proven empty.

This skill is for recognising the phase change and executing it cleanly. Done well, the
conversion turns an open-ended session that keeps re-firing into a cheap daily check that
acts the moment an input arrives and goes dormant when the cycle closes.

## Recognise the phase change

Convert when **all** of these hold. If any is false, you are still investigating — keep going.

1. **The reachable corpus is exhausted, and you can prove it.** Not "I've looked everywhere"
   — that claim has been wrong in every long investigation this pattern was distilled from.
   Proof means a mechanical enumeration (every directory above a size threshold, every
   account, every mailbox) cross-checked against what your documents actually cite. See
   `references/epistemic-rules.md` for the method and for why recall is not evidence.
2. **Every remaining gap names an external holder.** A bank, a supplier, a counterparty, a
   credential the owner must issue, a physical act only they can perform. If a gap's unblock
   condition is "search harder", it is not a gap yet — it is unfinished investigation.
3. **The work has become reactive.** What remains is "when X arrives, do Y". A routine's whole
   value is being awake when X arrives; a session's whole cost is staying awake while it
   doesn't.
4. **Continuity is at risk.** Context is compacting, findings are being corrected because
   earlier context was lost, or a completion hook is looping on a goal that is unsatisfiable
   from inside the environment. The last is the clearest signal: a hook demanding "complete
   the audit" when completion requires a warehouse stock count is not asking for more
   effort; it is asking for a different mechanism.

A common failure is converting too early — building the routine to escape a hard search
rather than because the search is done. The exhaustion proof in step 1 is the guard against
that. A rarer failure is converting too late, after three findings have already been
retracted because context loss let old errors resurface; the standing-rules discipline
below exists so those retractions become permanent knowledge rather than repeated pain.

## The conversion, in five steps

### 1. Prove exhaustion mechanically

Enumerate the corpus by machine, not memory. Cross-reference every substantial location
against the full text of everything you've written. What surfaces as *never cited* is your
candidate list; classify each candidate explicitly (already ingested under another name /
duplicate / out of scope / **genuinely unexamined**). Only when that last bucket is empty may
you write "exhausted".

Record the enumeration — the count, the categories, the one-line reason each uncited
location doesn't bear on the question. This is the evidence that lets the routine refuse to
re-search, and it is the thing a future reader will want to check before trusting the gap
list. `references/epistemic-rules.md` § *Exhaustion proof* gives the procedure.

### 2. Write the gap table — every row names a holder

| # | Gap | Unblocks when | Holder |
|---|---|---|---|

The **Unblocks when** column is the routine's trigger condition and must be *observable by
the routine itself*: a file appearing in a path, an environment variable being set, a
document landing in an upload folder. "When the bank responds" is a holder, not an unblock
condition — the routine can't see a bank respond, but it can see a statement PDF arrive.

The **Holder** column is what turns the gap list into a request schedule. If you can't name
who holds the input, you haven't understood the gap. It is worth writing, alongside the
state file, a companion document that addresses each gap to its holder with the exact
records needed (account numbers, item codes, date ranges) — that document is the thing a
lawyer, owner, or counterpart can act on without reading the investigation.

### 3. Distil standing rules from *corrected* errors only

The rules that go into the state file are not aspirations. Each must trace to a specific
wrong finding that was actually published and then retracted. A rule with an origin story
survives handoff because a fresh session can see *why* it exists; a rule without one gets
rationalised away the first time it's inconvenient.

Write each as: the rule, then the retraction it prevents. Keep them under ten; if you have
more, some are aspirations wearing a rule's clothing.

The investigations this pattern comes from produced the same shape of error three times
before the rule stuck: a *negative* finding ("payments stopped in 2022", "no supplier was
ever paid", "only 3.5% of items are priced") derived from an index or aggregate that
silently held a fraction of the underlying records. `references/epistemic-rules.md`
carries the full set with their origins; treat it as a starting list and replace with your
own domain's retractions.

### 4. Write the state file

One file, ≤120 lines, that every iteration reads first and rewrites last. It is the
**only** continuity mechanism — not the session history, not the full corpus, not a
memory system. A fresh session should be able to act correctly having read nothing else.

Its sections, in order: a status marker the runner checks · a contract paragraph telling
the reader what to read and what *not* to · a grip / progress table · the gap table · a
verification queue for iterations where every gap is blocked · the standing rules · deep
references loaded only on demand · an iteration log trimmed to the last five entries.

The ≤120-line cap is load-bearing. Without it the state file becomes a second history and
the context problem returns. Use `assets/STATE_TEMPLATE.md`; anatomy and the reasoning
behind each section are in `references/state-file.md`.

### 5. Build the runner

A scheduled workflow where **each run is a fresh session** that does **exactly one unit of
work** — the first unblocked step of a fixed priority list — then rewrites the state file
and stops. Fresh-session-per-run is what bounds context; one-unit-per-run is what makes
each iteration cheap enough to run daily and safe enough to run unattended.

The runner needs, in this order:

- **A gate job** separate from the iterate job. The gate reads the state file and decides
  whether to proceed at all: model credential present, state file exists, status marker not
  `COMPLETE`, and — critically — that this run was not triggered by the routine's own
  commit. Splitting gate from iterate keeps the expensive step from spinning up on a
  no-op.
- **Priority gates inside the prompt.** Credentials gate (if secret X is set, do the
  retrieval work) → new-input gate (if any gap's unblock condition is now true, ingest) →
  verification queue (otherwise, take the top unchecked item). First unblocked gate wins;
  do that one thing; stop.
- **A self-termination marker** in the state file that the gate honours, plus a
  manual-dispatch `force` input to override it. This is how the routine goes dormant when
  the cycle closes, without anyone editing the workflow.
- **A loop guard.** The routine writes to the same paths that trigger it. Tag every commit
  it makes with a literal marker and have the gate skip pushes carrying that marker. Read
  the commit message via an environment variable — never interpolate it into the script,
  because a commit message is untrusted input and inlining it is a shell-injection vector.
- **Event triggers, not just the clock.** `push` on the evidence paths and a
  `repository_dispatch` type so the routine reacts within a minute of an input landing
  rather than up to 24 hours later. Some agent actions reject `push` contexts outright, so
  the gate must **relay** a human push into a `repository_dispatch` (one API call with the
  workflow's own token) instead of merely logging that it can't proceed — otherwise the
  state file promises "reacts to a push" and the promise is false. The template does this.
- **Verification is not re-search.** When every gap is blocked, the routine works a
  verification queue: checks against *held* primaries that were never done (re-extracting
  a PDF to confirm an absence, mapping a count claim to file identities). Re-running
  queries over corpora the closure record marks exhausted is forbidden. Write the standing
  rules and the verification queue together and read them against each other — a rule
  that forbids opening summarised documents while a queue item requires opening them is a
  contradiction the fresh session cannot resolve.

`assets/routine-workflow.yml` is a parameterised, hardened GitHub Actions implementation.
It carries fixes for failures that were each discovered the hard way — including a stray
unindented comment inside a `run: |` block that silently killed every run for weeks while
reporting nothing. `references/workflow.md` explains each part and the pitfalls.

## What "done" looks like

- The exhaustion enumeration exists and is cited, with its uncited-location count and
  categorisation — and the classification was done by **identity** (this file / hash / id
  is cited here), not by a count ("12 papers summarised") or a name-substring match.
- The gap table has no row whose holder is the routine itself or whose unblock condition
  is a search. The project owner is a legitimate holder (an archive only they can unzip, a
  credential only they can set) — the test is "who has to act", not "who is external".
- The state file is under 120 lines and a fresh session could act on it alone.
- The runner has passed **one manual dispatch run** before anyone trusts the schedule — a
  workflow that parses locally can still fail in the runner's YAML loader or the action's
  event handling, and the only proof is a green run with a spawned job.
- The project's top-level instructions (CLAUDE.md or equivalent) say, in as many words:
  *this is now a routine; do not re-open it as a search task; read the state file first;
  never re-verify an item already marked passed* — plus the stop condition and the loop
  guard marker. Without that block the next session will re-investigate, because that is
  what sessions do.
- Every trigger the state file advertises actually leads to an iteration. If the platform
  can't iterate from a push, the gate relays it; if it can't relay, the state file says so.
- The message you hand the user matches the artifacts: the number of queue items, the file
  names, the triggers. Count them before you write the summary — a summary that says "two
  re-checks" over a queue of five is the first thing a reviewer will find.

## Two things that look like this pattern but aren't

**A session-local scheduler** (a cron inside the chat session). It dies with the session
and usually has a short auto-expiry. It is fine for watching a PR for an hour; it is the
wrong tool for anything that must outlive the conversation. If that is the only scheduler
available, say so and build the durable runner in the repository instead.

**A second, uncoordinated routine.** If someone spins up a parallel routine on the same
gaps with its own state file, you get two bills, two branches, and conflicting edits. Flag
it; consolidate or explicitly cross-reference. Don't silently let both run.

## Reference map

- `references/epistemic-rules.md` — exhaustion proof method; the standing rules with the
  retractions that produced them; the correction-at-source protocol. **Read before step 1.**
- `references/state-file.md` — section-by-section anatomy of the state file and why the
  line cap matters. **Read before step 4.**
- `references/workflow.md` — gate/iterate split, triggers, loop guard, self-termination,
  and the platform pitfalls. **Read before step 5.**
- `assets/STATE_TEMPLATE.md` — fill-in state file.
- `assets/routine-workflow.yml` — fill-in GitHub Actions runner.
