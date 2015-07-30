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
import re

from datetime import datetime
from tornado.options import define, options
from sdk.bc_api import BCApi

define("port", default=80, help="run on the given port", type=int)
BCApi.bc_app_id = 'c5d1cba1-5e3f-4ba0-941d-9b0a371fe719'
BCApi.bc_app_secret = '39a7a518-9ac8-4a9e-87bc-7885f33cf18c'
BCApi.wx_app_id = 'wx419f04c4a731303d'
BCApi.wx_app_secret = '21e4b4593ddd200dd77c751f4b964963'
api = BCApi()
home = 'http://queue.beecloud.cn/'

class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		user_agent = self.request.headers['User-Agent']
		ali_type = 'alipay'
		if re.match(".*(android|ipad|iphone|midp|rv:1.2.3.4|ucweb|windows ce|windows mobile)+.*", user_agent.lower()):
			ali_type='wapalipay'
		out_trade_no = str(uuid.uuid1()).replace('-','');
		sign = md5.new(BCApi.bc_app_id + "test" + "1" + out_trade_no + BCApi.bc_app_secret)
		print sign.hexdigest()
		self.render('templates/index.html', out_trade_no = out_trade_no, sign = sign.hexdigest(), ali_type=ali_type)

class PayHandler(tornado.web.RequestHandler):
	def post(self):
		try:
			pay_type = self.get_argument('paytype')
			print pay_type
			if pay_type == 'alipay':
			    
			    data = api.pay('ALI_WEB', 1, str(uuid.uuid1()).replace('-',''), '在线白开水', return_url = 'http://58.211.191.85:8088/result')
			    
			    print data
			    print data['err_detail']
			    sHtml = data['html']
			    self.write(sHtml)
			if pay_type == 'wapalipay':
			    data = api.pay('ALI_WAP', 1, str(uuid.uuid1()).replace('-',''), '在线白开水', return_url = 'http://58.211.191.85:8088/result')
			    print data
			    sHtml = data['html']
			    self.write(sHtml)
			if pay_type == 'wechatQr':
			    data = api.pay('WX_NATIVE', 1, str(uuid.uuid1()).replace('-',''), '在线白开水')
			    self.render('templates/nativeapi_demo.html', data=data['code_url'])
			if pay_type == 'jsapi':
			    self.redirect('/jsapi/demo')
			if pay_type == 'unionpay':
			    data = api.pay('UN_WEB', 1, str(uuid.uuid1()).replace('-',''), '在线白开水', return_url = 'http://58.211.191.85:8088/result')
			    print data
			    self.write(data['html'])
			if pay_type == 'qralipay':
			    temp = api.pay('ALI_QRCODE', 1, str(uuid.uuid1()).replace('-',''), '在线白开水', return_url = 'http://58.211.191.85:8088/result', qr_pay_mode = '0')
			    print temp
			    self.render('templates/qr_demo.html', qrapi=temp)
		except Exception, e:
			print e

class ResultHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('templates/result.html')

class JSApiHandler(tornado.web.RequestHandler):
	def get(self):
		code = ''
		try:
			code = self.get_argument("code")
		except Exception, e:
			print e
                        url = api.fetch_code(home + 'jsapi/demo/online_demo.php')
                        self.redirect(url)
			return None
		status, openid = api.fetch_open_id(code)
		data = api.pay('WX_JSAPI', 1, str(uuid.uuid1()).replace('-',''), 'jsapi demo', openid = openid)
		jsapi = {}
		jsapi['timeStamp'] = data['timestamp']
		jsapi['appId'] = data['app_id']
		jsapi['nonceStr'] = data['nonce_str']
		jsapi['package'] = data['package']
		jsapi['signType'] = data['sign_type']
		jsapi['paySign'] = data['pay_sign']
		self.render('templates/jsapi_demo.html', jsapi=json.dumps(jsapi))

class BillHandler(tornado.web.RequestHandler):
	def get(self):
	       channel = self.get_argument('channel')
	       if not channel:
	       	channel = 'WX'
	       data = api.query_bill(str(channel))
	       print data
	       bills = data['bills']
	       self.render('templates/bills.html', bills = bills, channel = channel)

class RefundsHandler(tornado.web.RequestHandler):
	def get(self):
	       channel = self.get_argument('channel')
	       if not channel:
	       	channel = 'WX'
	       data = api.query_refund(str(channel))
	       print data
	       refunds = data['refunds']
	       self.render('templates/refunds.html', refunds = refunds, channel = channel)

class RefundStatusHandler(tornado.web.RequestHandler):
	def get(self):
	       channel = self.get_argument('channel')
	       if not channel:
	       	channel = 'WX'
	       refund_no = self.get_argument('refund_no')
	       data = api.refund_status(str(channel), str(refund_no))
	       self.write(data)


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
	       url = data['url']
	       if url:
	       	print url
	       	self.redirect(url)
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
        		(r"/refunds", RefundsHandler),
        		(r"/refund_status", RefundStatusHandler),
        		(r"/jsapi/demo/online_demo.php", JSApiHandler),
	],**settings)
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
if __name__ == "__main__":
	main()
