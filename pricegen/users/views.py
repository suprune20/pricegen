# -*- coding: utf-8 -*-

from django.urls import reverse
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm

class NotImplementedView(TemplateView):
    template_name = 'not_implemented.html'

not_implemented = NotImplementedView.as_view()

class DashBoardView(TemplateView):
    template_name = 'dashboard.html'

dashboard = DashBoardView.as_view()

class LoginView(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        request.session.set_test_cookie()
        return render(request, 'login.html', {'form':form})

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url_default = '/'
            next_url = request.GET.get("redirectUrl", next_url_default)
            if next_url == '/logout/':
                next_url = next_url_default
            return redirect(next_url)
        return self.get(request, *args, **kwargs)

ulogin = LoginView.as_view()

class LogoutView(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('ulogin'))
        user = request.user
        logout(request)
        if request.GET.get("redirectUrl"):
            response = redirect(request.GET.get("redirectUrl"))
        else:
            response = redirect(reverse('ulogin'))
        return response

ulogout = LogoutView.as_view()
