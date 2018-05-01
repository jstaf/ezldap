'''
Utility functions for reading/writing to LDIF files.
'''

import os
import re
import copy
from io import StringIO
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
        content = StringIO(template.substitute(replacements))

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


def write_ldif(entries, path):
    '''
    Write self.entries as LDIF file.
    '''
    # because we're modifying the entries contained as we iterate through.
    with open(os.path.expanduser(path), 'w') as handle:
        _entries_to_handle(entries, handle)


def print_ldif(entries):
    '''
    Print an LDIF entry to stdout.
    '''
    with StringIO() as strbuf:
        _entries_to_handle(entries, strbuf)
        strbuf.seek(0)
        print(''.join(strbuf.readlines()))


def _entries_to_handle(entries, handle):
    entries_cp = copy.deepcopy(entries)
    for entry in entries_cp:
        handle.writelines(_dump_attributes('dn', entry.pop('dn')))
        #TODO only works with ldif-add, needs the ability to handle ldif-change
        handle.writelines(_dump_attributes('objectClass', entry.pop('objectClass')))
        for k, v in entry.items():
            handle.writelines(_dump_attributes(k, v))

        handle.write('\n')


def _dump_attributes(key, values):
    '''
    Convert a dictionary key/value pair (key: [value1, value2]) to a list of the
    form: ['key: value1', 'key: value2'].
    '''
    if not isinstance(values, list):
        values = [values]

    out = []
    for v in values:
        out.append('{}: {}\n'.format(key, v))

    return out
