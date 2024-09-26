from django.contrib import admin
from .models import Sensor, SensorData

# @admin.register(Sensor)
# class SensorAdmin(admin.ModelAdmin):
#     list_display = ('name', 'sensor_id')

# @admin.register(SensorData)
# class SensorDataAdmin(admin.ModelAdmin):
#     list_display = ('sensor', 'temperature', 'humidity', 'timestamp')

admin.site.register(Sensor)
admin.site.register(SensorData)