'''
Utility functions for reading/writing to LDIF files.
'''

import os
import re
import copy
from io import StringIO
from string import Template

import ldap3


class LDIFTemplateError(KeyError):
    '''
    A custom exception to better catch LDIF template errors specifcally instead
    of the ultra-vague KeyError.
    '''
    pass


def template(path, replacements=None):
    '''
    Read a file and substitute replacment entries for placeholders designated
    by $placeholder_name. If replacements is None, it simply opens and reads a
    file into a string.
    '''
    if replacements is None:
        return open(path).read()
    else:
        try:
            content = Template(open(path).read())
            return content.substitute(replacements)
        except KeyError as e:
            raise LDIFTemplateError('No value provided for LDIF key "{}"'
                .format(e.args[0])) from None


def ldif_read(path, replacements=None):
    '''
    Read an LDIF file into a list of dicts appropriate for use with ezldap.
    '''
    # read into a string buffer first
    path = os.path.expanduser(path)
    content = StringIO(template(path, replacements))

    operations = {
        'add': ldap3.MODIFY_ADD,
        'replace': ldap3.MODIFY_REPLACE,
        'delete': ldap3.MODIFY_DELETE
    }

    entries = []
    entry = {}
    changetype = 'add'
    next_change_attr = None
    next_change_type = 'add'
    for line in content:
        if line[0] == '#':
            continue
        if line[0] == '-':
            if next_change_type == 'delete' and len(entry[next_change_attr]) == 0:
                # The last entry ended with no entries and was also a "delete"
                # change. This should result in a delete change that deletes all
                # entries for that attribute.
                entry[next_change_attr].append((ldap3.MODIFY_DELETE, []))

            continue
        elif re.match(r'dn:', line):
            # new dn- add last entry, and start a new one
            if 'dn' in entry.keys():
                entries.append(entry)
                changetype = 'add'

            entry = {}

        match = re.findall(r'(\w+):\s*(.+)', line)
        if len(match) > 0:
            key = match[0][0]
            value = match[0][1].strip()

            if key == 'changetype':
                # determine changetype and skip line
                changetype = value
                continue
            elif key not in entry.keys() and key not in operations.keys():
                entry[key] = []

            if changetype == 'modify':
                # handle ldif-change LDIFs
                if key in operations.keys():
                    next_change_type, next_change_attr = key, value
                    if value not in entry.keys():
                        # a check in case the attribute has not already been added
                        entry[value] = []

                    continue
                elif key == next_change_attr:
                    # each change is handled separately,
                    # not the most efficient, but is an easier implementation
                    value = (operations[next_change_type], [value])
                else:
                    raise ValueError('Attribute does not match attribute to {}.'.format(next_change_type))

            entry[key].append(value)

    # last ldif object won't be added otherwise
    if 'dn' in entry.keys():
        entries.append(entry)

    return entries


def ldif_write(entries, path):
    '''
    Write self.entries as LDIF file.
    '''
    with open(os.path.expanduser(path), 'w') as handle:
        _entries_to_handle(entries, handle)


def ldif_print(entries):
    '''
    Print an LDIF entry to stdout.
    '''
    with StringIO() as strbuf:
        _entries_to_handle(entries, strbuf)
        strbuf.seek(0)
        print(''.join(strbuf.readlines()), end='')


def _entries_to_handle(entries, handle):
    '''
    Write entries to a filehandle.
    '''
    # because we're modifying the entries contained as we iterate through.
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
