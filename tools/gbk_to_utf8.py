#!/usr/bin/env python
# coding=utf-8

import subprocess, time


# iconv -f gbk -t utf8 ConfigManager.cpp -o ConfigManager.cpp
def iconv(filename):
    print("start iconv", filename)
    cmd = [
        "iconv",
        "-f",
        "gbk",
        "-t",
        "utf8",
        filename,
        "-o",
        filename,
    ]
    subprocess.call(cmd)



# find . -name "*.py" -or -name "*.md"

cmd = [
    "find",
    # "/data/wwwroot/server/server_hallid",
    "/data/wwwroot/server/hallid",
    "-name",
    "*.cpp",
    "-or",
    "-name",
    "*.h",
    "-or",
    "-name",
    "*.ini"
]

result = subprocess.check_output(cmd)
# print(type(result))
filelist = result.decode("utf-8").split("\n")
for filename in filelist:
    if not filename: continue
    # print(filename)
    iconv(filename)

# filename = "/data/wwwroot/server/hallid/Frame/Alloc/src/ConfigManager.h"
# iconv(filename)




