"""
Read and write LDIF files to/from a dict
"""

import sys
import io
import os
import re
from string import Template

def read_ldif(path, replacements=None):
    '''
    Read an LDIF file into a list of dicts appropriate for use with ezldap.
    '''
    # read into a string buffer first
    path = os.path.expanduser(path)
    if replacements is None:
        content = open(path)
    else:
        template = Template(open(path).read())
        content = io.StringIO(template.substitute(replacements))

    entries = []
    entry = {}
    for line in content:
        if line[0] in {'-', '#'}:
            continue
        elif re.match(r'dn:', line):
            # new dn- add last entry, and start a new one
            if 'dn' in entry.keys():
                entries.append(entry)

            entry = {}

        match = re.match(r'(\w+):\s*(.+)', line)
        if match:
            key = match[1]
            if key not in entry.keys():
                entry[key] = []

            entry[key].append(match[2].strip())

    # last ldif object won't be added otherwise
    if 'dn' in entry.keys():
        entries.append(entry)

    return entries


def write_ldif(entries, output=sys.stdout):
    '''
    Write self.entries as LDIF file.
    '''
    pass
