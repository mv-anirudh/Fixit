from django import forms
from .models import AvailabilitySchedule, Service, Booking, ServiceCategory
from django.core.exceptions import ValidationError
from datetime import *
from django.utils import timezone

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
        fields = ['booking_time', 'special_instructions', 'service_location']
        widgets = {
            'booking_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'special_instructions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'service_location': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        self.provider = kwargs.pop('provider', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        
        # Set booking date to today
        cleaned_data['booking_date'] = timezone.now().date()
        
        # Validate time against provider's availability
        if self.provider:
            day_of_week = cleaned_data['booking_date'].strftime('%A')
            availability = AvailabilitySchedule.objects.filter(
                provider=self.provider,
                day_of_week=day_of_week,
                is_available=True
            ).first()

            if not availability:
                raise forms.ValidationError('Provider is not available today.')

            booking_time = cleaned_data.get('booking_time')
            if (booking_time < availability.start_time or 
                booking_time > availability.end_time):
                raise forms.ValidationError('Selected time is outside provider availability.')

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