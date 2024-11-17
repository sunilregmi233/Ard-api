# urls.py

from django.urls import path
from .views import SensorListCreateView, SensorDetailView, SensorDataListCreateView, SensorDataDetailView, LatestDataForSensorsView
from . import views

urlpatterns = [
    # Endpoints for Sensors
    path('sensors/', SensorListCreateView.as_view(), name='sensor-list-create'),  # List and create sensors
    path('sensors/<int:pk>/', SensorDetailView.as_view(), name='sensor-detail'),  # Retrieve, update, delete specific sensor
    
    # Endpoints for Sensor Data
    path('sensor-data/', SensorDataListCreateView.as_view(), name='sensor-data-list-create'),  # List and create sensor data
    path('sensor-data/<int:pk>/', SensorDataDetailView.as_view(), name='sensor-data-detail'),  # Retrieve specific sensor data
    path('latest-sensors-data/', LatestDataForSensorsView.as_view(), name='latest-sensors-data'),

]
