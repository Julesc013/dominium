Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Capability Refusal Guidelines

Use these guidelines when adding optional systems, providers, commands,
Workbench modules, platform support, package/profile behavior, artifact trust
rules, release gates, setup checks, or runtime services.

## Define A Capability

Add a semantic capability ID, kind, owner, version, stability, description,
scope, determinism impact, security impact, and proof expectation. Do not encode
paths, temporary status, or implementation filenames in the ID.

Good IDs:

- `domino.render.software`
- `domino.storage.local`
- `dominium.workbench.validation`

Bad IDs:

- `runtime/render/software.cpp`
- `new-renderer-temp`
- `C:\\providers\\win32`

## Request A Capability

Requests must say whether the capability is required. Required missing
capabilities refuse. Optional missing capabilities may degrade only when
acceptable degradation is declared and evidence is produced.

## Degrade Explicitly

If selected behavior is weaker or different than requested behavior, emit a
degraded decision. Include requested capability, selected capability, diagnostic
code, evidence reference, compatibility impact, determinism impact, and recovery.

Do not silently choose a null renderer, software renderer, CLI projection,
omitted module, or fallback package path.

## Define Refusal Codes

Refusal codes must include owner, category, stability, reason, recovery,
diagnostic links, related capabilities or commands where relevant, and proof.

Use typed recovery actions rather than prose alone:

- `install_provider`
- `enable_pack`
- `upgrade_schema`
- `select_alternative`
- `run_migration`
- `use_degraded_mode`
- `disable_feature`
- `inspect_evidence`
- `contact_support`
- `not_recoverable`

## Connect To Commands

Commands that require capabilities should declare them in
`required_capabilities`. Command failures caused by missing capabilities should
use refusal codes and diagnostics, not private exceptions or free text.

## Connect To Evidence

Every refused or degraded capability decision should be reproducible from an
evidence packet or validation report. Evidence is proof output, not product
authority.
