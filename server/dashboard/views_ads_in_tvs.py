from django.shortcuts import render, redirect

from tv.models import BetweenDateSchedule, ManualControlSchedule, PlaysCoutdownSchedule
from .ads_serialisers import BroadcastInTvsDashboardSerializers,BroadcastInTvsDetailDashboardSerializers, DashboardTvsSerializer, ScheduleSerializer
from tv.models import BroadcastInTvs
from tv.models import Tv
def dashboard_ads_in_tvs_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    if request.method == "POST":
        pass
    all_broadcasts_in_tvs = BroadcastInTvs.objects.all()
    serialiser = BroadcastInTvsDashboardSerializers(all_broadcasts_in_tvs, many=True)
    context = {
        'broadcasts_in_tvs': serialiser.data
    }
    return render(request, 'dashboard/ads_in_tvs.html', context)

def dashboard_ads_in_tvs_add_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import AllowAny
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
import json
import datetime

from rest_framework.decorators import api_view, permission_classes

class AdsInTvsListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = BroadcastInTvs.objects.all()
    serializer_class = BroadcastInTvsDashboardSerializers
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['broadcast__name','activeSchedule__content_type','broadcast__media_type','tvs__name','tvs__id']
    search_fields = ['broadcast__name','tvs__name','broadcast__media_type',]


@api_view(['GET', 'POST',])
@permission_classes([IsAdminUser,])
def adsInTvsDetailView(request, id): 
    if request.method == 'GET':
        broadcast_in_tvs = BroadcastInTvs.objects.get(id=id)
        serialiser = BroadcastInTvsDetailDashboardSerializers(broadcast_in_tvs)
        return Response(serialiser.data)
    elif request.method == 'POST':
        broadcast_in_tvs = BroadcastInTvs.objects.get(id=id)
        serialiser = BroadcastInTvsDetailDashboardSerializers(broadcast_in_tvs, data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data)
        return Response(serialiser.errors)
    
@api_view(["GET",])
@permission_classes([IsAdminUser])
def dashboard_all_tvs(request):
    
    tvs = Tv.objects.all().prefetch_related('opening_hours')
    serializer = DashboardTvsSerializer(tvs, many=True)
    return Response(serializer.data)


@api_view(["POST",])
@permission_classes([IsAdminUser])
def dashboard_update_tvs_list_to_brod_in_tvs(request, id):
    broadcast_in_tvs = BroadcastInTvs.objects.get(id=id)
    tvs = request.data.get('tvs')
    # tvs = '[{"id":1,"name":"tv1"},{"id":2,"name":"tv2"}]'
    tvs = json.loads(tvs)
    tvs_ids = [tv['id'] for tv in tvs]
    broadcast_in_tvs.tvs.set(tvs_ids)
    broadcast_in_tvs.save()
    return Response({'message': 'success'})


def try_parsing_date(text):
    for fmt in ("%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')
@api_view(["POST",])
@permission_classes([IsAdminUser])
def dashboard_update_active_schedule_to_brod_in_tvs(request, id):
    broadcast_in_tvs = BroadcastInTvs.objects.get(id=id)
    new_schedule = request.data.get('schedule')
    new_schedule = json.loads(new_schedule)
    if broadcast_in_tvs.activeSchedule and new_schedule.get('content_type') == broadcast_in_tvs.activeSchedule.content_type:
        # only update the values
        # plays_countdown
        # between_dates
        # manual_control
        if broadcast_in_tvs.activeSchedule.content_type == 'between_dates':
            s = new_schedule.get('content').get('start_date')
            e = new_schedule.get('content').get('end_date')
            start = try_parsing_date(s)
            end = try_parsing_date(e)
            
            broadcast_in_tvs.activeSchedule.start_date = start
            broadcast_in_tvs.activeSchedule.end_date =end
        elif broadcast_in_tvs.activeSchedule.content_type == 'plays_countdown':
            broadcast_in_tvs.activeSchedule.plays_left = broadcast_in_tvs.activeSchedule.plays_left + new_schedule.get('change_plays_left', 0)
        elif broadcast_in_tvs.activeSchedule.content_type == 'manual_control':
            broadcast_in_tvs.activeSchedule.is_active_bool = new_schedule.get('is_active', False)
        broadcast_in_tvs.activeSchedule.save()
    else:
        # delete the old schedule
        try: 
            broadcast_in_tvs.activeSchedule.delete()
        except:
            pass
        # create a new schedule
        if new_schedule.get('content_type') == 'between_dates':
            s = new_schedule.get('content').get('start_date')
            e = new_schedule.get('content').get('end_date')
            start = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%MZ")
            end = datetime.datetime.strptime(e, "%Y-%m-%dT%H:%MZ")
            broadcast_in_tvs.activeSchedule = BetweenDateSchedule.objects.create(
                start_date=start,
                end_date=end,
                content_type='between_dates',
            )
        elif new_schedule.get('content_type') == 'plays_countdown':
            broadcast_in_tvs.activeSchedule = PlaysCoutdownSchedule.objects.create(
                plays_left=new_schedule.get('change_plays_left',0),
                content_type='plays_countdown',
            )
        elif new_schedule.get('content_type') == 'manual_control':
            broadcast_in_tvs.activeSchedule = ManualControlSchedule.objects.create(
                is_active_bool=new_schedule.get('is_active', False),
                content_type='manual_control',
            )
            
        broadcast_in_tvs.save()
    ser = ScheduleSerializer(broadcast_in_tvs.activeSchedule)
    data = ser.data
    return Response(data)