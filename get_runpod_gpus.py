import requests
import json
import os
import time # For adding a small delay between requests

def get_runpod_gpu_locations_detailed():
    """
    Fetches available GPU types and their locations from RunPod's GraphQL API.
    Iterates through known GPU types and data center IDs.
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

    # --- IMPORTANT: MANUALLY UPDATE THESE LISTS ---
    # You need to get these lists from RunPod's website or other API calls if available.
    # For GPU types, you can use the previous 'GpuTypes' query you tried.
    # For datacenter IDs, you need to manually collect them from the dropdown list on RunPod.io.
    ALL_GPU_TYPES = [
        "NVIDIA A100 PCIe", "NVIDIA A100 SXM", "NVIDIA A30", "NVIDIA A40",
        "NVIDIA B200", "NVIDIA H100 NVL", "NVIDIA H100 PCIe", "NVIDIA H100 SXM",
        "NVIDIA H200 SXM", "NVIDIA L4", "NVIDIA L40", "NVIDIA L40S", "AMD MI300X",
        "NVIDIA RTX 2000 Ada", "NVIDIA RTX 3070", "NVIDIA RTX 3080", "NVIDIA RTX 3080 Ti",
        "NVIDIA RTX 3090", "NVIDIA RTX 3090 Ti", "NVIDIA RTX 4000 Ada", "NVIDIA RTX 4070 Ti",
        "NVIDIA RTX 4080", "NVIDIA RTX 4080 SUPER", "NVIDIA RTX 4090", "NVIDIA RTX 5000 Ada",
        "NVIDIA RTX 5080", "NVIDIA RTX 5090", "NVIDIA RTX 6000 Ada", "NVIDIA RTX A2000",
        "NVIDIA RTX A4000", "NVIDIA RTX A4500", "NVIDIA RTX A5000", "NVIDIA RTX A6000",
        "NVIDIA RTX PRO 6000", "NVIDIA Tesla V100", "NVIDIA V100 FHHL", "NVIDIA V100 SXM2",
        "NVIDIA V100 SXM2 32GB", "UNKNOWN_GPU" # Add UNKNOWN_GPU if it appears in their type list.
    ]

    ALL_DATACENTER_IDS = [
        "AP-JP-1", "CA-MTL-1", "CA-MTL-2", # ... add all other IDs from the dropdown
        "EU-CZ-1", "EU-FI-1", "EU-NL-1", "EU-RO-1", "EU-SE-1", "EUR-IS-1", "EUR-IS-2", "EUR-IS-3",
        "OC-AU-1", "US-CA-2", "US-GA-2", "US-IL-1", "US-KS-2", "US-MD-1", "US-NC-1", "US-TX-3",
        "US-WA-1", "US-UT-1"
    ]
    # --- END OF MANUAL UPDATE SECTION ---


    # GraphQL Query - copied from your payload
    # Note the variables ($lowestPriceInput, $gpuTypesInput) in the query definition
    graphql_query_template = """
    query SecureGpuTypes($lowestPriceInput: GpuLowestPriceInput, $gpuTypesInput: GpuTypeFilter) {
      gpuTypes(input: $gpuTypesInput) {
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
    
    # Base lowestPriceInput - copied from your payload
    base_lowest_price_input = {
        "gpuCount": 1,
        "minDisk": 0,
        "minMemoryInGb": 8,
        "minVcpuCount": 2,
        "secureCloud": True,
        "compliance": None, # Null value for compliance
        "globalNetwork": False # As seen in your payload
    }


    found_gpu_locations = set() # Store unique combinations of GPU and Location

    for gpu_type_id in ALL_GPU_TYPES:
        for datacenter_id in ALL_DATACENTER_IDS:
            # Construct the variables for each specific query
            variables = {
                "gpuTypesInput": {
                    "id": gpu_type_id
                },
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
                    # Assuming gpuTypes will contain at most one entry for the specific GPU ID requested
                    if data['data']['gpuTypes']:
                        gpu_info = data['data']['gpuTypes'][0]
                        display_name = gpu_info.get('displayName', gpu_type_id)
                        lowest_price_info = gpu_info.get('lowestPrice', {})
                        stock_status = lowest_price_info.get('stockStatus')
                        
                        if stock_status and stock_status != "None" and stock_status != "Unavailable" and lowest_price_info.get('availableGpuCounts'):
                            # Consider it available if stockStatus is not null/None/Unavailable
                            # and if there are actual available counts (can adjust this logic)
                            found_gpu_locations.add(f"{display_name} in {datacenter_id} (Status: {stock_status})")
                elif 'errors' in data:
                    print(f"GraphQL Errors for {gpu_type_id} in {datacenter_id}: {json.dumps(data['errors'], indent=2)}")
                
            except requests.exceptions.RequestException as e:
                print(f"Error making request for {gpu_type_id} in {datacenter_id}: {e}")
                if 'response' in locals() and response is not None:
                    print(f"RunPod API Response content (Error): {response.text}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response for {gpu_type_id} in {datacenter_id}: {e}")
                if 'response' in locals() and response is not None:
                    print(f"RunPod API Response content: {response.text}")
            except Exception as e:
                print(f"An unexpected error occurred for {gpu_type_id} in {datacenter_id}: {e}")
            
            # Add a small delay to avoid hitting rate limits
            time.sleep(0.1) # 100 milliseconds delay

    return sorted(list(found_gpu_locations))

if __name__ == "__main__":
    locations = get_runpod_gpu_locations_detailed()
    if locations:
        print("Available RunPod GPU Types and Locations with Stock Status:")
        for loc in locations:
            print(f"- {loc}")
    else:
        print("Could not retrieve RunPod GPU types and locations, or none are available.")
