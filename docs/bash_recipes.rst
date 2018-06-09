=====================================
Bash recipes
=====================================

ezldap provides a command-line client that attempts to mimic the Python API as closely as possible. The goal is to make common LDAP operations available via the command-line.

Configuration
=========================

Configure ezldap before use
---------------------------------------

Both the Python API and the command line client use a set of config values
and LDIF templates stored in ``~/.ezldap/``.
To create these configs, run the following command: ::

  ezldap config

Sample output
(default values are in brackets,
just press `Enter` to accept the defaults and move to the next option)::

  LDAP host [ldap:///]:
  Bind DN (leave blank for anonymous bind) [cn=Manager,dc=ezldap,dc=io]:
  Bind password (leave blank to prompt for password) [password]:
  User base dn [ou=People,dc=ezldap,dc=io]:
  Group base dn [ou=Group,dc=ezldap,dc=io]:
  Host base dn [ou=Hosts,dc=ezldap,dc=io]:
  Default home directory for new users [/home]:

Delete your ezldap configuration
-------------------------------------

To delete an ezldap configuration it's as easy as: ::

  rm -r ~/.ezldap


Try out ezldap against a test LDAP server
------------------------------------------------

Assuming you've got Docker installed,
you can start a test LDAP instance with the following
(Bind DN is `cn=Manager,dc=ezldap,dc=io`,
bind password is `password`, the URI to bind to is `ldap:///`): ::

  docker run -p 389:389 -p 636:636 jstaf/ezldap

Query an LDAP server
============================================

Get information about your LDAP server
------------------------------------------

::

  ezldap server_info

Sample output: ::

  DSA info (from DSE):
    Supported LDAP versions: 3
    Naming contexts:
      dc=ezldap,dc=io
    Supported controls:
      1.2.826.0.1.3344810.2.3 - Matched Values - Control - RFC3876
      1.2.840.113556.1.4.319 - LDAP Simple Paged Results - Control - RFC2696

  [lines omitted for brevity]

      1.3.6.1.4.1.4203.1.5.4 - Language Tag Options - Feature - RFC3866
      1.3.6.1.4.1.4203.1.5.5 - language Range Options - Feature - RFC3866
    Schema entry: cn=Subschema
  Other:
    objectClass:
      top
      OpenLDAProotDSE
    structuralObjectClass:
  OpenLDAProotDSE
    configContext:
      cn=config
    monitorContext:
      cn=Monitor
    entryDN:

Get information about an objectClass
----------------------------------------

::

  ezldap class_info inetOrgPerson

::

  Object class: 2.16.840.1.113730.3.2.2
    Short name: inetOrgPerson
    Description: RFC2798: Internet Organizational Person
    Type: Structural
    Superior: organizationalPerson
    May contain attributes: audio, businessCategory, carLicense, departmentNumber,
      displayName, employeeNumber, employeeType, givenName, homePhone,
      homePostalAddress, initials, jpegPhoto, labeledURI, mail, manager, mobile,
      o, pager, photo, roomNumber, secretary, uid, userCertificate,
      x500uniqueIdentifier, preferredLanguage, userSMIMECertificate, userPKCS12

Search using LDAP filters
----------------------------------------------------

Search uses the same syntax as ``ldapsearch -x`` ::

  ezldap search objectClass=organizationalUnit

::

  dn: ou=Group,dc=ezldap,dc=io
  objectClass: organizationalUnit
  ou: Group

  dn: ou=People,dc=ezldap,dc=io
  objectClass: organizationalUnit
  ou: People

  dn: ou=Hosts,dc=ezldap,dc=io
  objectClass: organizationalUnit
  ou: Hosts

Search for entries by DN
-----------------------------

This function finds any DNs in a directory tree matching a keyword.
(Might not work for huge directories yet due to paging limits.)

::

  ezldap search_dn People

::

  ou=People,dc=ezldap,dc=io


Add entries
=========================================

Add a group
-------------------------

::

  ezldap add_group demo

::

  Success!

Verify the group has been created using ``ezldap search``
(you can also use ``ldapsearch -x``, it won't hurt my feelings...)

::
  ezldap search cn=demo

::

  dn: cn=demo,ou=Group,dc=ezldap,dc=io
  objectClass: top
  objectClass: posixGroup
  cn: demo
  gidNumber: 10000

Add a group using an alternate LDIF template
-------------------------------------------------

Chances are, the default LDIFs provided in this package won't match your organization's needs. No problem - ezldap works off of templates you can customize to your needs.
Let's create a copy of the default ``add_group.ldif`` and use that instead:

::

  cp ~/.ezldap/add_group.ldif custom_group.ldif
  vim custom_group.ldif

Perhaps we want our new group to be an ``extensibleObject`` in addition to
``top`` and ``posixGroup``. Our ``custom_group.ldif`` might look like this instead:

::

  dn: cn=$groupname,$groupdn
  objectClass: top
  objectClass: posixGroup
  objectClass: extensibleObject
  cn: $groupname
  gidNumber: $gid

To use this custom LDIF instead of the default,
we can specify the path to our custom LDIF as a command-line option
(if we wanted to use this as the default,
we could have edited ``~/.ezldap/add_group.ldif`` instead):

::

  ezldap add_group --ldif custom_group.ldif our-custom-group

::

  Success!

Let's check our work and make sure our group was created:

::

  ezldap search objectClass=extensibleObject

::

  dn: cn=our-custom-group,ou=Group,dc=ezldap,dc=io
  objectClass: top
  objectClass: posixGroup
  objectClass: extensibleObject
  cn: our-custom-group
  gidNumber: 10001

Add a user
---------------------

Creating a user is similar to creating a group.
The only thing to remember here is that if we do not specify a group to add a user to,
one will be created with the same name as that user:

::

  ezldap add_user jeff

::

  Creating LDAP group jeff... Success!
  Creating user jeff... Success!
  Adding jeff to LDAP group jeff... Success!
  Password: 4NEy5uTs47

Checking our work:

::

  ezldap search cn=jeff

::

  dn: cn=jeff,ou=Group,dc=ezldap,dc=io
  objectClass: top
  objectClass: posixGroup
  cn: jeff
  gidNumber: 10002
  memberUid: jeff

  dn: uid=jeff,ou=People,dc=ezldap,dc=io
  objectClass: top
  objectClass: posixAccount
  objectClass: shadowAccount
  objectClass: inetOrgPerson
  cn: jeff
  sn: jeff
  loginShell: /bin/bash
  uidNumber: 10000
  gidNumber: 10002
  gecos: jeff
  shadowMax: 180
  shadowWarning: 7
  homeDirectory: /home/jeff
  uid: jeff

As with ``add_group``, all of the steps
(adding a user, adding a group, adding the user to that group)
let you customize which LDIFs get used.

Add a user to a group
----------------------------

Let's add ``jeff`` to our ``demo`` group from earlier.

::

  ezldap add_to_group jeff demo

::

  Success!

Check our work:

::

  ezldap search cn=demo

::

  dn: cn=demo,ou=Group,dc=ezldap,dc=io
  objectClass: top
  objectClass: posixGroup
  cn: demo
  gidNumber: 10000
  memberUid: jeff

It looks like ``jeff`` was successfully added.

Modify an entry
=========================================

ezldap provides a modify command that can modify any attribute of an entry
(add, replace, delete).
What happens if we want to change the gidnumber of the ``demo`` group?

modify replace
--------------------------

::

  ezldap modify cn=demo,ou=Group,dc=ezldap,dc=io replace gidNumber 12345

::

  Success!


If we search for the demo group again, it should now reflect the new gidNumber:

::

  ezldap search cn=demo

::

  dn: cn=demo,ou=Group,dc=ezldap,dc=io
  objectClass: top
  objectClass: posixGroup
  cn: demo
  memberUid: jeff
  gidNumber: 12345

modify delete
--------------------------------

What if we want to delete "jeff" as a member?

::

  ezldap modify cn=demo,ou=Group,dc=ezldap,dc=io delete memberUid jeff

::

  Success!

Result:

::

  dn: cn=demo,ou=Group,dc=ezldap,dc=io
  objectClass: top
  objectClass: posixGroup
  cn: demo
  gidNumber: 12345

modify add
---------------

Let's restore jeff as a member and add that user back into the group:

::

  ezldap modify cn=demo,ou=Group,dc=ezldap,dc=io add memberUid jeff

Result:

::

  dn: cn=demo,ou=Group,dc=ezldap,dc=io
  objectClass: top
  objectClass: posixGroup
  cn: demo
  gidNumber: 12345
  memberUid: jeff

Renaming / moving objects
----------------------------------------

The ``modify_dn`` operation lets you rename and/or move objects around in a directory.
For convenience, the modify_dn provided by the ``ezldap`` command lets you
both move and rename an entry in one go.
To rename the ``demo`` group to ``new-name`` and move it into the ``ou=People`` container:

::

  ezldap modify_dn cn=demo,ou=Group,dc=ezldap,dc=io cn=new-name,ou=People,dc=ezldap,dc=io

::

  ezldap search cn=new-name


Result:
::

  dn: cn=new-name,ou=People,dc=ezldap,dc=io
  objectClass: top
  objectClass: posixGroup
  gidNumber: 12345
  memberUid: jeff
  cn: new-name

Miscellaneous operations
=======================================

Delete an object
--------------------------------------------

Maybe we realized that putting a group in the ``ou=People`` organizationalUnit
was a bad idea.
Maybe we just didn't want the ``new-name`` group anymore.
Note - since this is an inherently risky operation,
you'll be prompted for confirmation before deleting anything
(unless you use the ``-f``/``--force`` option).

::

  ezldap delete cn=new-name,ou=People,dc=ezldap,dc=io

::

  dn: cn=new-name,ou=People,dc=ezldap,dc=io
  objectClass: top
  objectClass: posixGroup
  gidNumber: 12345
  memberUid: jeff
  cn: new-name

  Delete object? (y/N) y
  Success!

Change a user's password
---------------------------------

Users frequently forget passwords.
Though hopefully you won't have to reset passwords manually for users every time,
there's a convenience function to speed things up: ``change_pw``.
In this case, the ``-s`` option lets us specify a new password.
To simply randomize it, leave this option out.

::

  ezldap change_pw -s jeff

::

  New password for jeff:
  Confirm password:
  Success!

Check a user's password
-------------------------------

Are you sure you typed that right? Absolutely sure? Let's check with ``check_pw``:

::

  ezldap check_pw jeff

::

  Enter password to verify...
  Password:
  Passwords match!

Other commands / help
=============================================

I've covered a few of the more common commands here.
For more information on commands,
refer to the ``ezldap`` client's command-line documentation
(just add either the ``-h`` or ``--help`` options to bring up detailed help for each command).

::

  ezldap --help

::

  usage: ezldap [-h] [-v]  ...

  ezldap CLI - Perform various options on an LDAP directory.

  optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit

  Valid commands:

    config        Configure ezldap (configs are stored in ~/.ezldap/).
    search        Search for entities by LDAP filter.
    search_dn     Search for and print DNs in a directory that match a keyword.
    add_user      Add a user.
    add_group     Add a group.
    add_to_group  Add a user to a group.
    add_host      Add a host.
    modify        Add, replace, or delete an attribute from an entity.
    modify_dn     Rename the DN of and/or move an entry.
    delete        Delete an entry from an LDAP directory.
    change_home   Change a user's home directory.
    change_shell  Change a user's default shell.
    change_pw     Change or reset a user's password.
    check_pw      Check a user's password.
    server_info   Print information about the LDAP server you are using.
    class_info    Print information about a specific LDAP objectClass.


For help on a given command:

::

  ezldap modify --help

::

  usage: ezldap modify [-h] dn {add,replace,delete} attribute value [replace_with]

  Add, replace, or delete an attribute from an entity.

  positional arguments:
    dn                    Distinguished Name (DN) of object to modify.
    {add,replace,delete}  Type of operation to perform. Can be one of: add,
                          replace, delete.
    attribute             Attribute to modify.
    value                 Value to add, replace, or delete. When performing a
                          delete operation, passing "-" will delete all values
                          for that attribute.
    replace_with          Value to replace an attribute with when performing a
                          replace operation.

  optional arguments:
    -h, --help            show this help message and exit

A note on errors
================================

If you run into an error, the ``ezldap`` client will immediately exit and print the reason for the error.
Operations do not get performed half-way and leave things in a broken state.
That said, I provide no guarantees or warranty of any kind while using this package.
If you want to check that things are working correctly, run the tests!
(You can also spin up a custom LDAP instance using a tool like Docker an test against that,
you can use this package's [Dockerfile](https://github.com/jstaf/ezldap/blob/master/tests/Dockerfile) as a reference to build your own test instances.)

Example error:

::

  ezldap class_info sldfjsldjfl

::

  objectClass "sldfjsldjfl" not found.
