
import sys
from google.api_core import exceptions
from google.auth import exceptions as auth_exceptions
from googleapiclient import discovery
from google.auth import default

def test_compute_quota_call():
    """
    Tests the consumerQuotaMetrics API call using 'compute.googleapis.com'.
    """
    try:
        credentials, project_id = default()

        if not project_id:
            print("Error: Could not determine Google Cloud project ID.")
            sys.exit(1)

        # Using 'compute.googleapis.com' as a test case from a working example
        service_name = 'compute.googleapis.com'
        print(f"Attempting to call consumerQuotaMetrics API with project: {project_id}")
        print(f"Using service: {service_name}\n")

        service_usage_client = discovery.build('serviceusage', 'v1', credentials=credentials)

        parent = f'projects/{project_id}/services/{service_name}'
        
        # This is the call that has been failing.
        request = service_usage_client.services().consumerQuotaMetrics().list(parent=parent)
        
        print("Successfully created the API request object.")
        response = request.execute()
        print("Successfully executed the API request.")

        metrics = response.get('metrics', [])
        if metrics:
            print(f"\nSuccessfully retrieved {len(metrics)} quota metrics for {service_name}.")
            print("This confirms the API call structure is correct.")
        else:
            # It's possible compute is enabled but has no specific quotas listed this way
            print(f"\nAPI call successful, but no quota metrics were returned for {service_name}.")
            print("This still confirms the API call structure is correct.")


    except exceptions.PermissionDenied as e:
        if "service is not enabled" in str(e):
            print(f"Test failed because the service '{service_name}' is not enabled for this project.")
            print("This is an expected outcome if you don't use Compute Engine.")
        else:
            print(f"Permission Denied: {e}")
    except AttributeError as e:
        print(f"TEST FAILED: {e}")
        print("This confirms the issue is not specific to the service being queried.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_compute_quota_call()
