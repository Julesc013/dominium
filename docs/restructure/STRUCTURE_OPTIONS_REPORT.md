Status: DERIVED
Last Reviewed: 2026-03-27
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI-5
Replacement Target: approved mapping lock for XI-5

# Structure Options Report

## Option Comparison

### OPTION A - Domain-first canonical layout

- Preferred: `no`
- Xi-5 Complexity: `HIGH`
- Automatic move count: `541`
- Manual review count: `241`
- Attic count: `13`

Advantages:
- Aligns immediately with the long-term domain-first topology.
- Makes later enforcement simpler once approved.

Architectural Drawbacks:
- Most aggressive normalization pressure on current product and legacy roots.
- Increases architectural invention risk for ambiguous runtime subsystems.

### OPTION B - Hybrid product/domain layout

- Preferred: `no`
- Xi-5 Complexity: `MED`
- Automatic move count: `637`
- Manual review count: `145`
- Attic count: `13`

Advantages:
- Clarifies product shells under apps/client, apps/server, apps/setup, and apps/launcher.
- Keeps shared domains explicit for lib/ui/platform/compat/tools.

Architectural Drawbacks:
- Still requires product/domain line-drawing for mixed client-appshell-ui surfaces.
- Legacy provider and shared support code remain ambiguous.

### OPTION C - Conservative migration layout

- Preferred: `yes`
- Xi-5 Complexity: `LOW`
- Automatic move count: `663`
- Manual review count: `132`
- Attic count: `0`

Advantages:
- Minimizes structural invention while still eliminating source-like directories.
- Best matches the current evidence and legacy product surfaces.

Architectural Drawbacks:
- Leaves deeper normalization work for later series after XI-5.
- Produces a less ideal immediate end-state for architecture freeze.
