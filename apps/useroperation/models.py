from django.db import models
from django.contrib.auth import get_user_model

from goods.models import Goods

# 自动获取AUTH_USER_MODEL
User = get_user_model()


# Create your models here.
class UserFav(models.Model):
    """
    用户收藏
    """
    user = models.ForeignKey(User,verbose_name='用户')
    goods = models.ForeignKey(Goods,verbose_name='商品')
    add_time = models.DateTimeField('添加时间',auto_now_add=True)

    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name
        # 联合唯一，同样的收藏记录只能有一条，也可以在serializer中使用validator来实现
        # 添加unique_together后要migration
        # 会返回'non_field_errors'
        unique_together = ('user','goods')

    def __str__(self):
        return self.user.name


class UserLeavingMessage(models.Model):
    """
    用户留言
    """
    MESSAGE_CHOICES = (
        (1,'留言'),
        (2,'投诉'),
        (3,'询问'),
        (4,'售后'),
        (5,'求购'),
    )

    user = models.ForeignKey(User, verbose_name='用户')
    message_type = models.IntegerField('留言类型',default=1,choices=MESSAGE_CHOICES,help_text='留言类型')
    subject = models.CharField('主题',max_length=100,default="")
    message = models.TextField('留言内容',default="",help_text='留言内容')
    file = models.FileField('上传的文件',upload_to='messages/images/',help_text='上传的文件')
    add_time = models.DateTimeField('添加时间',auto_now_add=True)

    class Meta:
        verbose_name = '用户留言'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.subject


class UserAddress(models.Model):
    """
    用户收货地址
    """
    user = models.ForeignKey(User, verbose_name='用户')
    province = models.CharField('省份',max_length=100,default='')
    city = models.CharField('城市',max_length=100,default='')
    district = models.CharField('区域',max_length=100,default='')
    address = models.CharField('详细地址',max_length=100,default='')
    signer_name = models.CharField('签收人',max_length=100,default='')
    signer_mobile = models.CharField('联系电话',max_length=11,default='')
    add_time = models.DateTimeField('添加时间',auto_now_add=True)

    class Meta:
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.subject
