import os
import requests
import json

API_URL = "https://api.runpod.io/graphql"
API_KEY = os.getenv("RUNPOD_API_KEY")

if not API_KEY:
    print("❌ Missing RUNPOD_API_KEY environment variable")
    exit(1)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

query = {
    "query": """
    query AllGpuTypes {
      gpuTypes {
        id
        displayName
        securePrice
        memoryInGb
        regions {
          id
          name
        }
      }
    }
    """
}

print("🚀 Sending request to RunPod API...")
try:
    response = requests.post(API_URL, headers=headers, json=query)
    if response.status_code != 200:
        print(f"❌ Failed to fetch data from RunPod")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        exit(1)

    data = response.json()
    with open("runpod_gpu_locations.json", "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Data saved to runpod_gpu_locations.json")

except Exception as e:
    print("❌ Exception occurred:", e)
    exit(1)
