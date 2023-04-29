#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2

data = "_method=POST&data%5BAttendance%5D%5Bcheck_out%5D=16%3A38&data%5BAttendance%5D%5Bcheck_out_remark%5D=&data%5BAttendance%5D%5Bid%5D=121404"

d = urllib.unquote(data)
print d

url = "http://meta.ied.com/index.php/monitor/getDistrictList"
params = {
          "id" : 7,
          "na" : 0,
          "all" : 1,
          }

req  = urllib2.Request(url)
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor)
opener.addheaders.append(('Cookie', 'oaname=v_jinlchen; TCOA_TICKET=70717C17A2371D551170AC852CFCAAB3E31AD96C6676A1BCD3BEFF20843DFDF5196FD889D2B8EDD3DD0834618F1F50E8E9E5009DB50300A820025A26CCDAE56AA80A3DBDFB40E3083CA9CE2F879CD44F09FEDA107789BD5E1ADD0A50B0D48B12900890AED40890204D13B4FF14B74BFA0B04C44809FEBB31643D83676931A8A071872BDCD57A99197C596320A2F2FACCEB69654F4D0ED35B9D71A3B1902EE14B3EEFA04034EC22E0626341C7CD4838A845CAC12F6216DEC0D16DD118A08CD7CE4CD7A8D19E400F09EB481EE8D40B43C8; PREF=6972f165fe36a981775adc824ae2f52605f64ced; ci_session=a%3A12%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%2235b7518c95e5c6e84f110f7e4780510a%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A12%3A%2210.96.147.68%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A101%3A%22Mozilla%2F5.0+%28Windows+NT+6.1%29+AppleWebKit%2F537.11+%28KHTML%2C+like+Gecko%29+Chrome%2F23.0.1271.64+Safari%2F537.11%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1371628989%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3Bs%3A13%3A%22previous_page%22%3Bs%3A53%3A%22http%3A%2F%2Fmeta.ied.com%2Findex.php%2Fmonitor%2FgetDistrictList%22%3Bs%3A6%3A%22oaname%22%3Bs%3A10%3A%22v_jinlchen%22%3Bs%3A6%3A%22userid%22%3Bs%3A1%3A%224%22%3Bs%3A7%3A%22perPage%22%3Bs%3A2%3A%2220%22%3Bs%3A5%3A%22serid%22%3Bs%3A1%3A%221%22%3Bs%3A8%3A%22username%22%3Bs%3A10%3A%22v_jinlchen%22%3Bs%3A6%3A%22iSerID%22%3Bs%3A1%3A%221%22%3B%7Dd769aa08f4b30f6c612701736644116f'))
response = opener.open(req, urllib.urlencode(params))
print response.read()