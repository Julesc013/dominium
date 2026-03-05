# Compiled Model Constitution

Status: CANONICAL  
Last Updated: 2026-03-06  
Scope: COMPILE-0 universal compiled model framework.

## 1) Purpose

Define one deterministic framework for compilation across SYS, PROC, and LOGIC-adjacent workloads, so domains do not diverge into bespoke compiler pipelines.

Compiled models are optimization artifacts only. Correctness remains defined by uncompiled model/process execution.

## 2) CompiledModel Definition

A `CompiledModel` is a derived artifact that represents a functionally equivalent reduced form of a declared source.

Supported type families:

- `compiled.automaton`
  - reduced deterministic state-machine representation
- `compiled.lookup_table`
  - deterministic table approximation over declared input domain
- `compiled.reduced_graph`
  - pruned/constant-folded deterministic graph
- `compiled.ir`
  - bounded deterministic instruction representation

## 3) Equivalence Proof Requirements

A compiled model is usable only with a declared reproducible equivalence proof.

Required proof declarations:

- `proof_kind`: `exact | bounded_error`
- source input signature reference
- source output signature reference
- verification procedure id
- error bound policy id when `bounded_error`
- deterministic proof hash/fingerprint

Proof verification procedure must be deterministic and replayable.

## 4) Validity Domain Requirements

Each compiled model declares validity assumptions:

- input ranges
- timing constraints (optional)
- environmental constraints (optional)

Runtime contract:

- if current inputs are inside validity domain and proof is valid, compiled path may execute
- if violated, compiled model is invalidated and runtime must fall back or force expand

## 5) Runtime Use Contract

Domains may execute compiled forms only through framework hooks:

1. `compiled_model_is_valid(compiled_model_id, current_inputs)`
2. `compiled_model_execute(compiled_model_id, inputs)`

Domains must not introduce direct custom compiled execution bypasses.

Reference implementation location:

- `src/meta/compile/compile_engine.py` (framework-owned hook surface only; no domain-specific wiring in COMPILE-0)

## 6) Forced Expand / Fallback Triggers

Compiled execution must trigger expand/fallback when:

- validity domain violated
- error bound exceeded
- explicit debug/inspection request requires uncompiled path

Forced expand behavior must be logged and explainable.

## 7) Governance And Determinism

- Compilation must be deterministic:
  - stable ordering
  - stable serialization
  - stable fingerprints
- Compilation outputs are derived and compactable.
- Compilation is optional and never required for correctness.
- No domain may ship bespoke runtime compiler semantics outside this framework.

## 8) Non-Goals

- No LOGIC full compiler implementation in COMPILE-0.
- No wall-clock or nondeterministic compile/runtime selection.
- No semantic changes to source model/process behavior.
