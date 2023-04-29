#!/usr/bin/python

import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.56.1', 22, 'root', '123456')
stdin, stdout, stderr = ssh.exec_command("df")
print stdout.readlines();
for i in stdout.readlines():
    print i
ssh.close()
