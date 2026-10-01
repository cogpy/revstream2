# The runner — gates, triggers, loop guard, self-termination

`assets/routine-workflow.yml` is a hardened GitHub Actions implementation. This document
explains each part so it can be adapted, and lists the failures that shaped it. Every
pitfall below cost real time to discover; several were invisible until a green run was
demanded rather than assumed.

## Why two jobs

The runner splits into a **gate** job and an **iterate** job. The gate is cheap: a
checkout and a shell script that reads the state file and a few environment facts, then
emits `proceed=true|false`. The iterate job — the expensive one that spins up an agent
session — only runs when the gate says so.

This split is what makes the routine safe to trigger liberally. Daily schedule plus
push-on-evidence plus external dispatch would be reckless if every trigger cost an agent
run; with the gate in front, a no-op costs seconds.

## What the gate checks, in order

1. **Model credential present.** Without it the iterate job cannot do anything. Skip
   with a warning rather than fail red — a red run on every schedule tick is noise that
   trains people to ignore the workflow.
2. **State file exists.** Nothing to iterate against otherwise.
3. **Loop guard.** If this is a `push` event and the head commit message carries the
   routine's marker, the push was the routine's own — skip. See *Loop guard* below.
4. **Platform event compatibility — relay, don't just report.** Some agent actions reject
   certain event contexts (see *Pitfalls*). If a human push can't drive an iteration, the
   gate fires a `repository_dispatch` with the workflow's own token and exits. Dispatches
   created with `GITHUB_TOKEN` *do* start workflow runs (push events created with it do
   not), so the relayed run arrives within a minute and enters through trigger 4. Without
   the relay the push trigger is decoration and every document that says "reacts to a push"
   is wrong.
5. **Self-termination.** If the state file's status marker reads `COMPLETE` and `force`
   wasn't passed, go dormant.

Only then `proceed=true`.

## Triggers

| Trigger | Purpose |
|---|---|
| `schedule` (daily, off-peak minute) | Baseline sweep. Pick a minute that isn't `:00` or `:30`. |
| `workflow_dispatch` with `force` input | Manual run; `force` overrides a `COMPLETE` marker. |
| `push` to main on the evidence paths | React to arriving inputs within a minute instead of up to 24h. **See pitfall below — may need the gate to redirect.** |
| `repository_dispatch` with a named type | External signal with no commit — e.g. when something is unzipped, or a record arrives by another channel. Fired with one `curl` to the dispatches endpoint. |

The dispatch route matters more than it looks. If the platform's agent action can't run
from a push context, dispatch is the *only* way to react to evidence faster than the
clock.

## Loop guard

The routine writes to the same paths that trigger it. Without a guard, every iteration's
commit fires the next iteration, forever.

The guard: every commit the routine makes carries a literal marker (e.g. `[routine-name]`)
in its message. The gate reads the head commit message and skips pushes that carry it.
Two implementation details that matter:

- **Read the message through an environment variable**, never by interpolating
  `${{ github.event.head_commit.message }}` into the `run:` script body. A commit message
  is untrusted input; inlining it into a shell script is a script-injection vector. Put it
  in `env:` and reference `$HEAD_MSG` — the shell sees a string, not code.
- **Make the marker requirement explicit in the iterate prompt**, with the consequence
  stated. A fresh session that doesn't know why the tag exists will drop it the first
  time it writes a tidy commit message.

## Self-termination

The state file carries a status line. When it reads `COMPLETE`, the gate refuses to
proceed. This is how the routine goes dormant when the cycle closes — no one edits or
disables the workflow, and it can be woken with `force: true` if a late input arrives.

The status line must be on its own line and preserved verbatim by every rewrite. The gate
greps for it; a reworded line silently disables the mechanism.

## Concurrency

`cancel-in-progress: false`. An iteration mid-way through rewriting the state file must
never be killed by the next trigger. A queued run is fine; a truncated state file is not.

## The iterate prompt

The prompt in the workflow is the routine's instruction. It should contain, in order:

1. **Continuity contract** — read only the state file and recent commit log; do not read
   the project history or corpus up front; last action is rewriting the state file within
   its line cap.
2. **The gates** — credentials gate, new-input gate, verification queue — with "first
   unblocked wins, do that one thing, stop".
3. **Standing rules** — the one-line forms, stated as mandatory with a sentence on why.
4. **Finish behaviour** — what to commit and where when work was done; what to do on a
   no-op (touch only the iteration log, open no PR).
5. **Commit tag requirement** — the loop-guard marker, with the consequence of omitting it.

Keep domain-specific detail in the state file's gap table and refer to it by row number
from the prompt. The prompt should rarely need editing; the state file changes every run.

## Pitfalls — each of these happened

**A comment at column 1 inside a `run: |` block.** YAML block scalars end at the first
line indented less than the block's content. An unindented `#` comment terminated the
scalar early and orphaned the lines after it. GitHub's parser rejected the file before
scheduling any job — so **every run for weeks completed with zero jobs and
`conclusion: failure`**, reporting nothing useful. Local `yaml.safe_load` reproduces it at
the exact line. Validate the file locally *and* demand one green run with a spawned job
before trusting the schedule.

**Duplicate mapping keys.** Uncoordinated edits by several agents left `github_token`
and an env key each defined twice with identical values. Harmless in that instance,
but a strict loader rejects them and the next edit may not keep them identical. Check
with a duplicate-key-aware loader.

**Session-local schedulers.** A cron created inside a chat session is not durable — it
dies with the session and typically auto-expires within days. If that is the only
scheduler on offer, the honest answer is "this needs to live in the repository", not "I've
set up a routine".

**`push` contexts rejected by the agent action.** The Anthropic Claude Code action
rejected `push` events outright ("Unsupported event type: push"). The first fix — have the
gate log "push cannot iterate, send a dispatch" — left every state file and CLAUDE.md
claiming the routine reacts to pushes when in fact nothing ever reached the iterate job
from one. Three independent reviews caught the same dead trigger. The template now relays
the push into a `repository_dispatch` from the gate; the iterate job is still never
reached directly from a push.

**Free-text `workflow_dispatch` inputs interpolated into `run:`.** Same class of defect as
the commit message: `${{ inputs.note }}` inside a script body is shell injection for anyone
who can dispatch the workflow. Every input goes through `env:`.

**OIDC token exchange.** The agent action may try to exchange an OIDC token for a GitHub
App token, which needs `id-token: write` *and* the app installed. Supplying
`github_token: ${{ secrets.GITHUB_TOKEN }}` explicitly sidesteps the exchange; the
template does both so it works either way.

**Unpinned action reference.** `@main` tracks upstream and can change behaviour under
you. Pin to a released major (`@v1`) — an audit routine benefits from a fixed runner.

**Missing model credential failing red.** If the API key secret isn't set, every trigger
produces a red run. The gate checks for the credential and skips with a `::warning::`
instead, so the routine is visibly dormant rather than visibly broken.

**A second uncoordinated routine.** Someone else spins up a parallel workflow on the
same gaps with its own branch and state file. Two bills, conflicting edits. Detect it
(look for sibling workflow files), then either consolidate or make both state files
cross-reference each other explicitly.

## Adapting to another platform

The contracts transfer; only the syntax changes. On GitLab CI, the gate is a `rules:`
block plus a first stage that exports a variable; on a plain cron host, the gate is a
shell script that exits non-zero to skip. Whatever the platform: gate before iterate, one
unit of work, marker-based loop guard with the commit message read as data, status-line
self-termination, and at least one non-clock trigger.
