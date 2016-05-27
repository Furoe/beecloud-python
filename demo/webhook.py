# -*- coding: utf-8 -*-
"""
    This module shows how to accept BeeCloud webhook push notifications.
    :created by xuanzhui on 2016/04/22.
    :copyright (c) 2015 BeeCloud.
    :license: MIT, see LICENSE for more details.
"""

# 这边只是演示如何接收beecloud webhook推送，实际项目中请遵循Flask项目规范，不要重复创建Flask app入口

# 接收webhook推送需要确保你的服务端地址能够在公网被访问

from flask import Flask, request
from beecloud.entity import BCApp
import hashlib

app = Flask(__name__)

# 请与你支付和退款的app参数保持一致
bc_app = BCApp()
bc_app.app_id = 'c5d1cba1-5e3f-4ba0-941d-9b0a371fe719'
bc_app.app_secret = '39a7a518-9ac8-4a9e-87bc-7885f33cf18c'


'''
推送标准：
	HTTP 请求类型 : POST
	HTTP 数据格式 : JSON
	HTTP Content-type : application/json
'''
@app.route('/webhook', methods=['POST'])
def app_accept_webhook():
	# 获取json数据
	json_data = request.get_json()

	# 第一步：验证数字签名
	# 从beecloud传回的sign
	bc_sign = json_data['sign']

	# 自己计算出sign -- App ID + App Secret + timestamp 的 MD5 生成的签名 (32字符十六进制) 
	timestamp = json_data['timestamp']

	my_sign = hashlib.md5((bc_app.app_id + bc_app.app_secret + str(timestamp)).encode('UTF-8')).hexdigest()

	# 判断两个sign是否一致
	if bc_sign != my_sign:
		return ''

	# 如果一致第一个检验通过
	'''
	理论上说到这一步就可以
	return 'success'
	以下的业务逻辑请根据商户内部需求处理，
	不需要重发了就应该返回success
	'''

	# 第二步：过滤重复的Webhook
	'''
	同一条订单可能会发送多条支付成功的webhook消息，
	这有可能是由支付渠道本身触发的(比如渠道的重试)，
	也有可能是BeeCloud的Webhook重试。
	客户需要根据订单号进行判重，忽略已经处理过的订单号对应的Webhook。
	'''
	# 获取订单号
	bill_num = json_data['transaction_id']
	'''
	以下为伪代码：
	#从自己系统的数据库中根据订单号取出订单数据，如发现已经支付成功，则忽略该订单
	bill_info = db_utils.get_bill_by_num(bill_num)
	if bill_info.pay_result == 'SUCCESS':
		return ''
	'''

	# 第三步：验证订单金额，以分为单位
	bill_fee = json_data['transaction_fee']
	'''
	以下为伪代码：
	# 如果金额不匹配，表明订单可能被篡改
	if bill_info.bill_fee != bill_fee:
		return ''
	'''

	# 如果金额匹配第二个检验通过

	# 第四步：处理业务逻辑和返回
	# 更新你的订单状态
	# update_bill(...)

	# 用户返回 success 字符串给BeeCloud表示 - 正确接收并处理了本次Webhook
	# 其他所有返回都代表需要继续重传本次的Webhook请求
	return 'success'


if __name__ == '__main__':
    app.debug = True
    # app.run(host='pythondemo.beecloud.cn', port=80)
    app.run(host='0.0.0.0')
