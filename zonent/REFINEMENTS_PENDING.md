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
| Stock2Shop (Pty) Ltd | PLATFORM/SUPPLIER | 138+ invoices (7754 of 8 Dec 2017 → 39701 of 28 Jun 2025), R502,563.58 extracted set, all addressed to Peter Faucitt / RWW |
| Sage South Africa (Pty) Ltd | SUPPLIER | Continuous 2016–2026; INV6008343 (4 Jul 2025): Pastel 5→10 users R20,750, order SO2059500 |

### Relation additions (Layer 3)

- REL_OWN: Darren Dennis Farrar → Addarory (Pty) Ltd (director; Rynette admission 8 Oct 2024)
- REL_SUPPLY: Addarory → SLG/RST (packaging + Guaiazulene; order SPO30431, 13 Feb 2025)
- REL_STOCK: Addarory supply categories ↔ SLG disappeared stock categories

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
- Multiple-books flag: SLG TB versions diverge FY2020 (R7.33M), FY2022 (R5.47M), FY2024 (3 irreconcilable versions incl. suspected ×1000 scale corruption of the R246,372 "R246k" entry, file dated 18 Feb 2024).

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
