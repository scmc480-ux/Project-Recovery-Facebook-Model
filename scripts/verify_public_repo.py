from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recovery_engine.validation.privacy import scan_public_tree


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()

    result = scan_public_tree(Path(args.root))
    if result["status"] == "pass":
        print("Public repository check passed.")
        return 0

    print("Public repository check failed:")
    for finding in result["findings"]:
        print(f"- {finding}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
