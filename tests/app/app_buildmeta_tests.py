import argparse
import json
import os
import shutil
import subprocess
import sys


def run_cmd(cmd):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    if result.returncode != 0:
        sys.stderr.write("FAIL: {}\n".format(cmd))
        sys.stderr.write(result.stdout)
        return False
    return True


def ensure_clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def require_keys(obj, keys, label):
    for k in keys:
        if k not in obj:
            raise AssertionError("missing {}.{} in metadata".format(label, k))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    temp_root = os.path.abspath(args.temp_root)
    ensure_clean_dir(temp_root)
    out_path = os.path.join(temp_root, "artifact_meta.json")

    if not run_cmd([
        args.tool,
        "--input",
        args.input,
        "--output",
        out_path,
        "--format",
        "json",
        "--product",
        "tools",
    ]):
        return 1

    with open(out_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("schema_version") != 1:
        raise AssertionError("schema_version mismatch")

    require_keys(data, ["artifact", "identity", "toolchain", "hashes"], "root")
    require_keys(data["artifact"], ["path", "file_name", "size", "sha256"], "artifact")
    require_keys(
        data["identity"],
        [
            "product",
            "product_version",
            "build_number",
            "build_id",
            "git_hash",
            "sku",
            "os",
            "arch",
            "renderer",
            "config",
            "artifact_name",
        ],
        "identity",
    )
    require_keys(
        data["toolchain"],
        [
            "id",
            "family",
            "version",
            "stdlib",
            "runtime",
            "link",
            "target",
            "os",
            "arch",
            "os_floor",
            "config",
        ],
        "toolchain",
    )
    require_keys(data["hashes"], ["artifact_sha256", "sidecar_sha256"], "hashes")

    if data["identity"]["product"] != "tools":
        raise AssertionError("unexpected product: {}".format(data["identity"]["product"]))

    if data["artifact"]["sha256"] != data["hashes"]["artifact_sha256"]:
        raise AssertionError("artifact hash mismatch")

    if not data["hashes"]["sidecar_sha256"] or len(data["hashes"]["sidecar_sha256"]) != 64:
        raise AssertionError("sidecar sha256 missing or invalid")

    artifact_name = data["identity"]["artifact_name"]
    for token in (
        data["identity"]["product"],
        data["identity"]["product_version"],
        data["identity"]["os"],
        data["identity"]["arch"],
        data["identity"]["renderer"],
        data["identity"]["config"],
    ):
        if token and token not in artifact_name:
            raise AssertionError("artifact_name missing token {}".format(token))

    if int(data["artifact"]["size"]) <= 0:
        raise AssertionError("artifact size invalid")

    return 0


if __name__ == "__main__":
    sys.exit(main())
