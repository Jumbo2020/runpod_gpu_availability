import requests
import json

def get_runpod_gpu_locations():
    """
    Fetches available GPU locations from RunPod's public API.
    """
    api_url = "https://www.runpod.io/api/v2/marketplace/pods"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # RunPod's API might change, so we need to inspect the structure.
        # As of my last knowledge update, available pods might be under 'pods' key
        # and locations under 'datacenterId' or similar.
        
        available_locations = set() # Use a set to store unique locations

        if data and isinstance(data, dict) and 'pods' in data:
            for pod in data['pods']:
                if 'datacenterId' in pod:
                    available_locations.add(pod['datacenterId'])
                # You might also find 'gpu' or 'gpuCount' in some pod entries
                # to filter for actual GPU pods if needed.
        elif isinstance(data, list): # Some APIs might return a list directly
            for item in data:
                if 'datacenterId' in item:
                    available_locations.add(item['datacenterId'])
                    
        # If the direct API above doesn't yield results, you might need to
        # explore the RunPod website's network requests in your browser's
        # developer tools to find the exact endpoint for available regions/GPUs.
        # RunPod sometimes changes its public facing API for marketplace data.

        if not available_locations:
            print("No specific GPU locations found using 'datacenterId'.")
            print("Please inspect RunPod's API documentation or network traffic for the correct field.")
            return []
        
        return sorted(list(available_locations))

    except requests.exceptions.RequestException as e:
        print(f"Error making request to RunPod API: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response from RunPod API: {e}")
        print(f"Response content: {response.text}")
        return []

if __name__ == "__main__":
    locations = get_runpod_gpu_locations()
    if locations:
        print("Available RunPod GPU Locations:")
        for loc in locations:
            print(f"- {loc}")
    else:
        print("Could not retrieve RunPod GPU locations.")
