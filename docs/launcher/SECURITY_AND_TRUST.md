# Security and Trust

Doc Version: 1

The launcher’s security model is centered on determinism, explicit trust boundaries, and verifiable artifacts. It does not add storefront, DRM, ads, or mandatory accounts.

## Trust Boundaries

- The launcher does not implicitly trust remote content.
- Artifact payloads are validated by hash before use.
- Newer/unknown TLV schema versions are refused; unknown tags within a supported version are skipped and preserved.

## Determinism and Auditability

- Core decisions depend only on explicit inputs and injected capabilities.
- All decisions that affect launch behavior are recorded in audit as “selected-and-why”.
- Runtime hardening rejects unsafe instance identifiers to prevent path traversal and out-of-root writes.

## Offline Operation

When artifacts required by an instance are present and verified, the launcher can plan and perform offline launches. Networking capability is optional and may be disabled.

## Packaging and Code Signing

Packaging must not change runtime behavior.
- Windows installers are per-user and do not install background services.
- macOS codesign integration is optional and may be stubbed by build configuration.
- Linux distribution is provided as portable archives (and optional AppDir-style layouts).

See `docs/launcher/BUILD_AND_PACKAGING.md`.

