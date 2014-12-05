#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import tornado.ioloop
import tornado.web
from pymongo import Connection

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class UserHandler(tornado.web.RequestHandler):
    tb = None
    def initialize(self, tb):
        self.tb = tb

    def get(self, p):
        cnt = self.user_count()
        nums = int(math.ceil(cnt/50))
        p = int(p)
        if p < 1 or p > nums:
            p = 1
        html = """
        <html><head><meta charset="utf-8"></head>
        <body><h3>Weibo User[cnt: %s][page: %s]: </h3><div>page: %s</div><div>%s</div></body></html>
        """ % (cnt, p, self.page(p, cnt), self.get_users(p))
        self.write(html)

    def page(self, p, cnt):
        nums = int(math.ceil(cnt/50))
        ret = ""
        if nums > 0:
            for i in range(1, nums+1):
                ret += " [<a href='/u/%s'>%s</a>] " % (i, i)
        return ret

    def get_users(self, p):
        ret = ""
        start = int(p) * 50
        data = self.tb.find().skip(start).limit(50)
        if data:
            for i in data:
                ret += "<li><a href='http://weibo.com/%s' taraget='_blank'>%s</a></li>\n" % (str(i['uid']), str(i['nickname'].encode('UTF-8')))
        return ret

    def user_count(self):
        return self.tb.find().count()

c = Connection()
tb_follow = c.sina.weibo_follow

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/u/(.*)", UserHandler, dict(tb=tb_follow)),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


