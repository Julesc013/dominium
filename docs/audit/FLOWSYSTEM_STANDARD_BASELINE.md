Status: BASELINE
Last Reviewed: 2026-02-28
Version: 1.0.0
Scope: ABS-3 FlowSystem substrate hardening.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# FlowSystem Standard Baseline

## 1) Solver Behavior
- Core flow engine now supports deterministic channel-tick execution ordered by `channel_id`.
- Tier-0 bulk solver enforces explicit capacity, delay, loss, priority, and overflow policy.
- Deterministic budget degradation processes only the first budgeted channels and defers the rest.

## 2) Capacity/Loss Semantics
- `capacity_per_tick` limits transferable amount.
- `loss_fraction` is applied with fixed-point deterministic rounding.
- Overflow policy is explicit per solver policy: `refuse|queue|spill`.

## 3) Ledger Integration
- Conserved quantity flows return explicit loss records for RS-2 exception/transformation handling.
- MAT logistics continues to emit shipment provenance events and RS-2 exception accounting for loss cases.

## 4) Migration Summary
- MAT logistics transfer execution now routes through core `FlowChannel` tick logic.
- Manifest lifecycle semantics remain unchanged (`planned|in_transit|delivered|lost|failed`).
- Existing refusal codes and deterministic fingerprints remain preserved.

## 5) Inspection + Overlay Integration
- Inspection adds channel-level flow summary and flow utilization sections.
- Logistics overlay colors edges by utilization with deterministic procedural color mapping.

## 6) Partition Hooks
- Flow channel ticks can emit deterministic cross-shard flow transfer plans from partition metadata.
- Hooks are structural only; no networking side effects are introduced.

## 7) Extension Notes
- INT can bind air/water/pressure channels to the same flow substrate using quantity IDs.
- SIG can bind non-conserved signal propagation channels without duplicating flow math.
- ECO can bind monetary/influence channels with policy-defined ledger treatment.

## 8) Gate Snapshot (2026-02-28)
1. RepoX PASS
   - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: pass (`status=pass`, findings=1 warn)
2. AuditX run
   - command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
   - result: pass (`status=pass`, findings=1684 warns; repo-wide existing warnings retained)
3. TestX PASS
   - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.core.flow_bulk_deterministic,testx.core.flow_loss_deterministic,testx.core.flow_budget_degrade_deterministic,testx.materials.flow_migration_equivalence,testx.core.cross_shard_flow_plan_deterministic`
   - result: pass (`selected_tests=5`, `cache_hits=0`, `cache_misses=5`)
4. strict build PASS
   - command: `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.abs3 --cache on --format json`
   - result: pass (`result=complete`, `bundle_id=bundle.base.lab`)
5. ui_bind --check PASS
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
   - result: pass (`result=complete`, `checked_windows=21`)
