Status: DERIVED
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: RS-3/5 time constitution baseline
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Time Constitution Baseline

## Delta-Time Policies
- Canonical coordinate remains `simulation_time.tick` (`u64`) and is authoritative for deterministic ordering.
- `dt_sim` is per-tick metadata (`time_tick_log[].dt_sim_permille`) produced by deterministic quantization rules.
- Policy set in current registry:
  - `time.policy.null`: fixed single-tick dt, pause allowed, rate change disabled.
  - `time.policy.default_realistic`: variable dt allowed, deterministic quantization via `dt.rule.standard`, branching allowed by policy extension.
  - `time.policy.rank_strict`: constrained variable dt range, no pause, branching forbidden.

## Checkpoint and Compaction Strategy
- Checkpoints are generated deterministically on tick cadence from `checkpoint_interval_ticks`.
- Checkpoint artifacts include canonical anchors: truth hash, ledger hash, pack lock hash, registry hashes.
- Intent logs are chunked deterministically by tick ranges.
- Compaction is deterministic and policy-driven:
  - keep every Nth checkpoint (plus terminal checkpoint)
  - merge intent log chunks deterministically
  - optional run-meta pruning by deterministic threshold
- Compaction preserves canonical replay outputs for retained history.

## Branching Semantics
- Time travel is lineage branching only, not in-place mutation.
- `process.time_branch_from_checkpoint` is law/policy-gated and ranked-forbidden.
- `tools/time/tool_time_branch_from_checkpoint.py` + `sessionx.time_lineage.branch_from_checkpoint(...)` create explicit branch artifacts:
  - `branch_id`
  - `parent_save_id`
  - `parent_checkpoint_id`
  - `divergence_tick`
  - `new_save_id`
- Branching copies parent save state into a new save lineage and keeps parent immutable.

## Multiplayer Constraints
- Handshake includes `time_control_policy_id` compatibility checks.
- Lockstep and authoritative/hybrid policy contexts resolve and enforce deterministic time policy state.
- Unauthorized time-control attempts emit anti-cheat signal `ac.time_control.unauthorized_change_attempt` and deterministic refusal behavior.
- Ranked policy forbids branch creation.

## Guardrails Added
- RepoX invariants:
  - `INV-NO-WALLCLOCK-IN-TIME-ENGINE`
  - `INV-TIME_BRANCH_IS_LINEAGE`
- AuditX analyzers:
  - `E44_WALL_CLOCK_TIME_USAGE_SMELL`
  - `E45_NONDETERMINISTIC_CHECKPOINT_SMELL`

## TestX Coverage Added
1. `test_variable_dt_determinism`
2. `test_pause_resume_determinism`
3. `test_checkpoint_interval_deterministic`
4. `test_branching_creates_new_lineage`
5. `test_ranked_branch_forbidden`
6. `test_compaction_preserves_replay`

## Validation Snapshot (2026-02-26)
- RepoX PASS:
  - `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Result: `status=pass`, `findings=0`.
- AuditX run:
  - `py -3 tools/auditx/auditx.py scan --repo-root . --changed-only --format json --output-root build/auditx/rs3_final`
  - Result: `result=scan_complete`, `findings_count=1590`.
- TestX PASS (RS-3 required suite):
  - `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset testx.time.variable_dt_determinism,testx.time.pause_resume_determinism,testx.time.checkpoint_interval_deterministic,testx.time.branching_creates_new_lineage,testx.time.ranked_branch_forbidden,testx.time.compaction_preserves_replay`
  - Result: `status=pass`, `selected_tests=6`.
- strict build PASS:
  - `C:\Program Files\CMake\bin\cmake.exe --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game dominium_client`
  - Result: build completed for strict targets.
- `ui_bind --check` PASS:
  - `py -3 tools/xstack/ui_bind.py --repo-root . --check`
  - Result: `result=complete`, `checked_windows=21`.

## Extension Points
- Domain-level relativity/time dilation can layer on top of tick + deterministic dt metadata.
- Branch policy can be expanded by law/profile without enabling retroactive mutation.
- Checkpoint and compaction policies can be tuned per experience profile while preserving deterministic lineage semantics.
