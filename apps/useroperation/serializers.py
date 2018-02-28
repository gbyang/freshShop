from rest_framework import serializers

from .models import UserFav,UserLeavingMessage,UserAddress
from goods.serializers import GoodsSerializer


class UserFavDetialSerializer(serializers.ModelSerializer):
    """
    收藏详情序列化
    """
    # 将goods序列化，返回id及其他信息，delete时就可以带着id过来
    # 配合lookup_field将对应记录删除
    goods = GoodsSerializer()

    class Meta:
        model = UserFav
        fields = ('goods',)


class UserFavSerializer(serializers.ModelSerializer):
    # 覆盖user字段，默认绑定当前user
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserFav
        fields = ('user', 'goods')


class LeavingMessageSerializer(serializers.ModelSerializer):
    """
    用户留言序列化
    """
    # 设置user为当前user
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    # read_only 不用上传，直接返回
    # write_only 不用返回，直接上传
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = UserLeavingMessage
        fields = '__all__'  # fields要返回id才能被delete


class AddressSerializer(serializers.ModelSerializer):
    """
    收货地址序列化
    """

    # 设置user为当前user
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    # read_only 不用上传，直接返回
    # write_only 不用返回，直接上传
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    # todo 各个字段验证
    class Meta:
        model = UserAddress
        fields = '__all__'