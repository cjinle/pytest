#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cookielib
import socket
import urllib
import urllib2
import time

url = "http://rd.tencent.com/outsourcing/attendances/edit/121404"
http_header = {
               "User-Agent" : "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
               "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "Accept-Language" : "zh-CN,zh;q=0.8",
               "Accept-Charset" : "GBK,utf-8;q=0.7,*;q=0.3",
               "Content-Type" : "application/x-www-form-urlencoded",
               "Cookie" : "pgv_pvid=4526336400; rd_login_via=login_via_password; CAKEPHP=1dtvnmgknr1jh9a512aqojc8j4; t_u=1402f0810e9867b99c75d11d2bad1be7d76b06e2e544f1d2de5c2d91f07e04a5d921b1148f6f77f6%7C0; session_site=TAPD",
               "Host" : "rd.tencent.com",
               "Referer" : "http://rd.tencent.com/outsourcing/attendances/check_out/121404?have_checked_out=true",
               }

params = {
          "_method" : "POST",
          "data[Attendance][sub_check_out]" : time.strftime("%H:%M"),
          "data[Attendance][sub_check_out_remark]" : "",
          "data[Attendance][id]" : "121404",
          }

timeout = 15
socket.setdefaulttimeout(timeout)

cookie_jar = cookielib.LWPCookieJar()
cookie = urllib2.HTTPCookieProcessor(cookie_jar)

proxy = {}

opener = urllib2.build_opener(cookie)
req = urllib2.Request(url, urllib.urlencode(params), http_header)
res = opener.open(req)

html = res.read()
open("tmp.html", "w").write(html)
print html

