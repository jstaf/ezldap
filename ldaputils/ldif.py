"""
Read and write LDIF files to/from a dict
"""

import sys
import re
import ldif

class LDIF(ldif.LDIFParser):
    def __init__(self, path=None):
        """
        Create a new LDIF reader. 
        If path is None, you are expected to populate self.entries.
        """
        self.entries = {}
        if path is not None:
            ldif.LDIFParser.__init__(self, open(path))
            self.parse()


    def handle(self, dn, entry):
        self.entries[dn] = entry


    def write(self, output=sys.stdout):
        """
        Write self.entries as LDIF file.
        """
        writer = ldif.LDIFWriter(output)
        for dn, entry in self.entries.items():
            writer.unparse(dn, entry)


    def replace_entries(self, replacements):
        """
        Replace placeholder entries with stuff from config file
        """
        new_entries = {}
        for dn, entry in self.entries.items():
            dn = _multi_replace('dn_placeholder', dn, replacements)
            for key, value in entry.items():
                entry[key] = _multi_replace(key, value, replacements)

            new_entries[dn] = entry

        # replace with updated dictionary
        self.entries = new_entries


def _multi_replace(key, val, replacements):
    """
    Attempt to replace a value with the first match in a set of replacements.
    Type safe (for the most part).
    """
    # lists must be unpacked and iterated over
    if isinstance(val, list):
        return [_multi_replace(key, x, replacements) for x in val]
   
    isbytes = False
    if isinstance(val, bytes):
        val = val.decode()
        isbytes = True

    # ints do not need to be replaced
    if not isinstance(val, int): 
        for replacement in replacements.keys():
            val = re.sub(replacement, str(replacements[replacement]), val)

    if isbytes:
        val = str(val).encode()
   
    return val


