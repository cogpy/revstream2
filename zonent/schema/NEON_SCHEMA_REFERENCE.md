# Neon Database Schema Reference

## Connection Details

| Property | Value |
|----------|-------|
| **Project ID** | `calm-silence-72212970` |
| **Database** | `neondb` |
| **Region** | `us-east-2` (AWS) |
| **Branch** | `main` |
| **Engine** | PostgreSQL (Neon Serverless) |

## Schema Overview

| Schema | Tables | Purpose |
|--------|--------|----------|
| `entity_relation` | entities, relations | ER-ABM agent graph |
| `event_timeline` | events, state_machines, state_transitions, transactions | Discrete event simulation |
| `stock_flow` | variables, flows, feedback_loops, simulation_history | System dynamics |
| `hypergraph` | nodes, hyperedges, symbolic_rules, type_hierarchy | Neuro-symbolic inference |
| `integration` | entity_mappings, cross_references, analysis_snapshots | Cross-paradigm binding |
| `consolidated_accounts` | accounts, transactions, elimination_entries, membrane_summary, qbo_entity_mapping | Group consolidation |
| `fund_flow` | edges, anomalies, entities | Forensic fund tracing |
| `accountant_records` | trial_balances, annual_financial_statements, invoices, sars_vat_documents | Forensic audit |

> **Note**: the seven core schemas enumerated in `CLAUDE.md` end with `fund_flow`, whose
> tables are confirmed live in the fincosys audit cycles (see
> `fincosys/audit/AUDIT_REPORT_2026-05-09.md` and the KSM cycle reports probing
> `fund_flow.edges` / `fund_flow.anomalies` / `fund_flow.entities`). `accountant_records`
> is an additional forensic-audit ingestion schema documented here; verify it against the
> live Neon project before building against it.

## Extensions Required
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

> **The DDL below is a reference, not a runnable script.** Tables are created
> schema-qualified, but the accompanying index and foreign-key statements use bare table
> names, reproducing the upstream fincosys source. None of these tables exist in `public`,
> so running the file top-to-bottom under a default `search_path` will fail. `transactions`
> is additionally declared in two schemas (`event_timeline` here, and `consolidated_accounts`
> whose DDL lives in `model/membrane-coa/MEMBRANE_COA_SPEC.md` — itself unqualified, so it
> shares this problem), so an unqualified reference to it is ambiguous as well as
> unresolvable. Qualify the names when provisioning.

---

## Access Control

> **Status: requires policy review before provisioning.**

Every schema in this database holds forensic financial records, communications evidence, and
legal material relating to named individuals in active High Court proceedings (case
2025-137857 — sourced from `cogpy/ad-res-j7`, the case-management repository for this
matter; this file is not the origin of that number).

The DDL below specifies **no access control whatsoever** — no
`ALTER TABLE ... ENABLE ROW LEVEL SECURITY`, no policies, no grants. Whatever subset of it
you successfully provision is readable in full by any role holding a connection string,
including `evidence` (with OCR text), `timeline_events`, `cases`, and
`integration.analysis_snapshots`.

Requirements for any deployment provisioned from this reference:

1. **Enable RLS on every table in every schema listed in the Schema Overview above.** Two of
   them have no DDL in this file: `consolidated_accounts` is defined in
   `model/membrane-coa/MEMBRANE_COA_SPEC.md`, and `accountant_records` is not transcribed
   anywhere in this repo — so this requirement spans documents and cannot be satisfied by
   reading this file alone. It also covers the unqualified tables in the Enhanced Schema
   section below. Note the Schema Overview's own caveat: `CLAUDE.md` enumerates seven schemas
   and its Purpose line says five, so the exact set is unsettled. This requirement is
   deliberately phrased against *whatever schemas actually exist* rather than a fixed count,
   so a miscount cannot leave one unprotected.
2. **Default deny.** RLS with no policy denies all access to non-owner roles; add policies
   explicitly rather than relying on a permissive default.
3. **Separate the service role from human roles.** Sync pipelines (fincosys Stage 6a) need
   broad write access; analyst and reporting roles should not inherit it.
4. **Do not grant `authenticated` blanket read** over evidence or accountant records.
   Scope reads to the entities a principal is authorised for.
5. **Audit reads, not just writes.** For evidence tables, read access is itself material to
   chain of custody.

The concrete policy set is a decision for whoever owns the Neon project — it depends on the
role model in use (Neon native roles vs a Supabase-style `service_role`/`authenticated`
split), which is not recorded anywhere in this repo. It is deliberately not invented here,
because a wrong-but-runnable policy on forensic evidence is worse than an explicit gap.
Replace this paragraph with the agreed `CREATE POLICY` set once settled.

---

## ENTITY_RELATION Schema

### entities
```sql
CREATE TABLE entity_relation.entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    description TEXT,
    state TEXT,
    metadata JSONB DEFAULT '{}',
    attributes JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_entities_active ON entities(is_active);
CREATE INDEX idx_entities_created_at ON entities(created_at DESC);
CREATE INDEX idx_entities_name_gin ON entities USING gin(to_tsvector('english', name));
CREATE INDEX idx_entities_state ON entities(state);
CREATE INDEX idx_entities_attributes ON entities USING gin(attributes);
```

### relations (entity_relation schema)
```sql
CREATE TABLE entity_relation.relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES entities(id),
    target_id UUID REFERENCES entities(id),
    relation_type TEXT NOT NULL,
    weight DECIMAL(3,2),
    attributes JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_relations_source ON relations(source_id);
CREATE INDEX idx_relations_target ON relations(target_id);
CREATE INDEX idx_relations_type ON relations(relation_type);
```

### entity_relationships (enhanced schema)
```sql
CREATE TABLE entity_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
    target_entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,
    strength DECIMAL(3,2),
    evidence_ids UUID[],
    temporal_data JSONB,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### entity_versions
```sql
CREATE TABLE entity_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    version_date TIMESTAMP NOT NULL,
    entity_data JSONB NOT NULL,
    compliance_status JSONB,
    change_description TEXT,
    changed_by TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## EVENT_TIMELINE Schema

### events
```sql
CREATE TABLE event_timeline.events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    payload JSONB DEFAULT '{}',
    caused_by UUID,
    transaction_index VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_entity ON events(entity_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_payload ON events USING gin(payload);
CREATE UNIQUE INDEX idx_events_tx_index ON events(transaction_index);
```

### state_machines
```sql
CREATE TABLE event_timeline.state_machines (
    id TEXT PRIMARY KEY,
    machine_type TEXT NOT NULL,
    current_state TEXT NOT NULL,
    attributes JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### state_transitions
```sql
CREATE TABLE event_timeline.state_transitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    state_machine_id TEXT REFERENCES state_machines(id),
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    triggered_by UUID,
    timestamp TIMESTAMPTZ NOT NULL,
    metadata JSONB DEFAULT '{}'
);

-- Index
CREATE INDEX idx_transitions_timestamp ON state_transitions(timestamp);
```

### transactions
```sql
CREATE TABLE event_timeline.transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_index VARCHAR(20) UNIQUE,
    account_number VARCHAR(20),
    statement_number INTEGER,
    sequence_number INTEGER,
    transaction_date DATE,
    description TEXT,
    amount DECIMAL(15,2),
    transaction_type TEXT,
    balance_after DECIMAL(15,2),
    category TEXT,
    counterparty TEXT,
    entity_code VARCHAR(10),
    currency VARCHAR(3) DEFAULT 'ZAR',
    payload JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(account_number, statement_number, sequence_number)
);

-- Indexes
CREATE INDEX idx_tx_account ON transactions(account_number);
CREATE INDEX idx_tx_statement ON transactions(statement_number);
CREATE INDEX idx_tx_date ON transactions(transaction_date);
CREATE INDEX idx_tx_type ON transactions(transaction_type);
CREATE INDEX idx_tx_category ON transactions(category);
CREATE INDEX idx_tx_counterparty ON transactions(counterparty);
CREATE INDEX idx_tx_entity ON transactions(entity_code);
```

---

## STOCK_FLOW Schema

### variables
```sql
CREATE TABLE stock_flow.variables (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    variable_type TEXT NOT NULL,
    initial_value DECIMAL(15,2),
    current_value DECIMAL(15,2),
    unit TEXT DEFAULT 'ZAR',
    description TEXT,
    equation TEXT,
    account_id TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_vars_type ON variables(variable_type);
CREATE INDEX idx_vars_account ON variables(account_id);
```

### flows
```sql
CREATE TABLE stock_flow.flows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_stock TEXT REFERENCES variables(id),
    target_stock TEXT REFERENCES variables(id),
    current_rate DECIMAL(15,4),
    unit TEXT DEFAULT 'ZAR/day',
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_flows_source ON flows(source_stock);
CREATE INDEX idx_flows_target ON flows(target_stock);
```

### feedback_loops
```sql
CREATE TABLE stock_flow.feedback_loops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    loop_type TEXT NOT NULL,
    variables TEXT[] NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### simulation_history
```sql
CREATE TABLE stock_flow.simulation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_name TEXT NOT NULL,
    time_step DECIMAL(10,2),
    state JSONB DEFAULT '{}',
    variable_id TEXT,
    value DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX idx_simhist_name ON simulation_history(simulation_name);
```

---

## HYPERGRAPH Schema

### nodes
```sql
CREATE TABLE hypergraph.nodes (
    id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    label TEXT NOT NULL,
    attributes JSONB DEFAULT '{}',
    embedding REAL[],
    truth_strength DECIMAL(3,2) DEFAULT 1.0,
    truth_confidence DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_nodes_type ON nodes(node_type);
```

### hyperedges
```sql
CREATE TABLE hypergraph.hyperedges (
    id TEXT PRIMARY KEY,
    edge_type TEXT NOT NULL,
    node_ids TEXT[] NOT NULL,
    roles JSONB DEFAULT '{}',
    attributes JSONB DEFAULT '{}',
    truth_strength DECIMAL(3,2) DEFAULT 1.0,
    truth_confidence DECIMAL(3,2) DEFAULT 1.0,
    tensor_representation REAL[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_hedges_type ON hyperedges(edge_type);
CREATE INDEX idx_hedges_nodes ON hyperedges USING gin(node_ids);
```

### symbolic_rules
```sql
CREATE TABLE hypergraph.symbolic_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    head_predicate TEXT,
    head_variables TEXT[],
    body JSONB,
    confidence DECIMAL(3,2),
    tensor_notation TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### type_hierarchy
```sql
CREATE TABLE hypergraph.type_hierarchy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subtype TEXT NOT NULL,
    supertype TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## INTEGRATION Schema

### entity_mappings
```sql
CREATE TABLE integration.entity_mappings (
    canonical_id TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    agent_model_id TEXT,
    event_model_id TEXT,
    dynamics_model_id TEXT,
    hypergraph_node_id TEXT,
    attributes JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX idx_mappings_type ON entity_mappings(entity_type);
```

### cross_references
```sql
CREATE TABLE integration.cross_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference_type TEXT NOT NULL,    -- 'OWNERSHIP' | 'TRANSACTION' | 'FEE'
    entities TEXT[] NOT NULL,
    model_references JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX idx_xref_type ON cross_references(reference_type);
```

### analysis_snapshots
```sql
CREATE TABLE integration.analysis_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_type TEXT NOT NULL,
    entity_id TEXT,
    snapshot_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX idx_snapshots_type ON analysis_snapshots(analysis_type);
```

---

## Enhanced Schema (ad-res-j7)

> **Owning schema not established.** The tables in this section — together with
> `entity_relationships` and `entity_versions` above — are declared without schema
> qualification and appear in no row of the Schema Overview, so it is not recorded which
> schema they belong to. The Access Control section requires RLS on `evidence`,
> `timeline_events` and `cases`; that requirement **cannot be actioned until their owning
> schema is established**. Resolve against the deployed project before provisioning.

### evidence
```sql
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    file_path TEXT,
    file_hash TEXT UNIQUE,
    file_type TEXT,
    file_size BIGINT,
    source TEXT,
    date_obtained DATE,
    date_created DATE,
    classification TEXT,
    sensitivity_level TEXT,
    metadata JSONB DEFAULT '{}',
    extracted_entities UUID[],
    ocr_processed BOOLEAN DEFAULT FALSE,
    ocr_text TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### timeline_events (enhanced)
```sql
CREATE TABLE timeline_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_date DATE NOT NULL,
    event_time TIME,
    title TEXT NOT NULL,
    description TEXT,
    event_type TEXT,
    significance TEXT,
    entities_involved UUID[],
    evidence_ids UUID[],
    location TEXT,
    metadata JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### cases
```sql
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_number TEXT UNIQUE NOT NULL,
    case_name TEXT NOT NULL,
    case_type TEXT,
    status TEXT DEFAULT 'active',
    description TEXT,
    start_date DATE,
    end_date DATE,
    jurisdiction TEXT,
    court TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Materialized Views

```sql
CREATE MATERIALIZED VIEW entity_statistics AS
SELECT entity_type, COUNT(*) as total_count,
       AVG(confidence_score) as avg_confidence,
       COUNT(CASE WHEN is_active THEN 1 END) as active_count
FROM entities GROUP BY entity_type;

CREATE MATERIALIZED VIEW timeline_summary AS
SELECT DATE_TRUNC('month', event_date) as month,
       event_type, COUNT(*) as event_count,
       AVG(confidence_score) as avg_confidence
FROM timeline_events GROUP BY DATE_TRUNC('month', event_date), event_type;
```

## Triggers

All tables with `updated_at` have auto-update triggers:
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;
```

## SQL Batch Files (fincosys)

| File | Lines | Content |
|------|-------|----------|
| 01_entities.sql | 2,645 | Entity INSERT statements |
| 02_relations.sql | 249 | Relation INSERT statements |
| 03_events.sql | 3,740 | Event INSERT statements |
| 04_state_machines.sql | 100 | State machine definitions |
| 05_state_transitions.sql | 1,065 | State transition records |
| 06_variables.sql | 55 | Stock-flow variables |
| 07_flows.sql | 28 | Flow definitions |
| 08_simulation_history.sql | 66 | Simulation snapshots |
| 09_hg_nodes.sql | 1,735 | Hypergraph nodes |
| 10_hyperedges.sql | 570 | Hyperedge definitions |
| 11_symbolic_rules.sql | 56 | Inference rules |
| 12_entity_mappings.sql | 531 | Cross-paradigm mappings |
| 13_cross_references.sql | 80 | Cross-model references |
| 14_analysis_snapshots.sql | 36 | Analysis results |
| integrated_entities.sql | 549 | Consolidated upserts |
| **Total** | **~11,505** | |
