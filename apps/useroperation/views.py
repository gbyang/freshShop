from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication

from .models import UserFav,UserLeavingMessage,UserAddress
from .serializers import UserFavSerializer,UserFavDetialSerializer,LeavingMessageSerializer,AddressSerializer
from utils.permissions import IsOwnerOrReadOnly


# CreateModelMixin：POST UserFavSerializer验证通过后自动使用fields的字段创建新记录
# ListModelMixin: GET 访问url可直接获得所有收藏记录
# DestroyModelMixin: DELETE url/id 可直接删除相应记录(id由lookup_field指定)
# RetrieveModelMixin: GET url/id 可查看相应记录(id由lookup_field指定)
class UserFavViewset(mixins.CreateModelMixin,mixins.DestroyModelMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
    用户收藏
    """
    queryset = UserFav.objects.all()
    serializer_class = UserFavSerializer

    # lookup_field是retrieve一条记录时使用的字段
    # 默认为model的id
    # 设置为UserFav中的字段goods_id（外键在数据表中表示为xxx_id），这样delete时可以直接通过返回的数据中goods对应的id进行删除（一个goods只对应一条记录）
    lookup_field = 'goods_id'

    # viewset权限认证
    # IsAuthenticated 代表登陆后才具有操作权限
    # IsOwnerOrReadOnly 只能操作当前用户的相关记录
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    # 在View中单独配置认证，避免在setting中配置全局认证
    # JSONWebTokenAuthentication 需要添加header进行认证，html中测试GET方法时比较麻烦
    # SessionAuthentication 添加Session认证，即可通过获取cookie中的sessionid进行验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    # 动态使用序列化器
    # 原因：添加收藏时需要的信息较少，获取收藏的详细信息时需要的信息较多
    def get_serializer_class(self):
        """
        :return: Serializer的类
        """
        # 获得个人资料时使用详细信息序列化
        if self.action == 'list':
            return UserFavDetialSerializer
        # 注册用户时使用注册信息序列化
        elif self.action == 'create':
            return UserFavSerializer
        # 其他情况下使用详细信息序列化
        return UserFavDetialSerializer

    # 重载get_queryset，只返回当前用户的queryset
    def get_queryset(self):
        # 测试sentry
        # a = {}
        # print(a['b'])
        return UserFav.objects.filter(user=self.request.user)

    # 重载perform_create，在添加收藏记录时为商品的收藏数+1
    # 可用信号量signal实现
    def perform_create(self, serializer):
        # 添加以下代码
        instance = serializer.save()
        goods = instance.goods
        goods.fav_num += 1
        goods.save()

    # 重载perform_destroy，在删除收藏记录时为商品的收藏数-1
    def perform_destroy(self, instance):
        # 添加以下代码
        goods = instance.goods
        goods.fav_num -= 1
        goods.save()
        instance.delete()



class MessagesViewset(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    """
    list:
        展示用户所有留言
    create:
        创建留言
    delete:
        删除留言
    """
    serializer_class = LeavingMessageSerializer
    queryset = UserLeavingMessage.objects.all()

    # viewset权限认证
    # IsAuthenticated 代表登陆后才具有操作权限
    # IsOwnerOrReadOnly 只能操作当前用户的相关记录
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    # 在View中单独配置认证，避免在setting中配置全局认证
    # JSONWebTokenAuthentication 需要添加header进行认证，html中测试GET方法时比较麻烦
    # SessionAuthentication 添加Session认证，即可通过获取cookie中的sessionid进行验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    # 只返回当前用户的留言
    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)


# ModelViewSet继承了
#             mixins.CreateModelMixin,
#             mixins.RetrieveModelMixin,
#             mixins.UpdateModelMixin,
#             mixins.DestroyModelMixin,
#             mixins.ListModelMixin,
class AddressViewset(viewsets.ModelViewSet):
    """
    收货地址管理
    list:
        获取收货地址
    create:
        创建收货地址
    update:
        更新收货地址
    delete:
        删除收货地址
    """
    serializer_class = AddressSerializer
    queryset = UserAddress.objects.all()

    # viewset权限认证
    # IsAuthenticated 代表登陆后才具有操作权限
    # IsOwnerOrReadOnly 只能操作当前用户的相关记录
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    # 在View中单独配置认证，避免在setting中配置全局认证
    # JSONWebTokenAuthentication 需要添加header进行认证，html中测试GET方法时比较麻烦
    # SessionAuthentication 添加Session认证，即可通过获取cookie中的sessionid进行验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    # 只返回当前用户的收货地址
    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)
