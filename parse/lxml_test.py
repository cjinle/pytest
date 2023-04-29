#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import urllib
import random
import cookielib
import socket
import sys
import os
from time import time, strptime, strftime, mktime

from lxml import etree

def strip_str(str):
    return str.strip()

def sign_in_func(url):
    print "sign in "

def sign_out_func(url):
    url = "http://rd.tencent.com/outsourcing/attendances/edit/121404"
    http_header = {
                   "User-Agent" : "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
                   "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                   "Accept-Language" : "zh-CN,zh;q=0.8",
                   "Accept-Charset" : "GBK,utf-8;q=0.7,*;q=0.3",
                   "Content-Type" : "application/x-www-form-urlencoded",
                   "Cookie" : "pgv_pvid=4526336400; rd_login_via=login_via_password; CAKEPHP=s314kjv9i64cbhioqs5aomrs66; t_u=1402f0810e9867b99c75d11d2bad1be73dce3e01be9dfb5fd713af856f01ee6189abca33d606d61b; session_site=TAPD",
                   "Host" : "rd.tencent.com",
                   "Referer" : "http://rd.tencent.com/outsourcing/attendances/check_out/121404?have_checked_out=true",
                   }
    params = {
              
              "_method" : "POST",
              "data[Attendance][sub_check_out]" : strftime("%H:%M"),
              "data[Attendance][sub_check_out_remark]" : "",
              "data[Attendance][id]" : "121404",
              }
    timeout = 15
    socket.setdefaulttimeout(timeout)
    cookie_jar = cookielib.LWPCookieJar()
    cookie = urllib2.HTTPCookieProcessor(cookie_jar)
    opener = urllib2.build_opener(cookie)
    req = urllib2.Request(url, urllib.urlencode(params), http_header)
    res = opener.open(req)
#    return res.read()
    return "sign out done!"

def call_browser(url):
    cmd = "C:\\Users\\v_jinlchen\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe %s " % url
    os.system(cmd) 

print "now time is: %s" % strftime("%Y-%m-%d %H:%M:%S")

now_ts = time()
date = strftime("%Y-%m-%d")
strptime(date + " 09:30:00", "%Y-%m-%d %H:%M:%S")
sign_in_ts = mktime(strptime(date + " 09:30:00", "%Y-%m-%d %H:%M:%S"))
sign_out_ts = mktime(strptime(date + " 18:00:00", "%Y-%m-%d %H:%M:%S"))

post_url = "http://rd.tencent.com/outsourcing/attendances/edit/121404"
url = "http://rd.tencent.com/outsourcing/attendances/getCheckInRecord?time=%s" % random.random()
main_url = "http://rd.tencent.com/outsourcing/attendances/check_out/123209"
opener = urllib2.build_opener()
opener.addheaders.append(('Cookie', 'pgv_pvid=4526336400; rd_login_via=login_via_password; CAKEPHP=1dtvnmgknr1jh9a512aqojc8j4; t_u=1402f0810e9867b99c75d11d2bad1be73dce3e01be9dfb5fee99fb1379cf4ad04c8ffad6645d53de; session_site=TAPD'))
#opener.addheaders.append(('Accept-Language', 'zh-CN,zh;q=0.8'))
#opener.addheaders.append(('Accept-Charset', 'gbk,utf-8'))

response = opener.open(url)
data = response.read()
tree = etree.HTML(data)
#print data
#sys.exit(1)
try:
    date_td = strip_str(tree.xpath('//table/tr[1]/td[1]/span/text()')[0]).split(" ")[0]
    sign_in = strip_str(tree.xpath('//table/tr[1]/td[2]/text()')[0])
    sign_out = strip_str(tree.xpath('//table/tr[1]/td[4]/text()')[0])
    
    if date_td == date:
        print "today is %s" % date
        if sign_in:
            print "sign in time: %s" % sign_in
        else:
            print "you have not sign in today!"
            call_browser(main_url)
            sign_in_func()
        
        if sign_out:
            print "sign out time: %s" % sign_out
        else:
            call_browser(main_url)
            print "you have not sign out today!"
        print sign_out_func(post_url)
            
    else:
        print "date error!"
except:
    print "Exception: not login!"





    


