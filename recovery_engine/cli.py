from __future__ import annotations

import argparse
from pathlib import Path

from recovery_engine.readers.facebook.reader import process_facebook_export


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-recovery")
    sub = parser.add_subparsers(dest="command", required=True)

    facebook = sub.add_parser("facebook", help="Run Facebook Reader v1.")
    facebook.add_argument("--source", required=True, help="Facebook export folder or zip file.")
    facebook.add_argument("--case-id", required=True, help="Stable case identifier.")
    facebook.add_argument("--output", default="outputs", help="Output root. Defaults to outputs.")
    facebook.add_argument("--strict", action="store_true", help="Fail when validation warnings are found.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "facebook":
        result = process_facebook_export(
            source=Path(args.source),
            case_id=args.case_id,
            output_root=Path(args.output),
            strict=args.strict,
        )
        print(f"Case written: {result.case_root}")
        print(f"Objects: {result.object_count}")
        print(f"Validation: {result.validation_status}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
