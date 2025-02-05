from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import authenticate,login,logout
from .forms import UserRegistrationForm,SiginForm
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
      