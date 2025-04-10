import requests
import re
import pandas as pd
from azure.identity import ClientSecretCredential

# Configuration
TENANT_ID = 'your_tenant_id'
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'

# Regex patterns
APP_NAME_PATTERN = re.compile(r'^snowflake-c\d{3}-.+?-client-spn0\d+$', re.IGNORECASE)
CONFIRMATION_NAME_PATTERN = re.compile(r'(c\d{3}-x\d-0\d{2})', re.IGNORECASE)
ENV_PATTERN = re.compile(r'\b(prod|dev|uat|buat)0?\d*\b', re.IGNORECASE)

# Authenticate and get token
credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
token = credential.get_token('https://graph.microsoft.com/.default').token
headers = {'Authorization': f'Bearer {token}'}

def get_all_apps():
    """Retrieve all application registrations with pagination"""
    all_apps = []
    url = 'https://graph.microsoft.com/v1.0/applications'
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        all_apps.extend(data['value'])
        url = data.get('@odata.nextLink')
    return all_apps

def process_applications(all_apps):
    """Process applications and collect required data"""
    apps_by_app_id = {app['appId']: app for app in all_apps}
    results = []
    
    for app in all_apps:
        app_name = app.get('displayName', '')
        
        # Validate app name pattern
        if not APP_NAME_PATTERN.match(app_name):
            continue
        
        # Extract confirmation name
        conf_match = CONFIRMATION_NAME_PATTERN.search(app_name)
        if not conf_match:
            continue
        confirmation_name = conf_match.group(1).upper()  # Normalize to uppercase
        
        # Process API permissions
        for resource_access in app.get('requiredResourceAccess', []):
            resource_app = apps_by_app_id.get(resource_access['resourceAppId'])
            if not resource_app or 'snowflake' not in resource_app['displayName'].lower():
                continue
                
            for access in resource_access.get('resourceAccess', []):
                perm = find_permission(resource_app, access['id'], access['type'])
                if perm:
                    env_match = ENV_PATTERN.search(perm.get('description', ''))
                    results.append({
                        'Application Name': app_name,
                        'Client ID': app['appId'],
                        'Confirmation Name': confirmation_name,
                        'API Name': resource_app['displayName'],
                        'Permission Description': perm.get('description'),
                        'Environment': env_match.group(0).upper() if env_match else 'N/A'
                    })
    return results

def find_permission(resource_app, perm_id, perm_type):
    """Find permission details in resource application"""
    if perm_type == 'Scope':
        return next((s for s in resource_app.get('oauth2PermissionScopes', []) if s['id'] == perm_id), None)
    elif perm_type == 'Role':
        return next((r for r in resource_app.get('appRoles', []) if r['id'] == perm_id), None)
    return None

# Main execution
if __name__ == '__main__':
    try:
        all_applications = get_all_apps()
        report_data = process_applications(all_applications)
        
        if report_data:
            pd.DataFrame(report_data).to_excel('snowflake_app_audit.xlsx', index=False)
            print("Successfully generated audit report")
        else:
            print("No matching applications found")
    except Exception as e:
        print(f"Error occurred: {str(e)}")