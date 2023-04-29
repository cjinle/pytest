#!/usr/bin/python
# Lok 2012-05-18

import subprocess

def uname_func():
    uname = "uname"
    uname_arg = "-a"
    print "Gathering system information with %s command:\n" % uname
    subprocess.call([uname, uname_arg])


def disk_func():
    disksplace = "df"
    disksplace_arg = "-h"
    print "Gathering diskplace information %s command:\n" % disksplace
    subprocess.call([disksplace, disksplace_arg])

def main():
    uname_func()
    disk_func()



if __name__ == "__main__":
    main()
