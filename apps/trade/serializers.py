import time

from rest_framework import serializers

from .models import Goods,ShoppingCart,OrderInfo,OrderGoods
from goods.serializers import GoodsSerializer
from MxShop.settings import alipay_private_key,alipay_pub_key
from utils.alipay import AliPay


class ShopCartDetailSetializer(serializers.ModelSerializer):
    """
    购物车详情序列化（用于list）
    """
    goods = GoodsSerializer(many=False) # 一条ShopCart记录对应一个goods

    class Meta:
        model = ShoppingCart
        fields = '__all__'


# Serializer 和 ModelSerializer的区别（crud方法的实现）
class ShopCartSerializer(serializers.Serializer):
    """
    购物车序列化（用于create，update，delete）
    """
    # 设置user为当前user
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    nums = serializers.IntegerField(required=True,label='数量',min_value=1,
                                    error_messages={
                                        'min_value':"商品数量不能小于1",
                                        'required':"请选择购买数量"
                                    })

    # 外键字段用PrimaryKeyRelatedField，Serializer要设置queryset参数，ModelSerializer就不用
    goods = serializers.PrimaryKeyRelatedField(required=True,queryset=Goods.objects.all())

    # Serializer并不像ModelSerializer实现了create，所以要手动重载
    # create方法主要是实现了model记录的保存，并返回该记录
    def create(self, validated_data):
        # 在Viewset中，request用self.request获取
        # Serializer中，request用elf.context['request']获取
        user = self.context['request'].user
        nums = validated_data['nums']  # validated_data是验证后的字典
        goods = validated_data['goods']

        # 是否存在记录
        existed = ShoppingCart.objects.filter(user=user,goods=goods)
        if existed:
            existed = existed[0]
            existed.nums += nums # 存在，数量增加（或减少）
            existed.save()
        else:
            # 不存在，创建记录
            existed = ShoppingCart.objects.create(**validated_data)

        return existed

    # Serializer并不像ModelSerializer实现了update，所以要手动重载
    # update方法主要是实现了model记录的更新，并返回该记录
    def update(self, instance, validated_data):
        """
        修改商品数量
        :param instance:
        :param validated_data:
        :return:
        """
        instance.nums = validated_data['nums']
        instance.save()
        return instance


class OrderGoodsSerializer(serializers.ModelSerializer):
    """
    订单物品序列化
    """
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = '__all__'


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    订单详情序列化（retrieve使用）
    """
    goods = OrderGoodsSerializer(many=True)

    # Serializer中的SerializerMethodField是用method动态生成的字段，它不在model中，一般read_only，直接返回
    alipay_url = serializers.SerializerMethodField(read_only=True)

    # 动态生成字段的方法定义为get_字段(self, obj): obj是这个serialzer本身
    def get_alipay_url(self, obj):
        """
        动态返回alipay_url的值
        :param obj:
        :return:
        """
        alipay = AliPay(
            appid="2016082100304253",
            app_notify_url="http://123.206.229.93:8000/alipay/return/",
            app_private_key_path=alipay_private_key,
            alipay_public_key_path=alipay_pub_key,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://123.206.229.93:8000/alipay/return/"  # 支付宝付款完成后返回的url
        )

        # 生成支付url
        url = alipay.direct_pay(
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
            # return_url="http://123.206.229.93:8000/" # 返回链接
        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
        return re_url

    class Meta:
        model = OrderInfo
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    """
    订单序列化（list,delete,create使用）
    """

    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    # 不允许提交，只读
    pay_status = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)

    # Serializer中的SerializerMethodField是用method动态生成的字段，它不在model中，一般read_only，直接返回
    alipay_url = serializers.SerializerMethodField(read_only=True)

    # 动态生成字段的方法定义为get_字段(self, obj): obj是这个serialzer本身
    def get_alipay_url(self, obj):
        """
        动态返回alipay_url的值
        :param obj:
        :return:
        """
        alipay = AliPay(
            appid="2016082100304253",
            app_notify_url="http://123.206.229.93:8000/alipay/return/",
            app_private_key_path=alipay_private_key,
            alipay_public_key_path=alipay_pub_key,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://123.206.229.93:8000/alipay/return/"  # 支付宝付款完成后返回的url
        )

        # 生成支付url
        url = alipay.direct_pay(
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
            # return_url="http://123.206.229.93:8000/" # 返回链接
        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
        return re_url

    def generate_order_sn(self):
        """
        生成订单号
        :return:
        """
        from random import Random
        ran_ins = Random()
        # serializer中request的取法 self.context['request']
        order_sn = "{time_str}{userid}{ran_str}".format(time_str=time.strftime('%Y%m%d%H%M%S'),userid=self.context['request'].user.id,ran_str=ran_ins.randint(10,99))
        return order_sn

    # 增加attrs的数据，viewset中的perform_create方法会使用attrs中所有的属性创建新记录
    def validate(self, attrs):
        attrs['order_sn'] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = '__all__'