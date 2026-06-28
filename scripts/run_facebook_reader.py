from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recovery_engine.readers.facebook.reader import process_facebook_export


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--output", default="outputs")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

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


if __name__ == "__main__":
    raise SystemExit(main())
