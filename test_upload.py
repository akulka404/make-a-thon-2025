import cv2
import requests
import base64
import json

IMGUR_CLIENT_ID = "f6363c4d8725b99"

def upload_to_imgur(image_data):
    """
    Uploads raw JPEG bytes to Imgur and returns the public URL of the uploaded image.
    """
    url = "https://api.imgur.com/3/upload"
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    data = {
        'image': base64.b64encode(image_data).decode('utf-8'),
        'type': 'base64'
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    link = response.json()['data']['link']
    return link

def capture_image_from_feed():
    """
    Captures an image from the camera feed when the 'c' key is pressed and uploads it to Imgur.
    """
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Failed to open camera.")
        return

    print("Press 'c' to capture an image or 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera.")
            break

        # Display the camera feed
        cv2.imshow("Camera Feed", frame)

        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):  # Capture image on 'c' key
            # Encode the frame as JPEG in memory
            success, encoded_image = cv2.imencode('.jpg', frame)
            if not success:
                print("Failed to encode image.")
                continue

            # Convert to bytes
            jpeg_bytes = encoded_image.tobytes()

            # Upload to Imgur
            print("Uploading image to Imgur...")
            public_url = upload_to_imgur(jpeg_bytes)
            print("Image uploaded successfully!")
            print("Public URL:", public_url)

            # Process the image and upload details to your API
            process_image(public_url)

        elif key == ord('q'):  # Quit on 'q' key
            break

    cap.release()
    cv2.destroyAllWindows()

def process_image(public_url):
    """
    Handles processing the image and sending the result to your API.
    """
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "You are a food image classification assistant. "
                        "Identify the food item in the image, then decide if it is fresh ('G') or rotten ('R'). "
                        "If the item is fresh, estimate how long until the item expires. "
                        "Use the most appropriate single timescale (days, months, or years). Only fill the field for that timescale. "
                        "Set the other offset fields to 0. If the item is rotten, set them all to 0. "

                        "Return your answer **only** in the following JSON format:\n\n"
                        "{\n"
                        "  \"food_name\": \"(String)\",\n"
                        "  \"food_quality\": \"(G or R)\",\n"
                        "  \"food_usage\": \"(U, Q, T, or C)\",\n"
                        "  \"expiry_offset_days\": (integer),\n"
                        "  \"expiry_offset_months\": (integer),\n"
                        "  \"expiry_offset_years\": (integer)\n"
                        "}\n\n"

                        "where:\n"
                        "- food_name is the name of the item (e.g. 'cauliflower').\n"
                        "- food_quality is 'G' if fresh ('Good'), 'R' if rotten.\n"
                        "- food_usage must be one of:\n"
                        "    'U' for 'Can use. Still good for storage'\n"
                        "    'Q' for 'Use quickly. Will go bad soon'\n"
                        "    'T' for 'Throw away'\n"
                        "    'C' for 'Compost'\n"
                        "- expiry_offset_days, expiry_offset_months, expiry_offset_years are integers.\n"
                        "  If fresh, choose **one** timescale to fill and set the others to 0. "
                        "  If rotten, set all three to 0.\n\n"

                        "Choose the 'food_usage' value based on how soon it needs to be used.\n"
                        "DO NOT include extra text or formatting outside the JSON."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": public_url,
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )

    # Parse the JSON response from GPT
    raw_json = response.choices[0].message.content

    try:
        # If the response has backticks, remove them before parsing
        cleaned_json = raw_json.strip("```json").strip("```").strip()
        parsed_data = json.loads(cleaned_json)
    except json.JSONDecodeError as e:
        print("\nError decoding JSON:", e)
        parsed_data = None

    # Add the public URL to the JSON data
    if parsed_data:
        parsed_data["image_url"] = public_url

        print("\nParsed JSON with Image URL (Formatted):")
        formatted_json = json.dumps(parsed_data, indent=2)
        print(formatted_json)

        # Send the data to your Django API
        send_to_api(parsed_data)

def send_to_api(data):
    """
    Sends the processed data to the Django API.
    """
    api_url = "http://127.0.0.1:8000/api/log_items/food_data/"
    try:
        response = requests.post(api_url, json=data)
        if response.status_code == 201:
            print("\nData successfully posted to the API.")
        else:
            print(f"\nFailed to post data. Status Code: {response.status_code}")
            print("Response:", response.text)
    except requests.RequestException as e:
        print(f"\nError while making POST request: {e}")


if __name__ == "__main__":
    capture_image_from_feed()

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
