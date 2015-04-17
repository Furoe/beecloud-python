# -*- coding: utf-8 -*-
import json
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import hashlib

from tornado.options import define, options

define("port", default=8088, help="run on the given port", type=int)
class MainHandler(tornado.web.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        appid = ''
        appsecret = ''
        timestamp = data['timestamp']
        sign = data['sign']
        thissign = hashlib.md5(appid+appsecret+str(timestamp))
        if thissign == sign:
            self.write('success')
            #处理业务逻辑
        else:
            self.write('any this except success')

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/webhook/demo/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
if __name__ == "__main__":
    main()
