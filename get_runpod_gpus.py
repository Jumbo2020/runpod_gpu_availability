import requests
import json
import os # ייבוא מודול os כדי לגשת למשתני סביבה

def get_runpod_gpu_locations():
    """
    Fetches available GPU locations from RunPod's API using an API Key.
    """
    # חשוב: יש לוודא שזו נקודת הקצה הנכונה של RunPod שדורשת API Key!
    # ייתכן שהנקודה הציבורית הקודמת (marketplace/pods) לא דורשת מפתח,
    # ואם תשתמש במפתח איתה, היא עלולה להיכשל או להחזיר שגיאה.
    # סביר להניח שתצטרך נקודת קצה אחרת עבור שימוש עם API Key.
    # לדוגמה: api_url = "https://api.runpod.io/v2/user/pods" או משהו דומה
    # בדוק את תיעוד ה-API של RunPod עבור נקודת קצה ספציפית זו.
    api_url = "https://api.runpod.io/v2/user/pods" # דוגמה לנקודת קצה שדורשת אימות
    # אם אתה רוצה מידע על ה-marketplace, ייתכן שנקודת הקצה תהיה שונה.
    # הנקודה שהחזירה 404 מקודם אולי עדיין קיימת אך שינתה שם או דורשת משהו אחר.
    # אם אין לך תיעוד API ספציפי מ-RunPod, תצטרך לנסות למצוא אותה דרך ה-Network tab בדפדפן.


    runpod_api_key = os.getenv('RUNPOD_API_KEY') # קריאת ה-API Key ממשתנה הסביבה

    if not runpod_api_key:
        print("Error: RUNPOD_API_KEY environment variable not set.")
        return []

    headers = {
        "Authorization": f"Bearer {runpod_api_key}", # דרך מקובלת להעביר API Key
        # לעיתים, API Key מועבר בכותרת אחרת כמו "X-Api-Key" או "Api-Key"
        # בדוק את תיעוד RunPod ספציפית לאיך להעביר את המפתח.
        # אם יש לך את ה-ID של המשתמש, ייתכן שתצטרך גם "X-User-Id": "YOUR_USER_ID"
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        available_locations = set()

        # המבנה של התגובה מ-API מאומת יכול להיות שונה מה-API הציבורי.
        # סביר להניח שזה יחזיר רשימה של פודים ששייכים לחשבון שלך,
        # או פודים זמינים שניתן ליצור.
        # תצטרך לבדוק את מבנה התגובה בפועל.
        
        # דוגמה למבנה תגובה נפוץ:
        if isinstance(data, dict) and 'pods' in data: # או 'availablePods', 'regions', וכו'
            for pod in data['pods']: # או 'items', 'instances'
                if 'datacenterId' in pod:
                    available_locations.add(pod['datacenterId'])
                # ייתכן שתרצה גם לסנן לפי 'gpuType', 'gpuCount', 'status' וכו'.
        elif isinstance(data, list): # אם התגובה היא ישירות רשימת אובייקטים
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
        # הדפסת התוכן של התגובה במקרה של שגיאה, אם קיימת
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
