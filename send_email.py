import smtplib, ssl
import os


port = 465
smtp_server = "smtp.gmail.com"
USERNAME = "wa9999253@gmail.com"
PASSWORD = "qbocnpmlhcbdyhrv"
TARGET_EMAIL = "wyhong0826@gmail.com"  # Target recipient email

message = """\
Subject: GitHub Email Report

This is your daily email report.
"""

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(USERNAME,PASSWORD)
    server.sendmail(USERNAME,TARGET_EMAIL,message) 