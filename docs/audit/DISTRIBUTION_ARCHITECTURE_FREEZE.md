Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: DIST-1 packaged bundle baseline and DIST-2 installer constitution

# Distribution Architecture Freeze

## Distribution Types

- Portable Full Bundle
- Installed Bundle
- Headless Server Bundle
- Tools-Only Bundle
- Development Bundle (optional, experimental)

## Layout Diagram

```text
<root>/
  install.manifest.json
  manifests/
    release_manifest.json
  bin/
    engine
    game
    client
    server
    setup
    launcher
  store/
    packs/
    profiles/
    locks/
  instances/
    default/
      instance.manifest.json
  saves/
  docs/
  LICENSE
  README
```

## Required Artifacts Checklist

- `install.manifest.json`
- `manifests/release_manifest.json`
- pinned semantic contract registry surface
- default linked instance
- default base-universe `pack_lock`

## Portability Checklist

- install root discovered by adjacency
- virtual paths only
- direct product launch from `bin/`
- no mandatory install registry dependency
- offline verification via release manifest tooling

## Current Staging Observations

- Canonical bundle roots detected: none
- Staging release manifest present: yes
- Fresh temporary manifest verifies current staged dist: complete
- Shipped staging release manifest verification result: refused
- Shipped staging manifest matches fresh generated manifest: no

### Current DIST-1 Gaps

- missing canonical bundle path: `LICENSE`
- missing canonical bundle path: `README`
- missing canonical bundle path: `install.manifest.json`
- missing canonical bundle path: `instances/default/instance.manifest.json`
- missing canonical bundle path: `store/locks`
- missing canonical bundle path: `store/packs`
- missing canonical bundle path: `store/profiles`

### Staging-Only Exclusions Still Present

- staging exclusion to remove during DIST-1 packaging: `bin/__pycache__`
- staging exclusion to remove during DIST-1 packaging: `logs/.gitkeep`
- staging exclusion to remove during DIST-1 packaging: `saves/.gitkeep`

## Portability and Verification Readiness

- Absolute-path hits in staged manifests: 0
- Ready for DIST-1 packaging pass: not yet
