from django import forms
from api.models import Sensor

class DataDownloadForm(forms.Form):
    sensor = forms.ModelChoiceField(
        queryset=Sensor.objects.all(),
        label="Sensor",
        widget=forms.Select(attrs={'class': 'form-select', 'aria-label': 'Select sensor'})
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", 'class': 'form-control'}),
        label="From"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", 'class': 'form-control'}),
        label="To"
    )