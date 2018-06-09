Walkthrough
==========================================

This is a quick walkthrough designed to show the basics of using ezldap to
query and modify an LDAP directory.
Please install `Docker <https://www.docker.com/community-edition>`_ before beginning this tutorial.

Spin up a test LDAP server
-------------------------------------

We will begin by starting an example LDAP server (OpenLDAP, in this case)
to add and subtract objects to.
This essentially is a throw-away LDAP server that will not impact our computer
or a production environment. You can test out operations on this container to
your heart's content.

To start our example LDAP server:

::

  docker run -p 389:389 -p 636:636 jstaf/ezldap

You should see something like the following:

::

  5b1b49a6 @(#) $OpenLDAP: slapd 2.4.45 (Dec  6 2017 14:25:36) $
    mockbuild@buildhw-08.phx2.fedoraproject.org:/builddir/build/BUILD/openldap-2.4.45/openldap-2.4.45/servers/slapd
  5b1b49a6 slapd starting

This is an example LDAP server with debug logging on.
As we make queries against this server, we will see them appear here.
Though the actual content is not important,
you can use this information to verify exactly what's happening when we perform
LDAP operations later.

To stop the container later on, just use ``Control-c``.
You do not need to worry about cleaning up or revisiting this container later,
it is completely disposable.

Setup and configure ezldap
-----------------------------------------

To install ezldap, run the following:

::

  pip install ezldap

Now we will configure ezldap to connect to the OpenLDAP instance running on our
demonstration Docker container. Run ``ezldap config``.
You will be prompted for the following.
I have provided the bind information for the container here:

* **LDAP host:**  ldap:///
* **Bind DN:** cn=Manager,dc=ezldap,dc=io
* **Bind password:** password (yes, it's "password")
* **User base dn:** ou=People,dc=ezldap,dc=io
* **Group base dn:** ou=Group,dc=ezldap,dc=io
* **Host base dn:** ou=Hosts,dc=ezldap,dc=io
* **Default home directory:** /home

When running ``ezldap config``, this will look like the following:

::

  Configuring ezldap...
  Default values are in [brackets] - to accept, press Enter.

  LDAP host: ldap:///
  Bind DN (leave blank for anonymous bind) [cn=Manager,dc=example,dc=com]: cn=Manager,dc=ezldap,dc=io
  Bind password (leave blank to prompt for password): password
  User base dn [ou=People,dc=example,dc=com]: ou=People,dc=ezldap,dc=io
  Group base dn [ou=Group,dc=example,dc=com]: ou=Group,dc=ezldap,dc=io
  Host base dn [ou=Hosts,dc=example,dc=com]: ou=Hosts,dc=ezldap,dc=io
  Default home directory for new users [/home]:

  Writing configs to ~/.ezldap/
  Edit config.yaml and the LDIF templates in ~/.ezldap/ to configure ezldap's behavior.

To check that you've entered this information correctly,
you can run the ``bind_info`` command:

::

  ezldap bind_info

If the Docker container is running and ezldap has been setup and configured correctly,
you should see the following:

::

  ldap://localhost:389 - cleartext - user: cn=Manager,dc=ezldap,dc=io - not lazy - bound - open - <local: [::1]:36788 - remote: [::1]:389> - tls started - listening - SyncStrategy - internal decoder

Next steps
-------------------------

Assuming you've reached this point, congratulations!
You are now set to use ezldap.

* To get started using the command-line LDAP client,
  see the `Bash recipes <bash_recipes.html>`_ page, and run through the examples there.

* To get started with the Python API,
  go to the `Python recipes <python_recipes.html>`_ page.
  More detailed information can be found by reading the `Python API documentation <python_api.html>`_.
