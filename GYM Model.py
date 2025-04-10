import re 
import smtplib
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText

def generate_html_body(file_path):
    html_body = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            box-sizing: border-box;
        }
        .container {
            max-width: 1200px;
            margin: 20px auto;
            padding: 30px;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            border-bottom: 2px solid #2c3e50;
            margin-bottom: 25px;
            padding-bottom: 15px;
        }
        .header h3 {
            color: #2c3e50;
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }
        .table-container {
            overflow-x: auto;
            margin: 20px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            min-width: 600px;
            background: white;
        }
        th {
            background-color: #2c3e50;
            color: #ffffff;
            font-weight: 600;
            padding: 12px 15px;
            text-transform: uppercase;
            font-size: 0.9em;
        }
        td {
            padding: 12px 15px;
            color: #34495e;
            border-bottom: 1px solid #ecf0f1;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        tr:hover {
            background-color: #f1f5f7;
        }
        .footer {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 0.9em;
        }
    </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
    """

    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    current_section = None
    in_table = False

    for line in lines:
        line = line.strip()
        # Check for account name
        match = re.search(r'SNOWFLAKE ACCOUNT NAME\s*:\s*(.*)', line, re.IGNORECASE)
        if match:
            if in_table:
                html_body += "</table></div>"
                in_table = False
            account_name = match.group(1).strip()
            html_body += f'<h3>Snowflake Account: {account_name}</h3>'
            continue
        
        # Check for table headers
        if '<th>' in line.lower():
            if not in_table:
                html_body += '<div class="table-container"><table><thead>'
                in_table = True
            html_body += line.replace('<th>', '<th>').replace('</th>', '</th>')
            continue
        
        # Check for table rows
        if '<tr>' in line.lower():
            if not in_table:
                html_body += '<div class="table-container"><table><tbody>'
                in_table = True
            html_body += line.replace('<td>', '<td>').replace('</td>', '</td>')
            continue

    # Close final table if needed
    if in_table:
        html_body += "</tbody></table></div>"
    
    # Add footer
    html_body += """
        </div>
        <div class="footer">
            <p>This is an automated report. Please do not reply to this email.</p>
            <p>Generated on: [DATE]</p>
        </div>
    </div>
    </body>
    </html>
    """

    return html_body

if __name__ == "__main__":
    file_path = r'/tmp/snow_pass_expiry.out'
    html_content = generate_html_body(file_path)
    
    # Email configuration
    HOST = "mail.example.com"
    PORT = 25
    FROM_EMAIL = "snowflake@noreply.example.com"
    TO_EMAIL = "recipient1@example.com;recipient2@example.com"
    SUBJECT = "Snowflake Password Expiry Report"
    
    # Create message
    msg = MIMEMultipart('mixed')
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = SUBJECT
    
    # Attach HTML content
    msg.attach(MIMEText(html_content, 'html'))
    
    # Send email
    with smtplib.SMTP(HOST, PORT) as server:
        server.set_debuglevel(1)
        server.sendmail(FROM_EMAIL, TO_EMAIL.split(';'), msg.as_string())