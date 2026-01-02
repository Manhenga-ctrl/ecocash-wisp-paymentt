
import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import sqlite3
from .services import EcoCashPayment
import time
from .models import Package, Transaction,Voucher
from django.db import transaction
import csv
import io
from django.shortcuts import render
from .forms import VoucherUploadForm
from .models import Voucher
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages



ECOCASH_STATUS_URL = "https://developers.ecocash.co.zw/api/ecocash_pay/api/v1/transaction/c2b/status/sandbox"
API_KEY = "MWocwVxw_vyA5tM8TiRpZGfkw3OzTkc2"

payment_processor = EcoCashPayment()



def get_voucher_by_package(package):
    """
    Fetch one unused voucher for a package and mark it as used.
    """
    

    with transaction.atomic():
        # Lock the first unused voucher for this package
        voucher = (
            Voucher.objects
            .select_for_update()       # lock row to prevent race conditions
            .filter(package=package, used=False)
            .first()
        )

        if voucher is None:
            return None

        # Mark voucher as used
        voucher.used = True
        voucher.save(update_fields=["used"])

        return voucher.voucher_code


# View to render payment page

def payment_page(request):

    packages= Package.objects.all()
    return render(request, "payment.html",{"packages": packages})

@csrf_exempt
def api_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    

    customer_msisdn = data.get("customerMsisdn")
    package = data.get("package")

   
    
    try:
        amount = Package.objects.values_list("amount", flat=True).get(package=package)
    except Package.DoesNotExist:
        amount = None
    
    
     
    customer_msisdn=str(customer_msisdn)
    customer_msisdn=customer_msisdn[1:]
    customer_msisdn="263"+str(customer_msisdn)
     
    if not customer_msisdn or not package:
        return JsonResponse({"error": "Missing fields"}, status=400)

    if not customer_msisdn.startswith("263") or len(customer_msisdn) != 12:
        return JsonResponse({"error": "Invalid phone number"}, status=400)

    result = payment_processor.make_payment(
        customer_msisdn,
        float(amount),
        package
    )

# Retrieve voucher based on package

    time.sleep(30)  
    

     
    try:
        status = Transaction.objects.values_list("status", flat=True).get(customer_msisdn=customer_msisdn)
    except Transaction.DoesNotExist:
        status = None
    
    

  # Wait for 30 seconds before checking status
    Voucher = get_voucher_by_package(package)
    

    if status=="SUCCESS":

            voucher = Voucher
        

    if status=="NULL" or status=="PENDING":
         voucher = "Payment is still being processed. Please wait."


    

    response_data = {
        "success": True,
        "message": "Payment request sent successfully",
        "voucher": voucher 
    }
    result = {**result, **response_data}
    return JsonResponse(result)




def upload_vouchers(request):
    message = ""
    packages= Package.objects.all()
    if request.method == "POST":
        form = VoucherUploadForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES['csv_file']

            if not csv_file.name.endswith('.csv'):
                message = "Please upload a CSV file."
            else:
                data = csv_file.read().decode('utf-8')
                io_string = io.StringIO(data)
                reader = csv.DictReader(io_string)
                for row in reader:
                 Voucher.objects.get_or_create(
            voucher_code=row['VOUCHER_CODE'].strip(),
            defaults={
                'package': row['PACKAGES'].strip()
            }
        )

                message = "Vouchers uploaded successfully!"

    else:
        form = VoucherUploadForm()

    return render(request, 'form.html', {
        'form': form,
        'message': message
        
    })



def voucher_list(request):
    packages= Package.objects.all()
    vouchers = Voucher.objects.all().order_by('used')  
    return render(request, 'voucher_list.html', {'vouchers': vouchers, 'packages': packages})


def delete_voucher(request, voucher_id):
    voucher = get_object_or_404(Voucher, id=voucher_id)
    voucher.delete()
    messages.success(request, f"Voucher {voucher.voucher_code} deleted successfully.")
    return redirect('voucher_list')