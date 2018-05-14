"""
Tools for generating and hashing OpenLDAP-compatible passwords.
Using SHA1 since that is the OpenLDAP default.

https://gist.github.com/rca/7217540 used as reference.
"""

import os
import re
import string
import hashlib
import base64
from random import SystemRandom

def random_passwd(length=10, ambiguous_chars=False):
    """
    Generate a readable, random password with no ambiguous characters
    (unless you set that option to true, of course).
    """
    chars = string.ascii_letters + string.digits
    if not ambiguous_chars:
        chars = re.sub('[1lIO0]', '', chars)

    r = SystemRandom()
    return ''.join(r.choice(chars) for char in range(length))


def ssha(val, salt):
    """
    Generate an SSHA hash.
    """
    ecrypt = hashlib.sha1(val.encode())
    ecrypt.update(salt)
    return ecrypt


def ssha_passwd(str_val):
    """
    Hash and salt a string using SHA1 algorithm and format for use with LDAP.
    """
    salt = os.urandom(4)
    out = ssha(str_val, salt)
    out = '{SSHA}' + base64.b64encode(out.digest() + salt).decode()
    return out


def ssha_check(ssha_val, str_val):
    """
    Check that a password decodes to the correct password.
    """
    ssha_val = base64.b64decode(ssha_val[6:])
    # SHA1 hashes are 20 characters
    salt = ssha_val[20:]
    digest = ssha_val[:20]

    # create a hash from str_val using original salt and see if it matches
    str_val_ssha = ssha(str_val, salt)
    return digest == str_val_ssha.digest()
