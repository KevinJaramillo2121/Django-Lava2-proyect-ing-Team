from django import forms
from django.utils import timezone

from services.models import Service
from vehicles.models import Vehicle

from .models import Booking


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"


class BookingCreateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["vehicle", "service", "scheduled_at", "notes"]
        widgets = {"scheduled_at": DateTimeLocalInput()}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["vehicle"].queryset = Vehicle.objects.filter(owner=user, is_active=True)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)

    def clean_scheduled_at(self):
        dt = self.cleaned_data["scheduled_at"]
        if dt < timezone.now():
            raise forms.ValidationError("No puedes reservar en el pasado.")
        return dt


class BookingUpdateForm(BookingCreateForm):
    pass
