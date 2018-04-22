"""
Read and write LDIF files to/from a dict
"""

import sys
import io
import os
from string import Template

class LDIF:

    def __init__(self, path=None, replacements=None):
        '''
        Create a new LDIF reader.
        If path is None, you are expected to populate self.entries.
        '''
        self.entries = []

        if path is not None:
            # read into a string buffer first
            path = os.path.expanduser(path)
            if replacements is None:
                content = open(path)
            else:
                template = Template(open(path).read())
                content = io.StringIO(template.substitute(replacements))

            #TODO reimplement

    def __str__(self):
        # dumps the output of ldif.write() to a string buffer
        strbuf = io.StringIO()
        self.write(strbuf)
        strbuf.seek(0)
        out = ''.join(strbuf.readlines())
        strbuf.close()
        return out


    def write(self, output=sys.stdout):
        '''
        Write self.entries as LDIF file.
        '''
        writer = ldif_.LDIFWriter(output)
        for dn, entry in self.entries.items():
            if '-' in entry.keys():
                entry.pop('-')

            writer.unparse(dn, entry)


    def populate(self, query):
        '''
        Populate entries from an LDAP query (like LDAP.search_s()).
        '''
        for dn, attrs in query:
            self.entries[dn] = attrs
