from django.urls import path
from .views import register_device, record_sensor_data, sensor_data_list, MapView , download_data_view, HomePageView, FaqView ,MediaView 

urlpatterns = [
    path("faq/", FaqView.as_view(), name="faq"),
    path("media/", MediaView.as_view(), name="media"),
    path("", HomePageView.as_view(), name="home"),
    path("data/", download_data_view, name="data"),
    # path('sensor-data/', SensorDataListView.as_view(), name='sensor-data-list'),
    # path('sensor-data/', sensor_data_list, name='sensor-data-list'),
    path('sensors-data', sensor_data_list, name='sensor-data-list'),
    path('probes/register/', register_device, name='register_device'),
    path('probes/record/', record_sensor_data, name='record_sensor_data'),
    #  path("download-data/", download_data_view, name="download_data"),
]