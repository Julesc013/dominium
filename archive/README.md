# Archive Root

Status: PROVISIONAL
Phase: CONVERGE-05

`archive/` is the canonical source repository root for historical, legacy, superseded, quarantined, and intentionally retained generated material.

This root is not active source authority. It is not a runtime, install, media, or distribution layout. Product, build, runtime, schema, domain, and pack semantics must not be inferred from archived paths unless a later reviewed task explicitly promotes a specific archived artifact back into active ownership.

Archive classes:

- `historical/` - old snapshots, obsolete docs, retired planning artifacts, and previous layout material.
- `legacy/` - legacy source or material retained for compatibility research or reference.
- `quarantine/` - unsafe, broken, deprecated, excluded, or review-pending material.
- `superseded/` - replaced material retained to preserve provenance.
- `generated/` - historical generated artifacts retained only when intentionally archived.

Future archive material must be placed under one of these class directories. New root-level archive-family directories such as `attic/`, `legacy/`, or `quarantine/` are retired and must not be recreated.

Quarantined material must remain visibly quarantined. Archived material must not silently re-enter builds, package exports, runtime paths, or source authority.
