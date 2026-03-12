Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Conservation Contracts and Exceptions

## Scope
This doctrine defines deterministic conservation accounting for aggregate simulation state. It adds auditable accounting and refusal guardrails without introducing new solver semantics.

## Conservation Items
A conserved quantity `Q` is tracked via an aggregate ledger channel.

- `ledger.mass_energy_total` (default realistic basis)
- `ledger.charge_total`
- `ledger.momentum_vector` (optional macro channel)
- `ledger.angular_momentum_vector` (optional macro channel)
- `ledger.ledger_balance` (economy-facing channel)
- `ledger.entropy_metric` (tracked; not enforced by default)

Ledgers are deterministic, aggregate, and scoped per tick per shard.

## Contract Modes per Quantity
Each quantity is governed by a mode in the active conservation contract set.

- `enforce_strict`: refuse net delta outside tolerance.
- `enforce_local`: same as strict, but boundary flux may be allowed when declared.
- `allow_with_ledger`: permit violations only when explicitly logged.
- `track_only`: never refuse; always log aggregate deltas.
- `ignore`: do not track and do not enforce.

## Explicit Exception Types
All violations must be explicit and attributable.

- `exception.boundary_flux`
- `exception.field_exchange`
- `exception.creation_annihilation`
- `exception.coordinate_gauge`
- `exception.numeric_error_budget`
- `exception.meta_law_override`

No silent conservation bypass is permitted.

## Attribution Contract
Every exception entry records:

- `tick`
- `shard_id`
- `domain_id`
- `process_id`
- `exception_type`
- `quantity_id`
- `delta` (signed fixed-point)
- `reason_code`
- `deterministic_fingerprint`

## Mass-Energy Equivalence Default
Default realistic universes conserve a combined channel: `ledger.mass_energy_total`.

Mass<->energy conversions must be logged as internal transfer events with zero net delta in the combined channel.

Alternate universes may choose separate conservation channels (`quantity.mass` and `quantity.energy`) by selecting a different contract set.

## Determinism and Cost
- Ledger accounting is aggregate (macro) by default.
- Entry ordering and hashes are deterministic.
- The exception ledger chains by `previous_ledger_hash` for replay/audit integrity.
