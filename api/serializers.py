# serializers.py

from rest_framework import serializers
from .models import Sensor, SensorData

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ['id', 'name', 'sensor_id']

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ['sensor', 'temperature', 'humidity', 'timestamp']  # Include sensor_id

    def create(self, validated_data):
        sensor_id = validated_data.pop('sensor_id')
        sensor = get_object_or_404(Sensor, sensor_id=sensor_id)
        return SensorData.objects.create(sensor=sensor, **validated_data)