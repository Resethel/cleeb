# -*- coding: utf-8 -*-
"""
URLs for the `contact` application.
"""
from django.urls import path
from .views import ContactView, contact_success_view

app_name = 'contact'
urlpatterns = [
    path('contact/', ContactView.as_view(), name='form'),
    path('contact/success/', contact_success_view, name='success'),
]
