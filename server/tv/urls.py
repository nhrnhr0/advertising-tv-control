

from django.urls import path
from .views import view_tv_api

    
urlpatterns = [
    path('api/<int:id>/', view_tv_api, name='view_tv'),
    
]