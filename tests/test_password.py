'''
Tests for various password hashing functions.
'''

import ezldap

def test_ssha_check():
    assert ezldap.ssha_check('{SSHA}qLhale/wd2F5xIeDIUiZVvRIc2RvBvlE', 'does this work?')
    assert ezldap.ssha_check('{SSHA}a2qHtrEmNDlqu0FsWLw/bvsJJQwuFXS4', 'i certainly hope so...')

def test_ssha_hash():
    assert ezldap.ssha_check(ezldap.ssha_passwd('also test hashing'), 'also test hashing')
    assert ezldap.ssha_check(ezldap.ssha_passwd('because its important'), 'because its important')
