#!/usr/bin/python3

# INET 4031
# Jimale Mohamed
# 10/30/2025
# 10/30/2025

"""
INET4031 - Automated user creation script

Reads colon-delimited user records from stdin and for each valid line:
  1) Creates a Linux user with GECOS data
  2) Sets the user’s password
  3) Adds the user to any supplemental groups

Input line format (5 fields):
  username:password:last:first:group1,group2
Use '-' in the groups position to mean “no supplemental groups”.
Lines that start with '#' are treated as comments and skipped.
Lines that do not have exactly 5 fields are skipped for safety.
"""

import os
import re
import sys

def main():
    for raw in sys.stdin:
        line = raw.rstrip('\n')

        # Skip comment lines
        if re.match(r'^#', line):
            continue

        # Split colon-delimited fields and require exactly 5
        fields = line.split(':')
        if len(fields) != 5:
            continue

        # Map fields: username:password:last:first:groups
        username, password, last, first, group_field = fields
        gecos = f"{first} {last},,,"
        groups = group_field.split(',')

        # Create account (dry run prints the command)
        print(f"==> Creating account for {username}...")
        cmd = f"/usr/sbin/adduser --disabled-password --gecos '{gecos}' {username}"
        print(cmd)
        os.system(cmd)

        # Set password (dry run prints the command)
        print(f"==> Setting the password for {username}...")
        cmd = f"/bin/echo -ne '{password}\\n{password}' | /usr/bin/sudo /usr/bin/passwd {username}"
        print(cmd)
        os.system(cmd)

        # Add to supplemental groups (skip '-' sentinel)
        for group in groups:
            if group != '-':
                print(f"==> Assigning {username} to the {group} group...")
                cmd = f"/usr/sbin/adduser {username} {group}"
                print(cmd)
                os.system(cmd)

if __name__ == '__main__':
    main()

