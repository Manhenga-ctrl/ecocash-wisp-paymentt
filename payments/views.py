
import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import sqlite3
from .services import EcoCashPayment
import time
from .models import Package


ECOCASH_STATUS_URL = "https://developers.ecocash.co.zw/api/ecocash_pay/api/v1/transaction/c2b/status/sandbox"
API_KEY = "MWocwVxw_vyA5tM8TiRpZGfkw3OzTkc2"

payment_processor = EcoCashPayment()
Database="db.sqlite3"



def get_voucher_by_package(package, db_path=Database):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Lock database to avoid duplicate usage
    conn.execute("BEGIN IMMEDIATE")

    cursor.execute("""
        SELECT id, voucher_code
        FROM payments_voucher
        WHERE used = 0 AND package = ?
        LIMIT 1
    """, (package,))

    voucher = cursor.fetchone()

    if voucher is None:
        conn.rollback()
        conn.close()
        return None

    voucher_id, voucher_code = voucher

    # Mark as used
    cursor.execute("""
        UPDATE payments_voucher
        SET used = 1
        WHERE id = ?
    """, (voucher_id,))

    conn.commit()
    conn.close()

    return voucher_code





# View to render payment page

def payment_page(request):

    packages= Package.objects.all()
    return render(request, "payment.html",{"packages": packages})

@csrf_exempt
def api_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    conn = sqlite3.connect("db.sqlite3")

    customer_msisdn = data.get("customerMsisdn")
    package = data.get("package")

   
    
    
    cursor = conn.cursor()   # use lowercase variable name

    cursor.execute(
    "SELECT amount FROM payments_package WHERE package = ?",
    (package,)
)
    row = cursor.fetchone()  # returns tuple like (50,)
    amount = row
    print(amount)

    amount=amount[0]
     
     
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
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    cursor.execute(
    "SELECT status FROM payments_transaction WHERE customer_msisdn = ?",
    (customer_msisdn,)
)

    status = cursor.fetchone()
    status=status[0]


  # Wait for 30 seconds before checking status
    Voucher = get_voucher_by_package(package)
    

    if status=="SUCCESS":

            voucher = Voucher
        

    if status=="NULL" or status=="PENDING":
         voucher = "Payment is still being processed. Please wait."


    

    response_data = {
        "success": True,
        "message": "Payment request sent successfully",
        "voucher": voucher  # ✅ Send voucher in response
    }
    result = {**result, **response_data}
    return JsonResponse(result)



