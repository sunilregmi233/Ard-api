from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from api.models import SensorData

class HomePageView(TemplateView):
    template_name = "home.html"



class SensorDataListView(ListView):
    model = SensorData
    template_name = 'SensorView.html'
    context_object_name = 'data'
  