Status: CANONICAL
Last Reviewed: 2026-04-07
Supersedes: none
Superseded By: none
Stability: stable
Future Series: XStack-to-AIDE extraction mapping, playable-baseline assembly follow-ups
Replacement Target: later explicit repo-operating-contract checkpoint or replacement artifact only
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `data/planning/checkpoints/checkpoint_c_zeta_mega_validation_and_closure.json`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `data/planning/next_execution_order_post_zeta.json`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_PLAYTEST_READINESS.md`, `docs/audit/ULTRA_REPO_AUDIT_GAPS_AND_TODOS.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_BUILD_RUN_TEST_MATRIX.md`, `docs/audit/ULTRA_REPO_AUDIT_WIRING_MAP.md`, `docs/xstack/XSTACK_SCOPE_FREEZE.md`, `data/xstack/xstack_scope_freeze.json`, `docs/xstack/XSTACK_INVENTORY_AND_CLASSIFICATION.md`, `data/xstack/xstack_inventory_and_classification.json`, `docs/xstack/AIDE_PORTABLE_TASK_CONTRACT.md`, `data/xstack/aide_portable_task_contract.json`, `docs/xstack/AIDE_EVIDENCE_AND_REVIEW_CONTRACT.md`, `data/xstack/aide_evidence_and_review_contract.json`, `docs/xstack/AIDE_POLICY_AND_PERMISSION_SHAPE.md`, `data/xstack/aide_policy_and_permission_shape.json`, `docs/xstack/AIDE_CAPABILITY_PROFILE_SHAPE.md`, `data/xstack/aide_capability_profile_shape.json`, `docs/xstack/AIDE_ADAPTER_CONTRACT.md`, `data/xstack/aide_adapter_contract.json`, `CMakePresets.json`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/sessionx/creator.py`, `tools/xstack/sessionx/runner.py`, `tools/xstack/testx_all.py`, `tools/validation/tool_run_validation.py`, `tools/mvp/runtime_entry.py`, `server/server_main.py`, `client/local_server/local_server_controller.py`, `server/net/loopback_transport.py`, `runtime/process_spawn.py`, `profiles/bundles/bundle.mvp_default.json`, `locks/pack_lock.mvp_default.json`, `data/session_templates/session.mvp_default.json`

# Codex Repo Operating Contract

## A. Purpose and Scope

This artifact freezes the canonical repo-operating contract for Codex work in the live Dominium repository.

It exists to solve a practical repo problem:

- the repo has many valid-looking wrappers, entrypoints, reports, and transitional surfaces
- the post-`Zeta` audit showed that startup ambiguity is itself a blocker
- future Codex runs need one stable operating contract for build, validation, local playtest targeting, directory authority, task sizing, comment discipline, and commit discipline

This artifact is baseline-first.
It is intentionally narrower than a platform design and intentionally more operational than the earlier portable AIDE contracts.

It governs:

- the canonical build path Codex should use now
- the canonical validation path Codex should use now
- the canonical repo-local playtest path Codex should target now
- the current session, profile, pack lock, template, and save-root rules
- which directory families are authoritative versus derived or generated
- which surfaces are frozen or deprioritized during playable-baseline work
- the task-sizing, code-comment, documentation, and commit rules Codex must follow in this repo

It is downstream of:

- the post-`Zeta` closure and ultra audit packet
- the `X-0` scope freeze
- the `X-1` XStack inventory and classification ledger
- the `X-2` through `X-6` portable contract freezes

It must remain compatible with current repo reality:

- admissible `Zeta` doctrine and gating work is complete
- no further internal `Zeta` prompt is required
- the immediate product priority is the canonical repo-local playable baseline
- the highest-value immediate engineering move is to harden one canonical repo-local playtest path around session creation plus local loopback authority, then rerun `FAST` validation and a selected playtest smoke slice

This artifact is an operating contract freeze.
It does not implement the canonical playtest command, a full AIDE runtime, a daemon, a compiler, a bakeoff framework, or broad repo restructuring.

## B. Canonical Build Path

Current build rule:

- the canonical configure preset is `cmake --preset verify`
- the canonical build preset is `cmake --build --preset verify`
- the canonical CTest preset, when compiled tests are needed, is `ctest --preset verify`

Why this is canonical now:

- `CMakePresets.json` defines aligned `verify` configure, build, and test presets
- the ultra audit identifies the `verify` lane as the strongest current build baseline for repo-local playable-baseline work
- the `verify` lane keeps tools, setup, launcher, game, and tests enabled while staying inside the repo’s verification posture

Codex must use the `verify` lane when:

- a task touches compiled runtime, launcher, setup, server, client, networking, or C/C++ behavior
- a task changes the canonical playtest path or compiled entrypoint wiring
- a task changes assumptions that need verified binaries under `out/build/vs2026/verify/`

Codex may skip a build only when the task is genuinely docs-only or Python-only and does not claim compiled-path verification.

Current "verified enough" meaning:

- for docs-only or mirror-only work, verified enough can mean JSON parsing, prose/mirror consistency, and `git diff --check`
- for Python or shell-path work, verified enough normally means at least `FAST` validation plus any directly relevant script-level checks
- for compiled or playtest-path work, verified enough means the `verify` configure/build lane ran and the impacted runtime or test surface was exercised honestly

What Codex must not assume:

- a successful configure alone is not a verified build
- an existing `out/build/vs2026/verify/` tree is not proof that current changes were rebuilt
- `local` and `release-check` are real presets, but they are not the canonical default lane for current baseline assembly work

## C. Canonical Validation Path

Current validation rule:

- the canonical minimum validation path is `python tools/validation/tool_run_validation.py --profile FAST`
- `python tools/xstack/testx_all.py --profile FAST` is the canonical XStack/TestX smoke companion when XStack tooling or validation surfaces are touched
- `ctest --preset verify` is the canonical compiled-test companion when the task implicates the verify binary lane

Role split:

- `FAST` validation is the repo-wide first pass and the minimum honest default for non-trivial work
- `TestX` is the higher-signal Python/XStack harness for tooling, control, compat, session, and validation-adjacent changes
- `CTest` is the compiled/runtime harness for verify-built binaries and related smoke coverage

Smoke is enough when:

- the task is small and localized
- the touched surface has a narrow validation target
- no broader runtime or compiled behavior was changed

A stronger run is needed when:

- the task changes build wiring, launcher/setup entrypoints, server or client runtime behavior, or session boot flow
- the task changes control, compat, validation, or trust semantics in a way that affects more than one narrow surface
- the prompt explicitly requires `STRICT`, `FULL`, or broader test execution

Honest validation language rules:

- say `verified` only when the relevant command actually completed successfully
- say `partially verified` when only a subset completed
- say `attempted but blocked` when a command failed or timed out for a real blocker
- say `not run` when a command was not executed
- never collapse `verified`, `likely`, `partial`, and `blocked` into one status class

## D. Canonical Local Playtest Path

Current canonical local playtest target:

- repo-local mode
- loopback-authoritative mode
- single-machine operation
- default MVP bundle and pack lock
- canonical `saves/<save_id>/` session materialization
- Python/AppShell operator shells instead of native wrapper-first assumptions

Current strongest public or semi-public path:

1. Prepare the verify lane when compiled artifacts are implicated:
   - `cmake --preset verify`
   - `cmake --build --preset verify`
2. Prefer the Python/AppShell shells as the operator-facing surfaces:
   - `python tools/setup/setup_cli.py ...`
   - `python tools/launcher/launch.py ...`
3. Materialize the session under the canonical repo-local save tree:
   - `python tools/xstack/session_create.py --save-id <save_id>`
4. Treat local loopback authority as the canonical runtime direction:
   - the strongest live authority path is rooted in `client/local_server/local_server_controller.py`
   - that controller drives the server runtime through deterministic local process spawn plus `server/net/loopback_transport.py`

Current default assumptions:

- bundle: `profile.bundle.mvp_default`
- pack lock: `pack_lock.mvp_default`
- session template: `session.mvp_default`
- server UI default inside the bundle: headless
- authority context is repo-local and loopback-oriented, not external multiplayer

Current public-path truthfulness:

- there is not yet one finished, stable, single public playtest command that Codex may claim is fully hardened
- the canonical path today is therefore a target recipe, not a completed one-command operator flow
- Codex must not invent a second "official" path just because another wrapper exists

What remains blocked or fragile:

- `server/server_main.py` repo-root resolution is still a blocker
- `tools/xstack/session_boot.py` and `tools/xstack/sessionx/runner.py` remain coupled to canonical `repo_root/saves/<save_id>` layout
- launcher supervision still has audit-noted instability
- non-loopback and native-shell-first surfaces remain stub-heavy or incomplete

What Codex must not assume yet:

- raw `python server/server_main.py` is not the canonical public playtest path
- `python -m server.server_main` is not a safe canonical substitute
- `python tools/mvp/runtime_entry.py --local-singleplayer` is transitional and must not be promoted into the canonical operator path without an explicit task
- alt save roots are not end-to-end supported just because `session_create.py` accepts `--saves-root`
- non-loopback multiplayer, installed-mode assumptions, and native launcher/setup parity are not baseline-ready

## E. Session / Profile / Save-Root Rules

Current session rules:

- use `tools/xstack/session_create.py` as the canonical session materialization entrypoint
- treat its default bundle assumption as `profile.bundle.mvp_default`
- treat the corresponding default pack lock as `pack_lock.mvp_default`
- treat the authored default template as `data/session_templates/session.mvp_default.json`
- treat `saves/<save_id>/` as the canonical bootable save layout for current repo-local work

Operational rules Codex must follow:

- when creating a new baseline-oriented session, start from the default bundle and lock unless the task explicitly requires a different profile family
- do not silently change save-root expectations in docs, scripts, or prompts
- do not advertise arbitrary `--saves-root` paths as supported for boot flow until `sessionx.runner` no longer hardcodes `repo_root/saves/<save_id>`
- if a task must use `session_boot`, point it at the canonical `saves/<save_id>/session_spec.json` layout and state the save-root coupling clearly

Current save-root truth:

- `session_create.py` can write to an alternate relative saves root
- current boot/runtime flow cannot honestly claim alternate save-root support because `sessionx.runner` resolves the active save directory back through `repo_root/saves/<save_id>`
- until that bug is fixed, Codex must describe alternate save-root support as blocked, not partially working

## F. Authoritative Directories

The following directory families are authoritative for current work, with the listed scope caveats.

### F1. Canon, Governance, And Task-Law

- `docs/canon/**`
  - canonical constitutional and glossary law
- `AGENTS.md`
  - canonical repo operating governance
- `docs/planning/**`
  - canonical planning authority only for the task-named artifacts in scope
- `docs/xstack/**`
  - canonical XStack/AIDE narrowing and operating-contract prose for this series

### F2. Semantic And Contract Roots

- `specs/reality/**`
  - canonical semantic reality law when touched
- `schema/**`
  - canonical semantic contract law
- `fields/**`
  - canonical field substrate

### F3. Runtime And Baseline Assembly Roots

- `appshell/**`
  - canonical shell and adapter surface for the current Python/AppShell operator path
- `tools/launcher/**`
  - canonical launcher shell family for repo-local operation
- `tools/setup/**`
  - canonical setup shell family for repo-local operation
- `tools/xstack/**`
  - canonical XStack tooling family for session creation, boot control, validation, and test harnesses
- `server/**`
  - authoritative server runtime and loopback transport code, even when some public entrypoints are currently fragile
- `client/local_server/**`
  - authoritative local loopback singleplayer controller path
- `runtime/**`
  - authoritative process and runtime helpers when touched by baseline assembly work

### F4. Profile, Lock, Pack, And Session Authoring Roots

- `profiles/bundles/**`
  - authoritative profile bundle declarations
- `locks/**`
  - authoritative pack lock declarations
- `data/session_templates/**`
  - authoritative authored session templates
- `packs/**`
  - canonical runtime packaging, activation, compatibility, and distribution-descriptor scope
- `data/packs/**`
  - authoritative within authored pack content and declaration scope, but still ownership-sensitive and not silently interchangeable with `packs/**`

### F5. Validation, Test, Release, And Trust Roots

- `tools/validation/**`
  - canonical validation entrypoint tooling
- `validation/**`
  - authoritative validation engine and support logic
- `tools/xstack/testx/**`
  - authoritative TestX harness family
- `tests/**`
  - authoritative broader test roots where present
- `release/**`, `repo/**`, `security/**`, `updates/**`
  - authoritative when release, trust, identity, or publication scope is explicitly in play

## G. Derived / Generated / Non-Authoritative Directories

The following directory families are useful, but Codex must not treat them as the primary source of truth.

- `data/planning/**`
  - machine-readable planning mirrors; derive from canonical planning prose and must not overrule it
- `data/xstack/**`
  - machine-readable mirrors for the XStack/AIDE series; required and important, but still mirrors of the canonical prose contracts
- `docs/audit/**`
  - audit evidence and operational reporting; highly relevant evidence, but not constitutional law
- `data/audit/**`
  - machine-readable audit evidence and reports; not canonical law
- `schemas/**`
  - validator-facing projections or advisory mirrors, not canonical semantic contract law
- `build/**`, `out/**`, `artifacts/**`, `.xstack_cache/**`, `run_meta/**`, `tmp/**`, `archive/**`
  - generated build, cache, report, and temporary outputs
- `dist/**`, `bundles/**`
  - built or packaged outputs, not authoring truth
- `saves/**`
  - generated runtime session instances; currently the canonical boot location for session instances, but not a canonical authored source root

Derived does not mean ignorable.
It means:

- consume as evidence, output, or runtime state
- do not silently promote into semantic authority
- do not rewrite canon because a generated root is easier to inspect

## H. Frozen Surfaces During Baseline Work

During the playable-baseline push, Codex should avoid touching the following unless a prompt explicitly targets them.

- broad post-baseline frontier work
- broad non-loopback multiplayer or external transport expansion
- full AIDE runtime, daemon, compiler, adapter ecosystem, or platformization work
- large renames or convergence passes that are not required to unblock the canonical repo-local playtest path
- ownership rebinding across `field/` versus `fields/`, `schema/` versus `schemas/`, or `packs/` versus `data/packs/`
- native launcher/setup shell completion work that does not directly unblock the baseline path
- release/publication/archive/trust policy changes unrelated to the active task
- doctrine rewrites under `docs/canon/**`, `AGENTS.md`, or equivalent protected roots unless the prompt is explicitly doctrine-facing
- promotion of `tools/mvp/runtime_entry.py` into the canonical public playtest path without an explicit task
- wrapper proliferation that creates a second or third "official" startup flow

Allowed exception rule:

- if a frozen surface contains a named blocker from the audit and the active prompt directly targets that blocker, a narrow fix is allowed
- the fix must remain extension-over-replacement and must not widen into speculative cleanup

## I. Task Sizing Policy

Codex should size work in this repo using the following default policy.

### I1. Big Prompts

Use big prompts for:

- repo audits
- topology and ownership reconciliation
- inventory and classification work
- multi-root planning or doctrine packaging
- narrow contract freezes like the X-series when they are documentation-first and evidence-heavy

Big prompts must not become stealth implementation sprees.
If the task starts mutating multiple runtime families without an explicit implementation mandate, split it.

### I2. Medium Prompts

Use medium prompts for:

- one vertical slice of the canonical playable-baseline path
- one blocker plus its immediate support docs or tests
- a targeted integration repair spanning a small number of closely related roots

Typical medium scope:

- one blocker or one operator workflow
- at most a handful of directly connected roots
- clear validation expectations

### I3. Small Prompts

Use small prompts for:

- one concrete bug
- one entrypoint correction
- one script or path fix
- one doc or JSON mirror update
- one validation or reporting repair

### I4. Too Broad

A task is too broad and should be split when it:

- mixes baseline blockers with frontier expansion
- mixes doctrine rewrite with runtime implementation
- spans multiple independent blockers from the audit gap ledger
- combines broad renaming, extraction, and baseline assembly work
- cannot be validated honestly inside one bounded change set

## J. Code / Comments / Docs Standards

When changing code, Codex must:

- add or clarify docstrings when entrypoint behavior, path assumptions, contracts, or failure modes are not obvious
- add short inline comments only where the logic would otherwise be hard to reconstruct quickly
- explain boundary conditions, refusal paths, fallback limits, and save-root or repo-root assumptions clearly
- document non-obvious operator expectations close to the code that enforces them
- keep documentation explicit about what is verified, likely, partial, blocked, or deferred
- avoid decorative, repetitive, or tutorial-style comments that do not help future debugging
- update paired prose and machine-readable mirrors together when both are part of the contract surface

When changing docs, Codex must:

- write operationally, not aspirationally
- name real commands, presets, paths, blockers, and defaults
- distinguish doctrine from implementation, implementation from integration, and integration from deferred extraction
- avoid converting audit evidence into stronger law than the repo currently supports

## K. Commit Standards

Required commit style:

- use explicit, audit-grade titles
- use verbose bodies that explain what changed, what did not change, what was verified, and what the change enables next
- mention blockers, deferred work, and limitations honestly
- keep unrelated dirty files out of the commit
- commit at meaningful boundaries rather than batching unrelated work into one change

Minimum commit body expectations:

- scope of the change
- canonical rules or paths frozen or modified
- surfaces intentionally left untouched
- validation run, skipped, blocked, or partial
- next prompt or next engineering move enabled

## L. Forbidden Operating Patterns

The following operating patterns are forbidden unless an explicit prompt authorizes them and the required review conditions are met.

- assuming documentation outranks live implementation when the authority order says otherwise
- treating reports, mirrors, or generated outputs as canonical law
- touching unrelated roots during baseline work because they look adjacent
- inventing a second canonical playtest path
- claiming validation success without running the relevant validation
- treating experimental or transitional wrappers as canonical operator surfaces without evidence
- silently promoting raw `server/server_main.py` or `tools/mvp/runtime_entry.py` into the public playtest path
- competing with the playable-baseline path by expanding into large AIDE runtime or platform work
- flattening `verified`, `likely`, `partial`, and `blocked` into one status label
- silently rebinding ownership-sensitive roots because one side is easier to consume

## M. Stability And Evolution

Stability class:

- stable until an explicit follow-up checkpoint replaces it

This artifact enables:

- the next XStack-to-AIDE extraction mapping prompt
- later playable-baseline assembly prompts that need one canonical operating rule set
- future Codex runs that need stable build, validation, playtest, directory-authority, and task-sizing guidance

This artifact must not change silently when:

- the canonical build lane changes
- the canonical validation lane changes
- the canonical local playtest path changes
- the default bundle, pack lock, session template, or save-root rules change
- the authoritative versus derived directory classes change
- baseline-frozen surfaces are reopened or reprioritized

Any such change requires an explicit follow-up artifact or replacement checkpoint rather than silent drift.
