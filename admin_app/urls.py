from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import upload_zip_file, LoginView, PODViewSet

router = DefaultRouter()
router.register(r'pods', PODViewSet)

urlpatterns = [
    path('upload/', upload_zip_file, name='upload_zip_file'),
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]
