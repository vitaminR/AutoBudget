import sys
from google.api_core import exceptions
from google.auth import exceptions as auth_exceptions
from googleapiclient import discovery
from google.auth import default

def check_gcp_services():
    """
    Authenticates with GCP and lists enabled services to find the correct one for quota checking.
    """
    try:
        # Authenticate using Application Default Credentials (ADC).
        # This looks for credentials set by `gcloud auth application-default login`
        # or the GOOGLE_APPLICATION_CREDENTIALS environment variable.
        credentials, project_id = default()

        if not project_id:
            print("Error: Could not determine Google Cloud project ID from credentials.")
            print("Please configure it using 'gcloud config set project YOUR_PROJECT_ID'")
            sys.exit(1)

        print(f"Successfully authenticated. Using project: {project_id}\n")

        # Create a client for the Service Usage API
        service_usage_client = discovery.build('serviceusage', 'v1', credentials=credentials)

        # List enabled services for the project
        print("Fetching enabled services (this may take a moment)...")
        request = service_usage_client.services().list(
            parent=f'projects/{project_id}',
            filter='state:ENABLED'
        )
        
        enabled_services = []
        while request is not None:
            response = request.execute()
            services = response.get('services', [])
            enabled_services.extend(services)
            request = service_usage_client.services().list_next(previous_request=request, previous_response=response)

        if not enabled_services:
            print("No enabled services found for this project.")
            return

        print("Found the following enabled services:")
        print("-" * 40)
        for service in enabled_services:
            # The name is usually in the format projects/123456/services/SERVICE_NAME
            service_name = service.get('config', {}).get('name', 'N/A')
            service_title = service.get('config', {}).get('title', 'N/A')
            print(f"- {service_name} ({service_title})")
        print("-" * 40)
        print("\nPlease look for a service related to 'AI Platform', 'Generative Language', or 'Vertex AI'.")
        print("Once you identify the correct service name, I can write another script to check its specific quotas.")


    except auth_exceptions.DefaultCredentialsError:
        print("Authentication failed. Could not find default credentials.")
        print("Please run 'gcloud auth application-default login' in your terminal and try again.")
        print("You may need to install the gcloud CLI first.")
        sys.exit(1)
    except exceptions.PermissionDenied as e:
        print(f"Permission Denied: {e}")
        print("The authenticated user may not have the 'serviceusage.services.list' permission.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_gcp_services()
