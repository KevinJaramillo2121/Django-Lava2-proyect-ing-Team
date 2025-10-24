# vehicles/forms.py
from django import forms

from .models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["plate", "make", "model", "year", "color", "is_active"]
        widgets = {
            "plate": forms.TextInput(attrs={"placeholder": "ABC-123"}),
        }

    def clean_plate(self):
        # Normalizamos aquí también por si cambia
        plate = self.cleaned_data["plate"].upper()
        return plate
