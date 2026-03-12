Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: release tool surface audit regenerated from TOOL-SURFACE-0 tooling

# Tool Surface Final

## Summary

- Stable umbrella product: `tool.attach_console_stub`
- Wrapped commands: `113`
- Alias adapters: `12`
- Subprocess adapters: `101`
- Surface fingerprint: `14a3a96edc24bb407ec2fa72b83efae7097b0abb89fa2159ce536e12ad4e45ec`

## Adapter Policy

- In-proc aliases are used when a stable AppShell command already exists.
- Out-of-proc Python adapters are used for standalone `tool_*.py` scripts and selected legacy pack scripts.
- Subprocess adapters execute with `cwd = repo root` and inject `--repo-root .` only when the wrapped tool declares that flag.

## Readiness

- `dom` namespaces now cover: `geo`, `worldgen`, `earth`, `sol`, `gal`, `logic`, `sys`, `proc`, `pack`, `lib`, `compat`, `diag`, `server`, `client`
- Registry drift findings: `0`
- Missing target findings: `0`
- Readiness: stable command umbrella is prepared for APPSHELL-PLATFORM-1 and virtual path hardening.
