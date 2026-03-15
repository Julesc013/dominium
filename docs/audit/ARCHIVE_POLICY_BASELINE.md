Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST-7/RELEASE
Replacement Target: signed publication bundles and multi-mirror release automation

# Archive Policy Baseline

## Retention Guarantees

- Immutable release id: `v0.0.0-mock`
- Release manifest hash retained: `67a1db16cfc6b985caccecca7d48de2c71dcce67a847c442dfcae2b0bdcc9458`
- Release index hash retained: `5daa6e38edbf6d33e5566c17f2a3971a75b3c031281f45d395be70fa895e6b11`
- Component graph hash retained: `dd76615a4a8887166efc90b2baf7cc7f9bf87f266ef3a5844f71aa6d646fd02c`
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

- Offline archive bundle hash: `6971e831dd07f11a0bf70b89cd7e4532b96d81498bb0e97b69b14ed5f325964b`
- Archive verification result: `complete`
- Ready for DIST-7 packaging: yes, with immutable release record, no-overwrite history path, and deterministic offline archive bundle generation.

