Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# REPLACEMENT-PROTOCOL-01 Audit

Result: PASS_WITH_WARNINGS

## Why

Dominium needs a governed way to replace implementations, providers, modules,
schemas, protocols, artifact formats, command handlers, validators, and
directory-owned surfaces without silent compatibility breakage.

## Files

- `contracts/replacement/replacement.contract.toml`
- `contracts/replacement/replacement_packet.schema.json`
- `contracts/replacement/replacement_kind.registry.json`
- `contracts/replacement/replacement_status.registry.json`
- `contracts/replacement/replacement_impact.schema.json`
- `contracts/replacement/replacement_proof.schema.json`
- `contracts/replacement/rollback_policy.contract.toml`
- `contracts/replacement/conformance_policy.contract.toml`
- `contracts/replacement/migration_refusal_policy.contract.toml`
- `tools/validators/repo/check_replacement_packet.py`
- `tests/contract/replacement/**`
- `docs/architecture/replacement_protocol.md`
- `docs/development/replacement_protocol_guidelines.md`

## Initial Inventory

The replacement inventory scanned 17,942 tracked files and classified 1,824
replacement-like historical or future-candidate files. Historical move/router/
repair evidence remains historical and is not converted into full replacement
packets here.

## Proof

- replacement validator strict: pass
- replacement fixtures: pass
- diagnostics validator: pass
- public surface validator: pass
- capability/refusal validator: pass
- fast strict: pass, 32/32 commands in 301.437 seconds

## Known Limitations

- Replacement protocol is provisional.
- No actual implementation replacement is performed.
- Migration and rollback runtimes are not implemented.
- Version/deprecation law is not implemented yet.

Next task: `VERSION-DEPRECATION-LAW-01`
