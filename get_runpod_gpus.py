import requests
import json
import os

def get_runpod_gpu_locations_graphql():
    """
    Fetches available GPU types from RunPod's GraphQL API.
    """
    api_url = "https://api.runpod.io/graphql"

    runpod_api_key = os.getenv('RUNPOD_API_KEY')

    if not runpod_api_key:
        print("Error: RUNPOD_API_KEY environment variable not set.")
        return []

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {runpod_api_key}",
    }

    # GraphQL query to get GPU types and their properties
    # You might need to adjust this query based on what fields RunPod's GraphQL API exposes for availability.
    # The 'locations' or 'datacenters' might be under a different query or nested within GPU objects.
    graphql_query = """
    query GpuTypes {
      gpuTypes {
        id
        displayName
        memoryInGb
        # There might be other fields like 'locations' or 'regions' here.
        # You'll need to inspect the actual response from the API.
        # For now, we'll just get the GPU types.
      }
    }
    """

    payload = {
        "query": graphql_query
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # The data structure for GraphQL responses is usually `data` -> `yourQueryName`
        if data and 'data' in data and 'gpuTypes' in data['data']:
            gpu_types = data['data']['gpuTypes']
            locations = set()
            
            # Since 'gpuTypes' might not directly contain 'datacenterId',
            # we'll list the available GPU display names as a form of "location/type".
            # If you find a field that directly indicates a physical location in the response,
            # you can adjust this logic to use it.
            for gpu_type in gpu_types:
                display_name = gpu_type.get('displayName')
                if display_name:
                    locations.add(display_name)
                # If you find location information (e.g., 'regions', 'datacenterId')
                # in the GPU type object, add it here:
                # if 'region' in gpu_type:
                #    locations.add(gpu_type['region'])


            if not locations:
                print("No GPU types found in GraphQL API response.")
                print("Please verify the GraphQL query and response structure.")
                return []
            
            return sorted(list(locations))
        else:
            print("Unexpected response structure from GraphQL API.")
            print(f"Full response: {json.dumps(data, indent=2)}")
            if 'errors' in data:
                print(f"GraphQL Errors: {json.dumps(data['errors'], indent=2)}")
            return []

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
    locations = get_runpod_gpu_locations_graphql()
    if locations:
        print("Available RunPod GPU Types/Locations:")
        for loc in locations:
            print(f"- {loc}")
    else:
        print("Could not retrieve RunPod GPU types/locations.")
