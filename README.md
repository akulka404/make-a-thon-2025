# NC State Make-A-Thon 2025
**Smart Food Guardian** – An IoT System to Reduce Household Food Waste

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)

---

## Project Overview

**Smart Food Guardian** is an IoT-based system developed for the NC State Make-A-Thon 2025. It helps households reduce food waste by:

1. **Capturing** images of food items using a connected camera.
2. **Classifying** food quality and estimating expiry using OpenAI's GPT-4o vision model.
3. **Storing** food item data in a Django REST API backed by a PostgreSQL database.
4. **Notifying** users via Pushcut when food items are expiring soon or have already expired.
5. **Automatically updating** expired food items in the database.

---

## Features

- 📸 Live camera feed with on-demand image capture
- 🤖 AI-powered food classification (name, quality, estimated expiry) via GPT-4o
- ☁️ Image hosting via Imgur API
- 🗄️ Django REST API for storing and querying food item records
- 🔔 Push notifications via Pushcut for expiring/expired items
- 🔄 Automatic status update for expired food items

---

## System Architecture

```
Camera (OpenCV)
      │
      ▼
 test_upload.py
      │ captures frame, uploads to Imgur
      ▼
  OpenAI GPT-4o
      │ classifies food, estimates expiry
      ▼
Django REST API  ◄──── fetch_data.py ──► Pushcut Notifications
 (PostgreSQL DB)         (polls API,
                        sends alerts,
                       updates expired)
```

---

## Prerequisites

- Python 3.10+
- PostgreSQL
- An [OpenAI API key](https://platform.openai.com/account/api-keys) with GPT-4o access
- An [Imgur API client ID](https://api.imgur.com/oauth2/addclient)
- A [Pushcut](https://www.pushcut.io/) account and webhook URL
- A webcam or compatible USB/CSI camera

### Python Dependencies

Install all required packages:

```bash
pip install django djangorestframework django-cors-headers whitenoise \
            psycopg2-binary python-dateutil requests opencv-python openai
```

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/akulka404/make-a-thon-2025.git
cd make-a-thon-2025
```

### 2. Configure the Database

Create a PostgreSQL database and user, then update `api/api/settings.py` with your credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

### 3. Apply Database Migrations

```bash
cd api
python manage.py migrate
```

### 4. Configure API Keys

In `test_upload.py`, set your Imgur client ID:
```python
IMGUR_CLIENT_ID = "your_imgur_client_id"
```

Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

In `fetch_data.py`, set your Pushcut webhook URL:
```python
PUSHCUT_URL = "https://api.pushcut.io/<your-token>/notifications/<notification-name>"
```

---

## Running the Application

### 1. Start the Django API Server

```bash
cd api
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

### 2. Capture and Classify Food Items

Run the main image capture and classification script:

```bash
python test_upload.py
```

- A live camera feed window will open.
- Press **`c`** to capture a frame — it will be uploaded to Imgur, classified by GPT-4o, and logged to the API.
- Press **`q`** to quit.

### 3. Check for Expiring/Expired Items & Send Notifications

Run the notification script (e.g., via a cron job or manually):

```bash
python fetch_data.py
```

This will:
- Fetch all food items from the API.
- Send a Pushcut notification for items expiring within 1 day.
- Send a Pushcut notification for already expired items and update their status in the database.

### 4. (Optional) Test Camera Only

```bash
python camera_test.py
```

Opens the default camera feed. Press **`q`** to quit.

### 5. (Optional) Test OpenAI Image Classification

```bash
python testimage.py
```

Sends a sample food image URL to GPT-4o and prints the classification result.

---

## API Reference

Base URL: `http://127.0.0.1:8000/api/log_items/`

### Food Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/food_data/` | List all food items |
| `POST` | `/food_data/` | Create a new food item |
| `DELETE` | `/food_data/` | Delete all food items |
| `GET` | `/food_data/<food_id>/` | Get a food item by ID |
| `PUT` | `/food_data/<food_id>/` | Update a food item by ID (partial updates supported) |
| `GET` | `/food_data/name/<food_name>/` | Get food items by name |

### POST `/food_data/` – Request Body

```json
{
  "food_name": "apple",
  "food_quality": "G",
  "food_usage": "U",
  "expiry_offset_days": 7,
  "expiry_offset_months": 0,
  "expiry_offset_years": 0,
  "image_url": "https://i.imgur.com/example.jpg"
}
```

### Field Reference

| Field | Values | Description |
|-------|--------|-------------|
| `food_quality` | `G` / `R` / `/` | Good / Rotten / Prefer not to say |
| `food_usage` | `U` / `Q` / `T` / `C` | Can use / Use quickly / Throw away / Compost |
| `expiry_offset_days` | integer | Days until expiry (from time of creation) |
| `expiry_offset_months` | integer | Months until expiry |
| `expiry_offset_years` | integer | Years until expiry |

`stored_date` and `stored_time` are set automatically on creation.  
`expired_date` and `expired_time` are computed as `stored_datetime + offsets`.

---

## How It Works

1. **Image Capture** (`test_upload.py`): OpenCV opens the connected camera. When `c` is pressed, the current frame is JPEG-encoded and uploaded to Imgur to get a public URL.

2. **AI Classification** (`test_upload.py` → OpenAI GPT-4o): The public image URL is sent to GPT-4o with a structured prompt. The model returns a JSON object with the food name, quality rating (`G`/`R`), usage recommendation (`U`/`Q`/`T`/`C`), and expiry offsets in days/months/years.

3. **Data Storage** (Django REST API): The classification result is `POST`ed to the Django API, which computes `expired_date`/`expired_time` from the provided offsets and stores the record in PostgreSQL.

4. **Expiry Monitoring & Notifications** (`fetch_data.py`): When run, this script fetches all records from the API, calculates time remaining until expiry (accounting for a configurable clock offset), and sends targeted Pushcut push notifications to the user's phone for items expiring within 24 hours or already expired. Expired items are automatically updated to `food_quality = R` and `food_usage = C` (Compost).

---

## Project Structure

```
make-a-thon-2025/
├── api/                        # Django REST API
│   ├── api/
│   │   ├── settings.py         # Django settings (DB, installed apps)
│   │   └── urls.py             # Root URL configuration
│   ├── log_items/
│   │   ├── models.py           # FOOD_DATA model
│   │   ├── serializers.py      # DRF serializer
│   │   ├── views.py            # API view logic
│   │   ├── urls.py             # App-level URL patterns
│   │   └── migrations/         # Database migrations
│   └── manage.py               # Django management script
├── camera_test.py              # Utility: test camera connection
├── fetch_data.py               # Expiry monitoring & Pushcut notifications
├── test_upload.py              # Main script: capture → classify → log
├── testimage.py                # Utility: test OpenAI image classification
└── README.md
```
