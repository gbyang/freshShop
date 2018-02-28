from django.conf.urls import url,include
from rest_framework import routers

from . import views_base
from . import views

# 使用router+ViewSet添加url路径
router = routers.DefaultRouter() # 初始化router
router.register(r'', views.GoodsListViewSet)  # 绑定url与ViewSet
router.register(r'categories', views.CategoryViewSet)  # 绑定url与ViewSet


# 不使用router进行url绑定，将http方法绑定到ViewSet中的函数
# goods_list = views.GoodsListViewSet.as_view({
#     'get':'list'
# })


app_name = 'goods'
urlpatterns = [
    # url(r'^$',goods_list,name='goods_list'), # 不使用router，直接用ViewSet传参调用完毕后返回的函数作为view
    url(r'^',include(router.urls),name='goods_list'), # include router.urls
]