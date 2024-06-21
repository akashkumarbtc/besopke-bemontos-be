from django.urls import path
from .views import upload_excel_file, LoginView

urlpatterns = [
    path('upload/', upload_excel_file, name='upload_excel_file'),
    path('login/', LoginView.as_view(), name='login'),
]
