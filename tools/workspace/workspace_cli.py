import argparse
import json
import os
import sys


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
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
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


def write_workspace_toml(path, workspace_id, workspace_version, overlays):
    overlays_list = ", ".join(['"{}"'.format(p) for p in overlays])
    lines = [
        'workspace_id = "{}"'.format(workspace_id),
        'workspace_version = "{}"'.format(workspace_version),
        "overlays = [{}]".format(overlays_list),
        "extensions = {}",
        "",
    ]
    write_text(path, "\n".join(lines))


def init_workspace(args):
    data_root = os.path.abspath(args.data_root)
    workspace_id = args.workspace_id
    if "." not in workspace_id:
        print("workspace_id not namespaced")
        return 1
    if args.path:
        root = os.path.abspath(args.path)
    else:
        root = os.path.join(data_root, "workspaces", workspace_id)
    os.makedirs(root, exist_ok=True)
    os.makedirs(os.path.join(root, "data"), exist_ok=True)
    os.makedirs(os.path.join(root, "schema"), exist_ok=True)
    write_workspace_toml(
        os.path.join(root, "workspace.toml"),
        workspace_id,
        args.workspace_version,
        ["data", "schema"],
    )
    print("Workspace initialized: {}".format(root))
    return 0


def mount_workspace(args):
    data_root = os.path.abspath(args.data_root)
    workspace_id = args.workspace_id
    root = os.path.join(data_root, "workspaces", workspace_id)
    toml_path = os.path.join(root, "workspace.toml")
    if not os.path.isfile(toml_path):
        print("workspace.toml missing: {}".format(toml_path))
        return 1
    rel_root = os.path.relpath(root, data_root)
    if rel_root.startswith(".."):
        print("workspace path must be under data root")
        return 1
    meta = parse_toml(toml_path)
    record = {
        "workspace_id": meta.get("workspace_id", workspace_id),
        "workspace_version": meta.get("workspace_version", "1.0.0"),
        "relative_path": rel_root.replace("\\", "/"),
        "overlays": meta.get("overlays", []),
    }
    index_dir = os.path.join(data_root, "index", "workspaces")
    os.makedirs(index_dir, exist_ok=True)
    write_json(os.path.join(index_dir, workspace_id + ".json"), record)
    print("Workspace mounted: {}".format(workspace_id))
    return 0


def validate_workspace(args):
    data_root = os.path.abspath(args.data_root)
    workspace_id = args.workspace_id
    root = os.path.join(data_root, "workspaces", workspace_id)
    toml_path = os.path.join(root, "workspace.toml")
    if not os.path.isfile(toml_path):
        print("workspace missing: {}".format(workspace_id))
        return 1
    meta = parse_toml(toml_path)
    overlays = meta.get("overlays", [])
    for overlay in overlays:
        if os.path.isabs(overlay) or ".." in overlay:
            print("invalid overlay path: {}".format(overlay))
            return 1
        overlay_path = os.path.join(root, overlay)
        if not os.path.isdir(overlay_path):
            print("overlay missing: {}".format(overlay_path))
            return 1
    print("Workspace OK.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Workspace CLI")
    sub = parser.add_subparsers(dest="cmd")

    init = sub.add_parser("init")
    init.add_argument("--data-root", required=True)
    init.add_argument("--workspace-id", required=True)
    init.add_argument("--workspace-version", default="1.0.0")
    init.add_argument("--path", default=None)

    mount = sub.add_parser("mount")
    mount.add_argument("--data-root", required=True)
    mount.add_argument("--workspace-id", required=True)

    validate = sub.add_parser("validate")
    validate.add_argument("--data-root", required=True)
    validate.add_argument("--workspace-id", required=True)

    args = parser.parse_args()
    if args.cmd == "init":
        return init_workspace(args)
    if args.cmd == "mount":
        return mount_workspace(args)
    if args.cmd == "validate":
        return validate_workspace(args)
    parser.print_usage()
    return 1


if __name__ == "__main__":
    sys.exit(main())
