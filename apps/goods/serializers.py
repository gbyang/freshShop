from rest_framework import serializers
from django.db.models import Q

from .models import Goods,GoodsCategory,GoodsImage,Banner,IndexAd,GoodsCategoryBrand


# **********Serializer的作用是将数据库中的数据转换成json格式*******
class CategorySerializer3(serializers.ModelSerializer):
    """
    三级Category
    """
    class Meta:
        model = GoodsCategory
        fields = "__all__"  # 接收所有字段


class CategorySerializer2(serializers.ModelSerializer):
    """
    二级Category
    """
    sub_cat = CategorySerializer3(many=True)
    class Meta:
        model = GoodsCategory
        fields = "__all__"  # 接收所有字段


class CategorySerializer(serializers.ModelSerializer):
    """
    一级Category
    """
    # 关联字段数据的添加【即反向查询】，related_name作为字段名，用外键的ModelSerializer实例化
    # many=True表示该字段关联多条数据【不加会报错】
    # 添加后，返回的json数据会增加sub_cat字段
    sub_cat = CategorySerializer2(many=True)
    class Meta:
        model = GoodsCategory
        fields = "__all__"  # 接收所有字段


class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ('image',)


# serializer类似于forms，不过是把数据序列化为json格式
class GoodsSerializer(serializers.ModelSerializer):
    # """
    # 继承serializers.Serializer时：
    # """
    # name = serializers.CharField(required=True,max_length=100)
    # click_num = serializers.IntegerField(default=0)
    # goods_front_image = serializers.ImageField()


    # 继承ModelSerializer时（比上面的方法简单）：
    # 使用CategorySerializer序列化的json数据覆盖原来的category外键字段，否则外键字段只会显示id
    category = CategorySerializer3()
    # 添加反向查询的image字段（注意many=True）
    images = GoodsImageSerializer(many=True)
    class Meta:
        model = Goods
        fields = '__all__' # __all__表示所有字段，fields也可以是数组或元组指定某些字段，跟form一样


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'


class BrandsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = "__all__"


class IndexGoodsSerializer(serializers.ModelSerializer):
    goods = serializers.SerializerMethodField()
    sub_cat = CategorySerializer2(many=True)
    brands = BrandsSerializer(many=True)
    ad_goods = serializers.SerializerMethodField()

    # 动态生成ad_goods字段
    # 因为只要返回IndexAd的goods数据，category数据不需要返回，所以使用get方法获取当前id对应的goods数据
    def get_ad_goods(self, obj):
        goods_json = {}
        ad_goods = IndexAd.objects.filter(category_id=obj.id)
        if ad_goods:
            good_ins = ad_goods[0].goods
            goods_json = GoodsSerializer(good_ins,many=False,context={'request':self.context['request']}).data
        return goods_json

    # 动态生成goods字段
    def get_goods(self, obj):
        goods = Goods.objects.filter(Q(category_id=obj.id)|Q(category__parent_category_id=obj.id)|Q(category__parent_category__parent_category_id=obj.id))
        # context={'request':self.context['request']} 会自动将域名加到image的地址前面
        # 只有在serializer中调用serializer才需要传入这个参数
        serializer = GoodsSerializer(goods, many=True, context={'request':self.context['request']})
        return serializer.data  # 返回序列化器中的data（json格式）

    class Meta:
        model = GoodsCategory
        fields = '__all__'