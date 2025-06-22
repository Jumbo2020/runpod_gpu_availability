import requests
import json
import os
import time # For adding a small delay between requests

def get_runpod_all_gpu_info():
    """
    Fetches all available GPU types and their details from RunPod's GraphQL API,
    without applying any filtering based on stock status or specific GPU type.
    It iterates through all known datacenter IDs.
    """
    api_url = "https://api.runpod.io/graphql" # GraphQL endpoint

    runpod_api_key = os.getenv('RUNPOD_API_KEY')

    if not runpod_api_key:
        print("Error: RUNPOD_API_KEY environment variable not set.")
        return []

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {runpod_api_key}",
    }

    # --- IMPORTANT: MANUALLY UPDATE THIS LIST ---
    # For datacenter IDs, you need to manually collect them from the dropdown list on RunPod.io.
    ALL_DATACENTER_IDS = [
        "AP-JP-1", "CA-MTL-1", "CA-MTL-2", "EU-CZ-1", "EU-FI-1", "EU-NL-1",
        "EU-RO-1", "EU-SE-1", "EUR-IS-1", "EUR-IS-2", "EUR-IS-3", "OC-AU-1",
        "US-CA-2", "US-GA-2", "US-IL-1", "US-KS-2", "US-MD-1", "US-NC-1",
        "US-TX-3", "US-WA-1", "US-UT-1"
    ]
    # --- END OF MANUAL UPDATE SECTION ---

    # GraphQL Query - Modified to get all GPU types for a given datacenter
    # We remove the gpuTypesInput filter to fetch all GPU types from the 'lowestPrice' context.
    graphql_query_template = """
    query SecureGpuTypes($lowestPriceInput: GpuLowestPriceInput) {
      gpuTypes {
        lowestPrice(input: $lowestPriceInput) {
          minimumBidPrice
          uninterruptablePrice
          minVcpu
          minMemory
          stockStatus
          compliance
          maxUnreservedGpuCount
          availableGpuCounts
          __typename
        }
        id
        displayName
        memoryInGb
        securePrice
        communityPrice
        oneMonthPrice
        oneWeekPrice
        threeMonthPrice
        sixMonthPrice
        secureSpotPrice
        __typename
      }
    }
    """
    
    # Base lowestPriceInput - removed all filtering parameters
    base_lowest_price_input = {
        "gpuCount": 1, # Still requesting at least 1 GPU, as it's a common use case
        "minDisk": 0,
        "minMemoryInGb": 0, # Set to 0 to not filter by memory
        "minVcpuCount": 0, # Set to 0 to not filter by vCPU
        "secureCloud": False, # Set to False to include all cloud types
        "compliance": None,
        "globalNetwork": False
    }

    all_gpu_details = [] # Store all found GPU details

    for datacenter_id in ALL_DATACENTER_IDS:
        # Construct the variables for each specific query
        variables = {
            "lowestPriceInput": {
                **base_lowest_price_input, # Unpack base input
                "dataCenterId": datacenter_id # Add the specific datacenter ID
            }
        }

        payload = {
            "operationName": "SecureGpuTypes",
            "query": graphql_query_template,
            "variables": variables
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Process the response
            if data and 'data' in data and 'gpuTypes' in data['data']:
                for gpu_info in data['data']['gpuTypes']:
                    display_name = gpu_info.get('displayName', gpu_info.get('id', 'Unknown GPU'))
                    lowest_price_info = gpu_info.get('lowestPrice', {})

                    gpu_detail = {
                        "gpuType": display_name,
                        "datacenterId": datacenter_id,
                        "stockStatus": lowest_price_info.get('stockStatus'),
                        "minimumBidPrice": lowest_price_info.get('minimumBidPrice'),
                        "uninterruptablePrice": lowest_price_info.get('uninterruptablePrice'),
                        "availableGpuCounts": lowest_price_info.get('availableGpuCounts'),
                        "memoryInGb": gpu_info.get('memoryInGb'),
                        "minVcpu": lowest_price_info.get('minVcpu')
                        # Add any other fields you wish to retrieve
                    }
                    all_gpu_details.append(gpu_detail)
            elif 'errors' in data:
                print(f"GraphQL Errors for datacenter {datacenter_id}: {json.dumps(data['errors'], indent=2)}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request for datacenter {datacenter_id}: {e}")
            if 'response' in locals() and response is not None:
                print(f"RunPod API Response content (Error): {response.text}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response for datacenter {datacenter_id}: {e}")
            if 'response' in locals() and response is not None:
                print(f"RunPod API Response content: {response.text}")
        except Exception as e:
            print(f"An unexpected error occurred for datacenter {datacenter_id}: {e}")
            
        # Add a small delay to avoid hitting rate limits
        time.sleep(0.1) # 100 milliseconds delay

    return all_gpu_details

if __name__ == "__main__":
    all_info = get_runpod_all_gpu_info()
    if all_info:
        print("All RunPod GPU Information (without stock filtering):")
        # You might want to format this output differently due to the volume of data
        for gpu in all_info:
            print(json.dumps(gpu, indent=2))
            print("-" * 30) # Separator for readability
    else:
        print("Could not retrieve any RunPod GPU information.")
