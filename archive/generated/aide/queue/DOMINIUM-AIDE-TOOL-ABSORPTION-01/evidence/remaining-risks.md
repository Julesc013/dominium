# Remaining Risks

Status: needs_review

- Full AIDE `eval run` did not complete within the local timeout.
- AIDE repo validation still reports unknown file classifications.
- AIDE verify still reports missing generated controller report refs in the review packet.
- Tool inventory contains 854 unknown candidates requiring manual classification or future classifier improvement.
- High-risk tool candidates include release, security, build, destructive-candidate, and authority-sensitive surfaces.
- XStack/AuditX/RepoX/TestX contain valuable old logic but need command contracts before wrapper execution.
- Q52 root recycling must remain evidence-only until root ownership, references, and safe validation paths are proved.
