# -*- coding: utf-8 -*-
import json
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import uuid
import os
import md5
import time

from datetime import datetime
from tornado.options import define, options
from sdk.bc_api import BCApi

define("port", default=8088, help="run on the given port", type=int)
BCApi.bc_app_id = 'c5d1cba1-5e3f-4ba0-941d-9b0a371fe719'
BCApi.bc_app_secret = '39a7a518-9ac8-4a9e-87bc-7885f33cf18c'
BCApi.wx_app_id = 'wx419f04c4a731303d'
BCApi.wx_app_secret = '21e4b4593ddd200dd77c751f4b964963'
api = BCApi()

class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		sign = md5.new(BCApi.bc_app_id + "test" + "8506" + "test0001" + BCApi.bc_app_secret)
		print sign.hexdigest()
		self.render('templates/index.html', out_trade_no = str(uuid.uuid1()).replace('-',''),sign = sign.hexdigest())

class PayHandler(tornado.web.RequestHandler):
	def post(self):
		try:
			pay_type = self.get_argument('paytype')
			if pay_type == 'alipay':
			    print '11111'
			    data = api.pay('ALI_WEB', 1, str(uuid.uuid1()).replace('-',''), '在线白开水', return_url = 'http://58.211.191.85:8088/result')
			    print '222222'
			    print data
			    sHtml = data['html']
			    self.write(sHtml)
			if pay_type == 'wechatQr':
			    data = api.pay('WX_NATIVE', 1, str(uuid.uuid1()).replace('-',''), '在线白开水')
			    self.render('templates/nativeapi_demo.html', data=data['code_url'])
			if pay_type == 'unionpay':
			    data = api.pay('UN_WEB', 1, str(uuid.uuid1()).replace('-',''), '在线白开水', return_url = 'http://58.211.191.85:8088/result')
			    self.write(data['html'])
			if pay_type == 'qralipay':
			    temp = api.pay('ALI_WEB', 1, str(uuid.uuid1()).replace('-',''), '在线白开水', return_url = 'http://58.211.191.85:8088/result', qr_pay_mode = '0')
			    self.render('templates/qr_demo.html', qrapi=temp)
		except Exception, e:
			print e

class ResultHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('templates/result.html')

class BillHandler(tornado.web.RequestHandler):
	def get(self):
	       channel = self.get_argument('channel')
	       if not channel:
	       	channel = 'WX'
	       data = api.query_bill(str(channel))
	       print data
	       bills = data['bills']
	       self.render('templates/bills.html', bills = bills, channel = channel)

class RefundHandler(tornado.web.RequestHandler):
	def get(self):
	       channel = self.get_argument('channel')
	       if not channel:
	       	channel = 'WX'

	       bill_no = self.get_argument("bill_no")
	       refund_fee = self.get_argument("refund_fee")
	       now = datetime.now()
	       date = now.strftime("%Y%m%d")
	       refund_no = str(date) + str(uuid.uuid1()).replace('-','')[0:23]
	       print refund_no
	       print bill_no
	       data = api.refund(channel, refund_fee, refund_no, bill_no)
	       print data
	       self.render('templates/refund_result.html', data = data)


def main():
	settings = {"static_path": os.path.join(os.path.dirname(__file__), "static")}
	tornado.options.parse_command_line()
	application = tornado.web.Application([
		(r"/", IndexHandler),
		(r"/pay", PayHandler),
		(r"/result",ResultHandler),
		(r"/bills", BillHandler),
		(r"/refund", RefundHandler),
	],**settings)
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
if __name__ == "__main__":
	main()