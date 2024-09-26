# views.py

from rest_framework import generics
from .models import Sensor, SensorData
from .serializers import SensorSerializer, SensorDataSerializer
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404


# List and Create Sensors
class SensorListCreateView(generics.ListCreateAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

# Retrieve, Update, and Delete Sensor (Optional if needed)
class SensorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

# List and Create Sensor Data
class SensorDataListCreateView(generics.ListCreateAPIView):
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer

    def post(self, request):
        # Use DRF's built-in serializer validation
        serializer = SensorDataSerializer(data=request.data)

        if serializer.is_valid():
            # Save the sensor data
            serializer.save()
            return Response({'message': 'Sensor data recorded successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# Retrieve Data for a Specific Sensor
class SensorDataDetailView(generics.RetrieveAPIView):
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer



