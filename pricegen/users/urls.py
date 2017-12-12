# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic.base import RedirectView

from django.conf import settings

from . import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^login/$', views.ulogin, name='ulogin'),
    url(r'^logout/$', views.ulogout, name='ulogout'),
    url(r'^not_implemented/$', views.not_implemented, name='not_implemented'),
    url(
        r'^favicon\.ico$',
        RedirectView.as_view(url='{0}img/favicon16x16.ico'.format(settings.STATIC_URL))
    ),

]
