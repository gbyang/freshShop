from django_filters import rest_framework as filters
from django.db.models import Q

from .models import Goods


# 自定义django-filter所使用的过滤器，进行指定字段指定匹配方式的过滤
class GoodsListFilter(filters.FilterSet):
    """
    自定义字段过滤规则
    """
    # 相当于shop_price__gte
    pricemin = filters.NumberFilter(name='shop_price',lookup_expr='gte',help_text='最低价格')
    # 相当于shop_price__lte
    pricemax = filters.NumberFilter(name='shop_price',lookup_expr='lte')
    # 相当于name__icontains
    name = filters.CharFilter(name='name',lookup_expr='icontains')
    # 如果不写lookup_expr，则条件为 =

    # 自定义过滤字段，不必加在fields中，要自定义过滤方法
    top_category = filters.NumberFilter(method='top_category_filter')
    # 自定义过滤方法
    # 参数（固定）：self, queryset(数据集合), name(参数名), value(传过来的值)
    # 返回：过滤后的queryset
    def top_category_filter(self, queryset, name, value):
        return queryset.filter(Q(category_id=value)|Q(category__parent_category_id=value)|Q(category__parent_category__parent_category_id=value))

    class Meta:
        model = Goods  # 绑定model
        fields = ['pricemin','pricemax','name', 'is_hot','is_new']  # 添加可过滤字段