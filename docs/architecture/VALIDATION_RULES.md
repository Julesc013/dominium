Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# VALIDATION_RULES

Status: binding.
Scope: single source of truth for invariant enforcement gates.

Failure format:
- Every violation MUST emit the invariant ID, then a short reason and location.
- Example: `INV-DET-ORDERING: ordering violation at engine/modules/core/det_order.c:123`.

Overrides:
- Overrides are explicit entries in `docs/architecture/LOCKLIST_OVERRIDES.json`.
- Each override MUST include: invariant ID, reason, expiry date.
- Overrides are forbidden on release/stable branches and must be visible in CI output.

## A) Language & Toolchain

## INV-LANG-C89 — Engine C code compiles as C89
- Scope: engine/ (C sources)
- Enforcement: CI build (strict C89), `tests/invariant/invariant_lang_c89.py` (token scan fallback)
- Failure format: `INV-LANG-C89: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-LANG-CPP98 — Game C++ code compiles as C++98
- Scope: game/ (C++ sources)
- Enforcement: CI build (strict C++98), `tests/invariant/invariant_lang_cpp98.py` (token scan fallback)
- Failure format: `INV-LANG-CPP98: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-HDR-C89 — Engine public headers compile as C89
- Scope: engine/include/**
- Enforcement: `tests/contract/public_header_c89_compile.py`
- Failure format: `INV-HDR-C89: <header>: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-HDR-CPP98 — Game public headers compile as C++98
- Scope: game/include/**
- Enforcement: `tests/contract/public_header_cpp98_compile.py`
- Failure format: `INV-HDR-CPP98: <header>: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-HDR-NO-STL-ABI — No STL across ABI boundaries
- Scope: engine/include/** and game/include/** public ABI surfaces
- Enforcement: header lint + compile checks (limited to forbidden includes/tokens)
- Failure format: `INV-HDR-NO-STL-ABI: <header>: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## B) Determinism

## INV-DET-NO-WALLCLOCK — No wall-clock dependencies in authoritative logic
- Scope: engine/modules/{core,sim,world}, game/{core,rules}
- Enforcement: `tests/invariant/invariant_no_wallclock.py`, RepoX rule
- Failure format: `INV-DET-NO-WALLCLOCK: <path:line>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-DET-NO-ANON-RNG — No anonymous RNG; named streams only
- Scope: engine/modules/{core,sim,world}, game/{core,rules}
- Enforcement: `tests/invariant/invariant_no_anon_rng.py`, determinism hardlock tests
- Failure format: `INV-DET-NO-ANON-RNG: <path:line>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-DET-ORDERING — Deterministic ordering everywhere
- Scope: engine/game authoritative execution, ordering contracts
- Enforcement: `tests/contract/deterministic_ordering_tests.py`, `tests/determinism/determinism_ordering_invariance.py`
- Failure format: `INV-DET-ORDERING: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-DET-REDUCTION — Deterministic reduction/merge only
- Scope: engine/modules/core reduction utilities and ordering contract
- Enforcement: `tests/contract/determinism_hardlock_tests.py`
- Failure format: `INV-DET-REDUCTION: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-DET-THREADCOUNT — Thread-count invariance (hash equality)
- Scope: perf fixtures and determinism fixtures
- Enforcement: `tests/determinism/determinism_thread_count_invariance.py`
- Failure format: `INV-DET-THREADCOUNT: <fixture>: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-DET-REPLAY-HASH — Replay hash invariance
- Scope: perf fixtures and replay stubs
- Enforcement: `tests/determinism/determinism_replay_hash_invariance.py`
- Failure format: `INV-DET-REPLAY-HASH: <fixture>: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## C) Float Policy

## INV-FP-AUTH-BAN — No float/double in authoritative logic
- Scope: engine/modules/{core,sim,world}, game/{core,rules}
- Enforcement: `tests/invariant/invariant_no_float_authoritative.py`, RepoX rule
- Failure format: `INV-FP-AUTH-BAN: <path:line>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-FP-QUARANTINE — Floating point only in explicit presentation zones
- Scope: client/, renderer, presentation-only code
- Enforcement: RepoX and architecture checks (manual + lint)
- Failure format: `INV-FP-QUARANTINE: <path:line>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## D) Process-Only Mutation

## INV-MUT-PROCESS-ONLY — Authoritative state changes only via Process execution
- Scope: engine/game authoritative state mutation paths
- Enforcement: `tests/invariant/invariant_process_only_mutation.py` (static), process guard runtime asserts (debug)
- Failure format: `INV-MUT-PROCESS-ONLY: <path:line>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-MUT-NO-DIRECT-SETTERS — No direct mutation helpers in core state
- Scope: engine/game authoritative state modules
- Enforcement: static lint in `tests/invariant/invariant_process_only_mutation.py`
- Failure format: `INV-MUT-NO-DIRECT-SETTERS: <path:line>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## E) Content / Path / Hard-Coded Prohibitions

## INV-NO-RAW-PATHS — No raw file paths in saves/packs/worlddefs/replays
- Scope: data/, schema/, tests/fixtures/, pack manifests
- Enforcement: `tests/invariant/invariant_no_raw_paths.py`, RepoX rule
- Failure format: `INV-NO-RAW-PATHS: <path:line>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-NO-HARDCODED-CONTENT — No hardcoded pack/world IDs in engine/game
- Scope: engine/, game/
- Enforcement: `tests/invariant/invariant_no_hardcoded_content_strings.py`, RepoX rule
- Failure format: `INV-NO-HARDCODED-CONTENT: <path:line>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-PACK-SCOPE — Packs only affect allowed scopes
- Scope: data/packs/**
- Enforcement: `tests/contract/pack_scope_enforcement_contracts.py`
- Failure format: `INV-PACK-SCOPE: <pack>: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## F) Enum & Extensibility Rules

## INV-ENUM-NO-OTHER — No enum members named OTHER/CUSTOM/UNKNOWN/MISC/UNSPECIFIED
- Scope: engine/, game/
- Enforcement: `tests/invariant/invariant_enum_no_other.py`, RepoX rule
- Failure format: `INV-ENUM-NO-OTHER: <path:line>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-OPEN-SET-IDS — Open sets use namespaced IDs, not enums
- Scope: schema/ and data/
- Enforcement: schema lint (manual + policy checks)
- Failure format: `INV-OPEN-SET-IDS: <schema>: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## G) Units & Magic Numbers

## INV-UNITS-ANNOTATED — Schema numeric fields must be unit-tagged
- Scope: schema/
- Enforcement: `tests/invariant/invariant_units_present.py`, `tests/contract/unit_annotation_validation.py`
- Failure format: `INV-UNITS-ANNOTATED: <schema>: <field>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-MAGIC-NO-LITERALS — No unexplained numeric literals in core logic
- Scope: engine/modules/{core,sim,world}, game/{core,rules}
- Enforcement: RepoX magic-number lint (diff-based heuristic; allows small structural integers <=16, hex/bitmasks, and fixed-point conversion helpers)
- Failure format: `INV-MAGIC-NO-LITERALS: <path:line>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## H) Schema Evolution

## INV-SCHEMA-VERSIONED — All schemas must be versioned
- Scope: schema/
- Enforcement: schema lint + CI checks
- Failure format: `INV-SCHEMA-VERSIONED: <schema>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-SCHEMA-UNKNOWN-PRESERVE — Unknown fields preserved
- Scope: schema/ and schema-driven data
- Enforcement: `tests/contract/schema_roundtrip_unknown_preservation.py`
- Failure format: `INV-SCHEMA-UNKNOWN-PRESERVE: <schema>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-SCHEMA-NO-SEMANTIC-REUSE — ID meanings never reused
- Scope: schema/, docs/architecture/SEMANTIC_STABILITY_POLICY.md
- Enforcement: schema lint + contract checks
- Failure format: `INV-SCHEMA-NO-SEMANTIC-REUSE: <schema>: <id>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-SCHEMA-CHANGE-NOTES — Schema changes require migration notes
- Scope: schema/
- Enforcement: `tests/contract/schema_change_notes_required.py`
- Failure format: `INV-SCHEMA-CHANGE-NOTES: <schema>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## I) OPS / Orchestration

## INV-OPS-COMPAT-REPORT — Compat report produced for ops actions
- Scope: tools/ops, tools/launcher, setup
- Enforcement: `tests/contract/compat_report_presence_contracts.py`
- Failure format: `INV-OPS-COMPAT-REPORT: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-OPS-TRANSACTIONAL — Install/remove/update operations are plan/stage/commit/rollback
- Scope: tools/ops, setup, launcher
- Enforcement: contract tests + ops validation
- Failure format: `INV-OPS-TRANSACTIONAL: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## J) Repo Governance (RepoX)

## INV-LOCKLIST-FROZEN — Frozen contract edits require override + expiry
- Scope: docs/architecture/CONTRACTS_INDEX.md frozen surfaces
- Enforcement: RepoX rule (diff-based)
- Failure format: `INV-LOCKLIST-FROZEN: <path>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-REPOX-STRUCTURE — Repository structure follows REPO_INTENT
- Scope: top-level repo layout
- Enforcement: RepoX rule
- Failure format: `INV-REPOX-STRUCTURE: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-REPOX-AMBIGUOUS-DIRS — No new ambiguous directories
- Scope: repo changes (diff-based)
- Enforcement: RepoX rule
- Failure format: `INV-REPOX-AMBIGUOUS-DIRS: <path>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## K) Reporting

## INV-REPORT-COMPLIANCE — Compliance report emitted in CI/tests
- Scope: scripts/ci/compliance_report.py
- Enforcement: `tests/contract/compliance_report_contracts.py`
- Failure format: `INV-REPORT-COMPLIANCE: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## L) Canon & Docs

## INV-CANON-INDEX — Canon index exists and is complete
- Scope: docs/architecture/CANON_INDEX.md
- Enforcement: RepoX rule + canon compliance report
- Failure format: `INV-CANON-INDEX: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-DOC-STATUS-HEADER — Docs status header required
- Scope: docs/**
- Enforcement: RepoX rule (header scan)
- Failure format: `INV-DOC-STATUS-HEADER: <path>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-CANON-NO-HIST-REF — Canonical docs must not reference historical docs
- Scope: docs/architecture/** (canonical)
- Enforcement: RepoX rule (reference scan)
- Failure format: `INV-CANON-NO-HIST-REF: <path>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-CANON-CODE-REF — Code references canonical docs only
- Scope: engine/, game/, client/, server/, tools/
- Enforcement: RepoX rule (doc reference scan)
- Failure format: `INV-CANON-CODE-REF: <path>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-CANON-NO-SUPERSEDED — Canonical docs must not be superseded
- Scope: docs/architecture/** (canonical)
- Enforcement: RepoX rule (header scan)
- Failure format: `INV-CANON-NO-SUPERSEDED: <path>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-SCHEMA-VERSION-BUMP — Schema changes require schema_version update
- Scope: schema/**
- Enforcement: RepoX rule (diff-based)
- Failure format: `INV-SCHEMA-VERSION-BUMP: <path>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)

## INV-REPORT-CANON — Canon compliance report emitted
- Scope: scripts/ci/compliance_report.py
- Enforcement: RepoX rule + compliance report contract
- Failure format: `INV-REPORT-CANON: <reason>`
- Overrides: allowed via LOCKLIST_OVERRIDES.json (expiry required)
