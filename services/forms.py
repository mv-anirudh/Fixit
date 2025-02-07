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

# forms.py


class ServiceSearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
               'placeholder': 'What service do you need?'}
    ))
    location = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
               'placeholder': 'Location'}
    ))
    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'px-4 py-2 rounded-lg border border-gray-300'})
    )
    price = forms.ChoiceField(
        choices=[
            ('', 'Price Range'),
            ('0-50', '$0 - $50'),
            ('51-100', '$51 - $100'),
            ('101+', '$101+')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'px-4 py-2 rounded-lg border border-gray-300'})
    )