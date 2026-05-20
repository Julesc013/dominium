# Artifact Identity Contract Fixtures

These fixtures define the initial validation behavior for
`tools/validators/contracts/check_artifact_identity.py`.

Valid fixtures prove that pack, replay, and evidence artifacts can identify
themselves without relying on path or filename identity.

Invalid fixtures prove that the validator rejects missing artifact IDs, path-like
IDs, filename IDs, missing schema IDs, and unknown artifact kinds.

The fixtures are not product artifacts and do not create compatibility promises.
