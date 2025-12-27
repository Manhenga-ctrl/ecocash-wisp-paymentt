import json
import os
from .models import VoucherTransaction

VOUCHER_FILE = os.path.join(
    os.path.dirname(__file__),
    "vouchers.json"
)


def load_vouchers():
    if not os.path.exists(VOUCHER_FILE):
        return []

    with open(VOUCHER_FILE, "r") as file:
        return json.load(file)


def save_vouchers(vouchers):
    with open(VOUCHER_FILE, "w") as file:
        json.dump(vouchers, file, indent=4)


def get_random_unused_voucher(package):
    """
    Returns a random unused voucher for the given package
    """
    vouchers = load_vouchers()

    for voucher in vouchers:
        if (
            voucher.get("package") == package
            and voucher.get("used") is False
        ):
            voucher["used"] = True
            save_vouchers(vouchers)
            return voucher

    return None


def check_reference(reference):
    """
    Prevent duplicate voucher issuing
    """
    return VoucherTransaction.objects.filter(
        source_reference=reference
    ).exists()
