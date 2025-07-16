import smtplib, ssl

port = 465
smtp_server = "smtp.gmail.com"
USERNAME = "wa9999253@gmail.com"
PASSWORD = "qbocnpmlhcbdyhrv"  # Remove spaces from app password
TARGET_EMAIL = "wyhong0826@gmail.com"

message = """\
Subject: GitHub Email Report

This is your daily email report.
"""

try:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(USERNAME, PASSWORD)
        server.sendmail(USERNAME, TARGET_EMAIL, message)
        print("✓ Email sent successfully!")
        
except smtplib.SMTPAuthenticationError:
    print("✗ Authentication failed. Check your username and password.")
except Exception as e:
    print(f"✗ Error sending email: {e}") 