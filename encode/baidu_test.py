# -*- coding: utf-8 -*-
import urllib2
import urllib

conn=urllib2.urlopen("http://www.baidu.com")
#html=str(conn.read())
html=conn.read().decode('utf-8')
html = html.encode('gbk')
print html
#print(html.decode("utf-8").encode("gbk"))

