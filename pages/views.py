from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from api.models import SensorData, Sensor
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view


# Record Sensor Data (Simplified)
@csrf_exempt
def record_sensor_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_id = data.get('sensor_id')
            temperature = data.get('temperature')
            humidity = data.get('humidity')

            # Find the sensor or return 404 if not found
            device = get_object_or_404(Sensor, sensor_id=device_id)

            # Create a new SensorData entry
            SensorData.objects.create(sensor=device, temperature=temperature, humidity=humidity)

            return JsonResponse({'message': 'Sensor data recorded successfully'}, status=201)
        except KeyError:
            return JsonResponse({'error': 'Invalid data provided'}, status=400)

class HomePageView(TemplateView):
    template_name = "home.html"



class SensorDataListView(LoginRequiredMixin, ListView):
    model = SensorData
    template_name = 'SensorView.html'
    context_object_name = 'sensor_data_page'
    login_url = '/accounts/login'  # Customize the login URL if needed
    paginate_by = 1000  # Set the number of entries per page

    def get_queryset(self):
        return SensorData.objects.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sensors'] = Sensor.objects.all()  # Fetch all sensors
        return context


# Device Registration (Optimize using DRF for consistency)
@csrf_exempt
def register_device(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_name = data.get('name')
            device_id = data.get('sensor_id')

            # Register the device if it doesn't exist
            device, created = Sensor.objects.get_or_create(name=device_name, sensor_id=device_id)
            message = 'Device registered successfully' if created else 'Device already registered'
            return JsonResponse({'message': message}, status=201 if created else 200)
        except KeyError:
            return JsonResponse({'error': 'Invalid data provided'}, status=400)


