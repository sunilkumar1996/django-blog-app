from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
import logging
from .forms import PersonRegistrationForm, PersonLoginForm

logger = logging.getLogger(__name__)

class RegisterView(View):
    template_name = "auth_app/register.html"

    def get(self, request, *args, **kwargs):
        context = {}
        logger.info(f"User visited in Register view")
        context['form'] = PersonRegistrationForm()
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = {}
        logger.info(f"User visited in Register view for submit form data")
        register_form = PersonRegistrationForm(request.POST or None)
        if register_form.is_valid():
            person = register_form.save()
            if person is not None:
                login(request,person)
                email = request.user.email
                logger.info(f"{email} has been successfully register!")
                return redirect('/')
        else:
            context['form'] = register_form
            logger.info(f"Error in register view")
            return render(self.request, self.template_name, context)

class LoginView(View):
    template_name = "auth_app/login.html"

    def get(self, request, *args, **kwargs):
        context = {}
        logger.info(f"User visited in Login view")
        context['form'] = PersonLoginForm()
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = {}
        logger.info(f"User submit form in login post")
        form = PersonLoginForm(request.POST or None)
        if form.is_valid():
            logger.info(f"Form valid in login view")
            username = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request,user)
                email = request.user.email
                logger.info(f"{email} has been successfully logged In!")
                return redirect('/')
            else:
                context['form'] = form
                logger.info(f"user not found!")
                return render(request, self.template_name, context)
        else:
            context['form'] = form
            logger.info(f"Invalid form data in login view")
            return render(request, self.template_name, context)

class Logout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        logger.info(f"Successfully logged out")
        return redirect('login_view')