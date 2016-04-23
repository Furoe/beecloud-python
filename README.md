## BeeCloud Python SDK (Open Source)

[![Build Status](https://travis-ci.org/beecloud/beecloud-python.svg)](https://travis-ci.org/beecloud/beecloud-python) ![license](https://img.shields.io/badge/license-MIT-brightgreen.svg) ![version](https://img.shields.io/badge/version-v3.0.0-blue.svg)

## 简介

本项目的官方GitHub地址是 [https://github.com/beecloud/beecloud-python](https://github.com/beecloud/beecloud-python)

本SDK是根据[BeeCloud Rest API](https://github.com/beecloud/beecloud-rest-api) 开发的 python SDK, 适用于python2.7、python3.4、python3.5。可以作为调用BeeCloud Rest API的示例或者直接用于生产。


## 安装 Python SDK
从pip快速安装  
`pip install beecloud`  
更新  
`pip install beecloud --upgrade`  
或者下载源码进入sdk安装  
`python setup.py install`  


## 依赖
sdk依赖于开源库[requests](http://docs.python-requests.org/en/latest/)，安装sdk时会自动安装，如果意外安装失败，可以手动安装

```
pip install requests
```

demo依赖于开源web框架[Flask](http://flask.pocoo.org/)，需手动安装

```
pip install Flask
```

## 准备工作
1. 注册开发者：猛击[这里](http://www.beecloud.cn/register)注册成为BeeCloud开发者。
2. 创建应用：使用注册的账号登陆[控制台](http://www.beecloud.cn/dashboard/)后，点击"+创建App"创建新应用

## 使用方法
* 具体使用请参考项目中的`demo`代码；
* 关于字符串的说明，对于`python2`如果需要传入的参数包含中文字符，请传入`unicode`，对于网络请求成功的情况，`BCResult`中返回结果的字符串也是`unicode`形式；对于`python3`，不需要考虑这样的细节；
* 以下的示例和`demo`中出现的关键字`u`（`unicode`）是为了兼容处理，在`python3`环境下不需要作这样的处理；
* 关于请求参数，公用字段（`app_id`，`timestamp`，`app_sign`）会自动处理，不要手动设置，其他字段和`REST API`一致（例如`REST API`中支付部分，对于`WX_JSAPI`支付方式，`openid`是必填的，假设请求参数名为`req_params`，那么应该添加这样的设置 `req_params.openid = 'openid_str'`），请参考[官网](https://beecloud.cn/doc/?index=0)说明，境外支付请参考[Github beecloud-rest-api](https://github.com/beecloud/beecloud-rest-api/)，以下不做额外介绍
* 返回结果是`beecloud.entity.BCResult`实例，包含以下公共字段，其他字段因不同API而异（例如`REST API`中支付部分，支付完成后会返回支付表记录唯一标识`id`，假设返回参数名为`result`，可以通过`result.id`获取结果），同理，请参照上一条列出的文档

参数名 | 说明
---- | -----
result_code | 返回码，0为正常
result_msg | 返回信息， OK为正常
err_detail | 具体错误信息

### 1.初始化

#### ①. `BCApp`对应于`BeeCloud`控制台中的应用，初始化：  

```
from beecloud.entity import BCApp
bc_app = BCApp()
bc_app.app_id = 'your app id'
# app secret被用于支付和查询
bc_app.app_secret = 'your app secret'
# master secret被用于打款和退款
bc_app.master_secret = 'your app master secret'
```

如果相关渠道尚未申请完成，想要体验sdk支付流程，可以开启测试模式

```
from beecloud.entity import BCApp
bc_app = BCApp()
# 不要在上线模式中设置该选项，否则会遇到BC验签错误相关提示
app.is_test_mode = True
bc_app.app_id = 'your app id'
bc_app.test_secret = 'your app test secret'
```

#### ②. 对于支付、打款和退款，需要初始化BCPay：

```python
from beecloud.pay import BCPay
bc_pay = BCPay()
bc_pay.register_app(bc_app)
```

#### ③. 对于查询需要初始化BCQuery：

```python
from beecloud.query import BCQuery
bc_query = BCQuery()
bc_query.register_app(bc_app)
```

### 2.支付
可以参考`demo.py`中`app_bill`

#### 原型：
通过`BCPay`的实例，以`pay`方法，结合`BCPayReqParams`参数，发起支付请求

#### 调用：

```python
req_params = BCPayReqParams()
req_params.channel = 'UN_WEB'
req_params.title = u'支付测试'
# 分为单位
req_params.total_fee = 1
req_params.bill_no = 'billno123'
# 可选参数
req_params.optional = {'lang': 'python', u'中文key': u'中文value'}
# 支付完成后的跳转页面
req_params.return_url = 'https://beecloud.cn/'
result = bc_pay.pay(req_params)
# 如果result.result_code为0表示请求成功
# 然后对相关的返回参数做处理，比如ALI_WEB会返回重定向url
```


### 3.退款
可以参考`demo.py`中`app_refund`；<br/>
退款接口包含预退款功能，当need_approval字段的值为true时，该接口开启预退款功能，预退款仅创建退款记录，并不真正发起退款，需后续调用审核接口

#### 原型：
通过`BCPay`的实例，以`refund`方法，结合`BCRefundReqParams`参数，发起退款请求

#### 调用：

```python
refund_params = BCRefundReqParams()
# 退款channel为选填参数
refund_params.channel = 'WX'
refund_params.refund_no = 'refundno123'
refund_params.bill_no = 'billno123'
# 分为单位
refund_params.refund_fee = 1
# need_approval为True时表示预退款，需要后期调用 预退款批量审核 API
# refund_params.need_approval = True
result = bc_pay.refund(refund_params)
# 如果result.result_code为0表示请求成功
# 对于支付宝退款，需要重定向至result.url
```


### 4.预退款批量审核
可以参考`demo.py`中`app_audit_pre_refunds`

#### 原型：
通过`BCPay`的实例，以`audit_pre_refunds`方法，结合`BCPreRefundAuditParams`参数，发起预退款批量审核

#### 调用：

```python
req_params = BCPreRefundAuditParams()
req_params.channel = 'WX'
req_params.ids = ['pre_refund_id1', 'pre_refund_id2']
req_params.agree = True
result = bc_pay.audit_pre_refunds(req_params)
# result.result_map为批量同意单笔结果集合
# 对于支付宝，需要重定向至result.url
```


### 5.打款
可以参考`demo.py`中`app_transfer`

#### 原型：
打款分**单笔打款**、**比可银行卡代付**、**批量打款**；  

 * **单笔打款**包含`WX_REDPACK`（微信红包）、`WX_TRANSFER`（微信企业打款）和`ALI_TRANSFER`（支付宝企业打款），通过`BCPay`的实例，以`transfer`方法，结合`BCTransferReqParams`参数发起打款；  

 * **比可银行卡代付**通过`BCPay`的实例，以`bc_transfer`方法，结合`BCCardTransferParams`参数发起代付；
  
 * **批量打款**目前只支持`ALI`（支付宝批量打款），通过`BCPay`的实例，以`batch_transfer`方法，结合`BCBatchTransferParams`参数发起打款；

#### 调用：
***单笔打款***  
以微信红包为例

```python
transfer_params = BCTransferReqParams()
transfer_params.channel = 'WX_REDPACK'
transfer_params.desc = u'打款说明'
# 微信为10位数字
transfer_params.transfer_no = '0123456789'
# 微信红包1.00-200元，此处以分为单位
transfer_params.total_fee = 100
transfer_params.channel_user_id = 'receiver_wechat_open_id'
# 微信红包初始化BCTransferRedPack
redpack = BCTransferRedPack()
redpack.send_name = 'BeeCloud'
redpack.wishing = u'BeeCloud祝福开发者工作顺利'
redpack.act_name = u'BeeCloud开发者测试中'
transfer_params.redpack_info = redpack
result = bc_pay.transfer(transfer_params)
# result.result_code等于0表示打款成功
# 对于支付宝需要重定向到result.url
```
  
***比可银行卡代付***

```python
transfer_params = BCCardTransferParams()
# 单位为分
transfer_params.total_fee = 1
transfer_params.bill_no = order_num_on_datetime()
# 最长支持16个汉字
transfer_params.title = u'python比可代付测试'
# 银行缩写编码
transfer_params.bank_code = 'BOC'
# 银行联行行号
transfer_params.bank_associated_code = '1043050000'
# 银行全名
transfer_params.bank_fullname = u'中国银行'
# DE代表借记卡，CR代表信用卡
transfer_params.card_type = 'DE'
# 帐户类型，P代表私户，C代表公户
transfer_params.account_type = 'C'
# 收款方的银行卡号
transfer_params.account_no = '5300000'
# 收款方的姓名或者单位名
transfer_params.account_name = u'苏州比可网络科技有限公司'
# 银行绑定的手机号，当需要手机收到银行入账信息时，该值必填，前提是该手机在银行有短信通知业务，否则收不到银行信息
transfer_params.mobile = '1850000'
# 附加数据，选填
transfer_params.optional = {'key1': u'选填的value'}

result = bc_pay.bc_transfer(transfer_params)
# result.result_code等于0表示代付请求成功，但是需要在webhook判定最终代付结果
```
  
***批量打款***

```python
transfer_params = BCBatchTransferParams()
# 11-32位数字字母组合
transfer_params.batch_no = 'abcdefg1234567'
transfer_params.account_name = u'苏州比可网络科技有限公司'
# 每一笔打款细项为BCBatchTransferItem实例
item1 = BCBatchTransferItem()
item1.transfer_id = order_num_on_datetime() + 'a'
item1.receiver_account = '1234567'
item1.receiver_name = u'某人1'
# 以分为单位
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
# result.result_code等于0时需要重定向到result.url
```


### 6.查询支付订单
可以参考`demo.py`中`app_query_bills`

#### 原型：
通过`BCQuery`的实例，以`query_bills`方法，结合`BCQueryReqParams`参数查询

#### 调用：
```python
query_params = BCQueryReqParams()
# 如果查询全部订单channel不设置即可
query_params.channel = 'WX'
# 限制只返回支付成功的订单
query_params.spay_result = True
result = bc_query.query_bills(query_params)
# 如果查询成功result.bills为beecloud.entity.BCBill的实例列表
```


### 7.查询退款订单
可以参考`demo.py`中`app_query_refunds`

#### 原型：
通过`BCQuery`的实例，以`query_refunds`方法，结合`BCQueryReqParams`参数查询

#### 调用：
```python
query_params = BCQueryReqParams()
# 如果查询全部订单channel不设置即可
query_params.channel = 'WX'
result = bc_query.query_refunds(query_params)
# 如果查询成功result.refunds为beecloud.entity.BCRefund的实例列表
```


### 8.查询支付订单数目
可以参考`demo.py`中`app_query_bills_count`

#### 原型：
通过`BCQuery`的实例，以`query_bills_count`方法，结合`BCQueryReqParams`参数查询

#### 调用：
```python
query_params = BCQueryReqParams()
# 如果查询全部订单channel不设置即可
query_params.channel = 'WX'
query_params.spay_result = True
result = bc_query.query_bills_count(query_params)
# 如果查询成功result.count表示满足条件的数目
```


### 9.查询退款订单数目
可以参考`demo.py`中`app_query_refunds_count`

#### 原型：
通过`BCQuery`的实例，以`query_refunds_count`方法，结合`BCQueryReqParams`参数查询

#### 调用：
```python
query_params = BCQueryReqParams()
# 如果查询全部订单channel不设置即可
query_params.channel = 'WX'
result = bc_query.query_refunds_count(query_params)
# 如果查询成功result.count表示满足条件的数目
```


### 10.根据ID查询支付订单
可以参考`demo.py`中`app_bill_by_id`

#### 原型：
通过`BCQuery`的实例，以`query_bill_by_id`方法，结合支付订单唯一标识id查询

#### 调用：
```python
result = bc_query.query_bill_by_id(bill_id)
# 如果查询成功result.pay为beecloud.entity.BCBill的实例
```


### 11.根据ID查询退款订单
可以参考`demo.py`中`app_refund_by_id`

#### 原型：
通过`BCQuery`的实例，以`app_refund_by_id`方法，结合退款订单唯一标识id查询

#### 调用：
```python
result = bc_query.query_refund_by_id(refund_id)
# 如果查询成功result.refund为beecloud.entity.BCRefund的实例
```


### 12.退款状态更新
可以参考`demo.py`中`app_query_refund_status`；<br/>
退款状态更新接口提供查询退款状态以更新退款状态的功能，用于对退款后不发送回调的渠道（WX、YEE、KUAIQIAN、BD）退款后的状态更新

#### 原型：
通过`BCQuery`的实例，以`query_refund_status`方法，结合渠道类型channel和退款单号refund_no查询

#### 调用：
```python
result = bc_query.query_refund_status(channel, refund_no)
# 如果查询成功result.refund_status为查询到的退款状态
```


## Demo
项目中的`demo`工程<br>
1. 请先安装sdk和[Flask](http://flask.pocoo.org/)，请参考`安装`和`依赖`<br/>
2. 运行：cmd进入`demo`文件夹后，运行
```shell
python demo.py
```


## 测试
项目中的`tests`工程为单元测试
>依赖[mock](https://pypi.python.org/pypi/mock)
`pip install mock`


## 常见问题
参见[FAQ](https://beecloud.cn/faq/)
