from django import forms
from api.models import Sensor

class DataDownloadForm(forms.Form):
    sensor = forms.ModelChoiceField(queryset=Sensor.objects.all(), label="Sensor")
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="From")
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="To")