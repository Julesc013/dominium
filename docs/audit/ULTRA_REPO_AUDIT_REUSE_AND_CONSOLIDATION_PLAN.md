# ULTRA REPO AUDIT REUSE AND CONSOLIDATION PLAN

Reuse-first recommendations grounded in the live repo rather than idealized redesign.

## Reuse Immediately

| Unit | Paths | Rationale |
| --- | --- | --- |
| Verify build preset and existing verify binaries | CMakeLists.txt<br>CMakePresets.json<br>out/build/vs2026/verify/bin/ | This is the fastest verified path to runnable client/server/tools shells. |
| Launcher and setup AppShell command surfaces | tools/launcher/launch.py<br>tools/setup/setup_cli.py<br>appshell/ | These are the strongest live repo-local command surfaces for packs, profiles, compat, trust, and supervision. |
| Default profile bundle, pack lock, and session template | profiles/bundles/bundle.mvp_default.json<br>locks/pack_lock.mvp_default.json<br>data/session_templates/session.mvp_default.json | They already define a coherent baseline configuration for a near-term playable slice. |
| Loopback authority and local singleplayer controller | client/local_server/local_server_controller.py<br>server/net/loopback_transport.py<br>runtime/process_spawn.py | This is the most evidence-backed way to get a local authoritative playtest loop before real network transport exists. |
| Release manifest, update resolver, and trust verifier | release/release_manifest_engine.py<br>release/update_resolver.py<br>security/trust/trust_verifier.py | These surfaces are already wired into setup/launcher compatibility and should be reused rather than replaced. |
| CTest/TestX/validation surface | tools/validation/<br>tools/xstack/testx_all.py<br>tests/playtest/ | The repo already has broad coverage scaffolding; it should gate baseline assembly rather than be rebuilt. |

## Wrap, Do Not Rewrite

| Unit | Paths | Rationale |
| --- | --- | --- |
| Public local playtest startup | tools/mvp/runtime_entry.py<br>client/local_server/local_server_controller.py<br>tools/xstack/session_create.py | A thin canonical wrapper is cheaper and safer than re-architecting startup paths. |
| Compiled launcher/setup shells | launcher/<br>setup/ | Use them as thin wrappers around the stronger Python/AppShell flows until native shells are worth finishing. |

## Consolidate After Baseline

| Unit | Paths | Rationale |
| --- | --- | --- |
| Session create/boot save-root handling | tools/xstack/sessionx/creator.py<br>tools/xstack/sessionx/runner.py | The same pipeline should not disagree about artifact location semantics. |
| Server startup entrypoints | server/server_main.py<br>tools/mvp/runtime_entry.py<br>out/build/vs2026/verify/bin/server.exe | Entry semantics should converge around a stable canonical startup path. |
| Doc path vocabulary | docs/audit/<br>docs/runtime/<br>docs/release/ | Stale src/ path mirrors and maturity overclaims create avoidable planning noise. |

## Leave Alone For Now

| Unit | Paths | Rationale |
| --- | --- | --- |
| Authority-ordering and ownership doctrine | docs/canon/<br>docs/planning/AUTHORITY_ORDER.md<br>docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md | Protected governance surfaces should not be rewritten during an audit/inventory prompt. |
| Canonical root splits such as fields/ vs field/ and schema/ vs schemas/ | fields/<br>field/<br>schema/<br>schemas/ | Doctrine explicitly warns against collapsing these ownership splits by convenience. |

## Retire Or Ignore During Baseline Work

| Unit | Paths | Rationale |
| --- | --- | --- |
| External multiplayer transport work | net/transport/tcp_stub.py<br>net/transport/udp_stub.py | Not needed for the first internal local playtest and still stubbed. |
| Broad repo-spanning convergence or rename work | legacy/<br>quarantine/<br>large convergence reports under docs/audit/ | These are valuable references but should not distract from assembling a runnable baseline quickly. |
