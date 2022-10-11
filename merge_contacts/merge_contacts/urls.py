from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('merge_contacts_2/admin/', admin.site.urls),
    path('merge_contacts_2/api/v1/', include('api_v1.urls', namespace='api_v1')),
]

