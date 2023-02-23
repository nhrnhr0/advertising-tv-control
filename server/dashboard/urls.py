

from django.urls import path
from .views import main_dashboard_view
from .views import dashboard_publishers_view,publishers_add_view, publishers_detail, dashboard_publishers_detail_add_broadcast,publishers_detail_edit
from .views import dashboard_tvs_view, tvs_add_view,tvs_detail,tvs_detail_edit,dashboard_publishers_broadcasts_api,tvs_detail_add_broadcast,tvs_detail_change_left_plays

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
    path('tvs/<int:id>/edit/', tvs_detail_edit, name='dashboard_tvs_detail_edit'),
]