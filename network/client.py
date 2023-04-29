#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""socket test"""

import socket
import random

HOST = 'localhost'
PORT = 30000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname('udp'))
s.connect((HOST, PORT))
# print dir(s)
content = "hello world from python client.py"
for i in range(99999):
#     str = "log_test.txt+_+1048576+_+|6301099|3|16120+_+2"
    str = "log_test.txt+_+1048576+_+|%s|%s|%s+_+2" % \
          (random.randint(1000000, 9999999), random.randint(1, 3), random.randint(1000, 99999))
    s.sendall(str)
# data = s.recv(1024)
s.close()

# print "Received", repr(data)