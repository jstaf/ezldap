"""
A module with several utils for sending mass emails 
(while activating large numbers of users).
"""

import smtplib
from email.mime.text import MIMEText

from .connection import config
from .ldif import _multi_replace

def email(message, subject, from_addr, to_addr, relay):
    msg = MIMEText(message)
    msg['subject'] = subject
    msg['from'] = from_addr
    msg['to'] = to_addr
    
    smtp = smtplib.SMTP(relay)
    smtp.send_message(msg)
    smtp.quit()


def message_from_template(path, replacements):
    with open(path) as f:
        message = f.readlines()
        message = ''.join(message)

    return _multi_replace('_unused', message, replacements)


