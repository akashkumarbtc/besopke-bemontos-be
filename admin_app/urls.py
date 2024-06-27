from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import upload_excel_file, LoginView, PODViewSet

router = DefaultRouter()
router.register(r'pods', PODViewSet)

urlpatterns = [
    path('upload/', upload_excel_file, name='upload_excel_file'),
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]
