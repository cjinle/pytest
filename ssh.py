#!/usr/bin/python

import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.55', 22, 'root', '123456')
stdin, stdout, stderr = ssh.exec_command("df")
for i in stdout.readlines():
    print i
ssh.close()