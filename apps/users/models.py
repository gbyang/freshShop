from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UserProfile(AbstractUser):
    """
    用户
    """
    name = models.CharField('用户名',blank=True,null=True,max_length=20,default='userwho')
    birthday = models.DateField('生日',blank=True,null=True)
    mobile = models.CharField('手机号码',null=True,blank=True,max_length=11)
    gender = models.CharField('性别',choices=(('male','男'),('female','女')),default='male',max_length=10)
    email = models.EmailField('邮箱',blank=True,null=True,max_length=100)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class VerifyCode(models.Model):
    """
    短信验证码
    """
    code = models.CharField('验证码',max_length=50)
    mobile = models.CharField('手机号码',max_length=11)
    add_time = models.DateTimeField('添加时间',auto_now_add=True)

    class Meta:
        verbose_name = '短信验证码'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code
