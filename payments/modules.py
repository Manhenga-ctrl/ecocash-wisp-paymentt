import sqlite3

def get_voucher_by_package(package, db_path="db.sqlite3"):
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






package_type = "1GB"   # or "premium", "gold", etc.

voucher = get_voucher_by_package(package_type)

if voucher:
    print(f"Voucher for {package_type}: {voucher}")
else:
    print(f"No vouchers available for {package_type}")
