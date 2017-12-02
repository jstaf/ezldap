from setuptools import setup

setup(
    name='ezldap',
    version='0.1',
    description='Scripts and Python bindings for easy LDAP operations.',
    url='https://github.com/jstaf/ezldap',
    author='Jeff Stafford',
    author_email='jeff.stafford@queensu.ca',
    license='BSD3',
    packages=['ezldap'],
    scripts=['scripts/*'],
    dependency_links=['https://github.com/python-ldap/python-ldap.git'],
    install_requires=[
        'PyYAML',
        'python-ldap'
    ]
)
