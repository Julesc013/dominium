import argparse
import os
import shutil
import subprocess
import sys
import tempfile


HEADER_EXTS = {".h", ".hh", ".hpp", ".hxx", ".inl"}


def iter_headers(root):
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            _, ext = os.path.splitext(name)
            if ext.lower() in HEADER_EXTS:
                yield os.path.join(dirpath, name)


def find_compiler(candidates):
    for name in candidates:
        path = shutil.which(name)
        if path:
            return path
    return None


def compile_with_gcc_like(compiler, include_dirs, header_rel):
    src = '#include "{}"\n'.format(header_rel)
    src += "int main() { return 0; }\n"
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "header_check.cpp")
        with open(src_path, "w", encoding="utf-8") as handle:
            handle.write(src)
        cmd = [
            compiler,
            "-std=c++98",
            "-pedantic-errors",
            "-Werror",
            "-Wall",
            "-Wextra",
            "-fsyntax-only",
        ]
        for include_root in include_dirs:
            cmd.extend(["-I", include_root])
        cmd.append(src_path)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return result.returncode, result.stdout


def compile_with_msvc(compiler, include_dirs, header_rel):
    src = '#include "{}"\n'.format(header_rel)
    src += "int main() { return 0; }\n"
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "header_check.cpp")
        with open(src_path, "w", encoding="utf-8") as handle:
            handle.write(src)
        cmd = [
            compiler,
            "/nologo",
            "/TP",
            "/W4",
            "/WX",
            "/Zc:forScope-",
            "/Zs",
        ]
        for include_root in include_dirs:
            cmd.append("/I{}".format(include_root))
        cmd.append(src_path)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return result.returncode, result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile game public headers as C++98.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-HDR-CPP98"
    include_root = os.path.join(repo_root, "game", "include")
    engine_include = os.path.join(repo_root, "engine", "include")
    if not os.path.isdir(include_root):
        print("{}: missing game include root".format(invariant_id))
        return 1
    if not os.path.isdir(engine_include):
        print("{}: missing engine include root".format(invariant_id))
        return 1
    include_dirs = [include_root, engine_include]

    headers = sorted(iter_headers(include_root))
    if not headers:
        print("{}: no headers found under game/include".format(invariant_id))
        return 1

    compiler = find_compiler(["clang++", "g++", "c++"])
    msvc = None if compiler else find_compiler(["cl"])

    if not compiler and not msvc:
        legacy = os.path.join(repo_root, "tests", "app", "legacy_header_tests.py")
        if not os.path.isfile(legacy):
            print("{}: no compiler and missing legacy header test".format(invariant_id))
            return 1
        result = subprocess.run([sys.executable, legacy, "--repo-root", repo_root],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if result.returncode != 0:
            print("{}: legacy header lint failed".format(invariant_id))
            if result.stdout:
                print(result.stdout.strip())
            return result.returncode
        if result.stdout:
            print(result.stdout.strip())
        print("compiler not found; used legacy header lint fallback")
        return 0

    failures = []
    for header in headers:
        rel = os.path.relpath(header, include_root).replace("\\", "/")
        if compiler:
            code, output = compile_with_gcc_like(compiler, include_dirs, rel)
        else:
            code, output = compile_with_msvc(msvc, include_dirs, rel)
        if code != 0:
            failures.append((rel, output.strip()))

    if failures:
        print("{}: header compile failures detected".format(invariant_id))
        for rel, output in failures:
            print("{}: compile failure".format(rel))
            if output:
                print(output)
        return 1

    print("game public headers compile as C++98")
    return 0


if __name__ == "__main__":
    sys.exit(main())
