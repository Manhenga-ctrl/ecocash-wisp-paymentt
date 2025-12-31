from django.contrib import admin

# Register your models here.

from .models import EcoCashTransaction, Transaction, Voucher, Package
admin.site.register(EcoCashTransaction)
admin.site.register(Transaction)
admin.site.register(Voucher)
admin.site.register(Package)

admin.site.site_header = "EcoCash Payment Admin"
admin.site.site_title = "EcoCash Payment Admin Portal"
admin.site.index_title = "Welcome to EcoCash Payment Admin Portal"