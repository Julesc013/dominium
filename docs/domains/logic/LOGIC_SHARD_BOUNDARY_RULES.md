Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# LOGIC Shard Boundary Rules

Status: normative
Version: 1.0.0
Scope: LOGIC-3 topology only

## Purpose

Logic topology may span authority regions only through explicit asynchronous boundaries.

This document forbids direct cross-shard synchronous wiring and defines the two allowed boundary forms for LOGIC-3.

## Rules

### 1. No direct cross-shard synchronous wiring
- A non-`sig_link` edge must not directly connect nodes on different shard ids.
- Cross-shard synchronous evaluation would violate deterministic boundary ordering and shard isolation.

### 2. Allowed boundary forms
- `edge.sig_link`
- explicit boundary artifact exchange declared on the edge or endpoint extensions

Valid extension markers include:
- `boundary_artifact_id`
- `boundary_artifact_exchange = true`

These markers declare that the link resolves through artifact handoff rather than same-tick synchronous propagation.

### 3. Node boundary metadata
- Nodes may declare `extensions.shard_id`.
- Validators compare source and target shard ids deterministically.
- Missing shard ids do not imply cross-shard routing; they mean shard topology is unspecified.

### 4. `sig_link` meaning
- `sig_link` is receipt-oriented and asynchronous.
- Transport, trust, encryption, delivery, and jamming semantics remain owned by SIG.
- LOGIC only validates that a shard-safe boundary seam exists.

### 5. Boundary artifacts
- Boundary artifacts are canonical exchange records, not hidden shortcuts.
- They must be explainable, provenance-friendly, and replay-safe.
- Future LOGIC execution layers may consume them, but LOGIC-3 only validates their declared presence.

## Validation Requirements

When `from_shard_id != to_shard_id`:
- `edge_kind = sig_link` is allowed
- non-`sig_link` edges require explicit boundary artifact exchange metadata
- otherwise validation refuses the network

Reason surfaces:
- `refusal.logic.network_invalid`
- `refusal.logic.loop_detected` if the same network also violates loop policy

Explain surfaces:
- `explain.logic_loop_detected`
- `explain.logic_timing_violation` for loop topologies that are only allowed with forced ROI

## Non-Goals

- No shard transport implementation
- No same-tick cross-shard propagation
- No hidden synchronization channel
