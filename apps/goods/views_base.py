from django.views.generic.base import View

from .models import Goods


class GoodsListView(View):
    """
    商品列表
    """
    def get(self, request):
        # 商品列表数组，存放所有商品
        json_list = []
        goods = Goods.objects.all()[:10]

        # ******将商品转换为json数据**************
        # 方法一：逐一转换
        # 优点：基本没有
        # 缺点：代码多，容易写错，不能转imageField，datetime等数据
        # for good in goods:
        #     # 将每个商品信息保存到一个dict
        #     json_dict = {}
        #     json_dict['name'] = good.name
        #     json_dict['category'] = good.category.name
        #     json_dict['market_price'] = good.market_price
        #     # json_dict['add_time'] = good.add_time 报错！无法序列化datetime
        #     # 将商品添加到商品数组中
        #     json_list.append(json_dict)


        # 方法二：model_to_dict方法
        # 优点：代码极为简单，每个字段都会转换成对应名字的json数据
        # 缺点：不能转imageField，datetime等数据
        # from django.forms.models import model_to_dict
        # for good in goods:
        #     json_dict = model_to_dict(good)
        #     json_list.append(json_dict)


        # 方法三：serializers.serialize方法
        # 优点：不必进行for循环，直接传入queryset即可自动将每个数据单独打包，将所有打包好的数据集合成一个数组
        # 缺点：格式较为固定，image路径是绝对路径，缺少前缀主机地址
        import json
        from django.core import serializers
        # 将queryset转换为json数组数据
        json_data = serializers.serialize('json',goods)
        # 将json数据转换为数组
        json_data = json.loads(json_data)

        from django.http import JsonResponse
        # JsonResponse要求传入对象为dict，若为数组，需要设置参数safe=False
        return JsonResponse(json_data, safe=False)