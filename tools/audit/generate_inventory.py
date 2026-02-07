import json
import os


def should_skip_dir(rel_path, exclude_set):
    parts = rel_path.split(os.sep)
    return parts[0] in exclude_set


def main():
    root = "."
    exclude = {".git", ".vs"}
    subdocs = {
        "engine": "docs/engine/README.md",
        "game": "docs/game/README.md",
        "client": "docs/app/README.md",
        "server": "docs/app/README.md",
        "launcher": "docs/app/README.md",
        "setup": "docs/app/README.md",
        "tools": "docs/tools/TOOLING_OVERVIEW.md",
        "libs": "docs/architecture/PROJECT_LIBRARIES.md",
        "schema": "docs/schema/SCHEMA_INDEX.md",
        "data": "docs/pack_format/PACK_MANIFEST.md",
        "ci": "docs/ci/README.md",
        "build": "docs/build/README.md",
        "dist": "docs/distribution/README.md",
        "updates": "docs/distribution/README.md",
        "tests": "docs/repox/TESTX_OVERVIEW.md",
    }

    items = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel == ".":
            rel = ""
        if rel and should_skip_dir(rel, exclude):
            dirnames[:] = []
            continue
        for name in filenames:
            path = os.path.join(rel, name) if rel else name
            if path.startswith(".git"):
                continue
            ext = os.path.splitext(name)[1].lower()
            category = None
            if ext in [".exe", ".dll", ".so", ".dylib"]:
                category = "binary"
            elif ext in [".a", ".lib"]:
                category = "library"
            if path.startswith("schema" + os.sep):
                category = "schema"
            elif path.startswith("tests" + os.sep) or path.startswith(
                "game" + os.sep + "tests" + os.sep
            ):
                category = "test"
            elif path.startswith("tools" + os.sep):
                category = "tool"
            elif path.startswith("data" + os.sep):
                category = "data"
            elif path.startswith("ci" + os.sep) or path.startswith(
                "scripts" + os.sep + "ci" + os.sep
            ):
                category = "ci"
            elif path.startswith("build" + os.sep) or path.startswith("out" + os.sep):
                category = "build"
            elif path.startswith("dist" + os.sep) or path.startswith(
                "updates" + os.sep
            ):
                category = "distribution"
            if category is None:
                continue

            subsystem = rel.split(os.sep)[0] if rel else ""
            if subsystem in ["", "tests", "scripts", "ci", "build", "out", "dist", "updates"]:
                subsystem = category
            doc = subdocs.get(subsystem, subdocs.get(category, ""))
            items.append(
                {
                    "path": path.replace("\\", "/"),
                    "category": category,
                    "subsystem": subsystem,
                    "doc": doc,
                }
            )

    summary = {}
    for it in items:
        summary[it["category"]] = summary.get(it["category"], 0) + 1

    inventory = {
        "root": os.path.abspath(root),
        "summary": summary,
        "items": items,
    }

    os.makedirs("docs/audit", exist_ok=True)
    with open("docs/audit/INVENTORY_MACHINE.json", "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
