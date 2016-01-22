# -*- coding: utf-8 -*-
"""
    This module shows sdk usage.
    :created by xuanzhui on 2015/12/25.
    :copyright (c) 2015 BeeCloud.
    :license: MIT, see LICENSE for more details.
"""
from flask import Flask, request, redirect, render_template, Markup
import datetime
# 实际项目中建议按需import
from beecloud.pay import BCPay
from beecloud.query import BCQuery
from beecloud.utils import order_num_on_datetime, local_timestamp_since_epoch
from beecloud.entity import BCApp, BCPayReqParams, BCRefundReqParams, BCChannelType, BCInternationalPayParams, \
    BCQueryReqParams, BCPreRefundAuditParams, BCBatchTransferParams, BCBatchTransferItem, BCTransferReqParams, \
    BCTransferRedPack

app = Flask(__name__)

# init
bc_app = BCApp()
bc_app.is_test_mode = True
bc_app.app_id = 'c5d1cba1-5e3f-4ba0-941d-9b0a371fe719'
# bc_app.app_secret = '39a7a518-9ac8-4a9e-87bc-7885f33cf18c'
# bc_app.master_secret = 'e14ae2db-608c-4f8b-b863-c8c18953eef2'
bc_app.test_secret = '4bfdd244-574d-4bf3-b034-0c751ed34fee'

bc_pay = BCPay()
bc_pay.register_app(bc_app)

bc_query = BCQuery()
bc_query.register_app(bc_app)


@app.route('/')
def hello_index():
    return app.send_static_file('index.html')


@app.route('/bill', methods=['POST'])
def app_bill():
    channel = request.form['channel']
    if channel.startswith('PAYPAL'):
        return _deal_with_international_pay(channel)
    else:
        return _deal_with_normal_pay(channel)


def _deal_with_normal_pay(channel):
    # wx js api 需要先获取支付人的open id
    req_params = BCPayReqParams()
    req_params.channel = channel
    req_params.title = u'python {:s} 支付测试'.format(channel)
    req_params.total_fee = 1
    req_params.bill_no = order_num_on_datetime()
    req_params.optional = {'lang': 'python', u'中文key': u'中文value'}
    # 支付完成后的跳转页面
    req_params.return_url = 'https://beecloud.cn/'
    # 支付宝网页支付(ALI_WEB)的选填参数，可以为商品详细页的url
    # req_params.show_url = 'https://beecloud.cn/'
    # 支付宝内嵌二维码支付(ALI_QRCODE)的必填参数
    if req_params.channel == BCChannelType.ALI_QRCODE:
        req_params.qr_pay_mode = '0'
    resp = bc_pay.pay(req_params)

    if resp.result_code:
        return resp.result_msg + ' # ' + resp.err_detail

    print("beecloud bill object id: " + resp.id)

    if not bc_app.is_test_mode and req_params.channel == BCChannelType.WX_NATIVE:
        return render_template('qrcode.html', raw_content=resp.code_url)
    elif hasattr(resp, 'url') and resp.url:
        return redirect(resp.url)
    elif hasattr(resp, 'html') and resp.html:
        return render_template('blank.html', content=Markup(resp.html))


def _deal_with_international_pay(channel):
    req_params = BCInternationalPayParams()
    req_params.channel = channel
    req_params.title = u'python {:s} 支付测试'.format(channel)
    req_params.total_fee = 1
    req_params.currency = 'USD'
    req_params.bill_no = order_num_on_datetime()
    # 支付完成后的跳转页面
    req_params.return_url = 'https://beecloud.cn/'

    resp = bc_pay.international_pay(req_params)

    if resp.result_code:
        return resp.result_msg + ' # ' + resp.err_detail

    if resp.id:
        print("beecloud bill object id: " + resp.id)

    if hasattr(resp, 'url') and resp.url:
        return redirect(resp.url)


@app.route('/bills')
def app_query_bills():
    query_params = BCQueryReqParams()
    if request.args.get('channel', '') != 'ALL':
        query_params.channel = request.args.get('channel', '')
    query_params.spay_result = True

    result = bc_query.query_bills(query_params)
    if result.result_code:
        return result.err_detail

    bills = result.bills
    return render_template('bills.html', bills=bills, channel=request.args.get('channel'))


@app.route('/bills_count')
def app_query_bills_count():
    query_params = BCQueryReqParams()
    if request.args.get('channel', '') != 'ALL':
        query_params.channel = request.args.get('channel', '')
    query_params.spay_result = True

    result = bc_query.query_bills_count(query_params)
    if result.result_code:
        return result.err_detail

    return str(result.count)


@app.route('/refunds')
def app_query_refunds():
    query_params = BCQueryReqParams()
    if request.args.get('channel', '') != 'ALL':
        query_params.channel = request.args.get('channel', '')

    # 过滤退款订单创建时间，此处表示只需要返回北京时间2016-1-13 15:30:00之后的订单
    query_params.start_time = local_timestamp_since_epoch(datetime.datetime(2016, 1, 13, 15, 30, 00))
    query_params.skip = 0
    query_params.limit = 16
    result = bc_query.query_refunds(query_params)
    if result.result_code:
        return result.err_detail
    return render_template('refunds.html', refunds=result.refunds, channel=request.args.get('channel'))


@app.route('/refunds_count')
def app_query_refunds_count():
    query_params = BCQueryReqParams()
    if request.args.get('channel', '') != 'ALL':
        query_params.channel = request.args.get('channel', '')

    # 过滤退款订单创建时间，此处表示只需要返回北京时间2016-1-13 15:30:00之后的订单
    query_params.start_time = local_timestamp_since_epoch(datetime.datetime(2016, 1, 13, 15, 30, 00))
    result = bc_query.query_refunds_count(query_params)
    if result.result_code:
        return result.err_detail

    return str(result.count)


@app.route('/refund_status')
def app_query_refund_status():
    channel = request.args.get('channel')
    refund_no = request.args.get('refund_no')

    result = bc_query.query_refund_status(channel, refund_no)
    if result.result_code:
        return result.err_detail

    return result.refund_status


@app.route('/query_pre_refunds')
def app_query_pre_refunds():
    query_params = BCQueryReqParams()
    if request.args.get('channel', '') != 'ALL':
        query_params.channel = request.args.get('channel', '')
    query_params.need_approval = True
    result = bc_query.query_refunds(query_params)
    if result.result_code:
        return result.err_detail
    return render_template('pre_refunds.html', pre_refunds=result.refunds)


@app.route('/audit_pre_refunds')
def app_audit_pre_refunds():
    req_params = BCPreRefundAuditParams()
    req_params.channel = request.args.get('channel')
    req_params.ids = request.args.get('ids', '').split('@')
    req_params.agree = True
    result = bc_pay.audit_pre_refunds(req_params)
    if not result.result_code:
        # 支付宝退款地址，需用户在支付宝平台上手动输入支付密码处理
        if req_params.channel == BCChannelType.ALI:
            print(result.result_map)
            # url在agree为True时返回
            return redirect(result.url)
        else:
            return str(result.result_map)
    else:
        return result.err_detail


@app.route('/refund')
def app_refund():
    refund_params = BCRefundReqParams()
    # 退款channel为选填参数
    refund_params.channel = request.args.get('channel', '')
    refund_params.refund_no = order_num_on_datetime()
    refund_params.bill_no = request.args.get('bill_no', '')
    refund_params.refund_fee = int(request.args.get('refund_fee', ''))
    if request.args.get('need_approval', ''):
        # 表示预退款，需要后期调用 预退款批量审核 API
        refund_params.need_approval = True
    result = bc_pay.refund(refund_params)
    if not result.result_code:
        # 支付宝退款地址，需用户在支付宝平台上手动输入支付密码处理
        if not refund_params.need_approval and refund_params.channel == BCChannelType.ALI:
            return redirect(result.url)
    return str(result.result_code) + ' # ' + result.result_msg + ' # ' + result.err_detail


@app.route('/bill/id/<bill_id>')
def app_bill_by_id(bill_id):
    result = bc_query.query_bill_by_id(bill_id)
    if result.result_code:
        return result.err_detail
    bill = result.pay
    return render_template('bill.html', bill=bill)


@app.route('/refund/id/<refund_id>')
def app_refund_by_id(refund_id):
    result = bc_query.query_refund_by_id(refund_id)
    if result.result_code:
        return result.err_detail
    m_refund = result.refund
    return render_template('refund_order.html', m_refund=m_refund)


@app.route('/transfer', methods=['POST'])
def app_transfer():
    channel = request.form['channel']
    # 批量打款
    if channel == 'ALI':
        transfer_params = BCBatchTransferParams()
        transfer_params.batch_no = order_num_on_datetime()
        transfer_params.account_name = u'苏州比可网络科技有限公司'
        item1 = BCBatchTransferItem()
        item1.transfer_id = order_num_on_datetime() + 'a'
        item1.receiver_account = '1234567'
        item1.receiver_name = u'某人1'
        item1.transfer_fee = 1
        item1.transfer_note = u'python支付宝批量打款item1'

        item2 = BCBatchTransferItem()
        item2.transfer_id = order_num_on_datetime() + 'b'
        item2.receiver_account = 'ali@account.c'
        item2.receiver_name = 'account2'
        item2.transfer_fee = 1
        item2.transfer_note = u'python支付宝批量打款item2'

        transfer_params.transfer_data = [item1, item2]

        result = bc_pay.batch_transfer(transfer_params)
    else:   # 单笔打款
        transfer_params = BCTransferReqParams()
        transfer_params.channel = channel
        transfer_params.desc = u'python {:s} 打款测试'.format(channel)
        if transfer_params.channel == BCChannelType.WX_REDPACK:
            # 微信为10位数字
            transfer_params.transfer_no = order_num_on_datetime()[0:10]
            # 微信红包1.00-200元
            transfer_params.total_fee = 100
            transfer_params.channel_user_id = 'o3kKrjlUsMnv__cK5DYZMl0JoAkY'
            redpack = BCTransferRedPack()
            redpack.send_name = 'BeeCloud'
            redpack.wishing = u'BeeCloud祝福开发者工作顺利'
            redpack.act_name = u'BeeCloud开发者测试中'
            transfer_params.redpack_info = redpack
        elif transfer_params.channel == BCChannelType.WX_TRANSFER:
            # 微信为10位数字
            transfer_params.transfer_no = order_num_on_datetime()[0:10]
            # 微信红包1.00-200元
            transfer_params.total_fee = 100
            transfer_params.channel_user_id = 'o3kKrjlUsMnv__cK5DYZMl0JoAkY'
        else:
            transfer_params.transfer_no = order_num_on_datetime()
            transfer_params.total_fee = 1
            transfer_params.channel_user_id = 'py@beecloud.cn'
            transfer_params.channel_user_name = 'py'
            transfer_params.account_name = u'苏州比可网络科技有限公司'

        result = bc_pay.transfer(transfer_params)

    if hasattr(result, 'url') and result.url:
        # 支付宝需要跳转到如下支付宝链接输入支付密码确认
        return redirect(result.url)

    return str(result.result_code) + ' # ' + result.result_msg + ' # ' + result.err_detail
        

@app.template_filter('format_utc_time')
def format_utc_time(s):
    return datetime.datetime.fromtimestamp(s/1000.0).strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    app.debug = True
    # app.run(host='0.0.0.0')
    app.run()
