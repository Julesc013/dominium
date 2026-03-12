Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# PACK-COMPAT-0 Retro Audit

## Scope

Audit target:
- existing `pack.json` shape and discovery
- current pack trust/capability sidecars
- current pack-lock generation
- current strict-vs-lab validation posture

## Findings

### Existing pack manifest format

- Runtime pack discovery is currently rooted at `packs/<category>/<pack_id>/pack.json`.
- `tools/xstack/pack_loader/loader.py` validates `pack.json`, resolves dependency tokens, and attaches sidecar policy metadata.
- Existing packs already use adjacent metadata sidecars:
  - `pack.trust.json`
  - `pack.capabilities.json`

### Existing SecureX / trust posture

- MVP trust posture is already represented locally through `pack.trust.json`; no online verification is required.
- `src/modding/mod_policy_engine.py` computes deterministic hashes for trust and capability sidecars and enforces `mod_policy.*`.

### Existing dependency / compatibility declarations

- Existing `pack.json` payloads declare:
  - `pack_id`
  - `version`
  - `compatibility.session_spec_min/max`
  - `dependencies`
  - contribution metadata
- There is no dedicated sidecar today for:
  - semantic contract ranges
  - required registries
  - degrade behavior
  - migration references

### Existing pack lock behavior

- `tools/xstack/registry_compile/compiler.py` includes trust/capability sidecar metadata in `resolved_packs`.
- `tools/xstack/registry_compile/lockfile.py` currently computes `pack_lock_hash` from:
  - `pack_id`
  - `version`
  - `canonical_hash`
  - `signature_status`
- Trust/capability hashes are present in the lock payload but are not yet part of the lock hash identity.
- There is no `pack.compat.json` hash in the lock today.

### Existing strict-mode behavior

- MOD-POLICY strictness already refuses disallowed trust levels/capabilities.
- There is no current strict/lab distinction for missing compatibility metadata because the compatibility sidecar does not yet exist.

## Required change shape

- Add a new adjacent sidecar:
  - `pack.compat.json`
- Keep `pack.json` unchanged for backward compatibility.
- Extend loader and lockfile surfaces to:
  - discover and normalize compatibility metadata
  - refuse missing compat manifests under strict policy
  - warn deterministically in lab/default modes
  - include compat hashes in the pack lock identity

## Non-Goals Confirmed

- No pack content rewrite is required.
- No online trust lookup is required.
- No simulation behavior change is required.
