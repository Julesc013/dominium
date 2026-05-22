import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def run_cmd(cmd):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    if result.returncode != 0:
        sys.stderr.write("FAIL: {}\n".format(" ".join(cmd)))
        sys.stderr.write(result.stdout)
        return False
    return True


def read_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def main():
    parser = argparse.ArgumentParser(description="Modpack/workspace tooling tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    modpack_cli = os.path.join(repo_root, "tools", "modpack", "modpack_cli.py")
    workspace_cli = os.path.join(repo_root, "tools", "workspace", "workspace_cli.py")

    if not os.path.isfile(modpack_cli):
        print("missing modpack_cli.py")
        return 1
    if not os.path.isfile(workspace_cli):
        print("missing workspace_cli.py")
        return 1

    with tempfile.TemporaryDirectory() as tmpdir:
        data_root_a = os.path.join(tmpdir, "data_a")
        data_root_b = os.path.join(tmpdir, "data_b")
        os.makedirs(data_root_a)
        os.makedirs(data_root_b)

        modpack_src = os.path.join(tmpdir, "modpack_src")
        if not run_cmd([
            sys.executable, modpack_cli, "create",
            "--out", modpack_src,
            "--modpack-id", "org.example.modpack",
            "--modpack-version", "1.0.0",
            "--packs", "org.example.pack.alpha",
        ]):
            return 1

        if not run_cmd([sys.executable, modpack_cli, "validate", "--root", modpack_src]):
            return 1

        if not run_cmd([sys.executable, modpack_cli, "install",
                        "--root", modpack_src, "--data-root", data_root_a]):
            return 1
        if not run_cmd([sys.executable, modpack_cli, "install",
                        "--root", modpack_src, "--data-root", data_root_b]):
            return 1

        installed_a = os.path.join(data_root_a, "modpacks", "org.example.modpack")
        installed_b = os.path.join(data_root_b, "modpacks", "org.example.modpack")
        for path in (installed_a, installed_b):
            if not os.path.isdir(path):
                print("modpack not installed: {}".format(path))
                return 1
            for name in ("modpack.toml", "capabilities.lock"):
                if not os.path.isfile(os.path.join(path, name)):
                    print("missing modpack file: {}".format(name))
                    return 1

        if read_file(os.path.join(installed_a, "modpack.toml")) != read_file(
            os.path.join(installed_b, "modpack.toml")
        ):
            print("modpack.toml differs across installs")
            return 1
        if read_file(os.path.join(installed_a, "capabilities.lock")) != read_file(
            os.path.join(installed_b, "capabilities.lock")
        ):
            print("capabilities.lock differs across installs")
            return 1

        # Workspace init/mount and removal safety.
        if not run_cmd([sys.executable, workspace_cli, "init",
                        "--data-root", data_root_a,
                        "--workspace-id", "org.example.workspace"]):
            return 1
        if not run_cmd([sys.executable, workspace_cli, "mount",
                        "--data-root", data_root_a,
                        "--workspace-id", "org.example.workspace"]):
            return 1
        if not run_cmd([sys.executable, workspace_cli, "validate",
                        "--data-root", data_root_a,
                        "--workspace-id", "org.example.workspace"]):
            return 1

        workspace_root = os.path.join(data_root_a, "workspaces", "org.example.workspace")
        shutil.rmtree(workspace_root)
        if not os.path.isdir(os.path.join(data_root_a, "modpacks")):
            print("workspace removal damaged modpack root")
            return 1

    print("Modpack/workspace tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
