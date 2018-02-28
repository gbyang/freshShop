from django.db import models
from django.contrib.auth import get_user_model

from goods.models import Goods

# 自动获取AUTH_USER_MODEL
User = get_user_model()


# Create your models here.
class ShoppingCart(models.Model):
    """
    购物车
    """
    user = models.ForeignKey(User,verbose_name='用户')
    goods = models.ForeignKey(Goods,verbose_name='商品')
    nums = models.IntegerField('商品数量',default=0)
    add_time = models.DateTimeField('添加时间',auto_now_add=True)

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = verbose_name
        unique_together = ('user','goods') # 一种商品只能有一条记录，多次添加只加数量不加记录

    def __str__(self):
        return '{}({})'.format(self.goods.name,self.nums)


class OrderInfo(models.Model):
    """
    订单
    """
    ORDER_STATUS = (
        ('WAIT_BUYER_PAY', '交易创建'),
        ('TRADE_CLOSED', '交易超时'),
        ('TRADE_SUCCESS', '交易成功'),
        ('TRADE_FINISHED', '交易结束'),
        ('paying', '待支付'),
    )

    # WAIT_BUYER_PAY
    # 交易创建，等待买家付款
    # TRADE_CLOSED
    # 未付款交易超时关闭，或支付完成后全额退款
    # TRADE_SUCCESS
    # 交易支付成功
    # TRADE_FINISHED
    # 交易结束，不可退款

    user = models.ForeignKey(User,verbose_name='用户')
    order_sn = models.CharField('订单号',null=True,blank=True, unique=True, max_length=30)
    trade_no = models.CharField('交易号',unique=True,null=True,blank=True,max_length=100)
    pay_status = models.CharField('订单状态',default='paying',choices=ORDER_STATUS,max_length=20)
    post_script= models.TextField('订单留言',null=True,blank=True,default="")
    order_mount = models.FloatField('订单金额',default=0.0)
    pay_time = models.DateTimeField('支付时间',null=True,blank=True)

    # 用户信息(不绑定外键，若绑定外键，地址修改后会影响订单的地址，所以只保存下单时的数据)
    address = models.CharField('收货地址',max_length=100,default=100)
    signer_name = models.CharField('签收人',default="",max_length=20)
    signer_mobile = models.CharField('联系电话',max_length=11)
    add_time = models.DateTimeField('添加时间',auto_now_add=True)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_sn


class OrderGoods(models.Model):
    """
    订单的商品详情
    """
    order = models.ForeignKey(OrderInfo,verbose_name='订单信息', related_name='goods')
    goods = models.ForeignKey(Goods,verbose_name='商品')
    goods_num = models.IntegerField('商品数量',default=0)
    add_time = models.DateTimeField('添加时间',auto_now_add=True)

    class Meta:
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order.order_sn
