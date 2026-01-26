import argparse
import json
import os
import shutil
import sys


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def write_text(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def parse_list(value):
    value = value.strip()
    if not value.startswith("[") or not value.endswith("]"):
        return []
    inner = value[1:-1].strip()
    if not inner:
        return []
    parts = []
    for token in inner.split(","):
        token = token.strip()
        if token.startswith('"') and token.endswith('"'):
            token = token[1:-1]
        if token:
            parts.append(token)
    return parts


def parse_toml(path):
    data = {}
    for raw in read_text(path).splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            data[key] = value[1:-1]
        elif value.startswith("["):
            data[key] = parse_list(value)
        else:
            data[key] = value
    return data


def write_modpack_toml(path, modpack_id, modpack_version, pack_format_version, packs, lockfile):
    packs_list = ", ".join(['"{}"'.format(p) for p in packs])
    lines = [
        'modpack_id = "{}"'.format(modpack_id),
        'modpack_version = "{}"'.format(modpack_version),
        "pack_format_version = {}".format(int(pack_format_version)),
        "packs = [{}]".format(packs_list),
        'lockfile = "{}"'.format(lockfile),
        "extensions = {}",
        "",
    ]
    write_text(path, "\n".join(lines))


def validate_modpack(root):
    toml_path = os.path.join(root, "modpack.toml")
    lock_path = os.path.join(root, "capabilities.lock")
    if not os.path.isfile(toml_path):
        return False, "modpack.toml missing"
    if not os.path.isfile(lock_path):
        return False, "capabilities.lock missing"
    data = parse_toml(toml_path)
    for key in ("modpack_id", "modpack_version", "pack_format_version", "packs"):
        if key not in data:
            return False, "missing field {}".format(key)
    modpack_id = data.get("modpack_id", "")
    if "." not in modpack_id:
        return False, "modpack_id not namespaced"
    lockfile = data.get("lockfile", "capabilities.lock")
    if os.path.isabs(lockfile) or ".." in lockfile:
        return False, "lockfile path must be relative"
    try:
        lock_data = json.load(open(lock_path, "r", encoding="utf-8"))
    except Exception:
        return False, "capabilities.lock invalid"
    for key in ("lock_id", "lock_format_version", "generated_by", "resolution_rules",
                "missing_mode", "resolutions", "extensions"):
        if key not in lock_data:
            return False, "capabilities.lock missing {}".format(key)
    return True, None


def cmd_create(args):
    root = os.path.abspath(args.out)
    if os.path.exists(root) and os.listdir(root):
        print("output directory not empty: {}".format(root))
        return 1
    os.makedirs(root, exist_ok=True)
    packs = [p for p in args.packs.split(",") if p] if args.packs else []
    lock_payload = {
        "lock_id": "{}.capabilities".format(args.modpack_id),
        "lock_format_version": 1,
        "generated_by": "modpack_cli",
        "resolution_rules": ["pack_version_desc", "pack_id_lex"],
        "missing_mode": "frozen",
        "resolutions": [],
        "extensions": {},
    }
    write_modpack_toml(
        os.path.join(root, "modpack.toml"),
        args.modpack_id,
        args.modpack_version,
        args.pack_format_version,
        packs,
        "capabilities.lock",
    )
    write_json(os.path.join(root, "capabilities.lock"), lock_payload)
    return 0


def cmd_validate(args):
    ok, err = validate_modpack(os.path.abspath(args.root))
    if not ok:
        print("FAIL: {}".format(err))
        return 1
    print("Modpack OK.")
    return 0


def cmd_install(args):
    root = os.path.abspath(args.root)
    ok, err = validate_modpack(root)
    if not ok:
        print("FAIL: {}".format(err))
        return 1
    data = parse_toml(os.path.join(root, "modpack.toml"))
    modpack_id = data.get("modpack_id")
    data_root = os.path.abspath(args.data_root)
    dest = os.path.join(data_root, "modpacks", modpack_id)
    if os.path.exists(dest):
        print("FAIL: destination exists: {}".format(dest))
        return 1
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copytree(root, dest)
    print("Installed modpack: {}".format(dest))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Modpack CLI")
    sub = parser.add_subparsers(dest="cmd")

    create = sub.add_parser("create")
    create.add_argument("--out", required=True)
    create.add_argument("--modpack-id", required=True)
    create.add_argument("--modpack-version", default="1.0.0")
    create.add_argument("--pack-format-version", default="1")
    create.add_argument("--packs", default="")

    validate = sub.add_parser("validate")
    validate.add_argument("--root", required=True)

    install = sub.add_parser("install")
    install.add_argument("--root", required=True)
    install.add_argument("--data-root", required=True)

    args = parser.parse_args()
    if args.cmd == "create":
        return cmd_create(args)
    if args.cmd == "validate":
        return cmd_validate(args)
    if args.cmd == "install":
        return cmd_install(args)
    parser.print_usage()
    return 1


if __name__ == "__main__":
    sys.exit(main())
