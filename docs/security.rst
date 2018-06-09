============================================
A note on security
=============================================

ezldap tries to do things the right way. It will attempt to force a StartTLS
operation before binding in all cases, and connecting to an ``ldaps://`` URI or
over port 636 will connect using SSL. Encryption is preferred by default. A
cleartext bind will only be performed if the server supports neither StartTLS or
SSL (and it will warn you when it does so!).

All of that said, one of the configuration options is to specify your bind
password as part of the config. *I highly recommend leaving this option blank.*
This would store your bind password in plaintext in ``~/.ezldap/config.yml``.
Don't do it! (The option is there purely for convenience while testing and maybe
if you wanted to add a huge swath of users from the command line.)

Instead of specifying your password using ``ezldap config``, just leave the bind
password field blank to be prompted for your password every time you perform a
bind using the bind DN (typically the directory manager). If you've already
specified a password and want to remove it, just delete the corresponding value
for ``bindpw`` in ``~/.ezldap/config.yml``.

Example:

::

  # assuming "bindpw" is not specified in ~/.ezldap/config.yml
  ezldap add_host compute-node 10.100.1.123

::

  Enter bind DN password...
  Success!

Operations that can be performed anonymously (using an anonymous bind without
credentials) are preferred by ``ezldap`` whenever possible. Generally ``ezldap``
will only prompt you for a bind password if it needs it.
