## BeeCloud Python SDK (Open Source)

![pass](https://img.shields.io/badge/Build-pass-green.svg) ![license](https://img.shields.io/badge/license-MIT-brightgreen.svg) ![version](https://img.shields.io/badge/version-v2.0.1-blue.svg)

## 简介

本项目的官方GitHub地址是 [https://github.com/beecloud/beecloud-python](https://github.com/beecloud/beecloud-python)

本SDK是根据[BeeCloud Rest API](https://github.com/beecloud/beecloud-rest-api) 开发的 python SDK, 适用于python2.5及以上版本。可以作为调用BeeCloud Rest API的示例或者直接用于生产。


## 安装 Python SDK

从pip快速安装  
`pip install beecloud`  
更新  
`pip install beecloud --upgrade`  
或者下载源码安装  
`python setup.py install`  

### **目前不能从pip安装, 请先下载源码安装**

## 依赖
demo的运行依赖于开源web框架[tornado](http://www.tornadoweb.cn/)

## 准备工作
三个步骤，2分钟轻松搞定：
1. 注册开发者：猛击[这里](http://www.beecloud.cn/register)注册成为BeeCloud开发者。
2. 创建应用：使用注册的账号登陆[控制台](http://www.beecloud.cn/dashboard/)后，点击"+创建App"创建新应用
3. 在代码中注册：

```python
BCApi.bc_app_id = 'your_beecloud_app_id_here'
BCApi.bc_app_secret = 'your_beecloud_app_secret_here'
```

## 使用方法
>具体使用请参考项目中的`demo`代码，是使用[tornado](http://www.tornadoweb.cn/)编写的一个web demo  
>参数的具体含义请参见注释

初始化代码：

```python
from sdk.bc_api import BCApi
BCApi.bc_app_id = 'your beecloud app id'
BCApi.bc_app_secret = 'your beecloud app secret'
api = BCApi()
```

1.支付

方法原型：

```python
def pay(self, channel, total_fee, bill_no, title, return_url = None, optional = None, show_url = None, qr_pay_mode = None, openid = None):
```

调用：

```python
#支付宝网页支付
data = api.pay('ALI_WEB', 1, str(uuid.uuid1()).replace('-',''), '在线白开水', return_url = 'http://58.211.191.85:8088/result')
#支付宝手机网页支付
data = api.pay('ALI_WAP', 1, str(uuid.uuid1()).replace('-',''), '在线白开水', return_url = 'http://58.211.191.85:8088/result')
#支付宝二维码支付
data = api.pay('ALI_WEB', 1, str(uuid.uuid1()).replace('-',''), '在线白开水', return_url = 'http://58.211.191.85:8088/result', qr_pay_mode = '0')
#微信二维码支付
data = api.pay('WX_NATIVE', 1, str(uuid.uuid1()).replace('-',''), '在线白开水')
#银联web支付
data = api.pay('UN_WEB', 1, str(uuid.uuid1()).replace('-',''), '在线白开水', return_url = 'http://58.211.191.85:8088/result')
```
2.退款

方法原型：

```python
def refund(self, refund_fee, refund_no, bill_no, channel=None, optional = None):
```
调用：

```python
data = api.refund(1, '201507083211', 'somebillno')
data = api.refund(1, '201507083211', 'somebillno')
data = api.refund(1, '201507083211', 'somebillno')
```
3.查询

* 查询支付订单

方法原型：

```python
def query_bill(self, channel = None, bill_no = None, start_time = None, end_time = None, skip = None, limit = None):
```
调用：

```python
data = api.query_bill(channel = 'WX')
data = api.query_bill(bill_no = '201508191010xxxxx')
#...
```
* 查询退款订单

方法原型：

```python
def query_refund(self, channel = None, bill_no = None, refund_no = None, start_time = None, end_time = None, skip = None, limit = None):
```
调用：

```python
data = api.query_refund('WX')
data = api.query_refund('bill_no' = '201508191010xxxxx')
data = api.query_refund('refund_no' = '201508191148vvvvvv')
#...
```
* 查询退款状态（只支持微信）

方法原型：

```python
def refund_status(self, channel, refund_no)
```
调用：

```python
data = api.refund_status('WX', '20150729000001')
```

## Demo
项目中的`demo`工程为我们的demo  
>请先安装[tornado](http://www.tornadoweb.cn/)

- 关于weekhook的接收
请参考demo中的`webhook.py`
文档请阅读 [webhook](https://github.com/beecloud/beecloud-webhook)

## 测试
TODO

## 常见问题
1. 由于支付宝的限制，beecloud的支付宝账号不能用来做demo测试， 所以支付宝demo的最后一步支付无法完成，请用户使用自己的appId和appSecret来进行测试

## 代码贡献
我们非常欢迎大家来贡献代码，我们会向贡献者致以最诚挚的敬意。

一般可以通过在Github上提交[Pull Request](https://github.com/beecloud/beecloud-python)来贡献代码。

Pull Request要求

- 代码规范 

- 代码格式化 

- 记得更新文档 - 保证`README.md`以及其他相关文档及时更新，和代码的变更保持一致性。

- 一个feature提交一个pull请求 - 如果你的代码变更了多个操作，那就提交多个pull请求吧。

- 清晰的commit历史 - 保证你的pull请求的每次commit操作都是有意义的。如果你开发中需要执行多次的即时commit操作，那么请把它们放到一起再提交pull请求。

## 联系我们
- 如果有什么问题，可以到BeeCloud开发者1群:**321545822** 或 BeeCloud开发者2群:**427128840** 提问
- 更详细的文档，见源代码的注释以及[官方文档](https://beecloud.cn/doc/?index=5)
- 如果发现了bug，欢迎提交[issue](https://github.com/beecloud/beecloud-python/issues)
- 如果有新的需求，欢迎提交[issue](https://github.com/beecloud/beecloud-python/issues)


##运行demo
需要安装`beecloud`和`tornado`  
shell里进入工程文件夹，运行

```shell
python demo/index.py
```
可自行修改端口
打开浏览器访问localhost即可
