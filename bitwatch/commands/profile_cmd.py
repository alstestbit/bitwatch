"""CLI subcommand: manage named watch profiles."""
from __future__ import annotations

import json
from pathlib import Path

from bitwatch import profile as prof


def add_subparser(subparsers):
    p = subparsers.add_parser("profile", help="manage named watch profiles")
    sub = p.add_subparsers(dest="profile_action")

    sub.add_parser("list", help="list saved profiles")

    save_p = sub.add_parser("save", help="save current flags as a profile")
    save_p.add_argument("name", help="profile name")
    save_p.add_argument("--flags", required=True, help="JSON object of flag overrides")
    save_p.add_argument("--profiles-file", default=None)

    show_p = sub.add_parser("show", help="show a profile")
    show_p.add_argument("name")
    show_p.add_argument("--profiles-file", default=None)

    del_p = sub.add_parser("delete", help="delete a profile")
    del_p.add_argument("name")
    del_p.add_argument("--profiles-file", default=None)

    p.set_defaults(func=run)


def run(args) -> int:
    pfile = Path(args.profiles_file) if getattr(args, "profiles_file", None) else None
    action = getattr(args, "profile_action", None)

    if action == "list":
        names = prof.profile_names(pfile)
        if not names:
            print("No profiles saved.")
        else:
            for n in names:
                print(n)
        return 0

    if action == "save":
        try:
            flags = json.loads(args.flags)
        except json.JSONDecodeError:
            print("Error: --flags must be a valid JSON object.")
            return 1
        prof.set_profile(args.name, flags, pfile)
        print(f"Profile '{args.name}' saved.")
        return 0

    if action == "show":
        data = prof.get_profile(args.name, pfile)
        if data is None:
            print(f"Profile '{args.name}' not found.")
            return 1
        print(json.dumps(data, indent=2))
        return 0

    if action == "delete":
        if prof.delete_profile(args.name, pfile):
            print(f"Profile '{args.name}' deleted.")
            return 0
        print(f"Profile '{args.name}' not found.")
        return 1

    print("No action specified. Use list, save, show, or delete.")
    return 1
