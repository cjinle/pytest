#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
多进程PING
"""
import time
import subprocess

ips = [ '192.168.1.%s' % i for i in range(1, 255) ]
file = './alive_ip.txt'
file_ob = open(file, 'w+')

def do_ping(ip):
    print time.asctime(), "DOING PING FOR", ip
    cmd = "ping -n 5 %s" % ip
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

z = []

for ip in ips:
    p = do_ping(ip)
    z.append((p, ip))
    
for p, ip in z:
    print time.asctime(), "WAITING FOR", ip
    p.wait()
    print time.asctime(), ip, "RETURNED", p.returncode
    if p.returncode == 0:
        file_ob.write(ip + "\n")
        
        
        
    


