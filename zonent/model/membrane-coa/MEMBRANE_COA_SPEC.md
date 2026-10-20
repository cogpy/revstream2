# Membrane Chart of Accounts: 4-Shell Topology Specification

## Overview

The Membrane CoA is a **4-shell topology** for group consolidation of 22+ entities.
Inspired by biological membrane theory, each shell represents a different boundary
of financial activity. The consolidation hub is **REZ (Rezonance)**.

## 4-Shell Structure

```
┌──────────────────────────────────────────────────────────────┐
│  ARENA (Shell 4)                                                 │
│  Code Range: 40100-69900                                         │
│  Entities: PORT, NEW (external parties)                          │
│  Treatment: SURVIVES consolidation                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  RELATIO (Shell 3)                                       │    │
│  │  Code Range: 10300-70400                                 │    │
│  │  Entities: RWD, VVA, FFT                                 │    │
│  │  Treatment: INTERCOMPANY ELIMINATION                     │    │
│  │                                                          │    │
│  │  ┌────────────────────────────────────────────────┐    │    │
│  │  │  AGENT (Shell 2)                                 │    │    │
│  │  │  Code Range: 10200-20200                         │    │    │
│  │  │  Entities: RST, RSA, SLG, REZ, RZA, RZI,        │    │    │
│  │  │            AYM, COR, RDH, RUK, KCH, KRN         │    │    │
│  │  │  Treatment: INCLUDED in group consolidation      │    │    │
│  │  │                                                  │    │    │
│  │  │  ┌──────────────────────────────────────┐    │    │    │
│  │  │  │  ARCHE (Shell 1)                         │    │    │    │
│  │  │  │  Code Range: 10100                       │    │    │    │
│  │  │  │  Entities: DJF, JF, PF (directors)       │    │    │    │
│  │  │  │  Treatment: EXCLUDED from consolidation   │    │    │    │
│  │  │  └──────────────────────────────────────┘    │    │    │
│  │  └────────────────────────────────────────────────┘    │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

> **Note on code ranges**: the shell code ranges above are indicative groupings from the
> 88-account REZ QBO chart of accounts and are **not disjoint** (Relatio's 10300-70400
> band overlaps Arena's 40100-69900). Shell membership is never derived from a numeric
> range alone: it is determined by the explicit per-entity assignments in this document
> and `registry/ENTITY_XERO_MAPPING.md`, and — for transactions — by the rule-based
> classifier (`fincosys/membrane_coa/scripts/classify_with_reconciliation.py`), which
> assigns shells 0-3 by entity and counterparty classification, not by account code.

## Entity Registry by Shell

### Arche (Personal Boundary)
| Code | Legal Name | Type | Role |
|------|-----------|------|------|
| DJF | Daniel James Faucitt | Natural Person | Director/Victim |
| JF | Jacqueline Faucitt | Natural Person | Director/Victim |
| PF | Peter Andrew Faucitt | Natural Person | Director/Perpetrator |

### Agent (Operational Core)
| Code | Legal Name | Type | Country |
|------|-----------|------|----------|
| RST | Regima Skin Treatments CC | CC | ZA |
| RSA | Regima SA Pty Ltd | Pty | ZA |
| SLG | Strategic Logistics CC | CC | ZA |
| REZ | Rezonance (Pty) Ltd | Pty | ZA |
| RZA | RegimA Zone Academy Ltd | Ltd | UK |
| RZI | RegimA Zone International | - | UK |
| AYM | AYMAC International CC | CC | ZA |
| COR | Corpclo 2065 CC | CC | ZA |
| RDH | RegimA Dr Harriet Ltd | Ltd | UK |
| RUK | RegimA UK Ltd | Ltd | UK |
| KCH | Kerchoonz Ltd | Ltd | UK |
| KRN | Karen Morris | Sole Trader | UK |

> **Known model gap (RWW)**: `registry/MASTER_ENTITIES.md` lists RWW (Regima Worldwide
> UK) as an organization with an active MOC account (62836164880), but RWW carries no
> shell assignment in the source fincosys model (`data/ENTITY_XERO_MAPPING.json` has no
> RWW entry; account 62836164880 is mapped under RWD in Relatio). Whether RWW is a
> distinct Agent-shell entity or an alias of RWD's UK operation is an open refinement
> question for the model owner — do not assume either treatment in consolidation logic.

> **Known model gap (FNB)**: `registry/MASTER_ENTITIES.md` lists FNB (First National Bank)
> as a financial institution, and it is the counterparty in the FEE cross-reference in
> `model/integration/CROSS_PARADIGM_SPEC.md`, but it carries no shell assignment here or in
> any registry. Its consolidation treatment is therefore undefined. Unlike the RWW gap above
> this one is not recorded upstream — it was identified in review of cogpy/zonent#9.

### Relatio (Inter-Entity)
| Code | Legal Name | Type | Significance |
|------|-----------|------|---------------|
| RWD | Regima Worldwide Distribution Pty Ltd | Pty | Distribution hub - NO independent revenue |
| VVA | Villa Via Arcadia No 2 CC | CC | Property rental - R22.8M capital extraction |
| FFT | Faucitt Family Trust | Trust | Trust vehicle - R2.85M violations |

### Arena (External)
| Code | Legal Name | Role |
|------|-----------|------|
| PORT | Portfolio (external) | External counterparties |
| NEW | New external | New external entities |

## 88-Account Chart of Accounts

The Membrane CoA defines 88 accounts provisioned in the REZ QBO consolidation hub,
structured across all 4 shells with proper intercompany elimination mapping.

## Consolidation Pipeline (6 Stages)

```
Stage 1: CoA       - Provision 88-account CoA in REZ QBO
Stage 2: Extract   - Pull trial balances from all entities
Stage 3: Transform - Classify accounts into membrane shells
Stage 4: Eliminate - Generate intercompany elimination journals
Stage 5: Report    - Consolidated P&L, BS, entity matrix
Stage 6: Bank-feed - Sync FNB transactions to REZ
```

## Intercompany Elimination

Total intercompany volume: **R58.58M** (largely unreconciled)

Key elimination pairs:
- RST <-> SLG (stock transfers, R13M loan)
- RST <-> RWD (distribution, revenue recognition)
- VVA <-> Group entities (rental charges, member loans)
- Trust <-> Beneficiaries (trust distributions, loans)

> Three of the four pairs above are quantified — RST<->SLG (R13M), VVA<->Group (R22.8M) and
> Trust<->Beneficiaries (R2.85M) — and `registry/ENTITY_XERO_MAPPING.md` supplies a fourth
> term that is **not** in the list above: REZ<->Group at R1.035M (IT services creditor).
> Those four total ~R39.7M against the stated R58.58M, leaving a ~R18.9M residual that
> corresponds to the one unquantified pair above, RST<->RWD. Note the terms are drawn from
> two documents, so the total is not reconstructible from this bullet list alone. Quantify
> the RST<->RWD leg before citing R58.58M as an auditable figure.

## Neon Schema

```sql
-- Schema: consolidated_accounts
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_number VARCHAR(20),
    account_name TEXT,
    entity_code VARCHAR(10),
    membrane_shell TEXT,           -- 'Arche' | 'Agent' | 'Relatio' | 'Arena'
    account_type TEXT,
    currency VARCHAR(3) DEFAULT 'ZAR',
    xero_org_name TEXT,
    qbo_realm_id TEXT,
    cipc_number TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_number VARCHAR(20),
    entity_code VARCHAR(10),
    membrane_shell TEXT,
    is_intercompany BOOLEAN DEFAULT FALSE,
    transaction_date DATE,
    amount DECIMAL(15,2),
    description TEXT,
    counterparty TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE elimination_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_entity VARCHAR(10),
    target_entity VARCHAR(10),
    amount DECIMAL(15,2),
    description TEXT,
    elimination_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Source Files
- Config: `fincosys/consolidation/scripts/config.py`
- Pipeline: `fincosys/consolidation/scripts/consolidate.py`
- Mapping: `fincosys/data/ENTITY_XERO_MAPPING.json` (v8.0)
- Migration: `fincosys/database/migrations/003_consolidated_accounts_entity_mapping.sql`
- Schema DDL: `fincosys/membrane_coa/scripts/schema_ddl.sql`
