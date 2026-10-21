# comcosys scan against the October 2026 findings (2026-10-21)

**Scope.** All 405,422 `.eml` files in `comcosys/exchange/` and `comcosys/gmail/` (88 mailboxes).
Every body in the archive is base64-encoded, so a raw grep only sees headers. A decoded plain-text
corpus (one file per mailbox, HTML stripped, 30 KB cap per message) was built in the scratchpad and
searched in full. Attachments are not held anywhere in the archive (sidecars confirm), so every
"attached" document below is absent.

**Coverage limit.** The Exchange archive runs Jul 2020 – **Jan 2024** (24 messages in Feb 2024, none
after); the Gmail archive is Feb–Jul 2015. Nothing from the 29 Feb 2024 year-end onward is reachable
here — the FY2024 closes, the 2025 SARS chain, the interdict period. The Sep 2023 spike (287k messages)
is `org@regima.zone` order notifications in `dan@regima.zone`, not correspondence.

Cross-checks "recorded?" were run against markdown in ad-res-j7, revstream2, fincosys/docs and
fincosys/data/stock. Cite by `Internet-Message-ID` and sidecar SHA-256, not filename.

---

## 1. Unrecorded — bears directly on an October 2026 finding

### 1.1 The 28 Jun 2022 SLG/RST forex conversion: the instruction chain (CROSS_REPO_FINDINGS_SYNC §"SLG forex")

The caselex finding verified the conversion from bank data (EUR 299,794.52 → R5,015,562.32, plus GBP and
USD legs; R4,000,000 then SLG→RST as four "Trs Dr H" legs booked to loan 5466) but had no document for
*who instructed it and on whose authority*. The archive holds the chain, all 24–30 Jun 2022:

| Time (UTC) | Message | What it shows |
|---|---|---|
| 24 Jun 10:00 | Rynette Farrar → FNB Gauteng Inward Transfers, cc Jax, Pete, Liz du Randt (FNB RM): "Please find attached an instruction to convert foreign funds into Rands." | **The written instruction originated with Rynette.** The attachment (the instruction itself) is not held. |
| 24 Jun 11:02 | RMB forex team leader → consultant: "Segment CR7, please check for indemnity" | FNB treated it as needing an indemnity check. |
| 24 Jun 11:32 | Rosslynne Kroats (FNB Forex) → **Daniel and Jacqueline**, cc Kayla: trying to reach them on 083 658 7019 / 082 657 6107 "to confirm an exchange rate for the attached transfer instructions" | **FNB's first call for authority went to Daniel and Jacqueline**, not to Rynette or Peter. `<JN1P275MB1334B960FF1153F8C0FF6DB0D4B49@…>` sha256 7091c032… |
| 24 Jun 13:32 | Kroats → **Peter**, cc Jax, Dan: "As per your telephonic conversation with Liz, kindly see below indicational exchange rates": SLG EUR 16.4779 / USD 15.7337; RST EUR 16.4779 / USD 15.7371; "the small GBP payments was settled as the system settles all payments under R200 000.00 automatically" | **Peter gave the go-ahead by telephone** to Liz du Randt. Both SLG *and* RST CFC balances were converted the same day. `<JN1P275MB1334B6179F60908FF538F3BCD4B49@…>` sha256 e49c8f94… |
| 30 Jun 08:32 | Du Randt → Rynette, Kroats: "Has this been concluded? Kindly confirm." Forwarded by Rynette to Jax and Pete 30 Jun 06:32 UTC | The conversion was still open at FNB's end on 30 Jun. `<2a28ca9a…@DB9PR08MB6569…>` sha256 509a8e9d… |

Arithmetic check: R5,015,562.32 ÷ EUR 299,794.52 = 16.7300, against the 24 Jun indicative 16.4779 —
consistent with execution on 28 Jun at that day's rate, as the bank data says.

Why it matters for the governing rule ("every intercompany movement is UNPROVEN until its causa,
authority and document are on the record"): the *conversion* has an authority trail (Rynette's written
instruction + Peter's telephonic confirmation, with FNB first seeking Daniel/Jacqueline). The
*onward R4M SLG→RST legs* do not appear in any email in the archive ("Trs Dr H", "5466", R4,000,000 in
a June/July 2022 message: zero hits). The authority gap is confined to the SLG→RST transfer, not the
conversion. Copies: `exchange/dan@regima.zone/inbox/2022-06-24_1132_…`, `…_1332_…`,
`exchange/jax@regima.zone/conflicts/2022-06-30_0632_…`.

### 1.2 River Road stock administration, Jan–May 2023 — a South African count that is on no list

`exchange/rynette@regima.zone/nox/` holds **190 messages from Noxolo Hadebe (nox@regima.zone)** to Rynette,
cc Jax and Pete, Jan–May 2023 (5/63/74/36/12 by month). None of it is cited in any repo
(`nox@regima.zone`, `Noxolo`, "stock brought forward", "collection note": 0 hits). Content:

- **Monthly "River Road stock brought forward" files** — e.g. 2 Feb 2023 "END OF JANUARY 2023 RIVER ROAD
  STOCK BROUGHT FORWAD" (attachment absent). `<AM6PR08MB3623A2666C186A006A66344FA6D69@…>` sha256 7c746cf0…
- **A physical finished-goods count, 9 Feb 2023** ("STOCK COUNT"): Scar Cream 15ml 449; 02 Purify 1,080;
  Derma Zest 100ml SA 5,967; Derma Zest 140ml SA 3,812; Pigment Perfector SA 1,022; Quantum Collagen 15ml
  SA 301; Acne Attack Rescue Serum 50ml SA 5,069; Scar Forte 50ml SA 3,619 — with two transfer-sheet
  corrections against "V.B" (9 boxes received not 8; 11 sent not 12).
  `<AM6PR08MB362302868A1730D12170FBB8A6D99@…>` sha256 b5ab5af9…
- **Raw materials physically at River Road and at "V.B"**, itemised with batch numbers and expiry,
  10 Feb and 2 Mar 2023 (Fermiskin, Retilactyl, L-Carnitine, Aquaphyline, Drieline, Tens'Up, Saponaire,
  Cetiol SB45 4×25 kg, Cosmedia DC, **Alistin SC 1×30 kg batch 5065.22**, RonaCare AP/Caffeine,
  Uvinul T150 60 kg, Glyco Repair 10 kg, **Colamate RM 204.12 kg drum "at V.B by the basement room"**).
- **Prime collection notes**: 15 Feb 2023 (Cetiol, Colamate, Cosmedia, RonaCare, Uvinul collected; rejects
  and packaging delivered) and 27 Feb 2023 (packaging + Biopeptide CL MBAL 5×1 kg).
  `<AM6PR08MB3623D9389D4E5D87AAB4925FA6A39@…>` sha256 aa927a2e…
- Packaging received from Big Foot at River Road (6 Feb 2023); "products lower than 500 in stock"
  reports; UK stock sales.
- **The Addarory Guaiazulene**: "GUAIAZULENE/AZULENE 1 X 1KG … batch 20230206, best before 2025-02-06,
  received at head office, put into stock, from V.B head office to River Road, 6 Mar 2023."
  `<AM6PR08MB3623D2F7939A09AE06D02A84A6B69@…>` sha256 9b62288f…

Implications:
1. `STOCK_COUNT_CLAIM_CORRECTION_2026_08_15` lists counts at Prime (2021), Salco (2021) and SOLO (2022).
   **A documented South African finished-goods count at River Road on 9 Feb 2023, and monthly stock
   files Jan–May 2023, should be added.**
2. The 2026-09-02 reframing "SLG never held stock centrally — stock sits at Prime, Jubilingo, Salco and
   the Bedfordview fulfilment locations" needs the Bedfordview leg made explicit: in early 2023 River
   Road / V.B held **raw materials and packaging as well as finished goods**, and raws moved River Road
   → Prime on collection notes. The raw-material mass balance (ledger gap 14–16) has a third holder.
3. Only one kilogram of Guaiazulene is evidenced entering stock (6 Mar 2023). Rynette's 28 Jul 2025
   "Addarory brought in the last two lots" is not contradicted, but the archive gives no second lot
   before Jan 2024.
4. Nox's reporting stops in May 2023 — the month after the April 2023 polygraph/police operation on
   packing staff (§3). Whether the monthly stock files continued after that is unknown from here.

### 1.3 The FNB online-banking rebuild and the complete FNB account list, 26 Sep – 5 Oct 2023

Six weeks before Peter's R5,000,000 moved into his Money Maximiser (16 Nov 2023), the FNB online-banking
profile was rebuilt from scratch. Unrecorded (Vukeya appears in the repos only as a name printed on a
2024 statement).

- 26 Sep 2023, Jax → Rynette, cc Pete: "We have pretty much had to start over again with the online
  banking … account NAMES next to the account numbers … all the money market and money on call accounts."
  **Her list of 15 FNB accounts** — SLG 62432501494 / 62593375829 / 62839612323 (EUR CFC); RWD
  62323196362 / 62836164880; RST 55270035642 / 62134839127 / 62839603835 (USD CFC); VVA 62423540807 /
  62812835744; PF Money Maximiser 62742245617; and 62027933606, 55270018789, 62060760404, 62012990132.
- 27 Sep 2023, Rynette's reply: "Here is the list with all the names. **The last four accounts are unknown
  to me**, so I presume it must be all your personal accounts." Those four are JF personal, PF personal,
  **CorpClo 2065 (62060760404) and Aymac International (62012990132)** per fincosys `MASTER_ACCOUNTS.json`
  — i.e. the bookkeeper disclaims knowledge of two business accounts. The names list itself was an
  attachment (absent). `<DB9PR08MB656909C1D13B71CF3ACC1BACBAC2A@…>` sha256 c2de5348…
- **All 15 accounts are in fincosys `MASTER_ACCOUNTS.json` and have canonical directories** — a
  contemporaneous owner-side validation of the registry's FNB layer.
- 2 Oct 2023, Rynette: statements for **15/09/2023 – 02/10/2023 on all eleven business accounts** (the
  window of the rebuild). `<DB9PR08MB65695DA1742D979135415F87BAC5A@…>` sha256 82a19274…
- 2 Oct 2023, Peter → FNB (Musa Vukeya, Patricia Sithole): "You dropped the call when you knew **my
  accountant and I** needed you on Friday … we had SARS amongst others to pay … **Please ALWAYS copy
  Pete@regima.com into all e-mails. The pass codes must always be sent via sms to me, not to our
  e-mails.**" Face-to-face training 5 Oct 2023 at 20 River Road, Morninghill.
  `<286001d9f516$75fb0110$61f10330$@regima.com>` sha256 59dfe2ef…; `<2b7b01d9f519$…>` sha256 c48e7a0c…

Relevance: (a) from Oct 2023 the online-banking OTPs for the business profile were directed to Peter's
phone by his own written instruction — a dated fact for the impersonation dilemma and for any "Peter does
not use email/computers" assertion (he writes these emails himself from pete@regima.com); (b) the
statement set Rynette requested for 15 Sep – 2 Oct 2023 is a defined window to pull from fincodat;
(c) the 16 Nov 2023 R5M/R3M movements follow the new profile, not the old one.

### 1.4 Insurance claim M220735 — damaged EU packaging, Mar–Jun 2023

Freight-insurance claim via Prestgroup / C&W Clearing for an export (DAP terms) to the Belgian
distributor (regima.eu, Michiel De Meulemeester). Payout to RegimA required the consignee's letter of
authority (31 Mar 2023, Rynette asks Michiel for it). Rynette's 25 Apr 2023 letter, endorsed by Jax
("a very good and correct letter"): the boxes sent back were EU packaging to be replaced, "Regima have
to replace all these boxes which cost a lot of money … This EU packaging cost a lot more than the SA
packaging". Still unresolved 9 Jun 2023 ("RegimA – Repackaging claim – M220735").
`<DB9PR08MB656956E5548197F2B304F6F8BA8F9@…>` sha256 eb772767…; `<DB7PR08MB3306EBA949281A8FB25489C1AC649@…>` sha256 e48e66b4…

Relevance: a documented 2023 destruction/replacement event on **EU-variant packaging** — the very codes
the Prime tracker flags as "EU packaging run to zero 2018–2022 with no EU sales printed" — and a
possible insurance receipt to look for in RWD/SLG bank data in mid-2023. Unrecorded in any repo.

### 1.5 Minor: the 2015 origin of the Villa Via loan-account treatment

30 Mar 2015, Bantjes (then at Servest) to Bernadine Wright, cc Peter and Jacqui: RegimA pays Villa Via's
municipal account; book it as a **loan account to Villa Via under Other Current Assets** in RegimA's
books. The RWD↔VVA account that moves by −R17,382,021.05 at 29 Feb 2024 descends from this design.
Context only; the Feb 2024 movement itself is outside the archive window.

---

## 2. Already recorded — native copies confirm, nothing to add

- **Ketoni / Baker McKenzie, 19 Apr – 2 Jun 2023** (Zoom 20 Apr with Bantjes, Pete, Kevin Derrick; Da Silva's
  Trust Property Control Act briefing; Bantjes 21 Apr "R10mil fine"; George Group's acquisition of the
  Quatro Group closed 16 May 2023 with Ketoni as shareholder; "reportable arrangement" and "section 8E"
  submissions needing the signed agreements; 9 May "allocate the Ketoni payment to Pete's shareholder
  loan account") — all in `evidence/ketoni/`, `docs/exchange-evidence/ketoni_motive.md`, EVENT_108/116.
- **Guaiazulene, Jan–Mar 2023** (Connock GBP 3,135/kg vs US$970/kg through Addarory, 15 Feb; Prime QC's
  Shandong Chuangying COA mismatch 16 Mar) — `BOM_EMAIL_EVIDENCE_2026_07_08`, `CROSS_REPO_FINDINGS_SYNC`.
- **D&K Management / Intrigue polygraphs, Mar–Apr 2023** (78 messages, incl. "Brief synopsis stealing at
  Regima" and the Krause resignation exchange of 14 Apr 2023, where Rynette writes of "the on-going
  stealing of stock … sku's of stock going missing and thousands of Rand losses") — recorded and
  **deliberately gated** in `ANNEXURES/JF19…/README.md` (non-party staff, POPIA). Left as is.
- **Witz Inc / "Cosmetology" matter, May–Aug 2023** — 50 repo hits.

## 3. Searched and absent (full decoded text, whole archive)

`5400/000`; "journal 789" or any journal reference of 22 Nov 2023; "Trs Dr H"; account 5466 (34 raw hits
are invoice/order numbers); SIN30813 / SI306198 / SIN30634; R17,383,567.17; R17,382,021.05;
R11,919,268.89; R246,372,00x; 63077691682 (the Money Maximiser number never appears — the Sep 2023 list
predates its opening); Nedbank 1648185185 ("Prime Regima" appears only in 8 FNB payment notifications,
2020–21); "Hannelle Evert" / SAIBA16721 (the 87 raw hits for "Hannelle" are the word *channelled*);
"manufacture an answer"; "main trustee"; J417 (one hit, a tweet); "two big intercompany invoices";
`members loan` only as a 22 Sep 2023 payment note (R4,809.62 Ekurhuleni + R1,307 Tshwane rates
"MEMBERS LOAN ACCOUNT Pay expenses"). Several of these are simply after the archive's end.

## 4. Suggested follow-ups

1. Record §1.1 as the authority document for the 28 Jun 2022 conversion (caselex authority register);
   request the 24 Jun 2022 instruction PDF from the Exchange sync database (attachment-sync).
2. Add the 9 Feb 2023 River Road count and the Jan–May 2023 monthly stock files to
   `STOCK_COUNT_CLAIM_CORRECTION_2026_08_15`; add River Road/V.B as a raw-material holder in the ledger;
   request the five monthly files and the two Prime collection notes (attachments).
3. Record §1.3 (FNB profile rebuild; OTPs to Peter; 15-account list) as an event; pull the 15 Sep –
   2 Oct 2023 statements for the eleven business accounts from fincodat as the matching exhibit.
4. Search RWD/SLG bank data Apr–Aug 2023 for a Prestgroup/insurer receipt against claim M220735.
5. The decoded corpus (`scratchpad/corpus/`, 88 files, ~700 MB, 405,422 records keyed by path) is
   reusable for further full-text passes this session; it is not in any repo.
