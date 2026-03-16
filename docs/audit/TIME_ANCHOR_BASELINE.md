Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# TIME-ANCHOR-0 Baseline

- tick_t is canonical uint64 with refusal threshold `18446744073708551615`.
- Anchor interval: `10000` ticks; emit on save and migration: `true`.
- Compaction windows must align to epoch anchors; merged intent logs carry lower/upper anchor ids.
- Readiness for ARCH-AUDIT-0: ready
- Verify fingerprint: `7cd818f36b5628616ec1a1fbd315d5dc8a6f03b33d416fa4370f87af97c4d167`
- Compaction fingerprint: `cf9f73c5073d82edc9fa985273215b4ed031e83bc5e0434635e6001bf04ba644`
