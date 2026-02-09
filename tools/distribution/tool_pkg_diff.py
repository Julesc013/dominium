#!/usr/bin/env python3
import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser(description="dompkg diff planning surface.")
    parser.add_argument("--from", dest="from_pkg", required=False)
    parser.add_argument("--to", dest="to_pkg", required=False)
    _ = parser.parse_args()
    print(json.dumps({
        "result": "refused",
        "refusal": {
            "code": "refuse.not_implemented",
            "message": "tool_pkg_diff is a planned surface only",
            "details": {},
        },
    }, indent=2))
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
