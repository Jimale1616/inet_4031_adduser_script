#!/usr/bin/python3
"""
INET4031 – Automated Linux user creation (interactive dry-run version)

- Prompts: Dry run? (Y/N)
- Dry-run (Y): do not execute OS commands, print what would run, and explain skipped lines
- Real run (N): execute OS commands; stay silent about skipped lines

Input (5 colon-separated fields):
  username:password:last:first:group1,group2
Use '-' in the groups field for “no supplemental groups”.
"""

import os
import re
import sys

def run(cmd: str, dry: bool):
    """Print the command; execute only if not in dry-run mode."""
    print(cmd)
    if not dry:
        os.system(cmd)

def main():
    # Ask for dry-run from the terminal (not stdin), so redirection won't interfere
    try:
        with open('/dev/tty', 'r') as tty:
            print("Dry run? (Y/N): ", end='', file=sys.stderr, flush=True)
            answer = tty.readline().strip().lower()
    except Exception:
        # If no TTY (non-interactive environment), default to DRY RUN for safety
        answer = 'y'

    dry = (answer == 'y')

    for lineno, raw in enumerate(sys.stdin, start=1):
        line = raw.rstrip("\n")

        # Skip blank and comment lines
        if not line or line.startswith("#"):
            if dry:
                reason = "blank" if not line else "comment"
                print(f"[skip line {lineno}] {reason} line")
            continue

        # Validate the line has exactly 5 fields
        fields = line.split(":")
        if len(fields) != 5:
            if dry:
                print(f"[skip line {lineno}] malformed: expected 5 fields, got {len(fields)} -> {line}")
            continue

        # Map fields
        username, password, last, first, group_field = fields
        gecos = f"{first} {last},,,"
        groups = [g.strip() for g in group_field.split(",")]

        # 1) Create user
        print(f"==> Creating account for {username}...")
        cmd = f"/usr/sbin/adduser --disabled-password --gecos '{gecos}' {username}"
        run(cmd, dry)

        # 2) Set password (non-interactive)
        print(f"==> Setting the password for {username}...")
        cmd = f"/usr/bin/echo '{username}:{password}' | /usr/sbin/chpasswd"
        run(cmd, dry)

        # 3) Add supplemental groups
        for group in groups:
            if group and group != "-":
                print(f"==> Assigning {username} to the {group} group...")
                cmd = f"/usr/sbin/adduser {username} {group}"
                run(cmd, dry)

if __name__ == "__main__":
    main()
