# serializers.py

from rest_framework import serializers
from .models import Sensor, SensorData

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ['id', 'name', 'sensor_id']

class SensorDataSerializer(serializers.ModelSerializer):
    sensor_id = serializers.CharField()  # Declare sensor_id here for incoming data

    class Meta:
        model = SensorData
        fields = ['sensor_id', 'temperature', 'humidity', 'timestamp']  # Include sensor_id

    def create(self, validated_data):
        sensor_id = validated_data.pop('sensor_id')
        try:
            # Retrieve the sensor based on the sensor_id
            sensor = Sensor.objects.get(sensor_id=sensor_id)
        except Sensor.DoesNotExist:
            raise serializers.ValidationError({'sensor_id': 'Sensor with this ID does not exist.'})

        # Create SensorData instance with the retrieved sensor
        return SensorData.objects.create(sensor=sensor, **validated_data)
    
