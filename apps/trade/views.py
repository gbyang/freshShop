import time

from rest_framework import viewsets,mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from django.shortcuts import redirect

from utils.permissions import IsOwnerOrReadOnly
from utils.alipay import AliPay
from .serializers import ShopCartSerializer,ShopCartDetailSetializer,OrderSerializer,OrderDetailSerializer
from .models import ShoppingCart,OrderInfo,OrderGoods
from MxShop.settings import alipay_private_key,alipay_pub_key

class ShoppingCartViewset(viewsets.ModelViewSet):
    """
    购物车功能
    list:
        获取购物车详情
    create:
        加入购物车
    ...
    """
    serializer_class = ShopCartSerializer
    queryset = ShoppingCart.objects.all()
    # 使用models中商品字段id查询记录详情（默认是使用model的id）
    lookup_field = 'goods_id'


    # viewset权限认证
    # IsAuthenticated 代表登陆后才具有操作权限
    # IsOwnerOrReadOnly 只能操作当前用户的相关记录
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    # 在View中单独配置认证，避免在setting中配置全局认证
    # JSONWebTokenAuthentication 需要添加header进行认证，html中测试GET方法时比较麻烦
    # SessionAuthentication 添加Session认证，即可通过获取cookie中的sessionid进行验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    # 重写queryset，只获取当前用户的购物车
    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    # 通过action动态绑定serializer
    def get_serializer_class(self):
        if self.action == 'list':
            return ShopCartDetailSetializer
        else:
            return ShopCartSerializer

    # 添加购物车时更新库存
    def perform_create(self, serializer):
        shop_cart = serializer.save()
        goods = shop_cart.goods
        goods.goods_num -= shop_cart.nums
        goods.save()

    # 删除购物车时更新库存
    def perform_destroy(self, instance):
        goods = instance.goods
        goods.goods_num += instance.nums
        goods.save()
        instance.delete()

    # 更新购物车时更新库存
    def perform_update(self, serializer):
        # model实例放在serializer.instance
        existed_record = ShoppingCart.objects.get(id=serializer.instance.id)
        existed_nums = existed_record.nums
        saved_record = serializer.save()
        nums = saved_record.nums-existed_nums
        goods = saved_record.goods
        goods.goods_num -= nums
        goods.save()


class OrderViewset(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.CreateModelMixin,mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    订单管理
    list:
        获取个人订单
    create:
        创建个人订单
    delete:
        取消订单
    """
    serializer_class = OrderSerializer
    queryset = OrderInfo.objects.all()

    # viewset权限认证
    # IsAuthenticated 代表登陆后才具有操作权限
    # IsOwnerOrReadOnly 只能操作当前用户的相关记录
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    # 在View中单独配置认证，避免在setting中配置全局认证
    # JSONWebTokenAuthentication 需要添加header进行认证，html中测试GET方法时比较麻烦
    # SessionAuthentication 添加Session认证，即可通过获取cookie中的sessionid进行验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        else:
            return OrderSerializer

    # 重写queryset，只获取当前用户的订单
    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    # 重载保存记录的方法
    def perform_create(self, serializer):
        # 保存订单（perform_create的原操作）
        order = serializer.save()
        # 保存订单对应的购物车信息并清空购物车（附加操作）
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        for shop_cart in shop_carts:
            order_goods = OrderGoods()
            order_goods.order = order
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            # 保存订单物品信息
            order_goods.save()
            # 删除购物车中的相应物品
            shop_cart.delete()


from rest_framework.views import APIView
from datetime import datetime
from rest_framework.response import Response
class AlipayView(APIView):
    """
    支付宝回调接口
    """
    def get(self, request):
        """
        支付宝同步调用返回
        :param request:
        :return:
        """
        # 将支付宝post的数据保存到字典中
        processed_dict = {}
        for key, value in request.GET.items():
            processed_dict[key] = value

        # 将sign从字典中移除
        sign = processed_dict.pop('sign')

        alipay = AliPay(
            appid="2016082100304253",
            app_notify_url="http://123.206.229.93:8000/alipay/return/",
            app_private_key_path=alipay_private_key,
            alipay_public_key_path=alipay_pub_key,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://123.206.229.93:8000/alipay/return/"  # 支付宝付款完成后返回的url
        )

        # 使用alipay_public_key为字典重新生成sign，与上面取出的的sign做比较，看数据是否有被修改
        verify_re = alipay.verify(processed_dict, sign)

        if verify_re is True:
            response = redirect('index')
            response.set_cookie('nextPath','pay',max_age=2)
            return response
        else:
            response = redirect('index')
            return response
        # # 两个签名一致，数据完整，进行本地订单状态的修改
        # if verify_re is True:
        #     order_sn = processed_dict.get('out_trade_no')
        #     trade_no = processed_dict.get('trade_no')
        #     trade_status = processed_dict.get('trade_status')
        #
        #     existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
        #     for existed_order in existed_orders:
        #         existed_order.trade_no = trade_no
        #         existed_order.pay_time = datetime.now()
        #         existed_order.pay_status = trade_status
        #         existed_order.save()
        #     # 向支付宝返回success
        #     return Response('success')

    def post(self, request):
        """
        支付宝异步调用返回
        :param request:
        :return:
        """

        # 将支付宝post的数据保存到字典中
        processed_dict = {}
        for key,value in request.POST.items():
            processed_dict[key] = value

        # 将sign从字典中移除
        sign = processed_dict.pop('sign')

        alipay = AliPay(
            appid="2016082100304253",
            app_notify_url="http://123.206.229.93:8000/alipay/return/",
            app_private_key_path=alipay_private_key,
            alipay_public_key_path=alipay_pub_key,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://123.206.229.93:8000/alipay/return/"  # 支付宝付款完成后返回的url
        )

        # 使用alipay_public_key为字典重新生成sign，与上面取出的的sign做比较，看数据是否有被修改
        verify_re = alipay.verify(processed_dict, sign)

        # 两个签名一致，数据完整，进行本地订单状态的修改
        if verify_re is True:
            order_sn = processed_dict.get('out_trade_no')
            trade_no = processed_dict.get('trade_no')
            trade_status = processed_dict.get('trade_status')

            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                # 更新销量
                order_goods = existed_order.goods.all()
                for order_good in order_goods:
                    goods = order_good.goods
                    goods.sold_num += order_good.goods_num
                    goods.save()
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.pay_status = trade_status
                existed_order.save()
            # 向支付宝返回success
            return Response('success')