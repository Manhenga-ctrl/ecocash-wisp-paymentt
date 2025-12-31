"""""
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
"""

from librouteros import connect

api = connect(
    host='10.10.2.1',
    username='chiponda',
    password='admin'
)

# Get generated vouchers from user manager
vouchers = api('/ip/hotspot/user/print')
for v in vouchers:
    username = v.get('name')  # handle both cases
    password = v.get('password', 'N/A')
    profile = v.get('profile', 'N/A')
    print(username, password, profile)