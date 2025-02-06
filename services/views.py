from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Service, ServiceCategory, Booking
from .forms import ServiceForm, BookingForm, ServiceSearchForm
from datetime import datetime

class ServiceListView(ListView):
    model = Service
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    paginate_by = 12

    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True)
        form = ServiceSearchForm(self.request.GET)
        
        if form.is_valid():
            category = form.cleaned_data.get('category')
            location = form.cleaned_data.get('location')
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')
            availability_date = form.cleaned_data.get('availability_date')

            if category:
                queryset = queryset.filter(category=category)
            if location:
                queryset = queryset.filter(
                    provider__service_areas__city__icontains=location
                ).distinct()
            if min_price is not None:
                queryset = queryset.filter(base_price__gte=min_price)
            if max_price is not None:
                queryset = queryset.filter(base_price__lte=max_price)
            if availability_date:
                day_name = availability_date.strftime('%A')
                queryset = queryset.filter(
                    provider__availability__day_of_week=day_name,
                    provider__availability__is_available=True
                ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ServiceSearchForm(self.request.GET)
        return context

class ServiceDetailView(DetailView):
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking_form'] = BookingForm(provider=self.object.provider)
        return context

class CreateBookingView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'services/create_booking.html'
    
    def get_success_url(self):
        return reverse_lazy('services:booking_detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.service = get_object_or_404(Service, pk=self.kwargs['service_id'])
        kwargs['provider'] = self.service.provider
        return kwargs

    def form_valid(self, form):
        form.instance.service = self.service
        form.instance.provider = self.service.provider
        form.instance.customer = self.request.user
        form.instance.total_amount = self.service.base_price
        messages.success(self.request, 'Booking created successfully!')
        return super().form_valid(form)

class BookingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Booking
    template_name = 'services/booking_detail.html'
    context_object_name = 'booking'

    def test_func(self):
        booking = self.get_object()
        return (self.request.user == booking.customer or 
                self.request.user == booking.provider.user)

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'services/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.user_type == 'customer':
            return Booking.objects.filter(customer=self.request.user)
        return Booking.objects.filter(provider__user=self.request.user)

class UpdateBookingStatusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Booking
    fields = ['status']
    template_name = 'services/update_booking_status.html'

    def test_func(self):
        booking = self.get_object()
        return self.request.user == booking.provider.user

    def get_success_url(self):
        return reverse_lazy('services:booking_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Booking status updated successfully!')
        return super().form_valid(form)

class ProviderDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Booking
    template_name = 'services/provider_dashboard.html'
    context_object_name = 'recent_bookings'

    def test_func(self):
        return self.request.user.user_type == 'service_provider'

    def get_queryset(self):
        return Booking.objects.filter(
            provider__user=self.request.user
        ).order_by('-created_at')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        provider = self.request.user.serviceprovider
        today = datetime.now().date()
        
        context.update({
            'pending_bookings': Booking.objects.filter(
                provider=provider,
                status='pending'
            ).count(),
            'today_bookings': Booking.objects.filter(
                provider=provider,
                booking_date=today
            ),
            'services': Service.objects.filter(provider=provider),
        })
        return context