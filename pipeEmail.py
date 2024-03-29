# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 00:03:33 2016

This program accepts text piped in on the command line and emails it from "me"
to "you"
example cat example.txt | grep -i -n -B10 -A10 "[Ee]rror" | python pipeEmail.py

@author: lmadeo
"""
# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.mime.text import MIMEText

import sys

# use stdin if it's full                                                        
if not sys.stdin.isatty():
    input_stream = sys.stdin
        
    msg = MIMEText(input_stream.read())
    input_stream.close()

    # if message body isn't empty, than send the email
    if msg.get_payload().strip(" ") != "": # magic trick to detect an empty message
        
        me = "djgravy@mwt.net"
        you = "lmadeo@wdrt.org"
        #msg['Subject'] = 'The contents of %s' % myText
        msg['Subject'] = 'Error message from autoCharlie ...'
        msg['From'] = me
        msg['To'] = you
        
        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        #s = smtplib.SMTP('localhost')
        s = smtplib.SMTP(host='smtp.mwt.net', port=587)
        s.sendmail(me, you, msg.as_string())
        s.quit()

    
    #server = smtplib.SMTP(host='smtp.gmail.com', port=587)
