import os
import json
import time
from google.cloud import compute_v1
from google.oauth2 import service_account
from google.api_core import exceptions

def get_gcp_gpu_locations_detailed():
    """
    Fetches available GPU types and their locations from GCP Compute Engine API.
    """
    # Load credentials from environment variable or file
    service_account_key_json = os.getenv('GCP_SERVICE_ACCOUNT_KEY')
    if not service_account_key_json:
        print("Error: GCP_SERVICE_ACCOUNT_KEY environment variable not set.")
        return []

    try:
        # Parse the JSON string from environment variable
        credentials_info = json.loads(service_account_key_json)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
    except json.JSONDecodeError as e:
        print(f"Error decoding GCP service account JSON: {e}")
        return []
    except Exception as e:
        print(f"Error setting up GCP credentials: {e}")
        return []

    # Initialize Compute Engine client
    compute_client = compute_v1.AcceleratorTypesClient(credentials=credentials)
    zone_client = compute_v1.ZonesClient(credentials=credentials)

    # List of known GPU types supported by GCP (based on provided web results)
    GPU_TYPES = [
        "nvidia-tesla-t4",
        "nvidia-tesla-v100",
        "nvidia-tesla-p100",
        "nvidia-tesla-p4",
        "nvidia-l4",
        "nvidia-a100-80gb",
        "nvidia-a100-40gb",
        "nvidia-h100-80gb",
        "nvidia-h200-141gb",
        "nvidia-b200",
        "nvidia-gb200"
    ]

    found_gpu_locations = set()

    try:
        # Get all available zones
        project = credentials_info.get('project_id')
        if not project:
            print("Error: Project ID not found in service account JSON.")
            return []

        zones = zone_client.list(project=project)

        for zone in zones:
            for gpu_type in GPU_TYPES:
                try:
                    # Check accelerator availability in the zone
                    accelerators = compute_client.list(project=project, zone=zone.name)
                    for accelerator in accelerators:
                        if accelerator.name == gpu_type:
                            # Verify resource availability by attempting to get machine types
                            # This is a proxy to check if resources are actually available
                            machine_client = compute_v1.MachineTypesClient(credentials=credentials)
                            try:
                                machine_types = machine_client.list(project=project, zone=zone.name)
                                # If we can list machine types, assume the zone is active
                                found_gpu_locations.add(f"{gpu_type} in {zone.name} (Region: {zone.region.split('/')[-1]})")
                            except exceptions.ResourceExhausted:
                                # ResourceExhausted indicates the zone might not have available resources
                                continue
                            except exceptions.ClientError as e:
                                print(f"Client error checking machine types in {zone.name} for {gpu_type}: {e}")
                                continue
                except exceptions.ClientError as e:
                    print(f"Error checking GPU {gpu_type} in {zone.name}: {e}")
                except Exception as e:
                    print(f"Unexpected error for {gpu_type} in {zone.name}: {e}")
                
                # Add a small delay to avoid hitting rate limits
                time.sleep(0.1)
    
    except exceptions.ClientError as e:
        print(f"Error accessing GCP Compute API: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return sorted(list(found_gpu_locations))

if __name__ == "__main__":
    locations = get_gcp_gpu_locations_detailed()
    if locations:
        print("Available GCP GPU Types and Locations:")
        for loc in locations:
            print(f"- {loc}")
    else:
        print("Could not retrieve GCP GPU types and locations, or none are available.")
