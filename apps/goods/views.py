from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.authentication import TokenAuthentication
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.throttling import AnonRateThrottle,UserRateThrottle

from .serializers import GoodsSerializer,CategorySerializer,BannerSerializer,IndexGoodsSerializer
from .models import Goods,GoodsCategory,Banner
from .filter import GoodsListFilter


# 继承PageNumberPagination对象即可自定义分页器
class GoodsPagination(PageNumberPagination):
    # 默认每页数据量
    page_size = 12
    # 最大每页数据量
    max_page_size = 15
    # 每页数据量参数名称（即：http://localhost/?page_size=30 这样每页数据量就会变成30，超过max_page_size还是只会返回max_page_size）
    page_size_query_param = 'page_size'
    # 页码参数名称（即：http://localhost/?gotopage=2  跳转到第2页）
    page_query_param = 'page'


# 继承APIView，也是rest-framework最简单的View
# rest-framwork的View与django的View返回Json数据的区别：
# rest-framwork返回的数据可以通过功能更丰富的html进行浏览，也可以选择只查看json数据
# 普通view只能查看json数据
# class GoodsListView(APIView):
#     """
#     获取所有商品
#     """
#     def get(self,request,format=None):
#         goods = Goods.objects.all()[:10]
#         # 获得goods的json序列化对象（在传入queryset时，需要设置many=True）
#         # 这种序列化方法比django的序列化方法好在image自动加上了MEDIA_URL的前缀
#         goods_serializer = GoodsSerializer(goods, many=True)
#         # 返回goods的序列化对象的json格式的data
#         return Response(goods_serializer.data)

# ListAPIView【继承了 mixins.ListModelMixin,generics.GenericAPIView（继承APIView），同时自动重写了get方法，get方法中调用了list方法】
# 这与将GoodsListView【继承 mixins.ListModelMixin,generics.GenericAPIView，自己手动重写get方法，get方法中调用list方法】效果一致
# 但是减少了许多代码的书写，generics中有许多这样的高度包装View（都是通过GenericAPIView与各种mixin组合而成）
# class GoodsListView(generics.ListAPIView):
#     """
#     获取所有商品
#     """
#     queryset = Goods.objects.all() # List的queryset数据
#     serializer_class = GoodsSerializer  # 对应的serializer
#     pagination_class = GoodsPagination  # 对应的分页器


# viewsets.GenericViewSet【继承了 ViewSetMixin,generics.GenericAPIView，同时重写了as_view方法，在request中加入了action】
# 相比较上面的方法，少了能返回json的list方法，因此还要继承 mixins.ListModelMixin
# 但不用手动重写get方法，可以在as_view方法中手动绑定get方法到list方法，或者使用router自动绑定get方法到list方法（看urls.py）
# viewsets中也有许多通过GenericAPIView与各种mixin组合而成的ViewSet
# ViewSet>GenericAPIView>APIView>View
# --------
# CacheResponseMixin会对retrieve和list请求返回的数据进行缓存，缓存时间可在settings中设置，放在第一个继承
class GoodsListViewSet(CacheResponseMixin, mixins.ListModelMixin,mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    商品列表，分页，搜索，获取，排序
    """
    # 限速类别（settings中也可以设置，这样设置是局部，settings设置是全局）
    throttle_classes = (AnonRateThrottle,UserRateThrottle)

    queryset = Goods.objects.all() # List的queryset数据
    serializer_class = GoodsSerializer  # 对应的serializer
    pagination_class = GoodsPagination  # 对应的分页器

    # **** 在setting中设置TokenAuthentication的话会进行全局认证，所以只在需要登陆的view中设置TokenAuthentication
    # authentication_classes = (TokenAuthentication,)

    # DjangoFilterBackend： django-filter提供的Backend，可针对某一字段进行过滤（可设置价格区间）
    # SearchFilter: django-rest-framework提供的Backend，可进行多字段搜索
    # OrderingFilter: django-rest-framework提供的Backend，可根据某个字段排序
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter)  #设置过滤器后端，可设置多个

    # filter_fields = ('name', 'shop_price')  # DjangoFilterBackend对应的过滤字段（过滤条件单一，都是=）
    filter_class = GoodsListFilter  # DjangoFilterBackend对应的Filter类（可自定义过滤条件，即__后面的字段）

    search_fields = ['name','goods_brief','goods_desc'] # SearchFilter对应的搜索字段，可在前面加上（^=$@）
                                                        # ^ 以关键词开头，= 完全匹配关键词

    ordering_fields = ['sold_num','shop_price']  # OrderingFilter对应的排序字段

    # 简单的过滤可以通过get_queryset方法来进行
    # def get_queryset(self):
    #     # 获取url中的min参数（url中的参数会自动被drf包装为request.query_params字典）
    #     price_min = self.request.query_params.get('min',0)
    #     return self.queryset.filter(shop_price__gt=price_min)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # 重载retrieve方法，加入下面两行代码
        # 实现当用户访问商品时点击数+1
        instance.click_num += 1
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# mixins.RetrieveModelMixin 实现了retrieve方法，继承RetrieveModelMixin后
# router会自动为对应的url添加(?P<pk>[^/.]+)匹配模式，不必调整urls
# 例：example.com/goods     获取所有食物（继承ListModelMixin）
#    example.com/goods/22  获取id为22的食物
#                         （继承RetrieveModelMixin,即使不继承ListModelMixin也能访问，
#                           只要设置了router.register(r'goods',CategoryViewSet)）
class CategoryViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
    list:
        展示商品分类
    """
    queryset = GoodsCategory.objects.filter(category_type=1) # 获取一级分类
    serializer_class = CategorySerializer  # 二级分类和三级分类由Serializer进行序列化


class BannerViewset(mixins.ListModelMixin,viewsets.GenericViewSet):
    """
    获取轮播图列表
    """
    queryset = Banner.objects.all().order_by('index')
    serializer_class = BannerSerializer


class IndexGoodsViewset(mixins.ListModelMixin,viewsets.GenericViewSet):
    """
    获取首页商品
    """
    serializer_class = IndexGoodsSerializer
    queryset = GoodsCategory.objects.filter(is_tab=True)