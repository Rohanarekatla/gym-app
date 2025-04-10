import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def generate_html_body(file_path):
    html_body = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Snowflake Password Expiry Report</title>
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f9f9f9;
                color: #333333;
                line-height: 1.6;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            .header {
                background-color: #0066cc;
                color: white;
                padding: 15px 20px;
                border-radius: 5px 5px 0 0;
                margin: -20px -20px 20px;
            }
            .header h1 {
                margin: 0;
                font-size: 24px;
                font-weight: 500;
            }
            .account-info {
                background-color: #f0f7ff;
                padding: 10px 15px;
                border-left: 4px solid #0066cc;
                margin-bottom: 20px;
                border-radius: 0 5px 5px 0;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 20px;
                border-radius: 5px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            th {
                background-color: #e6f0ff;
                color: #0066cc;
                font-weight: 600;
                text-align: left;
                padding: 12px 10px;
                font-size: 12px;
                text-transform: uppercase;
                border: 1px solid #d1e5ff;
            }
            td {
                padding: 10px;
                border: 1px solid #e6e6e6;
                font-size: 13px;
            }
            tr:nth-child(even) {
                background-color: #f5f9ff;
            }
            tr:hover {
                background-color: #e9f3ff;
            }
            .footer {
                font-size: 12px;
                color: #666666;
                text-align: center;
                margin-top: 20px;
                padding-top: 15px;
                border-top: 1px solid #eeeeee;
            }
            .warning {
                background-color: #fff8e6;
                color: #e67700;
            }
            .critical {
                background-color: #fff0f0;
                color: #cc0000;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Snowflake Password Expiry Report</h1>
            </div>
    """
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        current_section = None
        in_table = False

        for line in lines:
            line = line.strip()
            
            # Check for account name
            match = re.search(r'SNOWFLAKE ACCOUNT NAME\s*:\s*(.*)', line)
            if match:
                if in_table:
                    html_body += "</table>"
                    in_table = False
                
                account_name = match.group(1).strip()
                html_body += f'<div class="account-info"><h2>Account: {account_name}</h2></div>'
                html_body += "<table>"
                html_body += "<thead>"
                in_table = True
                continue
                
            # Check for table headers
            if '<tr><th>' in line:
                # Make the header row nicer
                line = line.replace('<tr><th>', '<tr><th>')  # Keep the original but add styling
                html_body += line
                html_body += "</thead><tbody>"
                continue
                
            # Check for table data
            if '<tr><td>' in line:
                # Check if this row contains information about expiring passwords
                if 'expir' in line.lower():
                    if 'days' in line.lower():
                        # Try to extract days until expiry
                        days_match = re.search(r'(\d+)\s*days', line.lower())
                        if days_match:
                            days = int(days_match.group(1))
                            if days <= 7:
                                line = line.replace('<tr><td>', '<tr class="critical"><td>')
                            elif days <= 14:
                                line = line.replace('<tr><td>', '<tr class="warning"><td>')
                
                html_body += line
                continue
    
        # Close the last table if needed
        if in_table:
            html_body += "</tbody></table>"
    
    html_body += """
            <div class="footer">
                <p>This is an automated report. Please do not reply to this email.</p>
                <p>For support, please contact your Snowflake administrator.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_body