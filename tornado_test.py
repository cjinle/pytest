#!/usr/bin/env python
## -*- coding: utf8 -*-

#notice: os sys is blocking system
#
import os,sys,time
import string
reload(sys) 
sys.setdefaultencoding('utf8')


from tornado import netutil
from tornado import process
from tornado.ioloop import IOLoop
from tornado import web
from tornado import httpserver


sys.path.append("../modules")

import Comm_MySQLOper
from Comm_RedisOper import RedisOper
from Comm_DBUtil import DBConfInstance
from Comm_Logger import FileLogger



class MainHandler(web.RequestHandler):
    def get(self):
        self.write("Hi Baby! I'am 10.132.74.91 \n")


##
#Req:    http://10.187.22.150:8888/getiparea/10.187.22.150/PBOY
#
#Res:    10.187.22.150|PBOY|1_4_1|
#

class GetLogIpAreaHandler(web.RequestHandler):
    def initialize(self,logger):
        self.logger = logger
        self.redis_conf = DBConfInstance.getRedisInstance("tlogdata")
        self.logger.info(" redis_conf=[%s]",self.redis_conf)
        self.redis_conn = RedisOper(logger, self.redis_conf)
        
    def get(self, str):
        str = str.replace('^','&').replace('*','|')
        self.logger.info(" get request info=[%s]",str)
        if str is None:
            raise web.HTTPError(404)
            self.clear()
        else:
            res,area=self.get_result_status(str)
            if res is True:
                self.write("ok")
            else:
                self.write("no")
                

    def get_result_status(self,str):
        #1&10.206.15.211&2013-08-28_08|2013-08-28_09&1&1
        #str=area + "&" + ip + "&" + vFieldInterval + "&" + 1 + "&" + 1
        result = self.redis_conn.query_hash_key_fields(str)
        if result:
            self.logger.info(" get result=[%s]",result[0])
            return True,result[0]
        else:
            return False,False



logname = "tornado_ip_server"
logger = FileLogger("../log/"+logname+".log")

application = web.Application([
    (r"/",MainHandler),
    (r"/getlogiparea/(.*)",GetLogIpAreaHandler,dict(logger=logger)),
])



if __name__ == "__main__":
    #------------------------------------------------------------
    #tcp server Base create http server
    #curl http://10.132.74.91:9999/getlogiparea/1&10.206.16.39&2013-08-28_02|2013-08-28_03&1&1
    #------------------------------------------------------------
    sockets = netutil.bind_sockets(9999,address='10.132.74.91')
    process.fork_processes(4)
    
    #tcp server
    #server = netutil.TCPServer()
    
    #http server
    server = httpserver.HTTPServer(application)
    
    server.add_sockets(sockets)
    IOLoop.instance().start()

    
    
#redis-cli -h 10.213.255.253 -n 1
#hkeys WEPANG&2013-08-28

