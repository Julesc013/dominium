import argparse
import json
import os
import subprocess
import sys
import tempfile


def _run(cmd, cwd):
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )


def _securex(repo_root, args):
    cmd = [sys.executable, os.path.join(repo_root, "tools", "securex", "securex.py")]
    cmd.extend(args)
    cmd.extend(["--repo-root", repo_root])
    return _run(cmd, repo_root)


def main():
    parser = argparse.ArgumentParser(description="SecureX pack signature tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    with tempfile.TemporaryDirectory(prefix="securex-pack-signature-") as temp_dir:
        pack_path = os.path.join(temp_dir, "sample.pack")
        sig_path = os.path.join(temp_dir, "sample.sig.json")
        with open(pack_path, "wb") as handle:
            handle.write(b"dominium-pack-sample\n")

        sign_result = _securex(
            repo_root,
            [
                "sign-pack",
                "--pack-path",
                pack_path,
                "--signer-id",
                "signer.dev",
                "--key-id",
                "key.test",
                "--key-material",
                "key-material-test",
                "--output",
                sig_path,
            ],
        )
        if sign_result.returncode != 0:
            print(sign_result.stdout)
            return 1
        sig_payload = json.load(open(sig_path, "r", encoding="utf-8"))
        if sig_payload.get("schema_id") != "dominium.schema.governance.pack_signature":
            print("signature schema mismatch")
            print(sign_result.stdout)
            return 1

        verify_result = _securex(
            repo_root,
            [
                "verify-pack",
                "--pack-path",
                pack_path,
                "--signature-json",
                sig_path,
                "--key-material",
                "key-material-test",
            ],
        )
        if verify_result.returncode != 0:
            print(verify_result.stdout)
            return 1

        with open(pack_path, "ab") as handle:
            handle.write(b"tamper")
        tampered_result = _securex(
            repo_root,
            [
                "verify-pack",
                "--pack-path",
                pack_path,
                "--signature-json",
                sig_path,
                "--key-material",
                "key-material-test",
            ],
        )
        if tampered_result.returncode == 0:
            print("tampered pack unexpectedly verified")
            print(tampered_result.stdout)
            return 1

    print("securex_pack_signature_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
