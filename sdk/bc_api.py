# -*- coding: utf-8 -*-
import hashlib
import urllib
import json
from util import httpGet, httpPost
import random
import re
from datetime import datetime
class BCApi(object):
    bc_servers = ['https://apibj.beecloud.cn', 'https://apisz.beecloud.cn', 'https://apiqd.beecloud.cn', 'https://apihz.beecloud.cn', 'https://api.beecloud.cn']
    #api version
    api_version = '1'

    #wx appid & appkey
    wx_app_id = ''
    wx_app_secret = ''

    #basic configuration appid & appkey
    bc_app_id = ''
    bc_app_secret = ''

    #api uris
    pay_url = 'rest/bill'
    refund_url = 'rest/refund'
    pay_query_url = 'rest/bills'
    refund_query_url = 'rest/refunds'
    refund_status_url = 'rest/refund/status'

    wx_red_url = 'pay/wxmp/redPack'
    wx_red_extra_url = 'pay/wxmp/redPackExtra'

    #channels
    pay_channels = ['WX_APP', 'WX_JSAPI', 'WX_NATIVE', 'ALI_WEB', 'ALI_APP', 'ALI_QRCODE', 'ALI_WAP', 'UN_WEB', 'UN_APP']
    refund_channels = ['WX', 'ALI', 'UN']
    query_channels = refund_channels + pay_channels

    #
    def sign(self):
        return hashlib.md5(self.bc_app_id + self.bc_app_secret).hexdigest()

    def bc_sign(self, timestamp):
        #return self.m.update(self.appid+self.appsecret)
        return hashlib.md5(self.bc_app_id + self.bc_app_secret + str(timestamp)).hexdigest()

    def random_server():
        return self.bc_servers[random.randint(0, len(self.bc_servers))];

    def param_miss(param):
        err_data = {}
        err_data['result_code'] = 4
        err_data['result_msg'] = 'MISS_PARAM'
        err_data['err_detail'] = str(param) + '是必填参数'
        return err_data

    def param_invalid(param, err_detail):
        err_data = {}
        err_data['result_code'] = 5
        err_data['result_msg'] = 'PARAM_INVALID'
        err_data['err_detail'] = str(param) + '不合法 ' + str(err_detail)

    def runtime_error():
        r = {}
        r['result_code'] = 14
        r['result_msg'] = 'RUN_TIME_ERROR'
        return r

    def pay(channel, total_fee, bill_no, title, return_url = None, optional = None, show_url = None,
            qr_pay_mode = None, openid = None):
        pay_data = {}

        if not self.bc_app_id or not self.bc_app_secret :
            return param_miss('bc_app_id, bc_app_secret')
        
        if not channel:
            return param_miss('channel')

        if not total_fee:
            return param_miss('total_fee')

        if not bill_no:
            return param_miss('bill_no')

        if channel == 'WX_JSAPI' && !openid:
            return param_miss('openid')

        if not channel in pay_channels:
            return param_invalid('channel', '应该在' + str(pay_channels) + '中')

        if not isinstance(total_fee, int) or total_fee < 0:
            return param_invalid('total_fee', 'total_fee以分为单位，为正整数')

        if len(title) > 32:
            return param_invalid('title', '32个字节内')

        if len(bill_no) > 32:
            return param_invalid('bill_no', '32个字节内')

        if not re.match('^[0-9a-zA-Z]+$', bill_no):
            return param_invalid('bill_no', '只能字母数字组合')
        
        pay_data['channel'] = channel        
        pay_data['bc_app_id'] = self.bc_app_id
        timestamp = datetime.utcnow()
        timestamp = long(timestamp) * 1000
        pay_data['timestamp'] = timestamp
        pay_data['app_sign'] = self.bc_sign(timestamp)

        pay_data['total_fee'] = total_fee
        pay_data['title'] = title
        pay_data['bill_no'] = bill_no

        if channel == 'WX_JSAPI' and openid: 
            pay_data['openid'] = openid

        if return_url:
            pay_data['return_url'] = return_url

        if optional: 
            pay_data['optional'] = optional

        if channel == 'ALI_WEB' and show_url:
            pay_data['show_url'] = show_url

        if channel == 'ALI_QRCODE' and qr_pay_mode:
            pay_data['qr_pay_mode'] = qr_pay_mode

        return httpPost(random_server + '/' + self.version + '/' + pay_url, urllib.urlencode(pay_data))

    def refund(channel, refund_fee, refund_no, bill_no, optional = None):
        pay_data = {}

        if not self.bc_app_id or not self.bc_app_secret :
            return param_miss('bc_app_id, bc_app_secret')
        
        if not channel:
            return param_miss('channel')

        if not refund_fee:
            return param_miss('refund_fee')

        if not refund_no:
            return param_miss('refund_no')

        if not channel in refund_channels:
            return param_invalid('channel', '应该在' + str(refund_channels) + '中')

        if not isinstance(refund_fee, int) or refund_fee < 0:
            return param_invalid('refund_fee', 'refund_fee以分为单位，为正整数')

        now = datetime.datetime.now()
        date = now.strftime("%Y%m%d")
        if len(refund_no) > 32 or not refund_no.startswith(str(date)) or not re.match('^[0-9a-zA-Z]+$', refund_no):
            return param_invalid('refund_no', '32个字节内, 8位日期开头加24为流水号, 流水号字母数字组合，流水号不能为000')

        if len(bill_no) > 32:
            return param_invalid('bill_no', '32个字节内')

        if not re.match('^[0-9a-zA-Z]+$', bill_no):
            return param_invalid('bill_no', '只能字母数字组合')
        
        pay_data = {}
        pay_data['channel'] = channel
        pay_data['bc_app_id'] = self.bc_app_id
        timestamp = datetime.utcnow()
        timestamp = long(timestamp) * 1000
        pay_data['timestamp'] = timestamp
        pay_data['app_sign'] = self.bc_sign(timestamp)

        pay_data['refund_fee'] = refund_fee
        pay_data['refudn_no'] = refudn_no
        pay_data['bill_no'] = bill_no
        

        if optional: 
            pay_data['optional'] = optional

        return httpPost(random_server + '/' + self.version + '/' + refund_url, urllib.urlencode(pay_data))

    def query_bill(self, channel, bill_no = None, start_time = None, end_time = None, skip = None, limit = None):
         if not self.bc_app_id or not self.bc_app_secret :
            return param_miss('bc_app_id, bc_app_secret')
        
        if not channel:
            return param_miss('channel')

        if not channel in query_channels:
            return param_invalid('channel', '应该在' + str(query_channels) + '中')

        pay_data = {}
        pay_data['channel'] = channel
        pay_data['bc_app_id'] = self.bc_app_id
        timestamp = datetime.utcnow()
        timestamp = long(timestamp) * 1000
        pay_data['timestamp'] = timestamp
        pay_data['app_sign'] = self.bc_sign(timestamp)

        if bill_no:
            pay_data['bill_no'] = bill_no

        if start_time:
            pay_data['start_time'] = start_time

        if end_time:
            pay_data['end_time'] = end_time

        if not skip:
            skip = 0

        if not limit:
            limit = 10

        pay_data['skip'] = skip
        pay_data['limit'] = limit 

        data = {}
        data['para'] = pay_data
        hCode, value = httpGet(random_server() + '/' + self.api_version + '/' + self.pay_query_url+ '?'+ urllib.urlencode(data))
        if hCode:
            return json.loads(value)
        else:
            return runtime_error()

   def query_refund(self, channel, bill_no = None, refund_no = None, start_time = None, end_time = None, skip = None, limit = None):
         if not self.bc_app_id or not self.bc_app_secret :
            return param_miss('bc_app_id, bc_app_secret')
        
        if not channel:
            return param_miss('channel')

        if not channel in query_channels:
            return param_invalid('channel', '应该在' + str(query_channels) + '中')

        pay_data = {}
        pay_data['channel'] = channel
        pay_data['bc_app_id'] = self.bc_app_id
        timestamp = datetime.utcnow()
        timestamp = long(timestamp) * 1000
        pay_data['timestamp'] = timestamp
        pay_data['app_sign'] = self.bc_sign(timestamp)

        if refund_no:
            pay_data['refund_no'] = refund_no

        if bill_no:
            pay_data['bill_no'] = bill_no

        if start_time:
            pay_data['start_time'] = start_time

        if end_time:
            pay_data['end_time'] = end_time

        if not skip:
            skip = 0

        if not limit:
            limit = 10

        pay_data['skip'] = skip
        pay_data['limit'] = limit 

        data = {}
        data['para'] = pay_data
        hCode, value = httpGet(random_server() + '/' + self.api_version + '/' + self.refund_query_url+ '?'+ urllib.urlencode(data))
        if hCode:
            return json.loads(value)
        else:
            return runtime_error()

    def refund_status(self, channel, refund_no = None):
         if not self.bc_app_id or not self.bc_app_secret :
            return param_miss('bc_app_id, bc_app_secret')
        
        if not channel:
            return param_miss('channel')

        if not channel == 'WX':
            return param_invalid('channel', '目前本接口只支持WX')

        pay_data = {}
        pay_data['channel'] = channel
        pay_data['bc_app_id'] = self.bc_app_id
        timestamp = datetime.utcnow()
        timestamp = long(timestamp) * 1000
        pay_data['timestamp'] = timestamp
        pay_data['app_sign'] = self.bc_sign(timestamp)

        if refund_no:
            pay_data['refund_no'] = refund_no

        data = {}
        data['para'] = pay_data
        hCode, value = httpGet(random_server() + '/' + self.api_version + '/' + self.refund_status_url+ '?'+ urllib.urlencode(data))
        if hCode:
            return json.loads(value)
        else:
            return runtime_error()


    #微信红包支付
    def bc_red_pack(self, mch_billno, re_openid, total_amount, nick_name, send_name, wishing, act_name, remark):
        pp_data = {}
        pp_data['appId'] = self.bc_app_id
        pp_data['appSign'] = self.sign()
        pp_data['mch_billno'] = mch_billno
        pp_data['re_openid'] = re_openid
        pp_data['total_amount'] = total_amount
        pp_data['nick_name'] = nick_name
        pp_data['send_name'] = send_name
        pp_data['wishing'] = wishing
        pp_data['remark'] = remark
        pp_data['act_name'] = act_name
        params = json.dumps(pp_data)
        data = {}
        data['para'] = params
        hCode, value = httpGet(random_server() + '/' + self.api_version + '/' + self.wx_red_url + '?'+ urllib.urlencode(data))
        #hCode, value = httpGet('http://127.0.0.1:8080/1/pay/wxmp/redPack?' + urllib.urlencode(data))
        if hCode :
            return json.loads(value)
        return None

    #微信红包支付
    def bc_red_pack_extra(self, mch_billno, re_openid, nick_name, send_name, wishing, act_name, remark, total_amount=None,
                       countPerUser=None, minA=None, maxA=None, probability=None, period=None):
        pp_data = {}
        pp_data['appId'] = self.bc_app_id
        pp_data['appSign'] = self.bc_sign()
        pp_data['mch_billno'] = mch_billno
        pp_data['re_openid'] = re_openid
        if total_amount:
            pp_data['total_amount'] = total_amount
        pp_data['nick_name'] = nick_name
        pp_data['send_name'] = send_name
        pp_data['wishing'] = wishing
        pp_data['remark'] = remark
        pp_data['act_name'] = act_name
        if countPerUser:
            pp_data['count_per_user'] = countPerUser
        if minA:
            pp_data['min'] = minA
        if maxA:
            pp_data['max'] = maxA
        if probability:
            pp_data['probability'] = probability
        if period:
            pp_data['period'] = period
        params = json.dumps(pp_data)
        data = {}
        data['para'] = params
        hCode, value = httpGet(random_server() + '/' + self.api_version + '/' + self.wx_red_extra_url+ '?'+ urllib.urlencode(data))
        #hCode, value = httpGet('http://127.0.0.1:8080/1/pay/wxmp/redPackExtra?' + urllib.urlencode(data))
        if hCode :
            return json.loads(value)
        return None

    # 获取code参考 fetch_code method
    def fetch_open_id(self, code):
        if not code :
            print 'need to login'
            return False, None
        url = self.create_fetch_open_id_url(code)
        hCode, hValue = httpGet(url)
        if hCode :
            return True, hValue
        else:
            return False, None

    # 获取openid的url生成方法
    def create_fetch_open_id_url(self, code):
        fetch_data = {}
        fetch_data['appid'] = self.wx_app_id
        fetch_data['secret'] = self.wx_app_secret
        fetch_data['grant_type'] = self.wx_fetch_openid_type
        fetch_data['code'] = code
        params = urllib.urlencode(fetch_data)
        return self.wx_sns_token_url_basic + params

    # 获取code 的url生成规则，redirect_url是微信用户登录后的回调页面，将会有code的返回
    def fetch_code(self, redirect_url):
        code_data = {}
        code_data['appid'] = self.wx_app_id
        code_data['redirect_uri'] = redirect_url
        code_data['response_type'] = 'code'
        code_data['scope'] = 'snsapi_base'
        code_data['state'] = 'STATE#wechat_redirect' 
        params = urllib.urlencode(code_data)
        return self.wx_oauth_url_basic + params
