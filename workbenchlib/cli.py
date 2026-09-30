"""Read-only Workbench command dispatch."""

import json
import sys

from workbenchlib.compare import compare, load_snapshot
from workbenchlib.inspect import main as inspect_main
from workbenchlib.desired import load_json
from workbenchlib.plan import plan
from workbenchlib.desired import validate_desired, validate_mapping
from workbenchlib.inspect import REPO_ROOT


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
    if len(args) == 3 and args[0] == "plan":
        try:
            desired = validate_desired(load_json(args[1]))
            snapshot = load_snapshot(args[2])
            mapping = validate_mapping(load_json(REPO_ROOT / "adapters/cachyos-software.json"))
            result = plan(desired, snapshot, mapping)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            print(f"plan: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    print("Usage: ./workbench inspect | compare <older.json> <newer.json> | plan <desired-state> <snapshot>", file=sys.stderr)
    return 2
