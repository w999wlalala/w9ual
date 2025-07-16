import smtplib, ssl
import os
from datetime import datetime

port = 465
smtp_server = "smtp.gmail.com"
USERNAME = "wa9999253@gmail.com"
PASSWORD = "zktw jybz lzyr dkyp"  # Remove spaces from app password
TARGET_EMAIL = "wyhong0826@gmail.com"

# Add detailed logging function
def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

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

# Start logging
log("=== Email Script Started ===")
log(f"Python script: {__file__}")

# Get execution context
context = get_execution_context()
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Log execution context
log(f"Execution source: {context['source']}")
if is_github_actions():
    log(f"🤖 Running in GitHub Actions")
    log(f"  Workflow: {context['workflow']}")
    log(f"  Run ID: {context['run_id']}")
    log(f"  Actor: {context['actor']}")
    log(f"  Ref: {context['ref']}")
    log(f"  Repository: {os.getenv('GITHUB_REPOSITORY', 'Unknown')}")
    log(f"  Event: {os.getenv('GITHUB_EVENT_NAME', 'Unknown')}")
else:
    log(f"👤 Running manually")
    log(f"  User: {context['user']}")
    log(f"  Host: {context['hostname']}")

# Create message based on execution context
if is_github_actions():
    message = f"""\
Subject: GitHub Actions Email Report - {current_time}

This email was sent by GitHub Actions:

Workflow: {context['workflow']}
Run ID: {context['run_id']}
Triggered by: {context['actor']}
Branch/Ref: {context['ref']}
Repository: {os.getenv('GITHUB_REPOSITORY', 'Unknown')}
Event: {os.getenv('GITHUB_EVENT_NAME', 'Unknown')}
Timestamp: {current_time}

This is your automated email report from GitHub Actions.
"""
else:
    message = f"""\
Subject: Manual Email Report - {current_time}

This email was sent manually:

User: {context['user']}
Host: {context['hostname']}
Timestamp: {current_time}

This is a manually triggered email report.
"""

log("Email message prepared")
log(f"From: {USERNAME}")
log(f"To: {TARGET_EMAIL}")
log(f"Subject: {'GitHub Actions' if is_github_actions() else 'Manual'} Email Report")

# Send email with detailed logging
log("Attempting to send email...")
try:
    log("Creating SSL context...")
    context_ssl = ssl.create_default_context()
    
    log(f"Connecting to SMTP server: {smtp_server}:{port}")
    with smtplib.SMTP_SSL(smtp_server, port, context=context_ssl) as server:
        log("Connected to SMTP server")
        
        log("Authenticating...")
        server.login(USERNAME, PASSWORD)
        log("Authentication successful")
        
        log("Sending email...")
        server.sendmail(USERNAME, TARGET_EMAIL, message)
        log("Email sent to SMTP server")
        
    if is_github_actions():
        log("✓ Email sent successfully from GitHub Actions!", "SUCCESS")
    else:
        log("✓ Email sent successfully from manual execution!", "SUCCESS")
        
except smtplib.SMTPAuthenticationError as e:
    log(f"✗ Authentication failed: {e}", "ERROR")
    log("Check your username and password in secrets", "ERROR")
except smtplib.SMTPException as e:
    log(f"✗ SMTP error: {e}", "ERROR")
except Exception as e:
    log(f"✗ Unexpected error: {e}", "ERROR")
    log(f"Error type: {type(e).__name__}", "ERROR")

log("=== Email Script Completed ===") 