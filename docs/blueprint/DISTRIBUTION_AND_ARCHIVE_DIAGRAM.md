Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored distribution and archive diagram after release and archive hardening

# Distribution and Archive Diagram

## Distribution and Archive Flow

```text
component graph -> install profiles -> release index -> release manifest
        |               |                 |                 |
        v               v                 v                 v
 trust roots ----> compatibility policy ----> update model ----> archive policy
        |                                                     |
        v                                                     v
  verification suites -------------------------------> offline archive bundle
```

## Notes

- Υ-series should turn these current release foundations into a stricter control plane.
- Trust roots, component graphs, and archive policies are already strong planning anchors.

