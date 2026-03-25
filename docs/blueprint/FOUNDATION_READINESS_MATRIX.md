Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored readiness matrix after implementation planning

# Foundation Readiness Matrix

## Readiness Table

| Capability | Readiness | Required series | Missing building blocks | Complexity | Confidence |
| --- | --- | --- | --- | --- | --- |
| `Compatibility-governed update rehearsal` | `ready_now` | `OMEGA, UPSILON` | control-plane consolidation only | `medium` | `high` |
| `Proof-backed rollback and replay pairing` | `ready_now` | `OMEGA, SIGMA` | unified operator dashboard only | `medium` | `high` |
| `Safe-mode degraded boot` | `ready_now` | `OMEGA, SIGMA` | operator-facing packaging polish only | `low` | `high` |
| `Canary mod deployment` | `foundation_ready_but_not_implemented` | `UPSILON, ZETA` | release rehearsal sandbox; live pack mount; compatibility-scored canary policy | `high` | `medium` |
| `Debug renderer sidecar` | `foundation_ready_but_not_implemented` | `PHI, SIGMA, ZETA` | renderer virtualization; observer-safe debug channels; sidecar lifecycle policy | `high` | `medium` |
| `Automatic yanking with deterministic downgrade` | `foundation_ready_but_not_implemented` | `OMEGA, UPSILON, ZETA` | live release controller; deterministic downgrade planner; runtime revocation choreography | `high` | `high` |
| `Live save migration` | `foundation_ready_but_not_implemented` | `UPSILON, ZETA` | online migration controller; save pause-free handoff; proof-backed rollback hooks | `high` | `medium` |
| `Live trust-root rotation` | `foundation_ready_but_not_implemented` | `UPSILON, ZETA` | online trust-root distribution; rotation receipts; coordinated downgrade and revoke workflow | `high` | `medium` |
| `Offscreen validation renderer` | `foundation_ready_but_not_implemented` | `PHI, UPSILON` | render abstraction; artifactized render snapshot pipeline | `medium` | `high` |
| `Proof-anchor health monitor` | `foundation_ready_but_not_implemented` | `SIGMA, UPSILON, ZETA` | live proof heartbeat service; health dashboards; rollback trigger policy | `medium` | `high` |
| `Release rehearsal in production-like sandbox` | `foundation_ready_but_not_implemented` | `OMEGA, UPSILON, SIGMA` | rehearsal orchestrator; promotion policy; operator signoff UI | `medium` | `high` |
| `Runtime drift detection` | `foundation_ready_but_not_implemented` | `SIGMA, UPSILON, ZETA` | runtime attestation feed; drift comparison service; operator cutover policy | `medium` | `high` |
| `Hot-swappable renderers` | `requires_new_foundation` | `PHI, UPSILON, ZETA` | render device abstraction; service lifecycle manager; side-by-side renderer state export | `very_high` | `medium` |
| `Live protocol upgrades` | `requires_new_foundation` | `SIGMA, PHI, UPSILON, ZETA` | multi-version protocol runtime; live negotiation cutover policy; rollback proofs | `very_high` | `medium` |
| `Mod hot activation` | `requires_new_foundation` | `UPSILON, ZETA` | live pack mount; runtime dependency arbitration; deterministic cutover receipts | `high` | `medium` |
| `Partial live module reload` | `requires_new_foundation` | `PHI, SIGMA, ZETA` | module loader; module state export; governed cutover plans | `very_high` | `medium` |
| `Renderer virtualization` | `requires_new_foundation` | `PHI, ZETA` | render service boundary; framegraph isolation; device-independent submission API | `high` | `medium` |
| `Snapshot isolation for all mutable state` | `requires_new_foundation` | `PHI, UPSILON, ZETA` | state partition protocol; copy-on-write runtime; WAL-like replay bridge | `very_high` | `medium` |
| `Distributed shard relocation` | `unrealistic_currently` | `PHI, UPSILON, ZETA` | deterministic replication; authority handoff; state partition transfer proofs | `very_high` | `low` |

