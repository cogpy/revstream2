# Epistemic rules — the discipline that survives handoff

These rules exist because a routine runs unattended, in a fresh session, with no memory
of the mistakes that were made before it was built. Anything not written down will be
re-made. The rules below were each distilled from a finding that was actually published in
a long forensic investigation and then had to be retracted; they are stated generally so
they transfer to any evidence-driven work, with the origin kept alongside so a reader can
judge whether the same failure applies to their domain.

Treat the list as a seed. Replace the origins with your own retractions as they happen.
A rule with no retraction behind it is an aspiration and will not hold.

---

## Exhaustion proof — how to earn the word "exhausted"

The failure this guards against: a corpus is declared exhausted from *recollection* of
what was searched. Recall is systematically wrong about coverage because it remembers the
searches, not the places the searches didn't reach. In the investigation this pattern comes
from, the "exhausted" claim was made three times before it was true, and each time the
missed material was in a location whose path said nothing about the subject.

Procedure:

1. **Enumerate mechanically.** Walk every repository / store / mailbox in scope and list
   every location above a size threshold (e.g. every directory holding ≥ 40 data files,
   every account, every folder). Do this with a script, not by hand.
2. **Cross-reference against your own citations — by identity.** Take the full text of
   everything the investigation has written and check which enumerated locations are
   *never mentioned*. Match on the thing itself (path, hash, message id, account number),
   not on a name substring: "the review log mentions Datadog" does not cover
   `datadog-soc2-2025.pdf`, and "12 papers fully summarised" is a count, not a list of
   which twelve. A cross-reference that reports zero unexamined because every vendor name
   appears somewhere has proven nothing. The uncited set is your candidate list — not
   proof of a gap, but proof of a place you haven't looked from the record's point of view.
3. **Classify every uncited location explicitly**, one line each:
   - already ingested under a different name / alias directory
   - duplicate of a cited location
   - out of scope, with the reason
   - **genuinely unexamined** ← the only bucket that blocks the word "exhausted"
4. **Record the enumeration** with counts per category. It goes in the closure record and
   is what a future reader checks before trusting the gap list.

Only when the "genuinely unexamined" bucket is empty may you write "exhausted". Anything
found after that point requires a **new input**, not a new query — which is precisely the
condition that makes a routine the right tool.

---

## The standing rules

### 1. Negative findings must be re-run against primaries, never an index

**Rule.** Any claim of the form "X never happened", "no payment exists", "no record was
kept", "only N% is covered" must be re-derived from the per-document / per-account primary
exports before it is relied on. An aggregate can only ever *understate* what the primaries
hold, and it never advertises its own holes.

**Origin.** A unified transaction index labelled "best source" in its own documentation
held ~27% of the transactions actually present on disk — 31 of 69 account directories were
absent from it entirely. Three published findings rested on that index: a manufacturer
payment cutoff in 2022 (payments continued; 2023 was the largest year on record), a
supplier last paid in 2017 (paid in 2025), and a price-coverage figure of 3.5% (actual
85.7%, from a price list sitting in a directory whose path said nothing about pricing).
Each was retracted. The pattern was identical every time: reasoning from the convenient
aggregate instead of the primaries beside it.

### 2. When an extract's metadata doesn't chain, re-read the source

**Rule.** If a per-period extract's opening balance, period, or sequence number does not
chain with its neighbours, the extract is suspect regardless of whether it passes its own
internal consistency check. Re-read the original document.

**Origin.** A bank-statement JSON extract carried a wrong statement number, wrong period,
wrong opening and closing balances, and only the tail of its transactions — yet it passed
`opening + Σ(captured) = closing` because the parser had started mid-page and the
"opening" it captured was a running balance. Excluding it as a "duplicate" dropped a
R720,000 payment made three days after a court order. The defect was invisible to every
check that didn't chain the extract against its neighbours.

### 3. Cite evidence by content identity, never by analyst-assigned filename

**Rule.** Refer to documents by a content hash, message ID, or decoded content — not by
the name someone gave the file when organising it.

**Origin.** Three files named for the same finding shared one message ID: one email
exported three times, which naive counting would have tripled into three corroborating
documents. Three other files named `..._bank_details_...` contained no bank details at
all. Filenames were labels applied by an earlier analyst and had drifted from content.

### 4. Bounds on floors are one-sided

**Rule.** When a total is a floor (unpriced or uncounted items contribute zero), the
uncertainty is `+x%`, never `±x%`. Missing items can only raise the figure. State a
central estimate and a ceiling as separate scenarios; never let a one-item peer
comparison masquerade as a symmetric band.

**Origin.** A costed-production total was published as "reliable to ±8%" where the band
covered one item's peer-price range and nine others had no bound at all. A review bot
caught it: the shape of the claim was wrong, not just the magnitude.

### 5. Corrections at source, superseded text retained

**Rule.** When a finding is corrected, edit the document that made the original claim —
don't only note the correction elsewhere. Keep the superseded text visible (struck through
or in a marked box) with the date and the reason. Never overwrite silently.

**Why.** A later reader must be able to see what was believed, when, and why it changed.
Silent overwrites destroy the audit trail that makes the correction itself credible, and
they let the same error re-enter from any cached copy of the old text.

### 6. Derived models are maps to sources, not sources

**Rule.** Data in a reconstruction, consolidation, or modelling workspace is derived. It
locates primary documents; it does not replace them. Never cite the reconstruction in a
filing; cite the document it points to. Provisional fill-ins (estimates used to complete a
model) must never be presented as recorded facts.

**Origin.** A reconstruction workspace was initially read as a live production system
being tampered with. The owner clarified it was a deliberate consolidation of disparate
sources. The governance alarm was withdrawn — but the evidentiary rule survived and got
sharper: the workspace is a *map*, and its known provisional entries are placeholders.

### 7. Planning artefacts ≠ execution records

**Rule.** Distinguish records of what was *planned* (suggested jobs, projected demand,
draft configurations) from records of what was *done* (released jobs, executed
transactions, submitted documents). Quantities from the former are demand, not
consumption.

**Origin.** 63 job numbers were initially treated as production runs. Native document text
showed every one was system-labelled "Suggested job" — planning output. A separate series
of released jobs existed and told a different story; one ingredient central to the case
had a released-job volume of exactly zero.

### 8. A quote is not a price paid

**Rule.** A benchmark that is a *quotation* — especially one solicited by the party whose
conduct is in question — cannot ground a "paid X% above market" claim. It bounds nothing
until a realised transaction price exists.

**Origin.** A 53% "overcharge" rested on comparing a supplier's price to a competitor's
quote. The email thread producing the quote showed the person under investigation had
requested it, that the co-owner regarded *that* competitor as the expensive one, and that
the stated purpose was to check the supplier was "still on par". The differential ran the
opposite way from the claim.

---

## Why these are written this way

Each rule above is one sentence of instruction and a paragraph of *why*. The why is not
decoration. A fresh session that reads "never cite by filename" will comply until the
filenames look reliable; a session that reads about the three files sharing one message ID
understands the failure mode and will recognise its cousins. Write your own rules the same
way: rule, then the retraction that earned it.
