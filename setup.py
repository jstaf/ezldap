from setuptools import setup
from glob import glob

setup(
    name='ezldap',
    version='0.1',
    description='Scripts and Python bindings for easy LDAP operations.',
    url='https://github.com/jstaf/ezldap',
    author='Jeff Stafford',
    author_email='jeff.stafford@queensu.ca',
    license='BSD3',
    packages=['ezldap'],
    scripts=glob('bin/*'),
    include_package_data=True,
    install_requires=[
        'PyYAML',
        'pyldap'  # python-ldap once v3.0 of python-ldap is available
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
