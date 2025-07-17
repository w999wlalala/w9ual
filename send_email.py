import smtplib, ssl
import os
from datetime import datetime
import time
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
sys.path.append(os.path.dirname(__file__))
from get_git_daily_usage import get_yesterday_git_log

port = 465
smtp_server = "smtp.gmail.com"
USERNAME = "wa9999253@gmail.com"
PASSWORD = "zktw jybz lzyr dkyp"  # Remove spaces from app password
TARGET_EMAIL = "wa9999253@gmail.com"
# TOKEN = os.environ.get('GITHUB_TOKEN')
TOKEN = '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'

git_log_content = get_yesterday_git_log(TOKEN)
print(git_log_content)

# Create email message with proper headers
msg = MIMEMultipart()
msg['From'] = USERNAME
msg['To'] = TARGET_EMAIL
msg['Subject'] = f"Daily Git Usage Reports... - {datetime.now().strftime('%Y-%m-%d')}"

# Add body to email
msg.attach(MIMEText(git_log_content, 'plain'))

# Convert to string
message = msg.as_string()
context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(USERNAME,PASSWORD)
    server.sendmail(USERNAME,TARGET_EMAIL,message)