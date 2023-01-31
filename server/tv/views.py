from django.http import JsonResponse
from django.shortcuts import render

from .serializers import TvSerializer
from .models import Tv, Broadcast, BroadcastInTv
# Create your views here.
def tv_view(request, id):
    tv_obj = Tv.objects.get(id=id)
    context = {
        'tv_obj': tv_obj,
    }
    return render(request, 'tv/view_tv.html', context)


def view_tv_api(request, id):
    tv_obj = Tv.objects.get(id=id)
    serializer = TvSerializer(tv_obj)
    info = serializer.data
    return JsonResponse(info, safe=False)
    pass