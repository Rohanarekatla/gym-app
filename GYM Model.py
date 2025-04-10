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
        * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; box-sizing: border-box; }
        .container { max-width: 1200px; margin: 20px auto; padding: 30px; background: #ffffff; 
                    border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { border-bottom: 2px solid #2c3e50; margin-bottom: 25px; padding-bottom: 15px; }
        .header h2 { color: #2c3e50; margin: 0; font-size: 24px; font-weight: 600; }
        .table-container { margin: 20px 0; overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; margin: 25px 0; min-width: 600px; }
        th { background-color: #2c3e50; color: #fff; padding: 12px 15px; text-transform: uppercase; }
        td { padding: 12px 15px; border-bottom: 1px solid #ecf0f1; color: #34495e; }
        tr:nth-child(even) { background-color: #f8f9fa; }
        .no-expiry { background: #f1f5f7; padding: 15px; border-radius: 4px; margin: 15px 0; 
                    color: #2c3e50; border-left: 4px solid #3498db; }
        .account-section { margin-bottom: 30px; }
        .footer { margin-top: 30px; padding-top: 15px; border-top: 1px solid #ecf0f1; 
                 color: #7f8c8d; font-size: 0.9em; }
    </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
            <h2>Snowflake Password Expiry Report</h2>
            <p>Generated on: {date}</p>
        </div>
    """

    accounts = []
    current_account = {}
    
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Parse accounts and their data
    for line in lines:
        line = line.strip()
        
        # Detect account name
        account_match = re.search(r'SNOWFLAKE ACCOUNT NAME\s*:\s*(.*)', line, re.IGNORECASE)
        if account_match:
            if current_account:
                accounts.append(current_account)
            current_account = {
                'name': account_match.group(1).strip(),
                'has_expiry': False,
                'rows': []
            }
            continue
        
        # Detect table headers
        if current_account and '<th>' in line.lower():
            current_account['headers'] = line
            continue
            
        # Detect table rows
        if current_account and '<tr>' in line.lower() and '<td>' in line.lower():
            current_account['has_expiry'] = True
            current_account['rows'].append(line)
    
    if current_account:
        accounts.append(current_account)

    # Build HTML content
    html_body = html_template.format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    for account in accounts:
        html_body += f'<div class="account-section">'
        html_body += f'<h3>{account["name"]}</h3>'
        
        if account['has_expiry']:
            html_body += '<div class="table-container">'
            html_body += '<table>'
            html_body += '<thead>' + account.get('headers', '') + '</thead>'
            html_body += '<tbody>' + ''.join(account['rows']) + '</tbody>'
            html_body += '</table></div>'
        else:
            html_body += '<div class="no-expiry">No password expiries found for this account</div>'
        
        html_body += '</div>'  # Close account-section

    # Add footer
    html_body += """
        <div class="footer">
            <p>This is an automated report. Please contact IT Security with any questions.</p>
        </div>
    </div>
    </body>
    </html>
    """

    return html_body

