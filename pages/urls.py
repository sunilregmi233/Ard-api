from django.urls import path
from .views import HomePageView, SensorDataListView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path('sensor-data/', SensorDataListView.as_view(), name='sensor-data'),
]