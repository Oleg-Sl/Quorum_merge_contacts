from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('mergecontacts/admin/', admin.site.urls),
    path('mergecontacts/api/v1/', include('api_v1.urls', namespace='api_v1')),
]

