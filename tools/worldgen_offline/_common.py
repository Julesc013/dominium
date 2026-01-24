import argparse
import hashlib
import json
from pathlib import Path


def repo_root():
    return Path(__file__).resolve().parents[2]


def cache_root(root):
    return root / "build" / "cache" / "assets"


def ensure_cache_path(path, root):
    cache_dir = cache_root(root).resolve()
    output = path.resolve()
    try:
        output.relative_to(cache_dir)
    except ValueError as exc:
        raise ValueError(f"output must be under {cache_dir}") from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, payload):
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def find_pack_manifests(paths):
    manifests = []
    for raw in paths:
        if raw.is_file() and raw.name == "pack_manifest.json":
            manifests.append(raw)
            continue
        if raw.is_dir():
            candidate = raw / "pack_manifest.json"
            if candidate.exists():
                manifests.append(candidate)
                continue
            manifests.extend(sorted(raw.rglob("pack_manifest.json")))
    return manifests


def collect_records(paths, filename):
    records = []
    for root in paths:
        for path in sorted(root.rglob(filename)):
            data = load_json(path)
            for record in data.get("records", []):
                record = dict(record)
                record["_source"] = str(path)
                records.append(record)
    return records


def compute_hash(payload):
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def parse_pack_paths(args):
    root = repo_root()
    if not args.packs:
        return [root / "data" / "packs"]
    return [Path(p).expanduser().resolve() for p in args.packs]
