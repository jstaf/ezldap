ldaputils
---------------------------------------------

An object-oriented Python LDAP API and set of bundled scripts to make
common LDAP tasks easier.

## Installation

Install Python 3.4+ and `pyldap` (`pip install --user pyldap`). 

**You must edit the configuration files in `etc/` before use!**

### etc/config.yaml

`config.yaml` is used to define connection credentials and "placeholder" values.
Any attribute in `config.yaml` with a name in UPPERCASE is a placeholder value.
You may also add arbitrary placeholders in `config.yaml` to be used later.

Required values:

* **host** - Your LDAP host.
* **binddn** - DN of your directory manager account.
* **binddn\_pass** - Password for the directory manager. Leave blank to prompt for passwordwhen connecting to LDAP.
* **uidstart** - `uidNumber` to begin making LDAP accounts at (will use highest numbered LDAP `uidNumber` otherwise).
* **gidstart** - `gidNumber` to begin making LDAP groups at (will use highest numbered LDAP `gidNumber` otherwise).

### .ldif files in /etc

These are the LDIF files used by this package's scripts to 
add/delete/modify LDAP entries.
Values in UPPERCASE will be automatically replaced by 
the UPPERCASE placeholder values in `config.yaml`.
You can edit these files to customize the behavior of ldaputils' scripts.

## Using this package

Refer to the scripts' command-line help (`./script-name -h`) for usage info and documentation.
Any scripts that modify the LDAP directory have a "dry-run" option (`--dry-run`/`-n`).
When run using the dry-run option, no changes will be performed.
All scripts print the LDIF of their retrieved data/changes to stdout 
(so you could use the result of a dry-run as an ldif for other tools like `ldapadd` for instance).

Keep in mind this package is under active development and may not be appropriate for all use cases.
Use at your own risk!

