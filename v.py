import sqlite3

# Connect to existing SQLite database
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Take input from user
customer_msisdn = input("Enter phone number: ")

# Fetch value using column
cursor.execute(
    "SELECT status FROM payments_transaction WHERE customer_msisdn = ?",
    (customer_msisdn,)
)

result = cursor.fetchone()

if result:
    print("Status:", result[0])
else:
    print("No record found for the given phone number.")

# Close connection
conn.close()
