from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls_api')),
    path('auth/', include('api.urls_auth'))
]
