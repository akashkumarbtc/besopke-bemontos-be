from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_app/', include('admin_app.urls')),
    path('pod_tracker_app/', include('pod_tracker_app.urls')),
]
