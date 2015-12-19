# -*- coding: utf-8 -*-
import json
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import hashlib

from tornado.options import define, options

define("port", default=8090, help="run on the given port", type=int)
class MainHandler(tornado.web.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        appid = ''
        appsecret = ''
        timestamp = data['timestamp']
        sign = data['sign']
        thissign = hashlib.md5(appid+appsecret+str(timestamp)).hexdigest()
        # 验证签名
        if thissign == sign:
            self.write('success')
            # 此处需要验证购买的产品与订单金额是否匹配:
            # 验证购买的产品与订单金额是否匹配的目的在于防止黑客反编译了iOS或者Android app的代码，
            # 将本来比如100元的订单金额改成了1分钱，开发者应该识别这种情况，避免误以为用户已经足额支付。
            # Webhook传入的消息里面应该以某种形式包含此次购买的商品信息，比如title或者optional里面的某个参数说明此次购买的产品是一部iPhone手机，
            # 开发者需要在客户服务端去查询自己内部的数据库看看iPhone的金额是否与该Webhook的订单金额一致，仅有一致的情况下，才继续走正常的业务逻辑。
            # 如果发现不一致的情况，排除程序bug外，需要去查明原因，防止不法分子对你的app进行二次打包，对你的客户的利益构成潜在威胁。
            # 如果发现这样的情况，请及时与我们联系，我们会与客户一起与这些不法分子做斗争。而且即使有这样极端的情况发生，
            # 只要按照前述要求做了购买的产品与订单金额的匹配性验证，在你的后端服务器不被入侵的前提下，你就不会有任何经济损失。

            # 处理业务逻辑
            channel_type = data['channelType']
            transaction_type = data['transactionType']
            trade_success = data['tradeSuccess']
            message_detail = data['messageDetail']
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
