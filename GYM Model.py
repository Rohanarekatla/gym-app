import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def generate_html_body(file_path):
    html_body = """
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #ffffff; border-radius: 5px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
        <div style="background-color: #003366; color: white; padding: 15px 20px; border-radius: 5px 5px 0 0; margin: -20px -20px 20px;">
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
                background-color: #003366;
                color: white;
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

    accounts_without_details = []
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        current_account = None
        in_table = False
        has_data = False
        buffer = ""  # Buffer to store current account's HTML content
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for account name
            match = re.search(r'SNOWFLAKE ACOUNT NAME\s*:\s*(.*)', line)
            if match:
                # If we were processing a previous account
                if current_account:
                    # Close table if needed
                    if in_table:
                        buffer += "</table>"
                        in_table = False
                    
                    # If data was found for previous account, add the buffer to html_body
                    # Otherwise, add account to the list of accounts without details
                    if has_data:
                        html_body += buffer
                    else:
                        accounts_without_details.append(current_account)
                
                # Start processing new account
                current_account = match.group(1).strip()
                has_data = False  # Reset data flag for new account
                buffer = ""  # Reset buffer
                
                # Look ahead to see if there's any data for this account
                # Prepare buffer but don't add to html_body yet
                buffer += f'<div style="background-color: #e6eef7; padding: 10px 15px; border-left: 4px solid #003366; margin-bottom: 20px; border-radius: 0 5px 5px 0;"><h3 style="color: #333333; margin: 0;">Snowflake Account Name: {current_account}</h3></div>'
                buffer += "<table>"
                in_table = True
                i += 1
                continue
                
            # Check for table headers
            if '<tr><th>' in line:
                buffer += line
                i += 1
                continue
                
            # Check for table data
            if '<tr><td>' in line:
                has_data = True  # We found data for this account
                
                # Style rows based on expiry days
                if 'expir' in line.lower() and 'days' in line.lower():
                    days_match = re.search(r'(\d+)\s*days', line.lower())
                    if days_match:
                        days = int(days_match.group(1))
                        if days <= 7:
                            line = line.replace('<tr><td>', '<tr style="background-color: #fff0f0;"><td>')
                        elif days <= 14:
                            line = line.replace('<tr><td>', '<tr style="background-color: #fff8e6;"><td>')
                
                buffer += line
                i += 1
                continue
            
            i += 1
    
        # Process the last account
        if current_account:
            if in_table:
                buffer += "</table>"
            
            if has_data:
                html_body += buffer
            else:
                accounts_without_details.append(current_account)
    
    # Add section for accounts without expiry details
    if accounts_without_details:
        html_body += """
        <div style="background-color: #e6eef7; padding: 10px 15px; border-left: 4px solid #003366; margin: 30px 0 20px; border-radius: 0 5px 5px 0;">
            <h3 style="color: #333333; margin: 0;">Accounts with No Expiry Details</h3>
        </div>
        """
        html_body += "<ul style='padding-left: 20px; color: #555;'>"
        for account in accounts_without_details:
            html_body += f"<li style='margin-bottom: 5px;'>{account}</li>"
        html_body += "</ul>"
        html_body += "<p style='color: #666; font-style: italic; margin-top: 10px;'>No password expiry details found for the above accounts.</p>"
    
    html_body += """
        <div style="font-size: 12px; color: #666666; text-align: center; margin-top: 20px; padding-top: 15px; border-top: 1px solid #eeeeee;">
            <p>This is an automated report. Please do not reply to this email.</p>
            <p>For support, please contact your Snowflake administrator.</p>
        </div>
    </div>
    """
    
    return html_body

