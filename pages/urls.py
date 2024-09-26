from django.urls import path
from .views import HomePageView, SensorDataListView, register_device, record_sensor_data

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path('sensor-data/', SensorDataListView.as_view(), name='sensor-data-list'),
    path('probes/register/', register_device, name='register_device'),
    path('probes/record/', record_sensor_data, name='record_sensor_data'),
]