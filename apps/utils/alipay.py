# pip install pycryptodome
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes

import json
from MxShop.settings import alipay_private_key,alipay_pub_key

class AliPay(object):
    """
    支付宝支付接口
    """
    def __init__(self, appid, app_notify_url, app_private_key_path,
                 alipay_public_key_path, return_url, debug=False):
        self.appid = appid
        self.app_notify_url = app_notify_url
        self.app_private_key_path = app_private_key_path
        self.app_private_key = None
        self.return_url = return_url
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())

        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.import_key(fp.read())


        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)
        return self.sign_data(data)

    def build_body(self, method, biz_content, return_url=None):
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    def sign_data(self, data):
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        sign = self.sign(unsigned_string.encode("utf-8"))
        ordered_items = self.ordered_data(data)
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in ordered_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)


if __name__ == "__main__":
    return_url = 'http://123.206.229.93:8000/alipay/return/?total_amount=100.00&timestamp=2018-01-06+14%3A39%3A17&sign=CRcjk4fPcuCwOKPRVW1a8BX3o2bSSsfRW0tr88OuBZ6kRJj2n0Q9LBU8knl5oJcf6WkfbYX0iJlglUwBppkn760B3J9mhqT%2BczA5s47u%2F7SBwJJTP2Nz2abW9U2amiUCWPsZUdweLYr8urkQrgR3KkX01HF5SqDrFcULEaq2j%2B5D6DhYwiAVTzI3Mrv5MSm2%2BTIsM22i5ebJhI1PT%2BeVjmLlBzolTL8R1DlJy%2BBNJyhZiQ09x9aEMkvr8fYMoOpJMRZwtCjfYz2vDjav%2Fm%2FuM%2BALrnk33piqMmKmk7kc7z%2FrbYESHEk%2FlDcEkGfeFYBV1Ndm5hKd%2BSdbxSdUBlmGWA%3D%3D&trade_no=2018010621001004460200258539&sign_type=RSA2&auth_app_id=2016082100304253&charset=utf-8&seller_id=2088102172401965&method=alipay.trade.page.pay.return&app_id=2016082100304253&out_trade_no=201702021137&version=1.0'
    alipay = AliPay(
        appid="2016082100304253",
        app_notify_url="http://123.206.229.93:8000/alipay/return/",
        app_private_key_path=alipay_private_key,
        alipay_public_key_path=alipay_pub_key,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        debug=True,  # 默认False,
        return_url="http://123.206.229.93:8000/alipay/return/" # 支付宝付款完成后返回的url
    )

    # 验证支付宝返回的数据签名
    o = urlparse(return_url)
    query = parse_qs(o.query)
    processed_query = {}
    ali_sign = query.pop("sign")[0]
    for key, value in query.items():
        processed_query[key] = value[0]
    print (alipay.verify(processed_query, ali_sign))

    # 生成支付url
    url = alipay.direct_pay(
        subject="测试订单",
        out_trade_no="201702021131156",
        total_amount=100,
        # return_url="http://123.206.229.93:8000/" # 返回链接
    )
    re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
    print(re_url)