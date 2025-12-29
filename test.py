from index import get_voucher_by_package

package_type = "1GB"   # or "premium", "gold", etc.

voucher = get_voucher_by_package(package_type)

if voucher:
    print(f"Voucher for {package_type}: {voucher}")
else:
    print(f"No vouchers available for {package_type}")
