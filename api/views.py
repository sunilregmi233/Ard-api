# views.py

from rest_framework import generics
from .models import Sensor, SensorData
from .serializers import SensorSerializer, SensorDataSerializer
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Max, Avg
from django.http import JsonResponse
from datetime import datetime, time, timedelta
from django.utils.timezone import now



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
        serializer = SensorDataSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Sensor data recorded successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



def calculate_heat_index(temperature, humidity):
    """
    Calculate the Heat Index using the provided formula.
    """
    T = temperature
    R = humidity
    hi = (-8.78469475556 +
          1.61139411 * T +
          2.33854883889 * R +
          -0.14611605 * T * R +
          -0.012308094 * (T ** 2) +
          -0.0164248277778 * (R ** 2) +
          0.002211732 * (T ** 2) * R +
          0.00072546 * T * (R ** 2) +
          -0.000003582 * (T ** 2) * (R ** 2))
    return round(hi, 2)

class LatestDataForSensorsView(APIView):
    def get(self, request):
        # Static list of sensor IDs
        sensor_ids = ["JK101", "JK102", "JK103", "JK104", "JK105",
                      "JK106", "JK107", "JK108", "JK109", "JK110"]

        # Dictionary of sensor coordinates (latitude and longitude)
        sensor_coordinates_dict = {
            "JK101": {"latitude": 26.7345, "longitude": 85.9289},
            "JK102": {"latitude": 26.7314, "longitude": 85.9313},
            "JK103": {"latitude": 26.7314, "longitude": 85.9279},
            "JK104": {"latitude": 26.7314, "longitude": 85.9249},
            "JK105": {"latitude": 26.7303, "longitude": 85.9316},
            "JK106": {"latitude": 26.7338, "longitude": 85.9205},
            "JK107": {"latitude": 26.7168, "longitude": 85.9201},
            "JK108": {"latitude": 26.7360, "longitude": 85.9348},
            "JK109": {"latitude": 26.7582, "longitude": 85.9403},
            "JK110": {"latitude": 26.7173, "longitude": 85.9225},
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

        current_time = now()
        valid_temp_range = (0, 50)
        valid_humidity_range = (0, 100)
        status_threshold = timedelta(minutes=5)
        recent_threshold = timedelta(minutes=3)

        # Calculate the start date for the last 7 days
        start_date = current_time - timedelta(days=7)

        # Query sensor data for the last 7 days
        seven_day_data = (
            SensorData.objects.filter(sensor__sensor_id__in=sensor_ids, timestamp__gte=start_date)
            .values("sensor__sensor_id", "timestamp__date")
            .annotate(
                avg_temperature=Avg("temperature"),
                avg_humidity=Avg("humidity")
            )
            .order_by("sensor__sensor_id", "timestamp__date")
        )

        # Organize 7-day data by sensor
        seven_day_averages = {}
        for entry in seven_day_data:
            sensor_id = entry["sensor__sensor_id"]
            date = entry["timestamp__date"]
            if sensor_id not in seven_day_averages:
                seven_day_averages[sensor_id] = []

            seven_day_averages[sensor_id].append({
                "date": date,
                "average_temperature": round(entry["avg_temperature"], 2) if entry["avg_temperature"] else None,
                "average_humidity": round(entry["avg_humidity"], 2) if entry["avg_humidity"] else None,
            })

        # Fetch the full records for the latest entries and include coordinates
        latest_data_records = []
        for entry in latest_entries:
            sensor_id = entry["sensor__sensor_id"]
            latest_timestamp = entry["latest_timestamp"]
            latest_data = SensorData.objects.filter(
                sensor__sensor_id=sensor_id,
                timestamp=latest_timestamp
            ).first()

            # Determine the sensor status
            if latest_data:
                time_diff = current_time - latest_timestamp
                if time_diff > status_threshold:
                    sensorstatus = "Inactive"  # No data for more than 5 minutes
                else:
                    in_range = (valid_temp_range[0] <= latest_data.temperature <= valid_temp_range[1] and
                                valid_humidity_range[0] <= latest_data.humidity <= valid_humidity_range[1])
                    if in_range and time_diff <= recent_threshold:
                        sensorstatus = "Working"  # Data in range and recent
                    else:
                        sensorstatus = "Error"  # Data out of range
            else:
                sensorstatus = "Inactive"  # No data found

            # Calculate averages for day and night if data exists
            if latest_data:
                day_start = time(6, 0, 0)
                night_start = time(18, 0, 0)
                day_avg = SensorData.objects.filter(
                    sensor__sensor_id=sensor_id,
                    timestamp__date=latest_data.timestamp.date(),
                    timestamp__time__gte=day_start,
                    timestamp__time__lt=night_start
                ).aggregate(
                    avg_temperature=Avg("temperature"),
                    avg_humidity=Avg("humidity")
                )

                night_avg = SensorData.objects.filter(
                    sensor__sensor_id=sensor_id,
                    timestamp__date=latest_data.timestamp.date(),
                    timestamp__time__lt=day_start
                ).aggregate(
                    avg_temperature=Avg("temperature"),
                    avg_humidity=Avg("humidity")
                )
                if latest_data and time_diff <= recent_threshold: 
                    heat_index = calculate_heat_index(latest_data.temperature, latest_data.humidity) 
                else:
                    heat_index = None
                        

                latest_data_dict = {
                    "sensor_id": sensor_id,
                    "temperature": latest_data.temperature,
                    "humidity": latest_data.humidity,
                    "heat_index": heat_index,
                    "timestamp": latest_data.timestamp,
                    "coordinates": sensor_coordinates_dict.get(sensor_id),
                    "temperature_day": round(day_avg["avg_temperature"], 2) if day_avg["avg_temperature"] else None,
                    "humidity_day": round(day_avg["avg_humidity"], 2) if day_avg["avg_humidity"] else None,
                    "temperature_night": round(night_avg["avg_temperature"], 2) if night_avg["avg_temperature"] else None,
                    "humidity_night": round(night_avg["avg_humidity"], 2) if night_avg["avg_humidity"] else None,
                    "status": sensorstatus,
                    "seven_day_averages": seven_day_averages.get(sensor_id, []),  # Add 7-day averages
                }
            else:
                latest_data_dict = {
                    "sensor_id": sensor_id,
                    "temperature": None,
                    "humidity": None,
                    "heat_index": None,
                    "timestamp": None,
                    "coordinates": sensor_coordinates_dict.get(sensor_id),
                    "temperature_day": None,
                    "humidity_day": None,
                    "temperature_night": None,
                    "humidity_night": None,
                    "status": sensorstatus,
                    "seven_day_averages": seven_day_averages.get(sensor_id, []),  # Add 7-day averages
                }
            latest_data_records.append(latest_data_dict)

        return Response(latest_data_records, status=status.HTTP_200_OK)
