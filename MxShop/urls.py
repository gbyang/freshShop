"""MxShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from MxShop.settings import MEDIA_ROOT
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework import routers
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token

import xadmin

from goods import views as good_views
from users import views as users_views
from useroperation import views as userop_views
from trade import views as tarde_views

# 使用router+ViewSet添加url路径
# 当ViewSet继承了ListModelMixin，会自动绑定 example.com/goods/ 到list
# 当ViewSet继承了RetrieveModelMixin，会自动绑定 example.com/goods/(?P<pk>[^/.]+)/ 到retrieve
# 当ViewSet继承了DestoryModelMixin，会自动绑定 example.com/goods/(?P<pk>[^/.]+)/ 到destory
router = routers.DefaultRouter() # 初始化router
router.register(r'goods', good_views.GoodsListViewSet, base_name='goods')  # 绑定url与ViewSet
router.register(r'categories', good_views.CategoryViewSet, base_name='categories')  # 绑定url与ViewSet
router.register(r'codes', users_views.SmsVerifyCodeViewset, base_name='codes')  # 绑定url与ViewSet
router.register(r'users', users_views.UserViewset, base_name='users')  # 绑定url与ViewSet
router.register(r'userfavs', userop_views.UserFavViewset, base_name='userfavs')
router.register(r'messages', userop_views.MessagesViewset, base_name='messages')
router.register(r'address', userop_views.AddressViewset, base_name='address')
router.register(r'shopcarts', tarde_views.ShoppingCartViewset, base_name='shopcarts')
router.register(r'orders', tarde_views.OrderViewset, base_name='orders')
router.register(r'banners', good_views.BannerViewset, base_name='banners')
router.register(r'indexgoods', good_views.IndexGoodsViewset, base_name='indexgoods')

from trade.views import AlipayView
from django.views.generic import TemplateView
urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    # 在api页面出现登陆按钮
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^docs/',include_docs_urls(title='慕学生鲜')),
    url(r'^media/(?P<path>.*)$',serve,{"document_root":MEDIA_ROOT}),

    # rest framework自带的Token认证。post提交json格式的username和password，会返回该用户的token
    # 若用户是第一次登陆，会自动创建token
    # 验证token，在header中加入 Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
    # 必须添加以下设置才能验证token
    # REST_FRAMEWORK = {
    #     'DEFAULT_AUTHENTICATION_CLASSES': (
    #         'rest_framework.authentication.TokenAuthentication'
    #     )
    # }
    # rest framework自带的Token认证存在两个问题，1.token没有过期时间 2.若是分布式服务器，还得将表同步到另一台服务器
    url(r'^api-token-auth/', views.obtain_auth_token),

    # djangorestframework-jwt包中的json web token认证解决了token认证存在的问题
    # 验证token，在header中加入 Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImdieWFuZyIsImV4cCI6MTUxNDk3MTQ5NiwiZW1haWwiOiI0NjU0MTM5NDdAcXEuY29tIn0.rkyTGgLPgQHShZJbaQTkF5pUMKZu8KFhvRBd68bJBMM
    # 必须添加以下设置才能验证token
    # REST_FRAMEWORK = {
    #     'DEFAULT_AUTHENTICATION_CLASSES': (
    #         'rest_framework_jwt.authentication.JSONWebTokenAuthentication'
    #     )
    # }
    url(r'^login/$', obtain_jwt_token), # 加$，避免与第三方登录url产生冲突

    url(r'^', include(router.urls)),

    url(r'^alipay/return/', AlipayView.as_view(), name='alipay'),

    url(r'^index/',TemplateView.as_view(template_name='index.html'),name='index'),

    # 第三方登录
    url('', include('social_django.urls', namespace='social')),
]
