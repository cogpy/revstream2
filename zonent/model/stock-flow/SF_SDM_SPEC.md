<!-- withdrawn-claims-banner -->
> ⛔ **This file contains claims since withdrawn or corrected (flagged 2026-10-10).** Do not reuse them; use the corrections:
> - corrected (`stock-stolen`): The R5,241,372.98 SLG write-off is an accounting residue (no FY2025 manufacture journal; 96.62% reconciled, GL-confirmed). Do not plead it as stolen or missing goods.
> Register and sources: `docs/strategic/WITHDRAWN_CLAIMS_REGISTER.json` (cogpy/ad-res-j7).

# Stock-Flow: System Dynamics Model (SF-SDM) Specification

## Overview

The SF-SDM paradigm implements a **system dynamics model** for inventory and cash flow
analysis with stocks, flows, auxiliary calculations, and feedback loops. It enables
continuous-time simulation of financial system behavior.

## Variable Types

```
STOCK      # Accumulated quantities (account balances, accumulated fees)
FLOW       # Rates of change (income/expense/fee rates in ZAR/day)
AUXILIARY  # Computed values (fee_burden_ratio, account_health_index)
CONSTANT   # Fixed parameters
EXOGENOUS  # External inputs
```

## Core Classes

### Variable
```python
@dataclass
class Variable:
    name: str
    var_type: VariableType       # STOCK | FLOW | AUXILIARY | CONSTANT | EXOGENOUS
    initial_value: float
    current_value: float
    unit: str = "ZAR"
    description: str
    equation: Optional[Callable] # For AUXILIARY variables
    history: List[Tuple[float, float]]  # (time, value)
```

### Flow
```python
@dataclass
class Flow:
    name: str
    source_stock: Optional[str]  # None = inflow from outside system
    target_stock: Optional[str]  # None = outflow to outside system
    rate_equation: Callable
    current_rate: float
    unit: str = "ZAR/day"
    description: str
    history: List[Tuple[float, float]]
```

### FeedbackLoop
```python
@dataclass
class FeedbackLoop:
    name: str
    loop_type: FeedbackType      # REINFORCING (positive) | BALANCING (negative)
    variables: List[str]         # Variable names in the loop
    description: str
```

## Simulation Loop

Each time step (dt = 1.0 day):

```
1. Compute Auxiliaries  -> Evaluate all AUXILIARY variable equations
2. Compute Flows        -> Calculate all FLOW rates from rate equations
3. Record State         -> Store current values in simulation_history
4. Update Stocks        -> Apply net flows: stock += (inflows - outflows) * dt
5. Advance Time         -> time += dt
```

## Key Metrics

| Metric | Formula | Unit |
|--------|---------|------|
| **account_health_index** | credits / (credits + debits + fees) | 0.0 - 1.0+ |
| **fee_burden_ratio** | total_fees / total_credits | 0.0 - 1.0 |
| **net_cash_flow** | total_credits - total_debits - total_fees | ZAR/month |

## Sample Data Points

| Account | Entity | Opening | Closing | Health | Fee Burden |
|---------|--------|---------|---------|--------|------------|
| 55270035642 | RST | R941,114 | R1,600,080 | 79% | 2.83% |
| 62012990132 | AYM | R39,778 | R43,212 | 79% | 2.83% |
| 62323196362 | RWD | R512,035 | R449,099 | 119% | 0.07% |
| 62836164880 | RWW MOC | R297,915 | R499,444 | 100% | 0.00% |
| 62060760404 | COR | - | - | 41% | 4.91% |

## Stock-Flow Diagram Structure

```json
{
    "stocks":     [{"name", "value", "unit", "description"}],
    "flows":      [{"name", "source", "target", "current_rate", "unit"}],
    "auxiliaries": [{"name", "value", "unit", "description"}],
    "constants":  [{"name", "value", "unit"}],
    "feedback_loops": [{"name", "loop_type", "variables", "description"}]
}
```

## Manufacturing BOM Relevance

The stock-flow model tracks:
- **Raw material stocks** (inventory accounts in SLG)
- **Finished goods stocks** (RST manufacturing output)
- **Intercompany transfer flows** (RST -> SLG -> RWD distribution)
- **R5.4M stock disappearance** (SLG: R13M debt to RST, R5.4M unaccounted)
- **Cost flow analysis** (purchases vs inventory vs COGS)

## Neon Schema

```sql
-- Schema: stock_flow
CREATE TABLE variables (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    variable_type TEXT NOT NULL,
    initial_value DECIMAL(15,2),
    current_value DECIMAL(15,2),
    unit TEXT DEFAULT 'ZAR',
    description TEXT,
    equation TEXT,
    account_id TEXT,
    updated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE flows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_stock TEXT REFERENCES variables(id),
    target_stock TEXT REFERENCES variables(id),
    current_rate DECIMAL(15,4),
    unit TEXT DEFAULT 'ZAR/day',
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE feedback_loops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    loop_type TEXT NOT NULL,       -- 'reinforcing' | 'balancing'
    variables TEXT[] NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE simulation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_name TEXT NOT NULL,
    time_step DECIMAL(10,2),
    state JSONB DEFAULT '{}',
    variable_id TEXT,
    value DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Source Files
- Model: `fincosys/models/stock_flow/system_dynamics_model.py`
- SQL: `fincosys/sql_batches/06_variables.sql` (55 lines)
- SQL: `fincosys/sql_batches/07_flows.sql` (28 lines)
- SQL: `fincosys/sql_batches/08_simulation_history.sql` (66 lines)
