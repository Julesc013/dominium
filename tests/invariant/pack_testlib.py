import json
import os


def write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def create_pack(
    repo_root: str,
    category: str,
    pack_id: str,
    version: str = "1.0.0",
    dependencies=None,
    contributions=None,
    signature_status: str = "signed",
) -> str:
    dependencies = list(dependencies or [])
    contributions = list(contributions or [])
    contribution_types = sorted(set(str(row.get("type", "")) for row in contributions if isinstance(row, dict)))

    pack_dir = os.path.join(repo_root, "packs", category, pack_id)
    manifest = {
        "schema_version": "1.0.0",
        "pack_id": pack_id,
        "version": version,
        "compatibility": {
            "session_spec_min": "1.0.0",
            "session_spec_max": "1.0.0",
        },
        "dependencies": dependencies,
        "contribution_types": contribution_types or ["registry_entries"],
        "contributions": contributions
        or [
            {
                "type": "registry_entries",
                "id": "{}.registry".format(pack_id),
                "path": "data/registry.json",
            }
        ],
        "canonical_hash": "placeholder.{}.{}".format(pack_id, version),
        "signature_status": signature_status,
    }
    write_json(os.path.join(pack_dir, "pack.json"), manifest)
    for row in manifest["contributions"]:
        rel = str(row.get("path", "")).replace("/", os.sep)
        write_json(
            os.path.join(pack_dir, rel),
            {
                "contrib_id": str(row.get("id", "")),
                "type": str(row.get("type", "")),
                "version": "1.0.0",
            },
        )
    return pack_dir

