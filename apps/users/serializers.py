import re
import datetime

from rest_framework import serializers
from MxShop.settings import MOBILE_REGEX
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator

from .models import VerifyCode

# 获取用户model
User = get_user_model()


class SmsSerializer(serializers.Serializer):
    """
    验证手机号码
    """
    mobile = serializers.CharField(max_length=11)

    # def validate_变量名,即可在序列化前验证字段是否正确
    def validate_mobile(self, mobile):
        # 验证用户是否存在
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError('用户已存在')

        # 验证手机号码是否合法
        if not re.match(MOBILE_REGEX, mobile):
            raise serializers.ValidationError('手机号码格式错误')

        # 验证上一次短信发送时间是否超过60s
        one_min_ago = datetime.datetime.now() - datetime.timedelta(seconds=60)
        if VerifyCode.objects.filter(mobile=mobile, add_time__gt=one_min_ago).count():
            raise serializers.ValidationError('距离上一次发送未超过60秒')

        # validate_xxx 函数最后一定要返回验证完成后的数值
        return mobile


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化
    """
    class Meta:
        model = User
        fields = ('name','gender','birthday','email','mobile')


class UserRegSerializer(serializers.ModelSerializer):
    # ModelSerializer中，当验证的字段不是需要返回的字段时，添加write_only=True
    code = serializers.CharField(required=True, write_only=True, min_length=4, max_length=4,
                                 error_messages={
                                     'blank': '请输入验证码',
                                     'required': '请输入验证码',
                                     'min_length': '验证码格式错误',
                                     'max_length': '验证码格式错误',
                                 },
                                 label='验证码',
                                 help_text='验证码')

    # 使用UniqueValidator验证用户唯一性，覆盖原model中的username字段
    username = serializers.CharField(required=True, allow_blank=False,label='用户名',
                                     validators=[UniqueValidator(queryset=User.objects.all(), message='用户已存在')])
    # 设置密码显示格式为password
    password = serializers.CharField(
        style={'input_type': 'password'},label='密码',
        write_only=True
    )

    # 若不对密码加以处理，密码会以明文保存在数据库中
    # ModelSerializer保存时需要调用create方法，重载create方法即可将密码加密
    # 这个功能也可以通过signal完成，就不需要重载create函数
    def create(self, validated_data):
        # 调用原create方法获取user（原create方法会将验证完的数据全部保存在创建的user中并返回）
        user = super(UserRegSerializer,self).create(validated_data=validated_data)
        # 调用user.set_password将明文密码加密
        user.set_password(validated_data['password'])
        # 保存user并返回
        user.save()
        return user

    def validate_code(self, code):
        """
        验证验证码
        :param code:
        :return:
        """
        # serializer中的初始数据都保存在initial_data字典中，若验证一个字段时需要另个字段的值，可从中获取
        code_records = VerifyCode.objects.filter(mobile=self.initial_data['username']).order_by('-add_time')
        if code_records:
            last_record = code_records[0]
            if code != last_record.code:
                raise serializers.ValidationError('验证码错误')

            five_min_ago = datetime.datetime.now() - datetime.timedelta(seconds=300)
            if five_min_ago > last_record.add_time:
                raise serializers.ValidationError('验证码过期')


        else:
            raise serializers.ValidationError('验证码错误')

    # 所有字段调用各自的validate_xx函数后，会调用validate函数，attrs是所有验证后的数据的保存的字典
    # CreateMixin会将attrs中的各个属性用于创建model，因此要删除model中不存在的属性（code）
    def validate(self, attrs):
        attrs['mobile'] = attrs['username']
        del attrs['code'] # 删除code
        return attrs

    class Meta:
        model = User
        # ModelSerializer中，可将model外的字段定义在Meta外，再加入field中
        # fields中的数据也是CreateMixin将会返回的数据
        # 若不想返回某个数据，添加write_only=True
        fields = ('username', 'code', 'mobile', 'password')
