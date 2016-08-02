# -*- coding: utf-8 -*-
"""
    beecloud.pay
    ~~~~~~~~~
    This module contains payment API.
    :created by xuanzhui on 2015/12/24.
    :copyright (c) 2015 BeeCloud.
    :license: MIT, see LICENSE for more details.
"""

from beecloud.entity import BCChannelType, BCResult, BCReqType, BCPlan, BCSubscription, _TmpObject
from beecloud.utils import get_rest_root_url, http_post, http_put, set_common_attr, \
    report_not_supported_err, obj_to_dict, attach_app_sign, rest_add_object, \
    rest_update_object, rest_delete_object


class BCPay:
    def __init__(self):
        self.bc_app = None

    def register_app(self, bc_app):
        """
        register app, which is mandatory before calling other API
        :param bc_app: beecloud.entity.BCApp
        """
        self.bc_app = bc_app

    def _bill_pay_url(self):
        if self.bc_app.is_test_mode:
            return get_rest_root_url() + 'rest/sandbox/bill'
        else:
            return get_rest_root_url() + 'rest/bill'

    def _international_pay_url(self):
        return get_rest_root_url() + 'rest/international/bill'

    def _bill_refund_url(self):
        return get_rest_root_url() + 'rest/refund'

    def _bill_transfer_url(self):
        return get_rest_root_url() + 'rest/transfer'

    def _bc_transfer_url(self):
        return get_rest_root_url() + 'rest/bc_transfer'

    def _batch_transfer_url(self):
        return get_rest_root_url() + 'rest/transfers'

    def _plan_url(self):
        return get_rest_root_url() + 'plan'

    def _subscription_url(self):
        return get_rest_root_url() + 'subscription'

    def pay(self, pay_params):
        """
        payment API, different channels have different requirements for request params
        and the return params varies.
        refer to restful API https://beecloud.cn/doc/?index=rest-api #2
        :param pay_params: beecloud.entity.BCPayReqParams
        :return: beecloud.entity.BCResult
        """
        attach_app_sign(pay_params, BCReqType.PAY, self.bc_app)
        tmp_resp = http_post(self._bill_pay_url(), pay_params, self.bc_app.timeout)

        # if err encountered, [0] equals 0
        if not tmp_resp[0]:
            return tmp_resp[1]

        # [1] contains result dict
        resp_dict = tmp_resp[1]

        bc_result = BCResult()
        set_common_attr(resp_dict, bc_result)

        if not bc_result.result_code:
            bc_result.id = resp_dict.get('id')
            # most channel will return url or html
            bc_result.html = resp_dict.get('html')
            bc_result.url = resp_dict.get('url')
            # WX_NATIVE
            if pay_params.channel == BCChannelType.WX_NATIVE:
                bc_result.code_url = resp_dict.get('code_url')
            # WX_JSAPI
            if pay_params.channel == BCChannelType.WX_JSAPI:
                bc_result.app_id = resp_dict.get('app_id')
                bc_result.package = resp_dict.get('package')
                bc_result.nonce_str = resp_dict.get('nonce_str')
                bc_result.timestamp = resp_dict.get('timestamp')
                bc_result.pay_sign = resp_dict.get('pay_sign')
                bc_result.sign_type = resp_dict.get('sign_type')

        return bc_result

    def refund(self, refund_params):
        """
        refund API, refund fee should not be greater than bill total fee;
        need_approval is for pre refund, you have to call [audit_pre_refunds] later on to execute real refund
        if the bill is paid with ali, you have to input your password on the returned url page
        refer to restful API https://beecloud.cn/doc/?index=rest-api #3
        :param refund_params: beecloud.entity.BCRefundReqParams
        :return: beecloud.entity.BCResult
        """
        if self.bc_app.is_test_mode:
            return report_not_supported_err('refund')

        attach_app_sign(refund_params, BCReqType.REFUND, self.bc_app)
        tmp_resp = http_post(self._bill_refund_url(), refund_params, self.bc_app.timeout)

        # if err encountered, [0] equals 0
        if not tmp_resp[0]:
            return tmp_resp[1]

        # [1] contains result dict
        resp_dict = tmp_resp[1]
        bc_result = BCResult()
        set_common_attr(resp_dict, bc_result)

        if not bc_result.result_code:
            bc_result.id = resp_dict.get('id')
            # url will be returned if bill is refunded and channel is in (ALI_APP, ALI_WEB, ALI_QRCODE)
            bc_result.url = resp_dict.get('url')

        return bc_result

    def audit_pre_refunds(self, pre_refund_params):
        """
        batch manage pre refunds;
        pre refund id list is required;
        each refund result is kept in result_map
        refer to restful API https://beecloud.cn/doc/?index=rest-api #4
        :param pre_refund_params: beecloud.entity.BCPreRefundReqParams
        :return: beecloud.entity.BCResult
        """
        if self.bc_app.is_test_mode:
            return report_not_supported_err('audit_pre_refunds')

        attach_app_sign(pre_refund_params, BCReqType.PAY, self.bc_app)
        tmp_resp = http_put(self._bill_refund_url(), pre_refund_params, self.bc_app.timeout)

        # if err encountered, [0] equals 0
        if not tmp_resp[0]:
            return tmp_resp[1]

        # [1] contains result dict
        resp_dict = tmp_resp[1]
        bc_result = BCResult()
        set_common_attr(resp_dict, bc_result)

        if not bc_result.result_code:
            # if agree is true and refund successfully
            bc_result.result_map = resp_dict.get('result_map')
            bc_result.url = resp_dict.get('url')

        return bc_result

    def _bill_transfer(self, url, transfer_params):
        attach_app_sign(transfer_params, BCReqType.TRANSFER, self.bc_app)
        req_dict = {}
        for k, v in transfer_params.__dict__.items():
            if v:
                if k == 'redpack_info':     # WX_REDPACK
                    req_dict[k] = obj_to_dict(v)
                elif k == 'transfer_data':      # batch_transfer
                    req_dict[k] = [obj_to_dict(item) for item in transfer_params.transfer_data]
                else:
                    req_dict[k] = v

        tmp_resp = http_post(url, req_dict, self.bc_app.timeout)

        # if err encountered, [0] equals 0
        if not tmp_resp[0]:
            return tmp_resp[1]

        # [1] contains result dict
        resp_dict = tmp_resp[1]
        bc_result = BCResult()
        set_common_attr(resp_dict, bc_result)

        if not bc_result.result_code:
            bc_result.id = resp_dict.get('id')
            # for ali
            bc_result.url = resp_dict.get('url')

        return bc_result

    def bc_transfer(self, transfer_params):
        """
        for BeeCloud transfer via bank card
        refer to https://beecloud.cn/doc/?index=rest-api-transfer
        :param transfer_params: beecloud.entity.BCCardTransferParams
        :return: beecloud.entity.BCResult
        """
        if self.bc_app.is_test_mode:
            return report_not_supported_err('bc_transfer')
        return self._bill_transfer(self._bc_transfer_url(), transfer_params)

    def transfer(self, transfer_params):
        """
        for WX_REDPACK, WX_TRANSFER, ALI_TRANSFER
        refer to https://beecloud.cn/doc/?index=rest-api-transfer
        redpack_info should be type of beecloud.entity.BCTransferRedPack
        :param transfer_params: beecloud.entity.BCTransferReqParams
        :return: beecloud.entity.BCResult
        """
        if self.bc_app.is_test_mode:
            return report_not_supported_err('transfer')
        return self._bill_transfer(self._bill_transfer_url(), transfer_params)

    def batch_transfer(self, transfer_params):
        """
        batch transfer, currently only ALI is supported
        refer to https://beecloud.cn/doc/?index=rest-api-transfer
        transfer_data should be type of beecloud.entity.BCBatchTransferItem
        :param transfer_params: beecloud.entity.BCBatchTransferParams
        :return: beecloud.entity.BCResult
        """
        if self.bc_app.is_test_mode:
            return report_not_supported_err('batch_transfer')
        return self._bill_transfer(self._batch_transfer_url(), transfer_params)

    def international_pay(self, pay_params):
        """
        international pay -- PayPal
        refer to https://github.com/beecloud/beecloud-rest-api/tree/master/international #2
        credit_card_info should be type of beecloud.entity.BCPayPalCreditCard
        :param pay_params: beecloud.entity.BCInternationalPayParams
        :return: beecloud.entity.BCResult
        """
        if self.bc_app.is_test_mode:
            return report_not_supported_err('international_pay')

        attach_app_sign(pay_params, BCReqType.PAY, self.bc_app)
        req_dict = {}
        for k, v in pay_params.__dict__.items():
            if v:
                if k == 'credit_card_info':
                    req_dict[k] = obj_to_dict(v)
                else:
                    req_dict[k] = v

        tmp_resp = http_post(self._international_pay_url(), req_dict, self.bc_app.timeout)

        # if err encountered, [0] equals 0
        if not tmp_resp[0]:
            return tmp_resp[1]

        # [1] contains result dict
        resp_dict = tmp_resp[1]
        bc_result = BCResult()
        set_common_attr(resp_dict, bc_result)

        if not bc_result.result_code:
            bc_result.id = resp_dict.get('id')
            # url is returned when channel is PAYPAL_PAYPAL
            bc_result.url = resp_dict.get('url')
            # credit_card_id is returned when channel is PAYPAL_CREDITCARD
            bc_result.credit_card_id = resp_dict.get('credit_card_id')

        return bc_result

    def send_sms_passcode(self, phone):
        """
        send sms verify code
        :param phone: phone number passcode sent to
        :return: beecloud.entity.BCResult, which contains sms_id
        """
        tmp_obj = _TmpObject()
        tmp_obj.phone = phone
        attach_app_sign(tmp_obj, BCReqType.PAY, self.bc_app)
        tmp_resp = http_post(get_rest_root_url() + "sms", tmp_obj, self.bc_app.timeout)

        # if err encountered, [0] equals 0
        if not tmp_resp[0]:
            return tmp_resp[1]

        # [1] contains result dict
        resp_dict = tmp_resp[1]

        bc_result = BCResult()
        set_common_attr(resp_dict, bc_result)

        if not bc_result.result_code:
            bc_result.sms_id = resp_dict.get('sms_id')

        return bc_result

    def create_plan(self, plan):
        """
        create subscription plan
        :param plan: beecloud.entity.BCPlan
        :return: beecloud.entity.BCResult
        """
        return rest_add_object(self.bc_app, self._plan_url(), plan, 'plan', BCPlan)

    def update_plan(self, plan_id, name=None, optional=None):
        """
        update subscription plan
        :param plan_id: plan object id
        :param name: plan name
        :param optional: dict -- key/value pairs
        :return: beecloud.entity.BCResult
        """
        return rest_update_object(self.bc_app, self._plan_url(), plan_id, name=name, optional=optional)

    def delete_plan(self, plan_id):
        """
        delete subscription plan
        :param plan_id: plan object id
        :return: beecloud.entity.BCResult
        """
        return rest_delete_object(self.bc_app, self._plan_url(), plan_id)

    def subscribe(self, subscription, sms_id, sms_code, coupon_code=None):
        """
        create subscription
        :param subscription: beecloud.entity.BCSubscription
                coupon_code should be used instead of coupon_id if there is a discount
                card_id or {bank_name, card_no, id_name, id_no, mobile} should be supplied
                card_id can be gotten from webhook provided that subscription is successful
                bank_name can be chosen from BCQuery.query_subscription_payment_supported_banks()
        :param sms_id: return by send_sms_passcode method
        :param sms_code: get from user phone
        :param coupon_code: the coupon code to apply to this subscription
        :return: beecloud.entity.BCResult
        """
        setattr(subscription, 'sms_id', sms_id)
        setattr(subscription, 'sms_code', sms_code)
        if coupon_code:
            setattr(subscription, 'coupon_code', coupon_code)
        return rest_add_object(self.bc_app, self._subscription_url(), subscription, 'subscription', BCSubscription)

    def update_subscription(self, sid, **kwargs):
        """
        create subscription
        :param sid: subscription id
        :param kwargs: items can updated, like amount=2
        :return: beecloud.entity.BCResult
        """
        return rest_update_object(self.bc_app, self._subscription_url(), sid, **kwargs)

    def cancel_subscription(self, sid):
        """
        create subscription
        :param sid: subscription id
        :return: beecloud.entity.BCResult
        """
        return rest_delete_object(self.bc_app, self._subscription_url(), sid)
