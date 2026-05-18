import hashlib
import json
import os


ALLOWLIST_REL = "contracts/repo/semantic_lint_allowlist.json"


def context_hash(text):
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def load_allowlist(repo_root, test_name):
    path = os.path.join(repo_root, ALLOWLIST_REL)
    if not os.path.exists(path):
        return set(), []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError) as exc:
        return set(), ["failed to read semantic lint allowlist: {0}".format(exc)]

    entries = payload.get("entries")
    if not isinstance(entries, list):
        return set(), ["semantic lint allowlist entries must be a list"]

    keys = set()
    errors = []
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append("semantic lint allowlist entry {0} must be an object".format(idx))
            continue
        if entry.get("test_name") != test_name:
            continue
        try:
            key = (
                str(entry["file"]),
                int(entry["line"]),
                str(entry["validator_message"]),
                str(entry["context_sha256"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append("semantic lint allowlist entry {0} is invalid: {1}".format(idx, exc))
            continue
        reason = str(entry.get("reason", "")).strip()
        disposition = str(entry.get("disposition", "")).strip()
        owner = str(entry.get("owner", "")).strip()
        if not reason or not disposition or not owner:
            errors.append("semantic lint allowlist entry {0} requires reason, disposition, and owner".format(idx))
            continue
        keys.add(key)

    return keys, errors


def is_allowed(allowlist, rel_path, line, label, text):
    key = (rel_path, int(line), label, context_hash(text))
    return key in allowlist
