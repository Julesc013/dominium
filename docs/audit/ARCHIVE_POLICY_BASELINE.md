Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST-7/RELEASE
Replacement Target: signed publication bundles and multi-mirror release automation

# Archive Policy Baseline

## Retention Guarantees

- Immutable release id: `v0.0.0-mock`
- Release manifest hash retained: `d5d2707f0a8911f4f24577f0b0a9cd4c5200ac9a6a637f4ba73d3edf56706ad5`
- Release index hash retained: `d04261cdc491a17dc3f6806ecf932a45b5c92146e811d6b5f41cab19de84eb73`
- Component graph hash retained: `f850e846bd0904b5bb2f3e0a75a03d6a4012d564093b5fa2964aadc2a4babdfe`
- Governance profile hash retained: `09273dc808ff2cf8edab36eb30ce4139212bcce8903a3ab5a3043a9fcfd08187`
- Release index history snapshot: `manifests/release_index_history/mock/v0.0.0-mock.json`
- Official release retention policy: no deletion of published mock release artifacts.

## Mirror Strategy

- Declared mirrors: mirror.cold_storage.default, mirror.primary.default, mirror.secondary.default
- Required policy: primary plus secondary mirror, with offline cold storage recommended.
- Provider binding: none; mirror identifiers remain provider-neutral and offline-first.

## Source Archive Policy

- Source archive hash: `(not recorded)`
- Mock default: source archive recording remains optional and additive for open or partially open releases.

## Readiness

- Offline archive bundle hash: `ae098b3f824272964aa9e872dcdffbaab15b91d7a1d3fce95cfd6625e3f32de0`
- Archive verification result: `complete`
- Ready for DIST-7 packaging: yes, with immutable release record, no-overwrite history path, and deterministic offline archive bundle generation.

