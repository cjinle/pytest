#!/usr/bin/env python
# mailer test


import sys
import smtplib
from email.mime.text import MIMEText
from email.message import Message

HOST='smtp.163.com'
PORT=25
USER='seeec@163.com'
PASS=''
TO='cjinle@gmail.com'
LOG='crawl/out.log'

def get_content():
    ret = []
    with open(LOG, 'r') as f:
        for line in f:
            if 'started' in line:
                ret = []
            else:
                ret.append(line)
    return ''.join(ret)

if __name__ == "__main__":
    smtp = smtplib.SMTP(local_hostname=HOST)
    smtp.set_debuglevel(1)
    smtp.connect(HOST, PORT)
    smtp.login(USER, PASS)
    msg = MIMEText(get_content())
    msg['Subject'] = 'test mail'
    msg['From'] = USER
    msg['To'] = TO

    smtp.sendmail(USER, TO, msg.as_string())
    print 'sendmail done.'

