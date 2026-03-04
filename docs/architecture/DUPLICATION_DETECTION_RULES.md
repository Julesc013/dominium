# Duplication Detection Rules

Status: Canonical (ARCH-REF-1)
Version: 1.0.0

## Scope
Mechanical duplication detection applies to runtime-authoritative code under `src/` and authoritative tool paths under `tools/xstack/sessionx/`.

## Rule Set
1. Graph duplication
- Any new node/edge traversal engine outside `src/core/graph` is a violation.

2. Flow duplication
- Any ad-hoc debit/credit transfer loop outside FlowSystem (`src/core/flow`) or ledger pathways is a violation.

3. State duplication
- Boolean/state flags representing transitions without `StateMachineComponent` integration is a violation.

4. Schedule duplication
- Any recurring timing loop not backed by `ScheduleComponent` is a violation.

5. Hazard duplication
- Any accumulation/threshold consequence loop not backed by `HazardModel` is a violation.

6. Direct intent dispatch
- Any direct intent envelope dispatch outside canonical control/interaction intent pipeline surfaces is a violation.

7. Legacy reference
- Production/runtime code references to `legacy/` are a violation.

## Enforcement Integration
- RepoX rules enforce deterministic structural constraints in CI profiles.
- AuditX analyzers provide smell detection and actionable diagnostics.
- TestX includes deterministic verification that these constraints remain active.
