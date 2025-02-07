from django import forms
from accounts.models import Certification, User,ServiceProvider,ServiceArea
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate


class UserRegistrationForm(UserCreationForm):
    
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 
                  'last_name', 'user_type', 'phone_number', 'address', 'city', 
                  'state', 'zip_code', 'profile_picture', 'bio', 'preferred_communication']
class ServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = ['business_name', 'description', 'experience_years']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove fields that should be set programmatically
        self.fields.pop('is_verified', None)
        self.fields.pop('rating', None)
        self.fields.pop('total_reviews', None)
        self.fields.pop('status', None)

class ServiceAreaForm(forms.ModelForm):
    class Meta:
        model = ServiceArea
        fields = ['city', 'state', 'zip_code']
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove provider field as it will be set in view
        self.fields.pop('provider', None)

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'issued_by', 'issued_date', 'expiry_date', 'document_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'issued_by': forms.TextInput(attrs={'class': 'form-control'}),
            'issued_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'document_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove provider field as it will be set in view
        self.fields.pop('provider', None)



class SiginForm(forms.Form):
        username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
        password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control"}))

    