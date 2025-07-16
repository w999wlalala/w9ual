import smtplib, ssl
import os
from datetime import datetime

port = 465
smtp_server = "smtp.gmail.com"
USERNAME = "wa9999253@gmail.com"
PASSWORD = "qbocnpmlhcbdyhrv"  # Remove spaces from app password
TARGET_EMAIL = "wyhong0826@gmail.com"

# Check if running in GitHub Actions
def is_github_actions():
    return os.getenv('GITHUB_ACTIONS') == 'true'

def get_execution_context():
    if is_github_actions():
        workflow = os.getenv('GITHUB_WORKFLOW', 'Unknown')
        run_id = os.getenv('GITHUB_RUN_ID', 'Unknown')
        actor = os.getenv('GITHUB_ACTOR', 'Unknown')
        ref = os.getenv('GITHUB_REF', 'Unknown')
        return {
            'source': 'GitHub Actions',
            'workflow': workflow,
            'run_id': run_id,
            'actor': actor,
            'ref': ref
        }
    else:
        return {
            'source': 'Manual/Local execution',
            'user': os.getenv('USER', 'Unknown'),
            'hostname': os.getenv('HOSTNAME', 'Unknown')
        }

# Get execution context
context = get_execution_context()
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Create message based on execution context
if is_github_actions():
    message = f"""\
Subject: GitHub Actions Email Report - {current_time}

This email was sent by GitHub Actions:

Workflow: {context['workflow']}
Run ID: {context['run_id']}
Triggered by: {context['actor']}
Branch/Ref: {context['ref']}
Timestamp: {current_time}

This is your automated email report from GitHub Actions.
"""
    print(f"🤖 Running in GitHub Actions - Workflow: {context['workflow']}")
else:
    message = f"""\
Subject: Manual Email Report - {current_time}

This email was sent manually:

User: {context['user']}
Host: {context['hostname']}
Timestamp: {current_time}

This is a manually triggered email report.
"""
    print(f"👤 Running manually by user: {context['user']}")

try:
    context_ssl = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context_ssl) as server:
        server.login(USERNAME, PASSWORD)
        server.sendmail(USERNAME, TARGET_EMAIL, message)
        if is_github_actions():
            print("✓ Email sent successfully from GitHub Actions!")
        else:
            print("✓ Email sent successfully from manual execution!")
        
except smtplib.SMTPAuthenticationError:
    print("✗ Authentication failed. Check your username and password.")
except Exception as e:
    print(f"✗ Error sending email: {e}") 