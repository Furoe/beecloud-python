# BeeCloud Python SDK & Example
## 安装 Python SDK
从pip快速安装  
`pip install beecloud`  
跟新  
`pip install beecloud --upgrade`  
或者从网站下载源码安装  
`python setup.py install`



## 微信网页内支付场景---JS API(网页内)支付接口
1.首先配置参数信息

``` python
    from bcpay.bc_api import BCApi
  
    #BeeCloud参数，从BeeCloud控制台获得
    bc_app_id = ''
    bc_app_secret = ''
  
    #微信参数
    wx_app_id = '' #微信公众号APPID唯一标识,支付审核通过后邮件中获得
    wx_app_secret = '' #微信公众号应用秘钥，在微信公众平台->开发者中心查看
    
    api = BCApi()
```

2.如果用户未授权，则先获得授权code

```python
    # 获取code 的url生成规则，redirect_url是微信用户登录后的回调页面，将会有code的返回
    def fetch_code(self, redirect_url):
```
3.获取openid  

```python
    # 获取微信用户的openid，需要微信用户先登录，获得code
    # 获取code参考 fetch_code method
    def fetch_open_id(self, code):
```

4.获取支付URL

``` python
    #微信服务号支付，需在微信中使用
    #body 商品描述
    #out_trade_no 商户订单号，16位，商户系统中唯一
    #total_fee 总价
    def bc_prepare_jsapi(self, openid, body, out_trade_no, total_fee):
```

5.跳转到获得的支付URL就可以开始支付（必须在微信中打开）


## 微信线下扫码购买场景---Native(原生)支付接口
1.首先配置参数信息

``` python
    from bcpay.bc_api import BCApi
  
    #BeeCloud参数，从BeeCloud控制台获得
    bc_app_id = ''
    bc_app_secret = ''
    
    api = BCApi()
```
2.获得二维码qrcode

```python
	#微信二维码支付，在任意浏览器打开，通过手机微信扫码支付
	#body 商品描述
    #out_trade_no 商户订单号，32位，商户系统中唯一
    #total_fee 总价
    def bc_prepare_nativeapi(self, body, out_trade_no, total_fee):
```
>商户的`out_trade_no`必须全局唯一,调试和生产环境,都需要使用唯一的订单号。注意: 当商户的同一个商户号绑定了公众号支付、小额刷卡、APP支付也需要加标识来区分, 不能出现重复。当发起支付返回失败时,一定要用原订单的 out trade no 而丌能重新生 成新的订单号収起支付,避免同一单重复支付。
  
3.通过获得的qrcode自行生成二维码图片（demo中提供了qrcode.js，是一种用js生成二维码图片的方式，供参考）  


## 支付宝网页支付
1.配置BeeCloud的appid和appsecrect:

```python
from bcpay.bc_api import BCApi

BCApi.bc_app_id = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
BCApi.bc_app_secret = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
api = BCApi()
```

2.调用SDK中的`bc_ali_web_pay`方法发起支付请求

```python
def bc_ali_web_pay(self, subject, total_fee, out_trade_no, return_url, show_url = None,
        anti_phishing_key = None, body = None):
```
代码中的各个参数含义如下： 
 
key | 说明  
---- | -----
return_url | 页面跳转同步通知页面路径，需http://格式的完整路径，不能加?id=123这类自定义参数，不能写成http://localhost/
seller_email | 卖家支付宝帐户，（必填）
out\_trade\_no | 商户订单号，商户网站订单系统中唯一订单号，（必填）
subject | 订单名称，（必填）
total_fee | 付款金额，（必填）
body | 订单描述（选填）
show_url | 商品展示地址，需以http://开头的完整路径，例如：http://www.商户网址.com/myorder.html（选填）
anti\_phishing\_key | 防钓鱼时间戳，若要使用请调用类文件submit中的query_timestamp函数（选填）
exter\_invoke\_ip | 客户端的IP地址，非局域网的外网IP地址，如：221.0.0.1（选填）

将`bc_ali_Web_pay`会返的内容输出到空白的网页，它会自动跳转到支付宝的收银台。


## 支付宝扫码支付
1.配置BeeCloud的appid和appsecrect:

```python
from bcpay.bc_api import BCApi

BCApi.bc_app_id = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
BCApi.bc_app_secret = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
api = BCApi()
```
2.构造biz_data  

```python 
biz_data = {"goods_info": { 
                    "id": "10001",
                    "name": "water ha",
                    "price": "0.01",
                    "desc": "nice "
                    },
                "ext_info": {
                    "single_limit": "2",
                    "user_limit": "3",
                    "logo_name": "BeeCloud"
                    },
                "need_address":"F",
                "trade_type":"1",
                "notify_url":"http://beecloud.cn/ali_test/aliqrcode/notify_url.php"
                }
``` 

biz_data参数说明:  

参数|参数名称|类型(字符长度)|参数说明|是否可为空|样例
---|-------|------------|-------|--------|----
trade_type|交易类型|String(1)|1:即时到账</br>2:担保交易</br>当本参数设置为2时,need_address必须为T。|不可空|1
need_address|是否需要收货地址|String(1)|T:需要</br>F:不需要</br>当本参数设置为 T 时,支付宝手 机客户端上会出现让用户填写收 货地址的信息。|不可空|T
goods_info|商品明细|String|商品明细信息,请参见 “4.2.2 goods_info参数说明”。|不可空|详见[goods_info参数样例”
return_url|通知商户下单URL|String(128)|商户生成二维码且用户使用了二维码,创建了一笔交易,支付宝通过该路径通知商户系统下订单。</br>如果为空则不通知商户系统。格式:以“http://”或“https://” 开头。|可空|http://www.test.com/r eturn_url.aspx
notify_url|通知商户支付结果url|String(128)|支付成功后,支付宝通过该路径通知商户支付成功,同时获取商户商品信息。</br>如果为空则不通知户系统。格式:以“http://”或“https://” 开头。</br>说明:支付宝通过何种方式获取商户商品信息,以及获取哪些信息,是在商户和支付宝签约时协商确定的。|可空|http://www.test.com/ notify_url.aspx
query_url|查询商品信息url|String(128)|商户码(友宝售货机码)的情况下,支付宝通过该地址获取商品信息。</br>biz_type=9 时,该参数不能为空。格式:以“http://”或“https://” 开头。|可空|http://www.test.com/ query_url.aspx
ext_info|扩展属性|String|扩展属性,请参见“4.2.3 ext_info参数说明”。|可空|详见“ext_info参数样例”
memo|备注|String(20)|备注信息。|可空|备注

goods_info 参数样例:

```python
{
	"id": "123456",
	"name": "商品名称", 
	"price": "11.23", 
	"inventory": "100", 
	"sku_title": "请选择颜色:", 
	"sku": [
		{
			"sku_id": "123456", 
			"sku_name": "白色", 
			"sku_price": "30.20", 
			"sku_inventory": "100"
		}, {
			"sku_id": "123456", 
			"sku_name": "白色", 
			"sku_price": "30.20", 
			"sku_inventory": "100"
		} ],
	"expiry_date": "2012-09-09 01:01:01|2012-09-19 01:02:59",
	"desc": "商品描述" 
}
```

ext_info 参数说明:  

参数|参数名称|类型(长度范围)|参数说明|是否可为空|样例
---|-------|------------|------|---------|----
single_limit|单次购买上限|String|单次购买上限,取值范围1~ 10,默认10。|单次购买上限必须小于或等于单用户购买上限。|可空|1
user_limit|单用户购买上限|String(6)|单用户购买上限,最多6位数字,默认无限制。|可空|1
pay_timeout|支付超时时间|String|支付超时时间,单位为分钟, 最小5分钟最大两天,默认15分钟。|可空|30
logo_name|二维码logo名称|String|二维码logo名称,最多5个汉字或者10个数字/字母.|可空|二维码
ext_field|自定义收集用户信息扩展字段|String|如果商户需要用户下单时提供一些简单的信息,比如手机号、身份证号等,可以通过此字段收集。<br>目前最多支持收集 2 项。 包含以下字段:<br>input_title:输入标题,不可空,长度限制为32个字符(中英文符号都为 1 个字符);<br>input_regex:输入内容, 正则表达式,可为空。<br>手机号<br> ^[1][3-8]+\\\d{9}$<br>邮箱<br> ^\\\w+([-+.]\\\w+)\*@\\\w+([- .]\\\w+)\*\\\\.\\\w+([-.]\\w+)*$<br>身份证 <br>^(\\\d{15}\|\\\d{17}(\\\d\|X\|x)) $|可空|{"input_title": "请输入手 机号码 ","input_regex":"^[1][3-8 ]+\\\d{9}$"}

ext_info 参数样例:  

```python
{
	"single_limit":"1",
	"user_limit":"1", 
	"pay_timeout":"30", 
	"logo_name":"二维码", 
	"ext_field":[
		{
			"input_title":"请输入手机号码", 
			"input_regex":"^[1][3-8]+\\d{9}$"
		},]
}
```

3.调用`bc_ali_qr_pay`方法获取支付宝二维码地址

```python
 #增加二维码(method=add)
 #修改二维码(method=modify)
 #暂停二维码(method=stop)
 #重新启用二维码(method=restart)
 
 #biz_data和qrcode根据需要传入
 def bc_ali_qr_pay(self, method, biz_data, qrcode):
```

##银联网页支付
1.配置BeeCloud的appid和appsecrect:

```python
from bcpay.bc_api import BCApi
BCApi.bc_app_id = 'c5d1cba1-5e3f-4ba0-941d-9b0a371fe719'
BCApi.bc_app_secret = '39a7a518-9ac8-4a9e-87bc-7885f33cf18c'
api = BCApi()
```
2.调用`bc_un_web_pay`方法调用银联支付

```python
//  @param orderId   商户系统内部的支付订单号,包含数字与字母,8-40位,确保在商户系统中唯一
//  @param traceId   支付用户ID，必须保证在商户系统中唯一.可通过traceId查询订单详情。
//  @param txnAmt    支付金额,以分为单位
//  @param orderDesc 订单描述
//  @param frontUrl  前台通知地址
def bc_un_web_pay(self, orderId, traceId, txnAmt, orderDesc, frontUrl):
```
将`bc_un_web_pay `返的内容输出到空白的网页，它会自动跳转到银联的收银台。

3.下面以`tornado`为例，展示完整过程： 
>本demo可以在本地测试

```python
import json
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import uuid

from tornado.options import define, options
from bcpay.bc_api import BCApi

define("port", default=8088, help="run on the given port", type=int)
BCApi.bc_app_id = 'c5d1cba1-5e3f-4ba0-941d-9b0a371fe719'
BCApi.bc_app_secret = '39a7a518-9ac8-4a9e-87bc-7885f33cf18c'
api = BCApi()
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        data = api.bc_un_web_pay(str(uuid.uuid1()).replace('-',''), 'sample_trace_id', '1', 'sample order desc', 'http://beecloud.cn')
        print data
        self.write(data['html']) 
def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/unweb/demo/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
if __name__ == "__main__":
    main()
```


##运行demo
需要安装`beecloud`和`tornado`  
进入example文件夹，Python执行demo文件即可，每个demo文件是一个功能，端口号定义在demo中
