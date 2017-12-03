"""
Read and write LDIF files to/from a dict
"""

import sys
import io
from string import Template
from collections import OrderedDict

import ldif as ldif_

class LDIF(ldif_.LDIFParser):

    def __init__(self, path=None, replacements={}):
        """
        Create a new LDIF reader. 
        If path is None, you are expected to populate self.entries.
        """
        self.entries = OrderedDict()
        
        if path is not None:
            template = Template(open(path).read())
            strbuf = io.StringIO(template.substitute(replacements))
            ldif_.LDIFParser.__init__(self, strbuf)
            self.parse()


    def __str__(self):
        # dumps the output of ldif.write() to a string buffer
        strbuf = io.StringIO()
        self.write(strbuf)
        strbuf.seek(0)
        out = ''.join(strbuf.readlines())
        strbuf.close()
        return out


    def __repr__(self):
        return str(self.entries)


    def __add__(self, ldif):
        new = LDIF()
        new.entries.update(self.entries)
        new.entries.update(ldif.entries)
        return new


    def __iadd__(self, ldif):
        self.entries.update(ldif.entries)
        return self


    def handle(self, dn, entry):
        self.entries[dn] = entry


    def write(self, output=sys.stdout):
        """
        Write self.entries as LDIF file.
        """
        writer = ldif_.LDIFWriter(output)
        for dn, entry in self.entries.items():
            writer.unparse(dn, entry)

        
    def populate(self, query):
        """
        Populate entries from an LDAP query (like LDAP.search_s()).
        """
        for dn, attrs in query:
            self.entries[dn] = attrs
