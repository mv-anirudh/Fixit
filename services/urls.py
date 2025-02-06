from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.ServiceListView.as_view(), name='service_list'),
    path('service/<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('service/<int:service_id>/book/', views.CreateBookingView.as_view(), name='create_booking'),
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('booking/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('booking/<int:pk>/update-status/', views.UpdateBookingStatusView.as_view(), 
         name='update_booking_status'),
    path('dashboard/', views.ProviderDashboardView.as_view(), name='provider_dashboard'),
]