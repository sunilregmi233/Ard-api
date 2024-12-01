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
from django.db.models import Max


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


class RecordSensorData(APIView):
    permission_classes = [IsAuthenticated]  # Require authentication

    def post(self, request):
        # Log incoming request data
        print(request.data)  # Check what's coming in
        serializer = SensorDataSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Sensor data recorded successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LatestDataForSensorsView(APIView):
    def get(self, request):
        # Static list of sensor IDs
        sensor_ids = ["JK101", "JK102", "JK103", "JK104", "JK105", 
                      "JK106", "JK107", "JK108", "JK109", "JK110"]

        # Dictionary of sensor coordinates (latitude and longitude)
        sensor_coordinates_dict = {
            "JK101": {"latitude": 26.7345, "longitude": 85.9289},  # Example coordinates for Panchkhal, Kavre
            "JK102": {"latitude": 26.7314, "longitude": 85.9313},  # Kathmandu
            "JK103": {"latitude": 26.7314, "longitude": 85.9279},  # Pokhara, Kaski
            "JK104": {"latitude": 26.7314, "longitude": 85.9249},  # Chitwan
            "JK105": {"latitude": 26.7303, "longitude": 85.9316},  # Lalitpur
            "JK106": {"latitude": 26.7338, "longitude": 85.9205},  # Bhaktapur
            "JK107": {"latitude": 26.7168, "longitude": 85.9201},  # Ramechhap
            "JK108": {"latitude": 26.7360, "longitude": 85.9348},  # Sindhupalchok
            "JK109": {"latitude": 26.7602, "longitude": 83.9431},  # Baglung
            "JK110": {"latitude": 26.7173, "longitude": 85.9225}   # Dhulikhel, Kavre
        }

        # Fetch the latest timestamp for each sensor based on sensor_id
        latest_entries = (
            SensorData.objects.filter(sensor__sensor_id__in=sensor_ids)
            .values("sensor__sensor_id")
            .annotate(latest_timestamp=Max("timestamp"))
        )

        if not latest_entries:
            return Response(
                {"message": "No data found for the provided sensor IDs."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch the full records for the latest entries and include coordinates
        latest_data_records = []
        for entry in latest_entries:
            latest_data = SensorData.objects.filter(
                sensor__sensor_id=entry["sensor__sensor_id"],
                timestamp=entry["latest_timestamp"]
            ).first()

            if latest_data:
                # Add sensor_id and coordinates to each data record
                latest_data_dict = {
                    "sensor_id": entry["sensor__sensor_id"],
                    "temperature": latest_data.temperature,
                    "humidity": latest_data.humidity,
                    "timestamp": latest_data.timestamp
                }

                # Add coordinates from the sensor_coordinates_dict
                coordinates = sensor_coordinates_dict.get(entry["sensor__sensor_id"])
                if coordinates:
                    latest_data_dict["coordinates"] = coordinates

                # Append to the list of records
                latest_data_records.append(latest_data_dict)
                print(latest_data_records)

        # Serialize the data (including coordinates)
        # serializer = SensorDataSerializer(latest_data_records, many=True)
        return Response(latest_data_records, status=status.HTTP_200_OK)