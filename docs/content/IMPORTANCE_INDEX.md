Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Importance Index

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


The importance index is a content-level field used to prioritize inspection,
navigation, and tooling. It MUST NOT change simulation truth.

## Field Definition

- Field type: `navigation.importance.index`
- Units: `unitless`
- Representation: typically procedural at macro LOD

## Usage

- Tools MAY use the index to rank regions or nodes for inspection.
- Clients MAY use it to focus rendering or reporting.
- The simulation MUST ignore the index for authoritative behavior.

## Tags

Importance fields MAY include tags such as:
- `navigation`
- `research`
- `hazards`

Tags are descriptive only. Unknown tags MUST be preserved.
