
from django.shortcuts import render, redirect
from tv.models import AdvertisingAgency
def dashboard_adv_agency_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    if request.method == 'POST':
        agency = AdvertisingAgency()
        agency.name = request.POST.get('name')
        agency.save()
    agencies = AdvertisingAgency.objects.all()
    return render(request, 'dashboard/adv_agency.html', {
        'all_agencies': agencies,
    })
    
def adv_agency_detail_view(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    agency = AdvertisingAgency.objects.get(id=id)
    return render(request, 'dashboard/adv_agency_detail.html', {
        'agency': agency,
    })
    
def adv_agency_detail_edit(request, id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('/admin/login/?next=' + request.path)
    agency = AdvertisingAgency.objects.get(id=id)
    if request.method == 'POST':
        # name,address,geojson,phone,email,contact_name,contact_phone,logo
        agency.name = request.POST.get('name')
        address = request.POST.get('address')
        if address:
            agency.address = address
        geojson = request.POST.get('geojson')
        if geojson:
            agency.geojson = geojson
        phone = request.POST.get('phone')
        if phone:
            agency.phone = phone
        email = request.POST.get('email')
        if email:
            agency.email = email
        contact_name = request.POST.get('contact_name')
        if contact_name:
            agency.contact_name = contact_name
        contact_phone = request.POST.get('contact_phone')
        if contact_phone:
            agency.contact_phone = contact_phone
        logo = request.FILES.get('logo')
        if logo:
            agency.logo = logo

        
        agency.save()
        return redirect('dashboard_adv_agency_detail', id=id)