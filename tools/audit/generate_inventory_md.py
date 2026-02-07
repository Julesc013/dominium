import json
import os
from datetime import date


def main():
    src = os.path.join("docs", "audit", "INVENTORY_MACHINE.json")
    dst = os.path.join("docs", "audit", "INVENTORY.md")
    with open(src, "r", encoding="utf-8") as f:
        inv = json.load(f)

    summary = inv.get("summary", {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(date.today().isoformat()),
        "Supersedes: none",
        "Superseded By: none",
        "",
        "# Repository Inventory (Machine-verified)",
        "",
        "Root: `{}`".format(inv.get("root", "")),
        "",
        "## Summary",
        "",
    ]
    for key in sorted(summary.keys()):
        lines.append("- {}: {}".format(key, summary[key]))
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Inventory items are path-based and cross-linked to owning subsystem docs where known.",
            "- This inventory excludes `.git` and `.vs`.",
            "- Build outputs may be incomplete if a full build has not been run.",
        ]
    )

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
