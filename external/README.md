Status: CANONICAL
Last Reviewed: 2026-05-23
Supersedes: none
Superseded By: none
Stability: provisional
Task: PROVIDER-STRUCTURE-CANON-01

# External Source Policy

Third-party source is fenced here. Dominium services remain first-party; external
libraries may only supply provider implementations or tooling inputs.

Canonical layout:

```text
external/upstream/<dependency>/
external/licenses/<dependency>.LICENSE
external/manifests/third_party.toml
external/patches/<dependency>/
```

Do not add `runtime/raylib`, `contracts/raylib`, app-specific raylib roots, or a
top-level vendor/library root. Provider code belongs under
`runtime/<service>/providers/<provider>`.

No third-party source is vendored by this policy file.
