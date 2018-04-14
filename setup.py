import glob
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
    scripts=glob.glob('bin/*'),
    include_package_data=True,
    install_requires=[
        'PyYAML',
        'python-ldap'
    ],
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest',
        'pytest-docker',
        'docker-compose'
    ],
    zip_safe=False
)
