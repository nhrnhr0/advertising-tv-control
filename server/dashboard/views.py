from django.shortcuts import render, redirect
# Create your views here.
from core.models import Publisher
from tv.models import BusinessType

def main_dashboard_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login', next=request.path)
    return render(request, 'dashboard/main_dashboard.html', {})

def dashboard_publishers_view(request):
    
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login', next=request.path)
    all_publishers = Publisher.objects.all()
    context = {
        'all_publishers': all_publishers
    }
    return render(request, 'dashboard/publishers.html', context)

def publishers_add_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login', next=request.path)
    if request.method == 'POST':
        publisher_name = request.POST.get('name')
        publisher = Publisher.objects.create(name=publisher_name)
        publisher.save()
        return redirect('dashboard_publishers_view')
    return render(request, 'dashboard/publishers_add.html', {})


def publishers_detail(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login', next=request.path)
    publisher = Publisher.objects.get(id=id)
    context = {
        'publisher': publisher
    }
    return render(request, 'dashboard/publishers_detail.html', context)


# get the file and the name of the file if exists and save it for the publisher
def publishers_detail_edit(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login', next=request.path)
    publisher = Publisher.objects.get(id=id)
    if request.method == 'POST':
        publisher_name = request.POST.get('name')
        publisher.name = publisher_name
        publisher.save()
        return redirect('dashboard_publishers_detail', id=id)
    context = {
        'publisher': publisher
    }
    return render(request, 'dashboard/publishers_detail.html', context)


def dashboard_publishers_detail_add_broadcast(request, id):
    from tv.models import Broadcast
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login', next=request.path)
    publisher = Publisher.objects.get(id=id)
    if request.method == 'POST':
        
        # create and save the broadcast to the publisher
        broadcast_name = request.POST.get('name')
        media = request.FILES.get('media')
        if not media:
            return redirect('dashboard_publishers_detail_edit', id=id)
        broadcast = Broadcast.objects.create(name=broadcast_name, media=media)
        broadcast.save()
        publisher.broadcasts.add(broadcast)
        publisher.save()
        return redirect('dashboard_publishers_detail_edit', id=id)
    context = {
        'publisher': publisher
    }
    return render(request, 'dashboard/publishers_detail_add_broadcast.html', context)


from django.http import JsonResponse
from django.core import serializers



def dashboard_publishers_broadcasts_api(request, id):
    from tv.models import Broadcast
    from .serializers import PublisherAssetsSerializer
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login', next=request.path)
    if id == 'all':
        broadcasts = Broadcast.objects.all()
    else:
        publisher = Publisher.objects.get(id=int(id))
        broadcasts = publisher.broadcasts.all()
    serializer = PublisherAssetsSerializer(broadcasts, many=True)
    data = serializer.data
    return JsonResponse(data, safe=False)



def dashboard_tvs_view(request):
    from tv.models import Tv
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login', next=request.path)
    all_tvs = Tv.objects.all()
    context = {
        'all_tvs': all_tvs
    }
    return render(request, 'dashboard/tvs.html', context)

def tvs_add_view(request):
    from tv.models import Tv
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login', next=request.path)
    if request.method == 'POST':
        tv_name = request.POST.get('name')
        if not tv_name:
            return redirect('dashboard_tvs_view')
        tv = Tv.objects.create(name=tv_name)
        tv.save()
    return redirect('dashboard_tvs_view')


def tvs_detail(request, id):
    from tv.models import Tv
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login', next=request.path)
    tv = Tv.objects.get(id=id)
    broadcasts = tv.broadcasts.all().order_by('broadcast_in_tv__order')
    publishers = Publisher.objects.all()
    business_types = BusinessType.objects.all()
    context = {
        'tv': tv,
        'broadcasts': broadcasts,
        'publishers': publishers,
        'business_types': business_types
    }
    return render(request, 'dashboard/tvs_detail.html', context)

def tvs_detail_add_broadcast(request, id):
    from tv.models import Tv, Broadcast
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login', next=request.path)
    tv = Tv.objects.get(id=id)
    if request.method == 'POST':
        broadcast_id = request.POST.get('broadcast_id')
        broadcast = Broadcast.objects.get(id=broadcast_id)
        plays = request.POST.get('plays_count')
        if not plays:
            plays = 0
        temp = tv.broadcasts.order_by('-broadcast_in_tv__order').first()
        if temp:
            order = temp.broadcast_in_tv.first().order + 10
        else:
            order = 0
        tv.broadcasts.add(broadcast, through_defaults={'plays_left': plays, 'active': False, 'order': order})
        tv.save()
        return redirect('dashboard_tvs_detail', id=id)
    return redirect('dashboard_tvs_detail', id=id)

def tvs_detail_change_left_plays(request, id):
    from tv.models import Tv, Broadcast, BroadcastInTv
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login', next=request.path)
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
        return redirect('login', next=request.path)
    tv = Tv.objects.get(id=id)
    if request.method == 'POST':
        tv_name = request.POST.get('name')
        tv.name = tv_name
        # get all the 
        # day_XXX opening_hour_XXX closing_hour_XXX from the form and save them to the tv
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
        
        
        # <input type="hidden" name="existing_broadcasts_ids[]" value="{{broadcast.id}}">
        # <input type="number" name="broadcast_{{broadcast.id}}_duration" value="{{broadcast.broadcast_in_tv.first.duration}}">
        # <input type="checkbox" name="broadcast_{{broadcast.id}}_active" {% if broadcast.broadcast_in_tv.first.active %}checked{% endif %}>
        # <input type="number" name="broadcast_{{broadcast.id}}_order" value="{{broadcast.broadcast_in_tv.first.order}}">

        # existing_broadcasts_in_tvs_ids = request.POST.getlist('existing_broadcasts_in_tvs_ids[]')
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