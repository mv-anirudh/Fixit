from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate,login,logout

from accounts.models import ServiceProvider
from .forms import CertificationForm, ServiceAreaForm, ServiceProviderForm, UserRegistrationForm,SiginForm
# Create your views here.
class IndexView(View):
    template_name="index.html"
    
    def get(self,request,*args,**kwargs):
        
        return render(request,self.template_name)
        

class SiginUpView(View):
    tempalte_name="Signup.html"
    form_class=UserRegistrationForm
    
    def get (self,request,*args,**kwargs):
        form_instance=self.form_class
        
        return render(request,self.tempalte_name,{"form":form_instance})
    
    def post(self,request,*args,**kwargs):
        
        form_data=request.POST
        form_instance=self.form_class(form_data)
        
        if form_instance.is_valid():    
            form_instance.save()
            
            print("created")
            
            return redirect("accounts:signin")
        
        print("not created")
        
        return render(request,self.tempalte_name,{"form":form_instance})
            
class SigninView(View):
    template_name="Signin.html"
    
    form_class=SiginForm
    
    def get(self,request,*args,**kwargs):
        form_instance=self.form_class
        
        return render(request,self.template_name,{"form":form_instance})
        
    def post(self,request,*args,**kwargs):
        form_data=request.POST
        
        form_instance=self.form_class(form_data)
        
        if form_instance.is_valid():
            
            data=form_instance.cleaned_data
            
            uname=data.get("username")
            
            pwd=data.get("password")
            
            user_obj=authenticate(request,username=uname,password=pwd)

            if user_obj:
                
                login(request,user_obj)
                print("session")
                
                return redirect("index")
        
        print("invalid cred")
        return render(request,self.template_name,{"form":form_instance})
    
class SiginOut(View):
    def get(self,request,*args,**kwargs):
        
        logout(request)
        
        print(request.user)
        return redirect("accounts:signin")   

class ServiceProviderRegistrationView(LoginRequiredMixin, CreateView):
    model = ServiceProvider
    form_class = ServiceProviderForm
    template_name = 'service_provider_registration.html'
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        # Redirect to the customer message page if the user is not a service provider
        if not request.user.is_authenticated or  request.user.user_type != 'service_provider':
            return render(request, 'customer_message.html')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['service_area_form'] = ServiceAreaForm(self.request.POST)
            context['certification_form'] = CertificationForm(self.request.POST)
        else:
            context['service_area_form'] = ServiceAreaForm()
            context['certification_form'] = CertificationForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        service_area_form = context['service_area_form']
        certification_form = context['certification_form']

        if service_area_form.is_valid() and certification_form.is_valid():
            service_provider = form.save(commit=False)
            service_provider.user = self.request.user
            service_provider.save()

            service_area = service_area_form.save(commit=False)
            service_area.provider = service_provider
            service_area.save()

            certification = certification_form.save(commit=False)
            certification.provider = service_provider
            certification.save()

            return redirect(self.success_url)
        else:
            # If forms are not valid, re-render the page with errors
            return self.render_to_response(self.get_context_data(form=form))  