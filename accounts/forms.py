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
        fields = ['business_name', 'description', 'experience_years', 'is_verified', 'rating', 'total_reviews', 'status']


class ServiceAreaForm(forms.ModelForm):
    class Meta:
        model = ServiceArea
        fields = ['provider', 'city', 'state', 'zip_code']


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['provider', 'name', 'issued_by', 'issued_date', 'expiry_date', 'document_url']


class SiginForm(forms.Form):
        username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
        password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control"}))

    