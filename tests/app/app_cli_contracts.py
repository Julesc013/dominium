import argparse
import os
import shutil
import subprocess
import sys

BUILD_INFO_KEYS = [
    "product=",
    "product_version=",
    "engine_version=",
    "game_version=",
    "build_number=",
    "build_id=",
    "git_hash=",
    "toolchain_id=",
    "protocol_law_targets=",
    "protocol_control_caps=",
    "protocol_authority_tokens=",
    "abi_dom_build_info=",
    "abi_dom_caps=",
    "api_dsys=",
    "api_dgfx=",
]


def run_cmd(cmd, expect_code=0, expect_nonzero=False, expect_contains=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    output = result.stdout
    if expect_nonzero:
        if result.returncode == 0:
            sys.stderr.write("FAIL: expected non-zero exit for {}\n".format(cmd))
            sys.stderr.write(output)
            return False
    elif expect_code is not None and result.returncode != expect_code:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
        sys.stderr.write(output)
        return False
    if expect_contains:
        for token in expect_contains:
            if token not in output:
                sys.stderr.write("FAIL: missing '{}' in output for {}\n".format(token, cmd))
                sys.stderr.write(output)
                return False
    return True


def check_build_info(exe, product_name):
    return run_cmd([exe, "--build-info"], expect_contains=BUILD_INFO_KEYS + ["product=" + product_name])


def check_basic_cli(exe, product_token):
    ok = True
    ok = ok and run_cmd([exe, "--help"], expect_contains=["usage"])
    ok = ok and run_cmd([exe, "--version"], expect_contains=[product_token])
    return ok


def ensure_clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True)
    parser.add_argument("--server", required=True)
    parser.add_argument("--launcher", required=True)
    parser.add_argument("--setup", required=True)
    parser.add_argument("--tools", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    ok = True

    ok = ok and check_basic_cli(args.client, "client ")
    ok = ok and check_basic_cli(args.server, "server ")
    ok = ok and check_basic_cli(args.launcher, "launcher ")
    ok = ok and check_basic_cli(args.setup, "setup ")
    ok = ok and check_basic_cli(args.tools, "tools ")

    ok = ok and check_build_info(args.client, "client")
    ok = ok and check_build_info(args.server, "server")
    ok = ok and check_build_info(args.launcher, "launcher")
    ok = ok and check_build_info(args.setup, "setup")
    ok = ok and check_build_info(args.tools, "tools")

    ok = ok and run_cmd([args.client, "--smoke"])
    ok = ok and run_cmd([args.server, "--smoke"])
    ok = ok and run_cmd([args.launcher, "--smoke"])
    ok = ok and run_cmd([args.setup, "--smoke"])
    ok = ok and run_cmd([args.tools, "--smoke"])

    ok = ok and run_cmd([args.client, "--ui=none", "--smoke"])
    ok = ok and run_cmd([args.server, "--ui=none", "--smoke"])
    ok = ok and run_cmd([args.launcher, "--ui=none", "--smoke"])
    ok = ok and run_cmd([args.setup, "--ui=none", "--smoke"])
    ok = ok and run_cmd([args.tools, "--ui=none", "--smoke"])

    ok = ok and run_cmd([args.client, "--deterministic", "--smoke"])
    ok = ok and run_cmd([args.server, "--deterministic", "--smoke"])
    ok = ok and run_cmd([args.launcher, "--deterministic", "--smoke"])
    ok = ok and run_cmd([args.setup, "--deterministic", "--smoke"])
    ok = ok and run_cmd([args.tools, "--deterministic", "--smoke"])

    ok = ok and run_cmd(
        [args.client, "--interactive", "--smoke"],
        expect_nonzero=True,
        expect_contains=["requires deterministic"],
    )
    ok = ok and run_cmd(
        [args.server, "--interactive", "--smoke"],
        expect_nonzero=True,
        expect_contains=["requires deterministic"],
    )
    ok = ok and run_cmd(
        [args.launcher, "--interactive", "--smoke"],
        expect_nonzero=True,
        expect_contains=["requires deterministic"],
    )
    ok = ok and run_cmd(
        [args.setup, "--interactive", "--smoke"],
        expect_nonzero=True,
        expect_contains=["requires deterministic"],
    )
    ok = ok and run_cmd(
        [args.tools, "--interactive", "--smoke"],
        expect_nonzero=True,
        expect_contains=["requires deterministic"],
    )

    ok = ok and run_cmd(
        [args.client, "--renderer=missing", "--smoke"],
        expect_nonzero=True,
        expect_contains=["unavailable"],
    )

    ok = ok and run_cmd(
        [args.launcher, "capabilities"],
        expect_contains=[
            "platform_backend=",
            "renderer_auto=",
            "renderer=",
            "platform_ext_dpi=",
            "platform_ext_window_mode=",
        ],
    )

    ok = ok and run_cmd(
        [args.server, "--ui=gui"],
        expect_nonzero=True,
        expect_contains=["gui not implemented"],
    )
    ok = ok and run_cmd(
        [args.launcher, "--ui=gui"],
        expect_nonzero=True,
        expect_contains=["gui not implemented"],
    )
    ok = ok and run_cmd(
        [args.setup, "--ui=gui"],
        expect_nonzero=True,
        expect_contains=["gui not implemented"],
    )
    ok = ok and run_cmd(
        [args.tools, "--ui=gui"],
        expect_nonzero=True,
        expect_contains=["gui not implemented"],
    )

    temp_root = os.path.abspath(args.temp_root)
    ensure_clean_dir(temp_root)
    setup_root = os.path.join(temp_root, "setup_root")
    ok = ok and run_cmd(
        [args.setup, "prepare", "--root", setup_root],
        expect_contains=["setup_prepare=ok"],
    )
    for name in ("program", "data", "user", "state", "temp"):
        if not os.path.isdir(os.path.join(setup_root, name)):
            sys.stderr.write("FAIL: missing directory {}\n".format(name))
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
