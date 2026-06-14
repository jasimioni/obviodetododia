#!/usr/bin/env python3

# Publishes an image post to Instagram using the Meta Graph API.
# Accepts direct --image_url and --caption or loads them from a posts/<date> folder.
# Prevents duplicate publishing by checking/creating a local "done" marker file.
# Reads API credentials and base URL from environment variables via .env.

import requests
import time
import dotenv
import os
import argparse
import json
from datetime import datetime

dotenv.load_dotenv()

ACCESS_TOKEN = os.getenv("META_API_TOKEN")
INSTAGRAM_ID = os.getenv("PAGE_ID")
BASE_IMAGE_URL = os.getenv("BASE_IMAGE_URL")
INSTAGRAM_API_VERSION = "v20.0"


def post_to_instagram(image_url: str, caption: str) -> bool:
    base_url = f"https://graph.facebook.com/{INSTAGRAM_API_VERSION}"

    # -------------------------------------------------------------
    # STEP 1: Create the media container (Media Container)
    # -------------------------------------------------------------
    print("Step 1: Creating media container...")
    
    container_url = f"{base_url}/{INSTAGRAM_ID}/media"
    
    container_payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': ACCESS_TOKEN
    }
    
    container_response = requests.post(container_url, data=container_payload)
    container_data = container_response.json()
    
    if "id" not in container_data:
        print("Error creating container:", container_data)
        return False
        
    container_id = container_data["id"]
    print(f"Container created successfully! ID: {container_id}")
    
    # It is good practice to wait a few seconds for the Instagram server
    # to finish processing and rendering the image before publishing.
    print("Waiting 5 seconds for image processing...")
    time.sleep(5)
    
    # -------------------------------------------------------------
    # STEP 2: Publish the created media (Media Publish)
    # -------------------------------------------------------------
    print("Step 2: Publishing to Instagram feed...")
    
    publish_url = f"{base_url}/{INSTAGRAM_ID}/media_publish"
    
    publish_payload = {
        'creation_id': container_id,
        'access_token': ACCESS_TOKEN
    }
    
    publish_response = requests.post(publish_url, data=publish_payload)
    publish_data = publish_response.json()
    
    if "id" not in publish_data:
        print("Error publishing:", publish_data)
        return False
        
    print(f"Success! Post published. Post ID: {publish_data['id']}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post an image to Instagram.")
    parser.add_argument("--image_url", type=str, help="The URL of the image to post.")
    parser.add_argument("--caption", type=str, help="The caption for the Instagram post.")
    parser.add_argument("--folder", type=str, help="The folder containing the image to post.")
    parser.add_argument("--date", type=str, help="The date for which to post the content (format: YYYY-MM-DD). If not provided, today's date will be used.")
    args = parser.parse_args()

    if args.image_url and args.caption:
        image_url = args.image_url
        caption = args.caption
    else:
        folder = args.folder
        if not args.folder:
            if args.date:
                try:
                    datetime.strptime(args.date, '%Y-%m-%d')
                except ValueError:
                    raise ValueError("Invalid date format. Please use YYYY-MM-DD.")
                folder = os.path.join("posts", args.date)
            else:
                today = time.strftime("%Y-%m-%d")
                folder = os.path.join("posts", today)
        
        # Check if done file exists to prevent reposting
        done_file_path = os.path.join(folder, "done")
        if os.path.exists(done_file_path):
            print(f"Post in folder '{folder}' has already been published to Instagram. Skipping.")
            exit(0)

        image_path = os.path.join(folder, "post_instagram_0.jpg")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")
        
        image_url = f"{BASE_IMAGE_URL}{image_path}"
        post_data_path = os.path.join(folder, "post_data.json")
        if not os.path.exists(post_data_path):
            raise FileNotFoundError(f"Post data not found at path: {post_data_path}")
        with open(post_data_path, "r", encoding="utf-8") as json_file:
            post_data = json.load(json_file)
        caption = post_data.get("caption")
        if not caption:
            raise ValueError(f"Caption not found in post data at path: {post_data_path}")

    print(f"Posting to Instagram with image URL: {image_url} and caption: {caption}")

    if post_to_instagram(image_url, caption):
        print("Post successfully published to Instagram!")
        if folder:
            done_file_path = os.path.join(folder, "done")
            with open(done_file_path, "w") as done_file:
                done_file.write(f"This post has been published to Instagram on {time.strftime('%Y-%m-%d %H:%M:%S')}.\n")
    else:
        print("Failed to publish post to Instagram.")
        exit(1)
