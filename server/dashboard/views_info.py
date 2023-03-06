
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse

from tv.models import playedBroadcast
def info_dashboard_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    return render(request, 'dashboard/info.html', {
    })

# @api_view(['GET',])
def info_played_broadcasts_api(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    # uuid,tv,broadcast,time,uri_key,is_approved
    played_broadcasts = playedBroadcast.objects.filter(is_approved=True).order_by('-time')
    played_broadcasts_values = played_broadcasts.values_list('uuid','tv__id', 'tv__name','broadcast__id', 'broadcast__name','time',)
    played_broadcasts_values_list = list(played_broadcasts_values)
    # return a 2d array of played broadcasts for the info dashboard (first row is the header)
    return JsonResponse([
        ['uuid','tv_id','tv_name','broadcast_id','broadcast_name','time'],
        *played_broadcasts_values_list
    ], safe=False)