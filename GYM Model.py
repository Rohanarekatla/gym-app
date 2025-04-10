import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def generate_html_body(file_path):
    html_body = """
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #ffffff; border-radius: 5px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
        <div style="background-color: #0066cc; color: white; padding: 15px 20px; border-radius: 5px 5px 0 0; margin: -20px -20px 20px;">
            <h1 style="margin: 0; font-size: 24px; font-weight: 500;">Snowflake Password Expiry Report</h1>
        </div>
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
                table-layout: fixed;
                margin-bottom: 15px;
                border-radius: 3px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            th, td {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            th {
                background-color: #e6f0ff;
                color: #0066cc;
                font-weight: 600;
                font-size: 12px;
            }
            tr:nth-child(even) {
                background-color: #f5f9ff;
            }
            .warning {
                background-color: #fff8e6;
            }
            .critical {
                background-color: #fff0f0;
            }
        </style>
    """

    with open(file_path, 'r') as file:
        lines = file.readlines()
        current_section = None
        in_table = False

        for line in lines:
            line = line.strip()
            
            # Check for account name
            match = re.search(r'SNOWFLAKE ACOUNT NAME\s*:\s*(.*)', line)
            if match:
                if in_table:
                    html_body += "</table>"
                    in_table = False
                
                account_name = match.group(1).strip()
                html_body += f'<div style="background-color: #f0f7ff; padding: 10px 15px; border-left: 4px solid #0066cc; margin-bottom: 20px; border-radius: 0 5px 5px 0;"><h3 style="color: #333333; margin: 0;">Snowflake Account Name: {account_name}</h3></div>'
                html_body += "<table>"
                in_table = True
                continue
                
            # Check for table headers
            if '<tr><th>' in line:
                html_body += line
                continue
                
            # Check for table data
            if '<tr><td>' in line:
                # Preserving original functionality while adding styling
                # Check if this row contains information about expiring passwords
                if 'expir' in line.lower() and 'days' in line.lower():
                    # Try to extract days until expiry
                    days_match = re.search(r'(\d+)\s*days', line.lower())
                    if days_match:
                        days = int(days_match.group(1))
                        if days <= 7:
                            line = line.replace('<tr><td>', '<tr style="background-color: #fff0f0;"><td>')
                        elif days <= 14:
                            line = line.replace('<tr><td>', '<tr style="background-color: #fff8e6;"><td>')
                
                html_body += line
                continue
    
        # Close the last table if needed
        if in_table:
            html_body += "</table>"
    
    html_body += """
        <div style="font-size: 12px; color: #666666; text-align: center; margin-top: 20px; padding-top: 15px; border-top: 1px solid #eeeeee;">
            <p>This is an automated report. Please do not reply to this email.</p>
            <p>For support, please contact your Snowflake administrator.</p>
        </div>
    </div>
    """
    
    return html_body

