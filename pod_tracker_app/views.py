# views.py
from rest_framework import generics
from admin_app.models import POD
from pod_tracker_app.serializers import PODSerializer


class PODDetailAPIView(generics.ListAPIView):
    serializer_class = PODSerializer

    def get_queryset(self):
        pod_number = self.kwargs['pod_number']
        queryset = POD.objects.filter(pod_number=pod_number)
        return queryset
