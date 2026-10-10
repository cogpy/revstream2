<!-- withdrawn-claims-banner -->
> ⛔ **This file contains claims since withdrawn or corrected (flagged 2026-10-10).** Do not reuse them; use the corrections:
> - corrected (`tb-246m-working-copy`): The 18 Feb 2024 SLG TB is a print of the live books carrying mis-scaled journal 789 (22 Nov 2023), not a corrupted working copy; FY2024 was closed at least twice.
> Register and sources: `docs/strategic/WITHDRAWN_CLAIMS_REGISTER.json` (cogpy/ad-res-j7).

# ZONENT Model Refinements — Pending Application

Per the Refinement Protocol (CLAUDE.md), discoveries are recorded here FIRST, then propagated
to source repos and synced to Neon (fincosys Stage 6a).

## From: Forensic Inventory & Manufacturing BOM Audit (2026-07-21)

Source: `ad-res-j7/docs/audit/FORENSIC_INVENTORY_MANUFACTURING_BOM_AUDIT_2026_07_21.md` (§9)

### Entity additions (Layer 3 ER-ABM / registry)

| Entity | Type | Evidence base |
|---|---|---|
| SUPP-ADDARORY (Addarory (Pty) Ltd) | SUPPLIER | R2.6M+ documented payments (Pastel/correspondence); ZERO bank trace in 76,098 txns — flag `settlement_channel_unknown` |
| Coptis SAS | PLATFORM/SUPPLIER | Subscription contract N° 1105 (18 Aug 2015), €1,010/yr, 3 users, signed Jacqui Faucitt (RST CEO) |
| Stock2Shop (Pty) Ltd | PLATFORM/SUPPLIER | 138 invoices (true range 13619 → 39701, 8 Dec 2017 → 28 Jun 2025; ⛔ the earlier "7754" start was withdrawn as unverifiable, ad-res-j7 audit §10), R502,563.58 extracted set, all addressed to Peter Faucitt / RWW |
| Sage South Africa (Pty) Ltd | SUPPLIER | Continuous 2016–2026; INV6008343 (4 Jul 2025): Pastel 5→10 users R20,750, order SO2059500 |

### Relation additions (Layer 3)

- REL_OWN: Darren Dennis Farrar → Addarory (Pty) Ltd (director; Rynette admission 8 Oct 2024)
- REL_SUPPLY: Addarory → SLG/RST (packaging + Guaiazulene; order SPO30431, 13 Feb 2025)
- REL_STOCK: Addarory supply categories ↔ SLG ~~disappeared~~ written-off stock categories — ⛔ *2026-10-07: do not model the FY2025 write-off as physical disappearance; see Corrections §C1 below*

### Event additions (Layer 4 ET-DSM)

| Date | Event | Amount |
|---|---|---|
| 2020-08-13 | Bantjies distributes final TBs + AJEs to pete@regima.com (et al.) | — |
| 2020-08-26 | Stock2Shop "Cancel Integration" email correspondence | — |
| 2025-07-04 | Sage 50cloud Pastel upgraded 5→10 users (month of server seizure) | R20,750.00 |

### Corrections

1. **Event dedup**: EVENT_051 duplicates EVENT_H005 (2020-02-20, AJEs R1,642,000) — merge; also EVENT_026 title:null near-duplicate.
2. **Classification fix**: Proficos rows in `fincosys/coa/classified_transactions.csv` misclassified — 56 rows coded intercompany (1.EXPENSE.INTERCO.SLC→RST), 33 coded self-transfer (0.ASSET.BANK.RST.INTERNAL); Proficos is an external third-party manufacturer — re-code as external.
3. **Entity-label misattribution**: `fincosys/membrane_coa/data/forensic/trial_balances.json` labels several "Strategic TB" / "TB SL" files as `entity: RST`; filenames are authoritative (SLG).
4. **Data-quality**: 77 GBP Goringe Accountants (UK) invoices misfiled under `mazaudit/suppliers/stock2shop/r2_invoices/` — re-attribute.
5. **Classification fix (gap-closure, confirmed 2026-07-21)**: `TXN_2f01f23f0cc7cd50` (SLG→"Regima Jars", R1,216,740.25, 2022-10-18) coded intercompany SLC→RST (shell 1, confidence 0.8) in `coa/classified_transactions.csv` — very likely a substring-match error on "Regima" in the payee name "Regima Jars"; sibling legs of the same 3-leg flow (RST→"Qu0056879" outbound, "Containers"→SLG inbound) are both correctly coded external. Strong circumstantial evidence this leg is a mislabeled Addarory payment (product context: containers/jars). Pending beneficiary-account confirmation, re-code to external (shell 2).
6. **Addarory supplier node — bank evidence found**: exact-amount search located both known Addarory payment amounts in the bank corpus: R1,216,740.25 (2022-10-18, three-leg flow via SLG, TXN_67bb242e2621e832/TXN_f322f8d92a00d856/TXN_2f01f23f0cc7cd50) and R1,388,883.75 (2024-12-03, RWD FNB OB payment, TXN_82c8acd526a8b7a5, ref 000000086, narration "...Regima Containers"). Neither field literally reads "Addarory" — counterparty labels are "Qu0056879"/"Containers"/"Regima Jars"/"Regima Containers". This updates the "zero bank trace" status noted in the initial refinement entry above: the SUPP-ADDARORY node should link these transaction IDs as candidate evidence, flagged `beneficiary_match: circumstantial_not_confirmed`.
7. **New candidate supplier entity**: "Alistin" — recurring SLG supplier, Xero invoice series 73,000-77,000+ (2020-2021, `data/xero_imports/62432501494/`). Strong candidate match for the VAT return's unidentified "MACC" INV73722 reference (R310,500 incl VAT, 20/08/2020) — a same-amount SLG payment to "Alistin" (TXN_b0f3c1b88eb8399f) occurs 8 days later (28/08/2020), funded by a same-day "Loan To Strategic" self-transfer (TXN_a35abc6f2cb0aa96).

### Stock-Flow parameter updates (Layer 5 SF-SDM)

- SLG Feb 2025 inventory adjustment, exact ledger figure: **R5,241,372.98** (P&L 2100/000, all inventory categories) — this is the single authoritative figure for the FY2025 event. **Do not additionally model the R1,443,217.78 (phantom opening finished goods) and R2,756,321.85 (impossible closing finished goods) figures as separate stocks/losses** — they are the balance-sheet Finished Goods (7700/000) component of this same event (their swing = R4,199,539.63), not additive amounts. A ~R1.04M residual (R5,241,372.98 − R4,199,539.63) falls on other inventory categories (raw materials/packaging/boxes/containers) not yet separately quantified. See `ad-res-j7/docs/strategic/STOCK_LOSS_SCHEDULE_2026_04_23.md` §1a for full reconciliation.
- FY2020 RST manufacturing signature: finished goods R12,805,083.10; Manufacture Cost/Recovery R0.00; 8200/050 Prime Products raw materials **-R150,562.11**.
- ~~Multiple-books flag: SLG TB versions diverge FY2020 (R7.33M), FY2022 (R5.47M), FY2024 (3 irreconcilable versions incl. suspected ×1000 scale corruption of the R246,372 "R246k" entry, file dated 18 Feb 2024).~~ ⛔ **Superseded 2026-10-07 — do not apply as written.** Re-derived from the source spreadsheets: the FY2020 R7.33M divergence does not exist (all four files identical on inventory; aggregate artefact); FY2022 R5.47M is unverified (no source held); FY2024 has **two** statements differing by a real retrospective restatement of **R936,873.05** (97% packaging), plus one working copy (18 Feb 2024, pre-year-end) to be excluded, with the ×1000 reading consistent-with but not proven. See Corrections §C2.

### Reconciliation with a parallel investigation branch (2026-07-21)

A concurrent branch (`claude/review-bom-docs-uMY6H`, merged to ad-res-j7 main via PR #4892)
independently worked overlapping evidence. Two of its findings materially affect items above and
the wider entity model:

- **Guaiazulene supplier corrected**: live SLG stock records (two independent 2025 snapshots,
  4 months apart) show the registered Guaiazulene supplier as **Symrise (SYM0001)**, not
  Addarory. The Addarory/Guaiazulene "circular supply" hypothesis has **no direct supporting
  evidence for this specific ingredient** — model it as an unproven hypothesis, not an
  established relation. The Addarory bank-evidence findings above (item 6) stand on their own
  (payment amounts located in the corpus); they do not, on their own, establish the
  circular-supply mechanism.
- **New live BOM/MRP data available**: 17 SLG finished-good formulas, 88 raw materials, real
  ERPNext consumption data (Apr–Nov 2025) — see `ad-res-j7/docs/strategic/MANUFACTURING_BOM_2026_07_21.md`
  and `ad-res-j7/evidence/manufacturing_bom/mrp_bom_graph.json`. Confirms "Alistin SC" (item
  R1905059) as an active current ingredient/supplier — independent corroboration of item 7
  above. Note: MRP entries are labelled "Suggested job" (planning-stage), not confirmed
  executed production — model accordingly if adding to the stock-flow layer.
- **Physical stock count claim scoped**: a genuine count exists for a separate UK "Salco"
  channel (23 Jul 2020–10 Nov 2021, favourable variance) — but SLG/RST's own SA warehouse stock
  (the entities central to this refinement file) still has no documented count located.

---

## Corrections (2026-10-07) — apply these in place of the superseded entries above

Source: `ad-res-j7/docs/audit/PHANTOM_STOCK_ROOT_CAUSE_2026_09_08.md`, `…_ADDENDUM_2026_09_22.md`,
`…_ADDENDUM2_2026_09_29.md`, and `ad-res-j7/docs/audit/BOM_INVESTIGATION_LEDGER.md` §2–§3.
Every figure re-derived from the primary trial-balance xlsx files, not from any aggregate.

### C1. The FY2025 write-off is a bookkeeping residue, not missing goods (model as such)

- `2400/000 Manufacture Cost / Recovery` = R0.00 in every held SLG and RST trial balance,
  FY2017–FY2025: the raw-materials→finished-goods conversion journal was never posted.
- Consequence in the books: packaging accumulates (R5.78M FY2019 → R8,424,603.19 FY2025),
  finished goods drains to a credit (R1,443,217.78 DR → R2,756,321.85 CR), and the FY2025
  `2100/000` plug of R5,241,372.98 is **96.62% explained by ledger movements alone**
  (FG collapse R4,199,539.63 + other inventory capitalised R1,219,150.81; residual R177,317.46).
- ZONENT impact: EVENT_025/EVENT_028 and any `REL_STOCK` edge must carry
  `nature: accounting_artefact_unposted_conversion`, not `physical_loss`. The R5.4M headline,
  the R5,241,372.98 ledger figure and the R4.2M FG swing are one event measured three ways —
  never summed (already noted at the 2026-07-22 entry; this makes it explicit for the edge type).
- Physical control: raw materials at Prime (4 Aug 2025) value to R931,511.91 at count-quarter
  list price and **reconcile** to book (R740,345.71 Feb 2025 / R970,881.11 Feb 2024).
  Packaging (R8.42M) has no count anywhere — untested, not inferred either way.

### C2. "Multiple books" — what survives

| Claim as recorded above | Status | Replace with |
|---|---|---|
| FY2020 versions diverge R7.33M | **Refuted** | Four files identical on all inventory rows (Boxes 898,930.17); the 8,231,078 was the FY2019 inventory total read into the Boxes row by the extractor |
| FY2022 R5.47M | **Unverified** | No FY2022 spreadsheet held; JSON-only; do not model |
| FY2024 three irreconcilable versions | **Replaced** | Two statements, reconciling to the cent via a retrospective **−R936,873.05** write-down (R905,004.19 packaging); the 18 Feb 2024 file is a pre-year-end working copy — exclude, do not call it a version |
| ×1000 scale corruption | **Hedged** | Consistent with, not proven; cite as "working copy, excluded" |

### C3. New, verified, not yet in the model

- **FY2025 TB in evidence does not foot** by R2,485,098.35, all in 5200/000 opening retained
  income. Inventory rows unaffected; the file is a working document. Any FY2025 balance taken
  into ZONENT must carry `source_status: working_document_unfooted` until the signed AFS/GL is held.
- **FY2023 raw materials credit balance**: 7540/000 = −R8,570,989.06 in the earlier FY2024
  file's comparative, +R429,010.94 in the issued one — a change of exactly R9,000,000.00 to a
  closed year (8001/000 changed by exactly R1,100,000.00 in the same pair). The negative-asset
  signature on raw materials two years before it appeared on finished goods. Weight limited by
  the working-copy source; needs the FY2023 primary TB (ledger gap 18).

### C4. Stock-count claim

The blanket "no physical stock count ever performed" is **refuted** (counts by Prime Mar 2021,
joint RegimA/Salco 1 Sep 2021, SOLO 8 Feb 2022; Salco is a South African logistics provider,
not a UK channel). Do not attach a `no_count_ever` attribute to any SLG/RST inventory node.
