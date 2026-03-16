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
- Release manifest hash retained: `5330c55253bed106f204ff8033895e4b726f7f36c37b70d013ec9a2f1bcc7f7f`
- Release index hash retained: `5901d288ee7793a4742ddff6a8f7e146991d43560f956ae6d492a7f59f5dc7c9`
- Component graph hash retained: `acb17b6581c02eac35ba1aae3fafd55d56b1b46638409550dc155244cd0949a2`
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

- Offline archive bundle hash: `1457dd53f7a034f75685074d7c171d41473ac3968e5060901131c29764306850`
- Archive verification result: `complete`
- Ready for DIST-7 packaging: yes, with immutable release record, no-overwrite history path, and deterministic offline archive bundle generation.
