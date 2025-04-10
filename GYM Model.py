import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def generate_html_body(file_path):
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            box-sizing: border-box; 
        }
        /* Rest of the CSS remains the same */
    </style>
    </head>
    <!-- Rest of the HTML template remains the same -->
    """

    accounts = []
    current_account = None
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Account detection
            account_match = re.search(r'SNOWFLAKE ACCOUNT NAME\s*:\s*(.*)', line, re.IGNORECASE)
            if account_match:
                if current_account:
                    accounts.append(current_account)
                current_account = {
                    'name': account_match.group(1).strip(),
                    'has_expiry': False,
                    'headers': '',
                    'rows': []
                }
                continue
            
            if current_account:
                # Header detection
                if '<th>' in line.lower():
                    current_account['headers'] = line
                
                # Row detection
                if '<tr>' in line.lower() and '<td>' in line.lower():
                    current_account['has_expiry'] = True
                    current_account['rows'].append(line)

        # Add the last account
        if current_account:
            accounts.append(current_account)

    # HTML generation with proper key handling
    html_body = html_template.format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    for account in accounts:
        html_body += f'<div class="account-section">'
        html_body += f'<h3>{account.get("name", "Unnamed Account")}</h3>'  # Safe key access
        
        if account.get('has_expiry', False):
            html_body += '<div class="table-container">'
            html_body += '<table>'
            html_body += f'<thead>{account.get("headers", "")}</thead>'
            html_body += f'<tbody>{"".join(account.get("rows", []))}</tbody>'
            html_body += '</table></div>'
        else:
            html_body += '<div class="no-expiry">No password expiries found</div>'
        
        html_body += '</div>'

    # Rest of the HTML template remains the same
    return html_body

# Rest of the code remains the same