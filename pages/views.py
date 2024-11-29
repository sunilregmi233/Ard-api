from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from api.models import SensorData, Sensor
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.paginator import Paginator
from django.http import JsonResponse
from .forms import DataDownloadForm
from django.http import HttpResponse
import csv
from django.contrib import messages
from django.utils.text import slugify
import logging, datetime
# # Record Sensor Data (Simplified)
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
    template_name = "SensorView.html"

class MapView(TemplateView):
    template_name = "Map.html"
    
# class DataDownloadView(TemplateView):
#     template_name = "DataDownload.html"

# Set up logging for debugging
logger = logging.getLogger(__name__)

def download_data_view(request):
    if request.method == "POST":
        form = DataDownloadForm(request.POST)
        if form.is_valid():
            sensor = form.cleaned_data["sensor"]
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]

            # Ensure start_date and end_date are datetime.date objects
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            # Log form data for debugging
            logger.debug(f"Sensor: {sensor}, Start Date: {start_date}, End Date: {end_date}")

            # Query SensorData related to the selected Sensor
            data = SensorData.objects.filter(
                sensor=sensor,
                timestamp__date__range=(start_date, end_date)
            )

            # Log the query for debugging
            logger.debug(f"Generated query: {data.query}")

            if not data.exists():
                logger.warning("No data found for the selected range.")
                messages.error(request, "No data found for the selected range.")
                return redirect("home")

            # Generate CSV response
            response = HttpResponse(content_type="text/csv")
            filename = f"{slugify(sensor.name)}_data_{start_date}_to_{end_date}.csv"
            response["Content-Disposition"] = f'attachment; filename="{filename}"'

            writer = csv.writer(response)
            writer.writerow(["Sensor Name", "Sensor ID", "Temperature (°C)", "Humidity (%)", "Timestamp"])

            for row in data:
                logger.debug(f"Writing row: {row.sensor.name}, {row.sensor.sensor_id}, {row.temperature}, {row.humidity}, {row.timestamp}")
                writer.writerow([row.sensor.name, row.sensor.sensor_id, row.temperature, row.humidity, row.timestamp])

            return response
        else:
            logger.error("Form validation failed.")
            messages.error(request, "Invalid form submission.")
    else:
        form = DataDownloadForm()

    return render(request, "DataDownload.html", {"form": form})

# class SensorDataListView(LoginRequiredMixin, ListView):
#     model = SensorData
#     template_name = 'SensorView.html'
#     context_object_name = 'sensor_data_page'
#     login_url = '/accounts/login'  # Customize the login URL if needed
#     paginate_by = 1000  # Set the number of entries per page

#     def get_queryset(self):
#         return SensorData.objects.order_by('-timestamp')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['sensors'] = Sensor.objects.all()  # Fetch all sensors
#         return context

def sensor_data_list(request):
    # Get sensor ID from request
    sensor_id = request.GET.get('sensor')
    
    # Get all sensors for the dropdown
    sensors = Sensor.objects.all()

    # Filter sensor data if a sensor is selected, otherwise get all data
    sensor_data_queryset = SensorData.objects.all()

    if sensor_id:
        sensor_data_queryset = sensor_data_queryset.filter(sensor_id=sensor_id)

    # Order the data by timestamp in descending order
    sensor_data_queryset = sensor_data_queryset.order_by('-timestamp')

    # Paginate the queryset (50 records per page)
    paginator = Paginator(sensor_data_queryset, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Check if the request is AJAX (for pagination via JavaScript)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [
            {
                'sensor_name': data.sensor.name,
                'sensor_id': data.sensor.sensor_id,
                'temperature': data.temperature,
                'humidity': data.humidity,
                'timestamp': data.timestamp,
            }
            for data in page_obj
        ]
        pagination_info = {
            'has_previous': page_obj.has_previous(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'number': page_obj.number,
            'num_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        }
        return JsonResponse({'data': data, 'pagination': pagination_info})

    # If not an AJAX request, render the full page with the sensor data
    context = {
        'sensors': sensors,  # For the sensor selection dropdown
        'page_obj': page_obj,  # Paginated sensor data for the table
    }
    return render(request, 'SensorView.html', context)

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


