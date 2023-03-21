

from django.urls import path
from .views import main_dashboard_view
from .views import dashboard_publishers_view,publishers_add_view, publishers_detail, dashboard_publishers_detail_add_broadcast,publishers_detail_edit
from .views import dashboard_tvs_view, tvs_action,tvs_add_view,tvs_detail,tvs_detail_edit,dashboard_publishers_broadcasts_api,tvs_detail_add_broadcast,tvs_detail_change_left_plays,tvs_detail_delete_broadcast_in_tv
from .views_adv_agency import dashboard_adv_agency_view,adv_agency_detail_view,adv_agency_detail_edit
urlpatterns = [
    
    path('', main_dashboard_view, name='main_dashboard_view'),
    
    path('publishers/', dashboard_publishers_view, name='dashboard_publishers_view'),
    path('publishers/add/', publishers_add_view, name='dashboard_publishers_add_view'),
    path('publishers/<int:id>/', publishers_detail, name='dashboard_publishers_detail'),
    path('publishers/<int:id>/edit/', publishers_detail_edit, name='dashboard_publishers_detail_edit'),
    path('publishers/<int:id>/broadcasts/add/', dashboard_publishers_detail_add_broadcast, name='dashboard_publishers_detail_add_broadcast'),
    path('publishers/<str:id>/broadcasts/', dashboard_publishers_broadcasts_api.as_view(), name='dashboard_publishers_broadcasts_api'),
    
    path('tvs/', dashboard_tvs_view, name='dashboard_tvs_view'),
    path('tvs/add/', tvs_add_view, name='dashboard_tvs_add_view'),
    path('tvs/<int:id>/', tvs_detail, name='dashboard_tvs_detail'),
    path('tvs/<int:id>/add_broadcast/', tvs_detail_add_broadcast, name='dashboard_tvs_detail_add_broadcast'),
    path('tvs/<int:id>/change_left_plays/', tvs_detail_change_left_plays, name='dashboard_tvs_detail_change_left_plays'),
    path('tvs/<int:tv_id>/delete_broadcast_in_tv/<int:broadcast_in_tv_id>/', tvs_detail_delete_broadcast_in_tv, name='dashboard_tvs_detail_delete_broadcast_in_tv'),
    path('tvs/<int:id>/edit/', tvs_detail_edit, name='dashboard_tvs_detail_edit'),
    path('tvs-action', tvs_action, name='tvs_action'),
    
    path('advertising-agency/', dashboard_adv_agency_view, name='dashboard_adv_agency_view'),
    path('advertising-agency/add/', dashboard_adv_agency_view, name='dashboard_adv_agency_add_view'),
    path('advertising-agency/<int:id>/', adv_agency_detail_view, name='dashboard_adv_agency_detail'),
    path('advertising-agency/<int:id>/edit/', adv_agency_detail_edit, name='dashboard_adv_agency_detail_edit'),
    
    
]