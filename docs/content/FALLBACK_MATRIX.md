Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# UPS Fallback Matrix

This matrix defines allowed fallback classes when capabilities are missing.
All fallbacks MUST be deterministic and MUST NOT alter authoritative truth.

| Capability Class | Allowed Fallback | Prohibited | Notes |
| --- | --- | --- | --- |
| simulation.truth.* | Compatibility downgrade (Frozen/Transform-only) | Heuristic simulation that mutates truth | Missing truth capabilities MUST stop authoritative simulation. |
| simulation.view.* | Disable feature or reduce fidelity | Injecting data not produced by processes | Subjective/derived views MAY degrade. |
| presentation.* | ASCII/text rendering | Any dependency on pack assets | Presentation MUST remain non-authoritative. |
| audio.* | Silence with timing preserved | Timing changes | Silence is acceptable; timing is not. |
| ui.* | Text UI or headless mode | UI-dependent simulation changes | UI is never authoritative. |
| tools.* | Disable tooling feature | Auto-enabling content | Tools MUST not mutate pack state. |

Notes:
- Capability classes are logical namespaces; packs may define finer-grained
  capabilities under these prefixes.
- If no fallback is defined, the system MUST fail loudly or downgrade mode.