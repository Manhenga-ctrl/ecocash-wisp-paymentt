import smtplib
from email.message import EmailMessage

EMAIL = "achiponda@linus.co.zw"
PASSWORD = "Genesis@2025"
TO = "anesuishechiponda@gmail.com"

msg = EmailMessage()
msg["Subject"] = "SMTP Setup Test"
msg["From"] = EMAIL
msg["To"] = TO
msg.set_content("SMTP email setup successful.")

# Try SSL first
try:
    with smtplib.SMTP_SSL("mail.linus.co.zw", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
    print("Email sent successfully with SSL!")
except Exception as e_ssl:
    print("SSL failed:", e_ssl)

    # Try TLS fallback
    try:
        with smtplib.SMTP("mail.linus.co.zw", 587) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
        print("Email sent successfully with TLS!")
    except Exception as e_tls:
        print("TLS failed:", e_tls)
