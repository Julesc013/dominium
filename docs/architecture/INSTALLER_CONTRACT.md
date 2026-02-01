Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Installer Contract (DIST1)





Status: binding.


Scope: installer responsibilities and refusal behavior.





## Required behavior


- Create data root on first install.


- Never modify or patch binaries after install.


- No content installed by default.


- Offline install must succeed without network access.





## Refusal behavior


- Missing permissions -> explicit refusal.


- Data root creation failure -> explicit refusal.





## See also


- `docs/architecture/DISTRIBUTION_LAYOUT.md`
