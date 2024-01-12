from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from api.models import SensorData
from django.contrib.auth.mixins import LoginRequiredMixin

class HomePageView(TemplateView):
    template_name = "home.html"



class SensorDataListView(LoginRequiredMixin, ListView):
    model = SensorData
    template_name = 'SensorView.html'
    context_object_name = 'sensor_data_page'
    login_url = '/accounts/login'  # Customize the login URL if needed
    paginate_by = 1000 # Set the number of entries per page

    def get_queryset(self):
        return SensorData.objects.order_by('-timestamp')
    
  
