from django import forms
from .models import Service, Booking, ServiceCategory
from django.core.exceptions import ValidationError
from datetime import datetime, time

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['category', 'name', 'description', 'base_price', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'base_price': forms.NumberInput(attrs={'min': 0}),
        }

    def clean_base_price(self):
        price = self.cleaned_data.get('base_price')
        if price <= 0:
            raise ValidationError('Price must be greater than zero')
        return price

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'service_location', 'special_instructions']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'booking_time': forms.TimeInput(attrs={'type': 'time'}),
            'special_instructions': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.provider = kwargs.pop('provider', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('booking_date')
        booking_time = cleaned_data.get('booking_time')

        if booking_date and booking_time:
            # Check if date is not in past
            if booking_date < datetime.now().date():
                raise ValidationError('Cannot book service for past dates')

            # Check provider availability
            if self.provider:
                day_name = booking_date.strftime('%A')
                availability = self.provider.availability.filter(
                    day_of_week=day_name,
                    is_available=True
                ).first()

                if not availability:
                    raise ValidationError(f'Provider is not available on {day_name}s')

                if (booking_time < availability.start_time or 
                    booking_time > availability.end_time):
                    raise ValidationError('Selected time is outside provider\'s working hours')

        return cleaned_data

class ServiceSearchForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.all(),
        required=False,
        empty_label="All Categories"
    )
    location = forms.CharField(required=False)
    min_price = forms.DecimalField(required=False, min_value=0)
    max_price = forms.DecimalField(required=False, min_value=0)
    availability_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )