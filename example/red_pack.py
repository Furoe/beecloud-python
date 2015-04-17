# -*- coding: utf-8 -*-
import json
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import uuid
import datetime, time
from tornado.options import define, options
from bcpay.bc_api import BCApi

define("port", default=8088, help="run on the given port", type=int)
BCApi.bc_app_id = 'c5d1cba1-5e3f-4ba0-941d-9b0a371fe719'
BCApi.bc_app_secret = '39a7a518-9ac8-4a9e-87bc-7885f33cf18c'
mch_id = '1234275402'
now = datetime.datetime.now()
date = now.strftime("%Y%m%d")
api = BCApi()
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #no格式: 十位数字每天不重复
        no = self.get_argument('no')
        #mch_billno格式：mch_id + 时间(yyyymmdd) + 十位不重复数字
        data = api.bc_red_pack(mch_id + date + no, 'o3kKrjlUsMnv__cK5DYZMl0JoAkY', 100, 'nick', 'nick', '中文', 'act', 'remark')
        print data
        self.write(data)
        self.write(data['return_msg'])
def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/redpack/demo/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
if __name__ == "__main__":
    main()
