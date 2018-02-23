ezldap
---------------------------------------------

An object-oriented Python LDAP API and set of bundled scripts to make
common LDAP tasks easier.
The focus of this package is autodetection of as many ldap config values
as possible, making a complex task like generating an LDIF and adding a
user as simple as `ldap-add-user <username>` 

## Installation

You'll need a copy of Python 3.4+ and the openldap development headers to start.
Running the tests requires `openldap-servers` as well. 

On Centos 7:

```{bash}
sudo yum -y install epel-release openldap-devel openldap-clients gcc gcc-g++
sudo yum -y install python34 python34-pip python34-devel
pip3 install --user git+https://github.com/jstaf/ezldap.git
```

Configure your LDAP connection details with `ldap-config` before using the package.
You do not need to run this script as root.
The connection details/LDIF templates/etc. for `ezldap` are stored in `~/.ezldap`.
Though you can store your bind password here, 
I do not recommend doing so, as it will be stored in cleartext. 
You may wish to configure the LDIF templates under `~/.ezldap` 
as well if you intend to use this package's add object functionality.

## Using this package

Refer to the scripts' command-line help (`./script-name -h`) for usage info and documentation.
Any scripts that modify the LDAP directory have a "dry-run" option (`--dry-run`/`-n`).
When run using the dry-run option, no changes will be performed.
All scripts print the LDIF of their retrieved data/changes to stdout 
(so you could use the result of a dry-run as an ldif for other tools like `ldapadd` for instance).

Keep in mind this package is under active development and may not be appropriate for all use cases.

