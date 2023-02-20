
from django.urls import path
from .views import tv_view,view_tv_api
urlpatterns = [
    path('<int:id>/', tv_view, name='view_tv'),
    path('api/<int:id>/', view_tv_api, name='view_tv'),
    
]