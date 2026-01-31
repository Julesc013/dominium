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


def compile_with_gcc_like(compiler, include_root, header_rel, language):
    src = '#include "{}"\n'.format(header_rel)
    if language == "c":
        src += "int main(void) { return 0; }\n"
        std_flag = "-std=c89"
    else:
        src += "int main() { return 0; }\n"
        std_flag = "-std=c++98"
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "header_check.{}".format("c" if language == "c" else "cpp"))
        with open(src_path, "w", encoding="utf-8") as handle:
            handle.write(src)
        cmd = [
            compiler,
            std_flag,
            "-pedantic-errors",
            "-Werror",
            "-Wall",
            "-Wextra",
            "-fsyntax-only",
            "-I",
            include_root,
            src_path,
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return result.returncode, result.stdout


def compile_with_msvc(compiler, include_root, header_rel, language):
    src = '#include "{}"\n'.format(header_rel)
    src += "int main(void) { return 0; }\n"
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "header_check.c")
        with open(src_path, "w", encoding="utf-8") as handle:
            handle.write(src)
        cmd = [
            compiler,
            "/nologo",
            "/TC",
            "/Za",
            "/W4",
            "/WX",
            "/Zs",
            "/I{}".format(include_root),
            src_path,
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return result.returncode, result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile engine public headers as C89.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-HDR-C89"
    include_root = os.path.join(repo_root, "engine", "include")
    if not os.path.isdir(include_root):
        print("{}: missing engine include root".format(invariant_id))
        return 1

    headers = sorted(iter_headers(include_root))
    if not headers:
        print("{}: no headers found under engine/include".format(invariant_id))
        return 1

    compiler = find_compiler(["clang", "gcc", "cc"])
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
            code, output = compile_with_gcc_like(compiler, include_root, rel, "c")
        else:
            code, output = compile_with_msvc(msvc, include_root, rel, "c")
        if code != 0:
            failures.append((rel, output.strip()))

    if failures:
        print("{}: header compile failures detected".format(invariant_id))
        for rel, output in failures:
            print("{}: compile failure".format(rel))
            if output:
                print(output)
        return 1

    print("engine public headers compile as C89")
    return 0


if __name__ == "__main__":
    sys.exit(main())
