import requests
import json
import os

def get_runpod_gpu_locations():
    """
    Fetches available GPU locations from RunPod's REST API using an API Key.
    """
    # This is the expected endpoint for marketplace pods as per recent RunPod API docs.
    api_url = "https://rest.runpod.io/v1/marketplace/pods"

    runpod_api_key = os.getenv('RUNPOD_API_KEY')

    if not runpod_api_key:
        print("Error: RUNPOD_API_KEY environment variable not set.")
        return []

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {runpod_api_key}",
        # RunPod's REST API typically uses "Authorization: Bearer YOUR_API_KEY"
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # The response structure for this endpoint is likely a list of pod objects.
        # We want to extract 'gpuId' (the type) and 'dataCenterId' (the location).
        
        # Use a set to store unique combinations of GPU type and location
        available_gpu_locations = set()

        if data and isinstance(data, list): # Expecting a list of pod objects directly
            for pod in data:
                gpu_type = pod.get('gpuId')
                datacenter_id = pod.get('dataCenterId')
                
                if gpu_type and datacenter_id:
                    available_gpu_locations.add(f"{gpu_type} in {datacenter_id}")
                # You might also want to filter by 'minBidPrice', 'currentBidPrice', 'gpuCount', etc.
                # if pod.get('gpuCount', 0) > 0 and pod.get('has  InternetAccess', False):
                #     available_gpu_locations.add(f"{gpu_type} in {datacenter_id}")

        elif data and isinstance(data, dict) and 'pods' in data: # In case it's nested under a 'pods' key
             for pod in data['pods']:
                gpu_type = pod.get('gpuId')
                datacenter_id = pod.get('dataCenterId')
                if gpu_type and datacenter_id:
                    available_gpu_locations.add(f"{gpu_type} in {datacenter_id}")
        else:
            print("Unexpected response structure from RunPod API.")
            print(f"Full response: {json.dumps(data, indent=2)}")
            return []

        if not available_gpu_locations:
            print("No available GPU locations found. The API might not have returned any current pods.")
            print("Please check RunPod's marketplace or your API key's permissions.")
            return []
        
        return sorted(list(available_gpu_locations))

    except requests.exceptions.RequestException as e:
        print(f"Error making request to RunPod API: {e}")
        if 'response' in locals() and response is not None:
            print(f"RunPod API Response content (Error): {response.text}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response from RunPod API: {e}")
        if 'response' in locals() and response is not None:
            print(f"RunPod API Response content: {response.text}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

if __name__ == "__main__":
    locations = get_runpod_gpu_locations()
    if locations:
        print("Available RunPod GPU Types and Locations:")
        for loc in locations:
            print(f"- {loc}")
    else:
        print("Could not retrieve RunPod GPU types and locations.")
