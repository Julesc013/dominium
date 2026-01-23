import argparse
import os
import re
import sys


def parse_report(path):
    data = {}
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
    return data


def split_list(value):
    if not value:
        return []
    return [item for item in value.split(";") if item]


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def main():
    parser = argparse.ArgumentParser(description="Verify integration wiring for products/backends/extensions.")
    parser.add_argument("--report", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    report_path = os.path.abspath(args.report)
    repo_root = os.path.abspath(args.repo_root)
    if not os.path.isfile(report_path):
        sys.stderr.write("FAIL: integration report not found: {}\n".format(report_path))
        return 1

    data = parse_report(report_path)
    testx_tests = set(split_list(data.get("registered_testx_tests", "")))

    errors = []

    products = {}
    for entry in split_list(data.get("registered_products", "")):
        parts = entry.split("|", 1)
        name = parts[0].strip()
        target = parts[1].strip() if len(parts) > 1 else ""
        if name:
            products[name] = target
    if not products:
        errors.append("no registered products")

    product_tests = {}
    for entry in split_list(data.get("registered_product_cli_tests", "")):
        parts = entry.split("|")
        if len(parts) < 4:
            continue
        product, version_test, build_info_test, smoke_test = parts[0:4]
        product_tests[product] = (version_test, build_info_test, smoke_test)

    for product in sorted(products.keys()):
        tests = product_tests.get(product)
        if not tests:
            errors.append("product '{}' missing CLI test registration".format(product))
            continue
        for test_name in tests:
            if test_name not in testx_tests:
                errors.append(
                    "product '{}' references missing TestX test '{}'".format(product, test_name)
                )

    renderer_backends = []
    for entry in split_list(data.get("registered_renderer_backends", "")):
        parts = entry.split("|", 1)
        name = parts[0].strip()
        availability = parts[1].strip() if len(parts) > 1 else "unknown"
        if name:
            renderer_backends.append((name, availability))
    if not renderer_backends:
        errors.append("no registered renderer backends")

    renderer_tests = {}
    for entry in split_list(data.get("registered_renderer_tests", "")):
        parts = entry.split("|")
        if len(parts) < 3:
            continue
        backend, explicit_test, caps_test = parts[0:3]
        renderer_tests[backend] = (explicit_test, caps_test)

    for backend, _availability in renderer_backends:
        tests = renderer_tests.get(backend)
        if not tests:
            errors.append("renderer backend '{}' missing test registration".format(backend))
            continue
        for test_name in tests:
            if test_name not in testx_tests:
                errors.append(
                    "renderer backend '{}' references missing TestX test '{}'".format(
                        backend, test_name
                    )
                )

    platform_backends = split_list(data.get("registered_platform_backends", ""))
    if not platform_backends:
        errors.append("no registered platform backends")

    docs_required = [
        os.path.join(repo_root, "docs", "app", "README.md"),
        os.path.join(repo_root, "docs", "platform", "README.md"),
        os.path.join(repo_root, "docs", "render", "README.md"),
        os.path.join(repo_root, "docs", "repox", "APRX_INTEGRATION_HOOKS.md"),
    ]
    for doc_path in docs_required:
        if not os.path.isfile(doc_path):
            errors.append("missing docs index: {}".format(doc_path))

    sys_header = os.path.join(repo_root, "engine", "include", "domino", "sys.h")
    if not os.path.isfile(sys_header):
        errors.append("missing platform header: {}".format(sys_header))
    else:
        ext_name_re = re.compile(r'^#define\\s+DSYS_EXTENSION_([A-Z0-9_]+)\\s+"([^"]+)"')
        ext_ver_re = re.compile(r'^#define\\s+DSYS_EXTENSION_([A-Z0-9_]+)_VERSION\\s+')
        ext_names = {}
        ext_versions = set()
        for line in read_text(sys_header).splitlines():
            name_match = ext_name_re.match(line)
            if name_match:
                key = name_match.group(1).lower()
                ext_names[key] = name_match.group(2)
            ver_match = ext_ver_re.match(line)
            if ver_match:
                ext_versions.add(ver_match.group(1).lower())
        for key in sorted(ext_names.keys()):
            if key not in ext_versions:
                errors.append("extension '{}' missing version macro".format(key))

        app_runtime = os.path.join(repo_root, "app", "src", "app_runtime.c")
        cli_contracts = os.path.join(repo_root, "docs", "app", "CLI_CONTRACTS.md")
        if not os.path.isfile(app_runtime):
            errors.append("missing app runtime file: {}".format(app_runtime))
        if not os.path.isfile(cli_contracts):
            errors.append("missing CLI contracts doc: {}".format(cli_contracts))
        if os.path.isfile(app_runtime) and os.path.isfile(cli_contracts):
            runtime_text = read_text(app_runtime)
            cli_text = read_text(cli_contracts)
            for key in sorted(ext_names.keys()):
                build_key = "platform_ext_" + key + "_api"
                if build_key not in runtime_text:
                    errors.append("build-info missing extension key '{}' in app_runtime.c".format(build_key))
                if build_key not in cli_text:
                    errors.append("CLI_CONTRACTS missing extension key '{}'".format(build_key))

    if errors:
        for err in errors:
            sys.stderr.write("FAIL: {}\n".format(err))
        return 1

    print("Integration meta-test OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
