Status: CANONICAL
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: DIST-3 clean-room distribution verification doctrine

# Distribution Verification Rules

## Purpose

DIST-2 verifies an assembled distribution tree offline and deterministically.
It does not package archives and it does not depend on network services.

## Verification Order

The verifier runs in this exact order:

1. layout check
2. release-manifest verification
3. offline pack verification
4. endpoint descriptor hash verification
5. forbidden-file scan
6. absolute-path scan
7. UI mode sanity checks

The verifier stops only after collecting the full deterministic report for the requested bundle.

## Refusal Codes

- `refusal.dist.missing_artifact`
  - required layout path or manifest-declared artifact is missing
  - remediation: rerun `python tools/dist/tool_assemble_dist_tree.py --repo-root . --platform-tag <platform> --channel mock`
- `refusal.dist.hash_mismatch`
  - release-manifest content hash, descriptor hash, or filelist-derived content hash does not match the bundle
  - remediation: regenerate the bundle and rerun `python tools/release/tool_generate_release_manifest.py ...`
- `refusal.dist.forbidden_file_present`
  - development payload, forbidden XStack governance surface, source file, or excluded scratch artifact is present in the bundle
  - remediation: remove the forbidden payload or rerun deterministic assembly
- `refusal.dist.absolute_path_leak`
  - manifest/config text includes an absolute host path or build-local path token
  - remediation: rewrite the artifact to use relative or logical virtual-path references, then regenerate the manifest

## Deterministic Scan Scope

- Layout is checked against the canonical portable-bundle requirements.
- Manifest verification uses RELEASE-1 offline verification rules.
- Pack verification uses bundled `setup packs verify`.
- Forbidden-file scanning uses sorted file traversal and a fixed exclusion policy.
- Absolute-path scanning uses sorted text-file traversal and canonical token detection.
- Mode sanity uses AppShell command surfaces with explicit `--mode cli` and `--mode tui` overrides where supported.

## XStack Policy in Distribution

`INV-NO-XSTACK-IN-DIST` is enforced against non-runtime XStack governance/dev surfaces.
The current portable runtime still requires a narrow support subset under `tools/xstack/`:

- `cache_store`
- `compatx`
- `pack_contrib`
- `pack_loader`
- `packagingx`
- `registry_compile`
- `sessionx`

Any other XStack surface in a distribution tree is a DIST-2 violation.

## Offline Requirement

- Verification must work with only the assembled distribution tree and the verifying Python runtime.
- Signatures remain optional and additive.
- No network lookup, repo-only registry lookup, or host registry lookup is permitted.
