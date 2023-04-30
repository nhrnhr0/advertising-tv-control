
"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tv.views import get_publisher_assets_as_tv_demo
from tv.views import save_broadcasts_played
from django.contrib.auth import views as auth_views
from core.views import pi_screenshot_view,telegram_webhook_view
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path("admin/", admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('tv/', include('tv.urls')),
    path('api/broadcasts-played/', save_broadcasts_played, name='save_broadcasts_played'),
    path('dashboard/', include('dashboard.urls')),
    path('pi_screenshot/<str:pi_key>/', pi_screenshot_view, name='pi_screenshot'),
    path('telegram-webhook/', telegram_webhook_view, name='telegram_webhook'),
    path('api/get-publisher-assets-as-tv-demo/<int:id>/', get_publisher_assets_as_tv_demo, name='get_publisher_assets_as_tv_demo'),
]


print('settings: ', settings)
if settings.DEBUG:
    urlpatterns = urlpatterns + \
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + \
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))


