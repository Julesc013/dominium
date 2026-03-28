Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/IPC_ATTACH_CONSOLES.md`, `docs/compat/NEGOTIATION_HANDSHAKES.md`, and `docs/release/FROZEN_INVARIANTS_v0_0_0.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# IPC Discovery
## Purpose

IPC discovery is the canonical local attach lookup surface for AppShell products.

It guarantees:

- endpoint discovery uses `VROOT_IPC` only
- endpoint manifest ordering is deterministic
- per-endpoint descriptor files are deterministic and offline
- attach flows must negotiate through CAP-NEG before console, log, or status channels open

## VROOT_IPC Layout

- Manifest: `VROOT_IPC/ipc_endpoints.json`
- Descriptor files: `VROOT_IPC/endpoints/<endpoint_id>.json`
- Address payloads: emitted by `appshell/ipc/ipc_transport.py`

## Discovery Flow

1. Initialize virtual paths and resolve `VROOT_IPC`.
2. Read `ipc_endpoints.json` and sort rows by `endpoint_id`, `product_id`, and `session_id`.
3. Read the endpoint descriptor file declared by `official.descriptor_rel_path`.
4. Run CAP-NEG handshake via `compat/handshake/handshake_engine.py` before opening channels.
5. Refuse the attach if negotiation is absent, mismatched, or unlogged.

## Canonical Channels

- `negotiation`
- `console`
- `log`
- `status`

## Determinism Rules

- transport selection is capability-gated and deterministic for the same environment
- frame serialization is canonical JSON
- `seq_no` is monotonic per channel
- endpoint descriptor files are keyed by deterministic `endpoint_id`
- retries are bounded iterations only

## Current Baseline

- VROOT probe result: `complete`
- VROOT IPC root: `D:/Projects/Dominium/dominium/build/appshell/ipc_unify/store/runtime`
- Manifest path: `D:/Projects/Dominium/dominium/build/appshell/ipc_unify/store/runtime/ipc_endpoints.json`
- Descriptor rel path: `endpoints/ipc.server.session.ipc_unify.vroot.json`
