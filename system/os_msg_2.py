#!/usr/bin/python
# Lok 2012-05-18

from os_msg import disk_func, uname_func
import subprocess, os

def tmp_space():
    tmp_usage = "du"
    tmp_arg = "-h"
    path = "/tmp"
    print "Space used in /tmp directory"
    subprocess.call([tmp_usage, tmp_arg, path])

def main():
    uname_func()
    disk_func()
    tmp_space()

if __name__ == "__main__":
    main()
