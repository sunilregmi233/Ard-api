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
from django.db.models import Max
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

# class HomePageView(TemplateView):
#     template_name = "SensorView.html"

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
                return redirect("/")

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


def get_latest_sensor_data():
    """
    Fetches the latest data for a predefined set of sensors and adds coordinates.
    Returns a list of dictionaries containing sensor data and coordinates.
    """
    # Static list of sensor IDs
    sensor_ids = ["JK101", "JK102", "JK103", "JK104", "JK105", 
                  "JK106", "JK107", "JK108", "JK109", "JK110"]

    # Dictionary of sensor coordinates
    sensor_coordinates_dict = {
        "JK101": {"latitude": 27.6415, "longitude": 85.5255},  # Panchkhal
        "JK102": {"latitude": 27.7172, "longitude": 85.3240},  # Kathmandu
        "JK103": {"latitude": 28.2096, "longitude": 83.9856},  # Pokhara
        "JK104": {"latitude": 27.5612, "longitude": 84.3585},  # Chitwan
        "JK105": {"latitude": 27.6648, "longitude": 85.6127},  # Lalitpur
        "JK106": {"latitude": 27.6773, "longitude": 85.4341},  # Bhaktapur
        "JK107": {"latitude": 27.6985, "longitude": 86.0352},  # Ramechhap
        "JK108": {"latitude": 27.9573, "longitude": 85.9164},  # Sindhupalchok
        "JK109": {"latitude": 28.3457, "longitude": 83.5761},  # Baglung
        "JK110": {"latitude": 27.6278, "longitude": 85.5326}   # Dhulikhel
    }

    # Fetch the latest timestamp for each sensor
    latest_entries = (
        SensorData.objects.filter(sensor__sensor_id__in=sensor_ids)
        .values("sensor__sensor_id")
        .annotate(latest_timestamp=Max("timestamp"))
    )

    if not latest_entries:
        return []

    # Collect the latest data for each sensor
    latest_data_records = []
    for entry in latest_entries:
        latest_data = SensorData.objects.filter(
            sensor__sensor_id=entry["sensor__sensor_id"],
            timestamp=entry["latest_timestamp"]
        ).first()

        if latest_data:
            # Add sensor_id, data, and coordinates
            latest_data_dict = {
                "sensor_id": entry["sensor__sensor_id"],
                "temperature": latest_data.temperature,
                "humidity": latest_data.humidity,
                "timestamp": latest_data.timestamp,
                "coordinates": sensor_coordinates_dict.get(entry["sensor__sensor_id"])
            }
            latest_data_records.append(latest_data_dict)

    return latest_data_records


def resource_map_view(request):
    """
    View for rendering the resource map page with the latest sensor data.
    """
    latest_data = get_latest_sensor_data()
    return render(request, "Map.html", {"latest_data": latest_data})