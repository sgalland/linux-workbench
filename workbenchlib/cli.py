"""Read-only Workbench command dispatch."""

import json
import sys

from workbenchlib.compare import compare, load_snapshot
from workbenchlib.inspect import main as inspect_main


def main(args: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if args is None else args)
    if args == ["inspect"]:
        return inspect_main(args)
    if len(args) == 3 and args[0] == "compare":
        try:
            result = compare(load_snapshot(args[1]), load_snapshot(args[2]))
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            print(f"compare: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    print("Usage: ./workbench inspect | compare <older.json> <newer.json>", file=sys.stderr)
    return 2
