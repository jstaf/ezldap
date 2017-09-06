"""
Read and write LDIF files to/from a dict
"""

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


    def write(self, output):
        """
        Write self.entries as LDIF file.
        """
        writer = ldif.LDIFWriter(output)
        for dn, entry in self.entries.items():
            writer.unparse(dn, entry)


