from random import choice
from utils.yunpian import YunPian

from django.shortcuts import render
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import viewsets,mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication

from .serializers import SmsSerializer,UserRegSerializer,UserDetailSerializer
from MxShop.settings import APIKEY
from .models import VerifyCode

# 使用get_user_model来获取User
User = get_user_model()


# Create your views here.
# 重写用户认证判断(增加手机登陆)
class CustomAuth(ModelBackend): # 需要继承ModelBackend，完成该类编写后配置settings中的AUTHENTICATION_BACKENDS字段即可
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username)|Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


# 创建数据要继承CreateModelMixin
class SmsVerifyCodeViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = SmsSerializer

    def generate_code(self):
        """
        生成随机验证码
        :return: 
        """
        seeds = '1234567890'
        random_str = []
        for i in range(4):
            random_str += choice(seeds) # 随机选择器在种子中选择一个字符
        return ''.join(random_str)


    # 重写CreateModelMixin的create函数
    def create(self, request, *args, **kwargs):
        # 获取serializer
        serializer = self.get_serializer(data=request.data)
        # 验证serializer的数据
        serializer.is_valid(raise_exception=True)

        # 验证通过的数据保存在validated_data字典中
        mobile = serializer.validated_data['mobile']

        # 获得验证码
        code = self.generate_code()

        # 初始化验证码发送工具
        yunpian = YunPian(APIKEY)

        # 发送验证码
        sms_re = yunpian.send_sms(code=code, mobile=mobile)

        # 验证码发送失败
        if sms_re['code'] != 0:
            return Response({
                'mobile':sms_re['msg']
            },status=status.HTTP_400_BAD_REQUEST) # Create失败返回400（RESTFUL api的标准）
        # 短信发送成功（返回的字典中code=0）
        else:
            vcode = VerifyCode(code=code, mobile=mobile)
            vcode.save()
            return Response({
                'mobile':mobile
            },status=status.HTTP_201_CREATED)  # Create成功返回201（RESTFUL api的标准）


class UserViewset(mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    用户相关操作
    """
    serializer_class = UserRegSerializer
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    # 动态使用序列化器
    # 原因：注册时需要的信息较少，获取个人详细信息时需要的信息较多
    def get_serializer_class(self):
        """
        :return: Serializer的类
        """
        # 获得个人资料时使用详细信息序列化
        if self.action == 'retrieve':
            return UserDetailSerializer
        # 注册用户时使用注册信息序列化
        elif self.action == 'create':
            return UserRegSerializer
        # 其他情况下使用详细信息序列化
        return UserDetailSerializer

    # 动态添加权限
    # 原因：不同的操作需要的权限不同
    def get_permissions(self):
        """
        :return: Permission的实例
        """
        # 获得个人资料时需要认证获取权限
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        # 注册用户时无需权限
        elif self.action == 'create':
            return []
        # 其他情况下不需要权限
        return []

    # 重写get_object，访问 users/id 时无论id是什么都返回当前user
    # retrieve和delete需要
    def get_object(self):
        return self.request.user

    # CreateModelMixin自带的create已经可以满足大部分model在serializer后保存的要求，并返回保存后的数据
    # 但是在此处我们需要在返回时添加自己的数据，因此重写create
    # 返回的数据中不会包含serializer中write_only的数据
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 获得user
        user = self.perform_create(serializer)

        # 用户注册完成后自动登陆
        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict['token'] = jwt_encode_handler(payload)
        re_dict['name'] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    # 重置perform_create，返回user
    def perform_create(self, serializer):
        return serializer.save()