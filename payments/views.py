


import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import EcoCashTransaction, VoucherTransaction
from .services import EcoCashPayment
from .modules import get_random_unused_voucher

ECOCASH_STATUS_URL = "https://developers.ecocash.co.zw/api/ecocash_pay/api/v1/transaction/c2b/status/sandbox"
API_KEY = "MWocwVxw_vyA5tM8TiRpZGfkw3OzTkc2"

payment_processor = EcoCashPayment()




# Create your views here.




def payment_page(request):
    return render(request, "payment.html")

@csrf_exempt
def api_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)

    customer_msisdn = data.get("customerMsisdn")
    
    package = data.get("package")  # ✅ CHANGED
    

     
    if package=="1GB":
        amount=1

    if package=="5GB":
        amount=5
    if package=="unlimited":
        amount=20

    else:
        amount=10



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

    if not customer_msisdn or not package or not amount:
        return JsonResponse({"error": "Missing fields"}, status=400)

    # For testing, generate a fake voucher code
    test_voucher = "TEST123ABC"

    response_data = {
        "success": True,
        "message": "Payment request sent successfully",
        "voucher": test_voucher  # ✅ Send voucher in response
    }
    result = {**result, **response_data}
    return JsonResponse(result)




def check_transaction(request):
    status_message = None

    if request.method == "POST":
        phone_number = request.POST.get("phone_number")

        transaction = EcoCashTransaction.objects.filter(
            customer_msisdn=phone_number
        ).last()

        if not transaction:
            return render(request, "index.html", {
                "error_message": "Phone number not found"
            })

        payload = {
            "sourceMobileNumber": phone_number,
            "sourceReference": transaction.source_reference
        }

        headers = {
            "X-API-KEY": API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(
            ECOCASH_STATUS_URL,
            json=payload,
            headers=headers
        )

        status = response.json().get("status")

        if status == "SUCCESS":
            if not VoucherTransaction.objects.filter(
                source_reference=transaction.source_reference
            ).exists():

                voucher = get_random_unused_voucher(transaction.package)  # ✅ CHANGED

                VoucherTransaction.objects.create(
                    source_reference=transaction.source_reference,
                    voucher_code=voucher["Voucher ID"],
                    phone_number=phone_number
                )

                status_message = (
                    f"✅ PAYMENT SUCCESS. YOUR {transaction.package.upper()} "
                    f"VOUCHER: {voucher['Voucher ID']}"
                )

        else:
            status_message = f"🔄 STATUS: {status}"

    return render(request, "index.html", {
        "status_message": status_message
    })

