import sys
from google.api_core import exceptions
from google.auth import exceptions as auth_exceptions
from googleapiclient import discovery
from google.auth import default
import json

def check_vertex_quotas():
    """
    Authenticates with GCP and retrieves quotas for the Vertex AI API.
    """
    try:
        credentials, project_id = default()

        if not project_id:
            print("Error: Could not determine Google Cloud project ID from credentials.")
            sys.exit(1)

        service_name = 'aiplatform.googleapis.com'
        print(f"Successfully authenticated. Using project: {project_id}")
        print(f"Fetching quotas for: {service_name}\n")

        service_usage_client = discovery.build('serviceusage', 'v1', credentials=credentials)

        parent = f'projects/{project_id}/services/{service_name}'
        
        request = service_usage_client.consumerQuotaMetrics().list(parent=parent)
        
        print(f"{ 'Quota Metric':<80} { 'Limit':<20} { 'Current Usage':<20}")
        print("-" * 120)

        while request is not None:
            response = request.execute()
            metrics = response.get('metrics', [])
            
            if not metrics:
                print("No quota metrics found for this service.")
                break

            for metric in metrics:
                metric_name = metric.get('displayName', 'N/A')
                
                limit_info = metric.get('consumerQuotaLimits', [{}])[0]
                quota_buckets = limit_info.get('quotaBuckets', [])

                limit_value = "N/A"
                # The bucket with 'per day' is often the most relevant one for daily quotas
                for bucket in quota_buckets:
                    if bucket.get('dimensions') and bucket['dimensions'].get('per_day'):
                        limit_value = bucket.get('effectiveLimit')
                        break
                if limit_value == "N/A": # fallback to first available limit
                    for bucket in quota_buckets:
                        if 'effectiveLimit' in bucket:
                            limit_value = bucket.get('effectiveLimit')
                            break

                current_usage = "0"
                for bucket in quota_buckets:
                    if 'consumedValue' in bucket:
                        current_usage = bucket.get('consumedValue')
                        break

                print(f"{metric_name:<80} {str(limit_value):<20} {str(current_usage):<20}")

            request = service_usage_client.consumerQuotaMetrics().list_next(
                previous_request=request, previous_response=response
            )

    except auth_exceptions.DefaultCredentialsError:
        print("Authentication failed. Please run 'gcloud auth application-default login'.")
        sys.exit(1)
    except exceptions.PermissionDenied as e:
        print(f"Permission Denied: {e}")
        print("The authenticated user may not have the 'serviceusage.services.get' permission.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_vertex_quotas()