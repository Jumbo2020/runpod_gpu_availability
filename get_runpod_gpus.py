import requests
import json
import os

def get_runpod_gpu_locations():
    """
    Fetches available GPU locations from RunPod's API using an API Key.
    """
    api_url = "https://api.runpod.io/v2/user/pods" # Example URL - verify with RunPod API documentation

    runpod_api_key = os.getenv('RUNPOD_API_KEY')

    if not runpod_api_key:
        print("Error: RUNPOD_API_KEY environment variable not set.")
        return []

    headers = {
        "Authorization": f"Bearer {runpod_api_key}",
        # Verify the correct header for RunPod API Key. It might be "X-Api-Key" or "Api-Key".
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        available_locations = set()
        
        # Adjust parsing logic based on actual RunPod API response structure.
        if isinstance(data, dict) and 'pods' in data:
            for pod in data['pods']:
                if 'datacenterId' in pod:
                    available_locations.add(pod['datacenterId'])
        elif isinstance(data, list):
             for item in data:
                if 'datacenterId' in item:
                    available_locations.add(item['datacenterId'])
        
        if not available_locations:
            print("No specific GPU locations found in API response.")
            print("Please verify the API endpoint and response structure.")
            return []
        
        return sorted(list(available_locations))

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
        print("Available RunPod GPU Locations:")
        for loc in locations:
            print(f"- {loc}")
    else:
        print("Could not retrieve RunPod GPU locations.")
