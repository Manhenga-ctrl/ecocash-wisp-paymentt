from django.urls import path
from . import views

urlpatterns = [
    path("", views.payment_page),
    path("api/payment/", views.api_payment),
      path('upload-vouchers/', views.upload_vouchers, name='upload_vouchers'),
      path('vouchers/', views.voucher_list, name='voucher_list'),
       path('delete-voucher/<int:voucher_id>/', views.delete_voucher, name='delete_voucher'),
   
]
