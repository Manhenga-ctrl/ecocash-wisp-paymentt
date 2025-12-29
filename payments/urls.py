from django.urls import path
from . import views

urlpatterns = [
    path("", views.payment_page),
    path("api/payment/", views.api_payment),
   
]
