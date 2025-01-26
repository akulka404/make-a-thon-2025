import requests
from datetime import datetime, timedelta

# Your local Django API endpoints
API_URL = "http://127.0.0.1:8000/api/log_items/food_data/"  # Replace with your actual endpoint
UPDATE_URL = "http://127.0.0.1:8000/api/log_items/food_data/"  # Replace with the update endpoint

# Your Pushcut webhook URL
PUSHCUT_URL = "https://api.pushcut.io/Z3yNUruw-fsKJdKjucv3L/notifications/Make-A-Thon'25"  # Replace <YOUR-WEBHOOK-URL> with your Pushcut webhook URL

# Time offset between the Django API clock and your local clock (in hours)
TIME_OFFSET = timedelta(hours=5)

def fetch_data():
    """
    Fetch data from the Django API.
    """
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()  # Assuming the API returns JSON
        else:
            print(f"Failed to fetch data: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def get_items_expiring_or_expired(data):
    """
    Identify items expiring in 1 day or less and those already expired.
    Adjusts for time offset between Django API and local clock.
    """
    items_to_notify = {"expiring_soon": [], "expired": []}
    now = datetime.now()
    for item in data:
        # Adjust expiry date/time for the time offset
        expiry_date = datetime.strptime(
            f"{item['expired_date']} {item['expired_time']}", "%Y-%m-%d %H:%M:%S"
        ) - TIME_OFFSET
        time_difference = expiry_date - now
        # Expiring in 1 day or less
        if timedelta(0) < time_difference <= timedelta(days=1):
            items_to_notify["expiring_soon"].append(item)
        # Already expired
        elif time_difference <= timedelta(0):
            items_to_notify["expired"].append(item)
    return items_to_notify

def notify_via_pushcut(items, notification_type):
    """
    Send notifications through Pushcut for items expiring soon or already expired.
    """
    for item in items:
        if notification_type == "expiring_soon":
            payload = {
                "notification": "Make-A-Thon'25",  # Name of your Pushcut notification
                "title": "Food Item Expiring Soon!",
                "text": f"The item '{item['food_name']}' will expire on {item['expired_date']} at {item['expired_time']}. Use it soon!",
            }
        elif notification_type == "expired":
            payload = {
                "notification": "Make-A-Thon'25",  # Name of your Pushcut notification
                "title": "Expired Item Alert",
                "text": f"The item '{item['food_name']}' expired on {item['expired_date']} at {item['expired_time']}. Consider throwing it away or using it for compost.",
            }
        try:
            response = requests.post(PUSHCUT_URL, json=payload)
            if response.status_code == 200:
                print(f"Notification sent for {item['food_name']} ({notification_type})")
            else:
                print(f"Failed to send notification for {item['food_name']} ({notification_type}): {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error sending notification ({notification_type}): {e}")

def update_expired_items(items):
    """
    Automatically update the values for expired food items.
    """
    for item in items:
        update_payload = {
            "food_id": item["food_id"],
            "food_quality": "R",  # Set quality to 'R'
            "food_usage": "C",    # Set usage to 'C'
        }
        # Construct the URL dynamically
        update_url = f"{UPDATE_URL}{item['food_id']}/"  # Use the base URL and append the food_id
        try:
            response = requests.put(update_url, json=update_payload)
            if response.status_code == 200:
                print(f"Updated food item {item['food_name']} (ID: {item['food_id']})")
            else:
                print(f"Failed to update food item {item['food_name']} (ID: {item['food_id']}): {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error updating food item {item['food_name']} (ID: {item['food_id']}): {e}")

if __name__ == "__main__":
    # Fetch data from the API
    data = fetch_data()

    # Get items expiring in 1 day or less and already expired
    items_to_notify = get_items_expiring_or_expired(data)

    # Send notifications for expiring soon items
    if items_to_notify["expiring_soon"]:
        notify_via_pushcut(items_to_notify["expiring_soon"], "expiring_soon")
    else:
        print("No items expiring in 1 day or less.")

    # Send notifications for expired items
    if items_to_notify["expired"]:
        notify_via_pushcut(items_to_notify["expired"], "expired")
        # Automatically update expired items
        update_expired_items(items_to_notify["expired"])
    else:
        print("No items have expired.")
