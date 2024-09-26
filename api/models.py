# models.py

from django.db import models

class Sensor(models.Model):
    name = models.CharField(max_length=100)
    sensor_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)  # ForeignKey to Sensor model
    temperature = models.FloatField()
    humidity = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Data from {self.sensor.name} at {self.timestamp}"
