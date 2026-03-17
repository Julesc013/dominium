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
- Release manifest hash retained: `3ebd3e248df5abbc937cee6ed6caa9e0177e7f3445cf25eed67ea6295cd6fbf4`
- Release index hash retained: `d7bd143684eabbcb1d2bb5637fcbb280b7c4a58767f1ff8c6a27d099909abd92`
- Component graph hash retained: `02c9ec2f257c3984935c329771a521044c9ca8733e51e8dec2fb0e66f878bf5f`
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

- Offline archive bundle hash: `52d8343669f2a60bbc90e6d2609d22b6148a0328993e44d270c8be88ef337cc1`
- Archive verification result: `complete`
- Ready for DIST-7 packaging: yes, with immutable release record, no-overwrite history path, and deterministic offline archive bundle generation.

