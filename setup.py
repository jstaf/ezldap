from setuptools import setup

# import version from version.py so it's only specified in one spot
exec(open('ezldap/version.py').read())

setup(
    name='ezldap',
    version=__version__,
    description='Scripts and Python bindings for easy LDAP operations.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jstaf/ezldap',
    author='Jeff Stafford',
    author_email='jeff.stafford@queensu.ca',
    license='BSD3',
    packages=['ezldap'],
    scripts=['bin/ezldap'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'PyYAML',
        'ldap3'
    ],
    setup_requires=['pytest-runner'],
    tests_require=[
        'pandas',
        'pytest',
        'pytest-docker',
        'pytest-cov',
        'docker-compose'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta'
    ]
)
