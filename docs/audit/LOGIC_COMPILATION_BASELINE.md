Status: DERIVED
Last Reviewed: 2026-03-08
Supersedes: none
Superseded By: none
Scope: LOGIC-6 deterministic compilation, proof, runtime selection, and SYS collapse integration.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# LOGIC Compilation Baseline

## Summary

LOGIC-6 completes the lawful compilation and collapse layer for validated `LogicNetworkGraph` networks.

The baseline is:
- deterministic
- proof-gated
- validity-domain bounded
- compute-budgeted
- explicit about fallback and forced expand
- replay-verifiable
- integrated with SYS macro capsules without changing LOGIC semantics

## Compile Targets And Policies

Supported exact targets:
- `compiled.reduced_graph`
  - canonical reduced program for general validated networks
- `compiled.lookup_table`
  - exhaustive bounded input enumeration for small combinational networks
- `compiled.automaton`
  - bounded explicit-state exploration for sequential networks

Registered compile policies:
- `compile.logic.default`
  - `max_lookup_input_width = 8`
  - `max_state_space_nodes = 256`
  - `allow_bounded_error = false`
- `compile.logic.lab`
  - `max_lookup_input_width = 12`
  - `max_state_space_nodes = 1024`
  - `allow_bounded_error = true`
- `compile.logic.rank_strict`
  - `max_lookup_input_width = 6`
  - `max_state_space_nodes = 128`
  - `allow_bounded_error = false`

Selection remains deterministic:
- canonical source serialization
- stable target choice by eligibility and policy
- identical source hash plus identical compile policy yields identical compiled payload hash and compiled model id

## Proof Methods

Required proof methods:
- `compiled.reduced_graph`
  - exact structural equivalence hash proof
- `compiled.lookup_table`
  - exact exhaustive lookup-table proof over canonical lexicographic input enumeration
- `compiled.automaton`
  - exact explored-state hash plus transition-table hash proof

Proof surfaces retained in replay/proof bundles:
- `compile_result_hash_chain`
- `compiled_model_hash_chain`
- `equivalence_proof_hash_chain`
- `logic_compile_policy_hash_chain`
- `forced_expand_event_hash_chain`

No compiled execution is lawful without a proof row that verifies.

## Runtime Selection Rules

Compiled execution is selected only when:
- the network binding names a compiled model
- the equivalence proof exists and verifies
- the validity domain exists and matches the current validation hash
- the compiled source hash still matches the network binding
- instrumentation has not forced a debug expand

When the compiled path is invalid:
- runtime logs explicit fallback
- runtime emits `explain.logic_compiled_invalid`
- runtime forces expand through SYS-style forced-expand records when needed
- silent fallback is forbidden

Debug inspection remains instrumentation-gated:
- lawful debug requests require a logic analyzer instrument and access-policy approval
- compiled introspection remains derived and compactable
- authoritative inspection forces expand back to L1

## SYS Integration Rules

LOGIC controllers can collapse into SYS through:
- `template.logic_controller`
- `macro.logic_controller.compiled`

Collapsed execution remains lawful only while the compiled model stays inside its validity domain.

Forced expand triggers include:
- compiled validity-domain violation
- missing or mismatched proof/source hash
- debug inspection request
- timing or oscillation anomalies inherited from LOGIC-5 gates

Expand restores:
- full network graph
- explicit state vectors
- standard L1 `Sense -> Compute -> Commit -> Propagate` execution

## Coverage Evidence

Target coverage sealed by TestX:
- `test_compile_reduced_graph_deterministic`
  - reduced-graph compilation stable across repeated compiles
- `test_compile_lookup_table_exactness_small`
  - lookup-table enumeration and exact proof preserved
- `test_compile_automaton_state_exploration_deterministic`
  - automaton state exploration and transition proof stable
- `test_runtime_prefers_compiled_when_valid`
  - compiled path selected when validity checks pass
- `test_invalid_compiled_falls_back_logged`
  - invalid compiled path falls back explicitly and logs explain/forced expand
- `test_replay_compiled_vs_l1_hash_match`
  - compiled replay matches L1 output/state hashes on bounded fixtures

## Stress Harness

Baseline compile stress lane:
- tool:
  - `python tools/logic/tool_run_logic_compile_stress.py --repo-root . --element-pairs 24 --tick-count 8 --out-json docs/audit/LOGIC6_COMPILE_STRESS.json`
- scenario:
  - deterministic 48-element compiled logic network based on the LOGIC-4 stress topology
  - compiled replay compared directly against L1 replay
- result:
  - `compiled_type_ids = ["compiled.reduced_graph"]`
  - `compiled_path_observed = true`
  - `signals_match = true`
  - `states_match = true`
  - `tick_signal_match = true`
  - `max_elements_evaluated = 48`
  - `max_compute_units_used = 148`
  - `compile_result_hash_chain = 8466659baacc9a747159755e4a0acdcebec737c432da69c261095bb4dee7c653`
  - `compiled_model_hash_chain = 86f307b5a675184269daa7c487e1b114a5638c909f7df80f73aff9ad8ea4c423`
  - `equivalence_proof_hash_chain = 7f6926603b3d0cfb49be0b7706ee97d2a0887b7ce93cb85bf25ec4a9c7033344`
  - `logic_compile_policy_hash_chain = 131f92331d7f3bfd339bce78fe2fae506db382e07fb4702b0927b9fbff4ad8d1`
  - `forced_expand_event_hash_chain = 4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
  - `deterministic_fingerprint = d681b4fd34600a50c89465f380fc1d1914e998c0d3fadf5ba611f05ded8da86c`

## Validation Seal

- topology map refreshed
  - fingerprint: `2e8c5618bf4272de04a6e10da04f0ea56dc6d32c853ed599ab45a4a25563b39f`
  - size: `2288994` bytes
- `AuditX STRICT`
  - pass with `findings = 2225`, `promoted_blockers = 0`
- `TestX STRICT` targeted LOGIC-6/topology subset
  - pass with `selected_tests = 9`
- strict build
  - `canonical_content_hash = 9cdabc6762b207303ef749adddf995b3fe64fe1d0605241cf417330f1966e2b5`

## Readiness

Ready for LOGIC-7:
- compiled introspection and debug-driven forced expand seams exist
- replay bundles already preserve compile/proof hash chains for analyzer tooling

Ready for LOGIC-8:
- validity-domain gates and explicit fallback paths provide the seam for future fault/noise invalidation
- bounded-error compile policy remains explicit and off by default outside policy-gated lab use
