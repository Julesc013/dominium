import os
import re


def main():
    ctest_file = os.path.join("out", "build", "vs2026", "verify", "CTestTestfile.cmake")
    if not os.path.exists(ctest_file):
        return 1

    add_test_re = re.compile(r"add_test\(\"([^\"]+)\"")
    tests = []
    with open(ctest_file, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = add_test_re.search(line)
            if m:
                tests.append(m.group(1))

    categories = {}
    for name in tests:
        prefix = name.split("_")[0] if "_" in name else name
        categories.setdefault(prefix, 0)
        categories[prefix] += 1

    out_path = os.path.join("docs", "audit", "TEST_COVERAGE_MATRIX.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Status: DERIVED\n")
        f.write("Last Reviewed: 2026-02-07\n")
        f.write("Supersedes: none\n")
        f.write("Superseded By: none\n\n")
        f.write("# Test Coverage Matrix (CTEST)\n\n")
        f.write("Source: `{}`\n\n".format(ctest_file.replace("\\", "/")))
        f.write("## Summary by prefix\n\n")
        for key in sorted(categories.keys()):
            f.write("- {}: {}\n".format(key, categories[key]))
        f.write("\n## Total\n\n")
        f.write("- tests: {}\n".format(len(tests)))
        f.write("\n## Notes\n\n")
        f.write("- This is a structural inventory only; semantic mapping requires manual review.\n")
        f.write("- Use test names as the first-pass signal for capability and invariant coverage.\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
