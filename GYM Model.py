import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def generate_html_body(file_path):
    # CSS with escaped curly braces
    css_style = """
    <style>
        * {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            box-sizing: border-box;
        }}
        .container {{
            max-width: 1200px;
            margin: 20px auto;
            padding: 30px;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 2px solid #2c3e50;
            margin-bottom: 25px;
            padding-bottom: 15px;
        }}
        .header h2 {{
            color: #2c3e50;
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .table-container {{
            margin: 20px 0;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            min-width: 600px;
        }}
        th {{
            background-color: #2c3e50;
            color: #fff;
            padding: 12px 15px;
            text-transform: uppercase;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
            color: #34495e;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .no-expiry {{
            background: #f1f5f7;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
            color: #2c3e50;
            border-left: 4px solid #3498db;
        }}
        .account-section {{
            margin-bottom: 30px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
    """

    html_template = f"""<!DOCTYPE html>
    <html>
    <head>
        {css_style}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Snowflake Password Expiry Report</h2>
                <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
    """

    accounts = []
    current_account = None

    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                
                # Detect account name
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
                    # Detect table headers
                    if '<th>' in line.lower():
                        current_account['headers'] = line
                    
                    # Detect table rows
                    if '<tr>' in line.lower() and '<td>' in line.lower():
                        current_account['has_expiry'] = True
                        current_account['rows'].append(line)

            # Add the last account
            if current_account:
                accounts.append(current_account)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return ""

    # Build HTML content
    for account in accounts:
        html_template += f'<div class="account-section">'
        html_template += f'<h3>{account.get("name", "Unnamed Account")}</h3>'
        
        if account.get('has_expiry', False):
            html_template += '<div class="table-container">'
            html_template += '<table>'
            html_template += f'<thead>{account.get("headers", "")}</thead>'
            html_template += f'<tbody>{"".join(account.get("rows", []))}</tbody>'
            html_template += '</table></div>'
        else:
            html_template += '<div class="no-expiry">No password expiries found for this account</div>'
        
        html_template += '</div>'  # Close account-section

    # Add footer
    html_template += """
            <div class="footer">
                <p>This is an automated report. Please contact IT Security with any questions.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html_template
