#!/usr/bin/env python3
import argparse
import json

from dompkg_lib import DomPkgError, extract_package, refusal_payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract deterministic dompkg artifacts.")
    parser.add_argument("--pkg", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    try:
        payload = extract_package(args.pkg, args.out, overwrite=args.overwrite)
        print(json.dumps(payload, indent=2))
        return 0
    except DomPkgError as exc:
        print(json.dumps(refusal_payload(exc.code, exc.message, exc.details), indent=2))
        return 3
    except Exception as exc:  # pragma: no cover
        print(json.dumps(refusal_payload("refuse.internal_error", "extract failed", {"error": str(exc)}), indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
