# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('pod/<str:pod_number>/',
         views.PODDetailAPIView.as_view(), name='pod-detail'),
]
