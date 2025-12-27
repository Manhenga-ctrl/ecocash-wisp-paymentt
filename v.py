import sqlite3
import smtplib
from email.mime.text import MIMEText

def send_unused_voucher(db_path='vouchers.db', recipient_email='example@example.com'):
    """
    Fetch an unused voucher from the database, send it via email, and mark it as used.
    """
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ensure table exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vouchers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voucher_code TEXT NOT NULL,
            used INTEGER DEFAULT 0
        )
        ''')
        conn.commit()
        
        # Fetch one unused voucher
        cursor.execute("SELECT id, voucher_code FROM vouchers WHERE used = 0 LIMIT 1")
        voucher = cursor.fetchone()
        
        if voucher:
            voucher_id, voucher_code = voucher
            
            # --- Sending via email ---
            sender_email = "your_email@gmail.com"   # replace with your email
            sender_password = "your_app_password"  # Gmail app password recommended

            subject = "Your Internet Voucher"
            body = f"Here is your voucher code: {voucher_code}"

            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = recipient_email

            # Connect to Gmail SMTP server
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
            
            print(f"Voucher {voucher_code} sent to {recipient_email}")
            
            # Mark voucher as used
            cursor.execute("UPDATE vouchers SET used = 1 WHERE id = ?", (voucher_id,))
            conn.commit()
        else:
            print("No unused vouchers left.")
    
    except sqlite3.Error as e:
        print("Database error:", e)
    except smtplib.SMTPException as e:
        print("Email sending error:", e)
    finally:
        if conn:
            conn.close()

# Example usage
send_unused_voucher(recipient_email='friend@example.com')
