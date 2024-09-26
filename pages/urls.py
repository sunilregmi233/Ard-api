from django.urls import path
from .views import HomePageView, register_device, record_sensor_data, sensor_data_list

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    # path('sensor-data/', SensorDataListView.as_view(), name='sensor-data-list'),
    path('sensor-data/', sensor_data_list, name='sensor-data-list'),
    path('probes/register/', register_device, name='register_device'),
    path('probes/record/', record_sensor_data, name='record_sensor_data'),
]