Status: DERIVED
Last Reviewed: 2026-05-20
Task: PUBLIC-SURFACE-REGISTRY-01

# Public Surface Contract Fixtures

These fixtures exercise `tools/validators/repo/check_public_surface.py`.

- `valid_minimal_public_surface.toml` is expected to pass.
- `invalid_missing_owner.toml` is expected to fail because a surface has no owner.
- `invalid_stable_without_proof.toml` is expected to fail because stable surfaces require proof.

They are test fixtures only and are not product or compatibility surfaces.
