import sqlite3
import requests
import time
import logging

# =======================
# CONFIGURATION
# =======================

DB_PATH = "db.sqlite3"
TABLE_NAME = "payments_transaction"

API_URL = "https://developers.ecocash.co.zw/api/ecocash_pay/api/v1/transaction/c2b/status/sandbox"
API_KEY = "MWocwVxw_vyA5tM8TiRpZGfkw3OzTkc2"


POLL_INTERVAL = 5  # seconds

HEADERS = {
    "Content-Type": "application/json",
    "X-API-KEY": API_KEY
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =======================
# DATABASE FUNCTIONS
# =======================

def get_pending_transactions():
    """
    Fetch all transactions not marked as SUCCESS
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT customer_msisdn, source_reference, package
            FROM {TABLE_NAME}
            WHERE status IS NULL OR status != 'SUCCESS'
            ORDER BY datetime(timestamp) ASC
        """)
        return cursor.fetchall()


def update_transaction_status(source_reference, status):
    """
    Update transaction status using source_reference
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE {TABLE_NAME}
            SET status = ?
            WHERE source_reference = ?
        """, (status, source_reference))
        conn.commit()


# =======================
# ECOCASH STATUS CHECK
# =======================

def check_ecocash_status(transaction):
    customer_msisdn, source_reference, package = transaction

    payload = {
        "sourceMobileNumber": customer_msisdn,
        "sourceReference": source_reference
    }

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

    except requests.RequestException as e:
        logging.error("API error for %s: %s", source_reference, e)
        return

    status = data.get("status")

    if status == "SUCCESS":
        logging.info("SUCCESS: %s", source_reference)

        if package == "1GB":
            logging.info("Deliver BASIC package")
        elif package == "5GB":
            logging.info("Deliver STANDARD package")
        elif package =="unlimited":
            logging.info("Deliver PREMIUM package")
        else:
            logging.warning("Unknown package: %s", package)

        update_transaction_status(source_reference, "SUCCESS")

    elif status == "PENDING":
        logging.info("PENDING: %s", source_reference)

    else:
        logging.warning("FAILED/UNKNOWN: %s → %s", source_reference, status)
        update_transaction_status(source_reference, status or "FAILED")


# =======================
# POLLING LOOP
# =======================

if __name__ == "__main__":
    logging.info("EcoCash polling started (every %s seconds)", POLL_INTERVAL)

    while True:
        try:
            pending_transactions = get_pending_transactions()

            if not pending_transactions:
                logging.info("No pending transactions")
            else:
                for tx in pending_transactions:
                    check_ecocash_status(tx)

        except Exception as e:
            logging.error("Polling error: %s", e)

        time.sleep(POLL_INTERVAL)
