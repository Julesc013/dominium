# Remaining Risks

Status: needs_review

- Q52 and Q53 evidence are uncommitted because git write permission is blocked in the current sandbox.
- Full AIDE eval remains timeout-prone.
- `py -3` launcher is inaccessible; Python 3.14 direct path works.
- Default `python` is Python 3.8 and is too old for current AIDE write helpers.
- AIDE verify remains WARN while generated evidence is dirty.
- Repo/root/tool classifiers still have unknown candidates.
- Tool absorption and root recycling are evidence-only; no wrapper execution or migration is approved.
