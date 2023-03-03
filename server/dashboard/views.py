from django.shortcuts import render, redirect
# Create your views here.
from core.models import Publisher
from dashboard.serializers import PublisherAssetsSerializer
from tv.models import AdvertisingAgency
from tv.models import BusinessType
from django.conf import settings
from django.http import JsonResponse
from django.core import serializers
from core.models import Publisher, PublisherType
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
def main_dashboard_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    return render(request, 'dashboard/main_dashboard.html', {})

def dashboard_publishers_view(request):
    
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    all_publishers = Publisher.objects.all()
    context = {
        'all_publishers': all_publishers
    }
    return render(request, 'dashboard/publishers.html', context)

def publishers_add_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    if request.method == 'POST':
        publisher_name = request.POST.get('name')
        publisher = Publisher.objects.create(name=publisher_name)
        publisher.save()
        return redirect('dashboard_publishers_view')
    return render(request, 'dashboard/publishers_add.html', {})


def publishers_detail(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    publisher = Publisher.objects.get(id=id)
    publishers_types = PublisherType.objects.all()
    adv_agencies = AdvertisingAgency.objects.all()
    context = {
        'publisher': publisher,
        'publishers_types': publishers_types,
        'adv_agencies': adv_agencies
    }
    return render(request, 'dashboard/publishers_detail.html', context)


# get the file and the name of the file if exists and save it for the publisher
def publishers_detail_edit(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    publisher = Publisher.objects.get(id=id)
    if request.method == 'POST':
        publisher_name = request.POST.get('name')
        publisher.name = publisher_name
        # about
        # geojson
        # publishers_types
        # logo
        # phone
        # email
        # contact_name
        # contact_phone
        # qr_link
        publisher.about = request.POST.get('about')
        publisher.geojson = request.POST.get('geojson')
        publisher_types = request.POST.getlist('publishersType')
        publisher.publishers_types.clear()
        for publisher_type in publisher_types:
            publisher.publishers_types.add(publisher_type)
        logo = request.FILES.get('logo')
        if logo:
            publisher.logo = logo
        
        address = request.POST.get('address')
        if address:
            publisher.address = address
        
        phone = request.POST.get('phone')
        if phone:
            publisher.phone = phone
        email = request.POST.get('email')
        if email:
            publisher.email = email
        contact_name = request.POST.get('contact_name')
        if contact_name:
            publisher.contact_name = contact_name
        contact_phone = request.POST.get('contact_phone')
        if contact_phone:
            publisher.contact_phone = contact_phone
        
        publisher.qr_link = request.POST.get('qr_link', '')

        adv_agency_id = request.POST.get('adv_agency')
        if adv_agency_id:
            adv_agency = AdvertisingAgency.objects.get(id=adv_agency_id)
            publisher.adv_agency = adv_agency
        else:
            publisher.adv_agency = None
        
        publisher.save()
        return redirect('dashboard_publishers_detail', id=id)
    context = {
        'publisher': publisher
    }
    return render(request, 'dashboard/publishers_detail.html', context)


def dashboard_publishers_detail_add_broadcast(request, id):
    from tv.models import Broadcast
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    publisher = Publisher.objects.get(id=id)
    if request.method == 'POST':
        
        # create and save the broadcast to the publisher
        broadcast_name = request.POST.get('name')
        medias = request.FILES.getlist('media')
        # if not media:
        #     return redirect('dashboard_publishers_detail_edit', id=id)
        # broadcast = Broadcast.objects.create(name=broadcast_name, media=media)
        # broadcast.save()
        # publisher.broadcasts.add(broadcast)
        # publisher.save()
        
        for media in medias:
            if broadcast_name == '':
                bname = media.name
            else:
                if len(medias) == 1:
                    bname = broadcast_name
                else:
                    bname = broadcast_name + '_' + media.name
            broadcast = Broadcast.objects.create(name=bname, media=media)
            broadcast.save()
            publisher.broadcasts.add(broadcast)
            publisher.save()
        return redirect('dashboard_publishers_detail_edit', id=id)
    context = {
        'publisher': publisher
    }
    return render(request, 'dashboard/publishers_detail_add_broadcast.html', context)




# def dashboard_publishers_broadcasts_api(request, id):
#     from tv.models import Broadcast
#     from .serializers import PublisherAssetsSerializer
#     if not request.user.is_authenticated or not request.user.is_superuser:
#           return redirect('/admin/login/?next=' + request.path)
#     if id == 'all':
#         broadcasts = Broadcast.objects.all()
#     else:
#         publisher = Publisher.objects.get(id=int(id))
#         broadcasts = publisher.broadcasts.all()
#     serializer = PublisherAssetsSerializer(broadcasts, many=True)
#     data = serializer.data
#     return JsonResponse(data, safe=False)
class dashboard_publishers_broadcasts_api(APIView, PageNumberPagination):
    page_size = 10
    max_page_size = 1000
    def get_queryset(self):
        from tv.models import Broadcast
        from .serializers import PublisherAssetsSerializer
        if not self.request.user.is_authenticated or not self.request.user.is_superuser:
            return redirect('login', next=self.request.path)
        if self.kwargs['id'] == 'all':
            broadcasts = Broadcast.objects.all()
        else:
            publisher = Publisher.objects.get(id=int(self.kwargs['id']))
            broadcasts = publisher.broadcasts.all()
            
        if self.request.query_params.get('not_in_tv'):
            from tv.models import Tv
            exclude_tv = Tv.objects.get(id=int(self.request.query_params.get('not_in_tv')))
            broadcasts = broadcasts.exclude(tv=exclude_tv)
        if self.request.query_params.get('page_size'):
            self.page_size = int(self.request.query_params.get('page_size'))
        return broadcasts
    
    def get(self, request, id, format=None):
        broadcasts = self.paginate_queryset(self.get_queryset(), request)
        serializer = PublisherAssetsSerializer(broadcasts, many=True)
        data = serializer.data
        return self.get_paginated_response(data)


def dashboard_tvs_view(request):
    from tv.models import Tv
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    all_tvs = Tv.objects.all()
    context = {
        'all_tvs': all_tvs
    }
    return render(request, 'dashboard/tvs.html', context)

def tvs_add_view(request):
    from tv.models import Tv
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    if request.method == 'POST':
        tv_name = request.POST.get('name')
        if not tv_name:
            return redirect('dashboard_tvs_view')
        tv = Tv.objects.create(name=tv_name)
        tv.save()
    return redirect('dashboard_tvs_view')

from django.core.paginator import Paginator

def tvs_detail(request, id):
    from tv.models import Tv
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    tv = Tv.objects.get(id=id)
    page_size = request.GET.get('page_size', settings.DEFAULT_PAGE_SIZE)
    broadcasts = tv.broadcasts.all().order_by('broadcast_in_tv__order')
    publishers = Publisher.objects.all()
    # broadcasts_paginator = Paginator(broadcasts, page_size)
    
    business_types = BusinessType.objects.all()
    context = {
        'tv': tv,
        # 'broadcasts': broadcasts,
        'broadcasts': broadcasts,
        'publishers': publishers,
        # 'paginators_page_obj': broadcasts_paginator.get_page(broadcasts_page_number),
        'business_types': business_types,
    }
    return render(request, 'dashboard/tvs_detail.html', context)

def tvs_detail_add_broadcast(request, id):
    from tv.models import Tv, Broadcast
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    tv = Tv.objects.get(id=id)
    if request.method == 'POST':
        broadcast_id = request.POST.get('broadcast_id')
        broadcast = Broadcast.objects.get(id=broadcast_id)
        plays = request.POST.get('plays_count')
        if not plays:
            plays = 0
        # temp = tv.broadcasts.order_by('-broadcast_in_tv__order').first()
        from django.db.models import Max
        max_order = tv.broadcasts.all().aggregate(Max('broadcast_in_tv__order'))['broadcast_in_tv__order__max']
        if max_order == None:
            max_order = 0
        order = max_order + 10
        tv.broadcasts.add(broadcast, through_defaults={'plays_left': plays, 'active': False, 'order': order})
        tv.save()
        return redirect('dashboard_tvs_detail', id=id)
    return redirect('dashboard_tvs_detail', id=id)

def tvs_detail_change_left_plays(request, id):
    from tv.models import Tv, Broadcast, BroadcastInTv
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    tv = Tv.objects.get(id=id)
    if request.method == 'POST':
        broadcast_in_tv_id = request.POST.get('broadcast_in_tv_id')
        plays = request.POST.get('plays_count')
        if not plays:
            plays = '0'
        broadcast_in_tv_obj = BroadcastInTv.objects.get(id=broadcast_in_tv_id)
        broadcast_in_tv_obj.plays_left = broadcast_in_tv_obj.plays_left + int(plays)
        broadcast_in_tv_obj.save()
        tv.save()
        return redirect('dashboard_tvs_detail', id=id)
    return redirect('dashboard_tvs_detail', id=id)

def tvs_detail_edit(request, id):
    from tv.models import Tv
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    tv = Tv.objects.get(id=id)
    if request.method == 'POST':
        # request.POST: 'qr_link':'https://ms-global.co.il''new_day[]':'1''new_opening_hour[]':'06:00''new_closing_hour[]':'18:00''existing_broadcasts_ids[]':'4''existing_broadcasts_in_tvs_ids[]':'45''broadcast_2_duration':'2''broadcast_2_order':'35''broadcast_3_duration':'20.0''broadcast_3_order':'25''broadcast_11_duration':'10.0''broadcast_11_active':'on''broadcast_11_order':'55''broadcast_4_duration':'20.0''broadcast_4_order':'65''publisher':''
        # saving tv name and basic info
        tv_name = request.POST.get('name')
        tv.name = tv_name
        
        tv.address = request.POST.get('address')
        tv.manual_turn_off = request.POST.get('manual_turn_off', False) == 'on'
        # save business types add/remove
        businessTypeIds = request.POST.getlist('businessType')
        for businessTypeId in businessTypeIds:
            businessType = BusinessType.objects.get(id=businessTypeId)
            if businessType not in tv.buisness_types.all():
                tv.buisness_types.add(businessType)
        for businessType in tv.buisness_types.all():
            if str(businessType.id) not in businessTypeIds:
                tv.buisness_types.remove(businessType)
        
        # logo
        logo = request.FILES.get('logo', None)
        phone = request.POST.get('phone', None)
        email = request.POST.get('email', None)
        contact_name = request.POST.get('contact_name', None)
        contact_phone = request.POST.get('contact_phone' , None)
        if logo:
            tv.logo = logo
        if phone:
            tv.phone = phone
        if email:
            tv.email = email
        if contact_name:
            tv.contact_name = contact_name
        if contact_phone:
            tv.contact_phone = contact_phone
        

        

        new_what_not_to_show = request.POST.get('not_to_show_list',None)
        new_what_to_show = request.POST.get('yes_to_show_list',None)
        
        from tv.models import ContentWithHistory
        if new_what_not_to_show:
            tv.not_to_show_list.add(ContentWithHistory.objects.create(content=new_what_not_to_show,
            content_type=ContentWithHistory.NOT_TO_SHOW
            ))
        if new_what_to_show:
            tv.yes_to_show_list.add(ContentWithHistory.objects.create(content=new_what_to_show,
            content_type=ContentWithHistory.YES_TO_SHOW
            ))
        
        
        
        # save opening hours
        opening_hours_ids = request.POST.getlist('opening_hour_id[]')
        for opening_hours_id in opening_hours_ids:
            opening_hour = request.POST.get('opening_hour_'+opening_hours_id)
            closing_hour = request.POST.get('closing_hour_'+opening_hours_id)
            day = request.POST.get('day_'+opening_hours_id)
            to_delete = request.POST.get('delete_opening_hour_'+opening_hours_id)
            obj = tv.opening_hours.get(id=opening_hours_id)
            if to_delete:
                obj.delete()
            else:
                obj.from_hour = opening_hour
                obj.to_hour = closing_hour
                obj.weekday = day
                obj.save()

        new_opening = request.POST.getlist('new_opening_hour[]')
        new_closing = request.POST.getlist('new_closing_hour[]')
        new_days = request.POST.getlist('new_day[]')
        
        for i in range(len(new_opening)):
            if new_opening[i] and new_closing[i] and new_days[i]:
                tv.opening_hours.create(from_hour=new_opening[i], to_hour=new_closing[i], weekday=new_days[i])
        
        
        # saving table information
        existing_broadcasts_ids = request.POST.getlist('existing_broadcasts_ids[]')
        for existing_b_id in existing_broadcasts_ids:
            duration = request.POST.get('broadcast_'+existing_b_id+'_duration')
            active = request.POST.get('broadcast_'+existing_b_id+'_active')
            order = request.POST.get('broadcast_'+existing_b_id+'_order')
            # existing_btv_id = existing_broadcasts_in_tvs_ids[existing_broadcasts_ids.index(existing_b_id)]
            obj = tv.broadcasts.get(id=existing_b_id)
            broad_in_tv = obj.broadcast_in_tv.first()
            broad_in_tv.duration = float(duration)
            broad_in_tv.active = active == 'on'
            broad_in_tv.order = int(order)
            broad_in_tv.save()
            obj.save()
        tv.save()
    return redirect('dashboard_tvs_detail', id=id)
    # context = {
    #     'tv': tv
    # }
    # return render(request, 'dashboard/tvs_detail.html', context)