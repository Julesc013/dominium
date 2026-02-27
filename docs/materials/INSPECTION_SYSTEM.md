Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, RS-5, ED-3, ED-4, MAT-0..MAT-8.

# Inspection System (MAT-9)

## Purpose
Define canonical, tier-aware inspection behavior as derived artifacts with deterministic caching, deterministic degradation, and epistemic safety.

## Core Principle
Inspection is a query-only process that produces an inspection snapshot artifact.
- Inspection never mutates authoritative TruthModel state.
- Inspection is process-driven and auditable.
- Inspection outputs are cacheable derived artifacts keyed by canonical inputs.

## Fidelity Levels
- `inspect.macro`
  - Aggregate summaries only.
  - Stock, flow, backlog, risk, and high-level causality summaries.
- `inspect.meso`
  - Adds structural/logistics/project graph details.
  - Includes deterministic commitment and event stream summaries.
- `inspect.micro`
  - Includes ROI micro part summaries from MAT-7 materialization only when law/entitlements and budget allow.
  - Deterministically degrades to meso if unavailable/forbidden.

## Questions Inspection Must Answer
- Current state:
  - material stocks
  - flows/manifests
  - AG/construction progress
  - maintenance backlog and failure risk summaries
- Causality:
  - linked commitments
  - linked events
  - available reenactment artifact references
- History:
  - bounded range summaries via event stream indices

## Budgeting and Degradation (RS-5)
Inspection execution is budgeted.
- Section-level cost units are deterministic.
- If requested fidelity exceeds budget:
  - deterministic degrade order: `micro -> meso -> macro`
- If strict-budget policy is enabled and macro cannot fit:
  - refuse with `refusal.inspect.budget_exceeded`
- Otherwise return best allowed degraded result.

## Cache Contract
Inspection snapshot cache key must include:
- `target_id`
- `truth_hash_anchor`
- requested fidelity
- epistemic policy identity
- section policy identity (if configured)

Repeated requests with equivalent inputs must return equivalent snapshot hashes.

## Epistemic Safety (ED-3 / ED-4)
Inspection output is filtered by authority and law.
- Diegetic view:
  - coarse indicators
  - quantized risk/wear/backlog
  - no hidden micro identity leakage
- Lab/admin view (law permitting):
  - deeper numeric detail
  - micro part IDs only when explicitly allowed

Outside ROI:
- micro part identity and hidden distributions must not be exposed.

## Causality Integration (MAT-8)
Inspection includes deterministic summaries and links for:
- commitments
- event stream indices
- reenactment artifacts

Inspection does not generate or alter canonical causality data except through explicit non-inspection processes.

## Time and History
Inspection may request bounded historical ranges.
- Uses existing compacted indices/artifacts.
- Must respect RS-3 compaction/checkpoint contracts.
- Time queries are deterministic for identical inputs.

## Multiplayer and Ranked
- Inspection requests are intents in authoritative/hybrid modes.
- Server computes snapshots and applies law/epistemic filters.
- Ranked profiles may cap max fidelity and max budget.
- Forbidden inspect attempts are explicitly refused and auditable.

## Refusal Codes
- `refusal.inspect.forbidden_by_law`
- `refusal.inspect.budget_exceeded`
- `refusal.inspect.target_invalid`