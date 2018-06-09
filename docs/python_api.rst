Python API
=========================================

This is the page for ezldap's Python API documentation.
For general-purpose recipes and use cases,
check out the `Python recipes <python_recipes>`_.

Connection
-------------------------------------

.. autofunction:: ezldap.ping

.. autofunction:: ezldap.supports_starttls

.. autofunction:: ezldap.auto_bind

.. autofunction:: ezldap.dn_address

.. autofunction:: ezldap.clean_uri

.. autoclass:: ezldap.Connection
   :members:
   :inherited-members:
   :special-members: __init__

LDIF parser and utilities
-------------------------------------

.. autofunction:: ezldap.ldif_read

.. autofunction:: ezldap.ldif_write

.. autofunction:: ezldap.ldif_print

.. autofunction:: ezldap.template

Password utilities
-------------------------------------

.. autofunction:: ezldap.random_passwd

.. autofunction:: ezldap.ssha_passwd

.. autofunction:: ezldap.ssha_check

.. autofunction:: ezldap.ssha
