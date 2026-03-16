Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PLATFORM/DIST
Replacement Target: release-pinned target policy contracts and trust-gated update selection

# Target Capability Rules

Fingerprint: `1fda69af0918a7cb43fa8ff850ac3dd7319261710085e7d913e72fb10596dcd0`

## Gate Requirements

- Tier 1 targets must pass `CONVERGENCE-GATE-0`, `DIST-3`, and `DIST-4` before they are treated as shippable.
- Tier 2 targets may ship with deterministic CLI/TUI fallback only and may omit native UI or advanced renderer backends.
- Tier 3 targets are declared only; they must not appear in the default `release_index.json` artifact list.

## Capability Gating

- Setup and release-index resolution use the target matrix row plus platform capability registry row for the resolved target.
- CAP-NEG endpoint descriptors must expose `os_id`, `abi_id`, `arch_id`, and `tier` through the `official.*` descriptor extensions.
- Capability overrides in the target matrix are additive filters over the family-level platform capability registry and must remain deterministic.

## Release Index Policy

- Only Tier 1 targets that are actually built, plus Tier 2 targets if they are actually built, may appear in the default release index.
- Tier 3 rows remain declared in the target matrix registry but are excluded from default downloadable artifact lists.
