import sqlite3
import requests
import json
import time


# CONFIGURATION


DB_PATH = "db.sqlite3"
TABLE_NAME = "payments_transaction"
VOUCHERS_TABLE = 'index_voucher'

API_URL = "https://developers.ecocash.co.zw/api/ecocash_pay/api/v1/transaction/c2b/status/sandbox"
API_KEY = "hG7OMSH6YZvna7iOS6YxeJeyodDK7ltn"

HEADERS = {
    "Content-Type": "application/json",
    "X-API-KEY": API_KEY
}

POLL_INTERVAL = 5  

# FETCH DATA FROM SQLITE


def get_transaction_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT customer_msisdn, source_reference,package
        FROM {TABLE_NAME}
        ORDER BY datetime(timestamp) DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise Exception(" No transaction found in database")

    return row  # (customer_msisdn, source_reference)


# MAIN LOGIC


def check_ecocash_status():
    customer_msisdn, source_reference ,package= get_transaction_from_db()

    payload = {
        "sourceMobileNumber": customer_msisdn,
        "sourceReference": source_reference
    }

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    try:
        data=response.json()
        status=data.get("status", "SUCCESS")
        if status=="SUCCESS":

            if package=="basic":
                print("basic package")

            if package=="standard":
                print("Standard")

            if  package=="premiunm":
                print('premium')

        else:
            print(" Transaction still pending...")

    except ValueError:
        print(response.text)


# RUN FOREVER (POLLING LOOP)


if __name__ == "__main__":
    print(" EcoCash status polling started (every 10 seconds)")

    while True:
        try:
            check_ecocash_status()
        except Exception as e:
            print(" Error:", str(e))

        time.sleep(POLL_INTERVAL)
