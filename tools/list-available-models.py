#!/usr/bin/env python3

from google import genai
import dotenv
import os

# Initialize the client with your API key
dotenv.load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_TOKEN"))

print("Fetching available models from your endpoint...\n")

# The .list() method scans models accessible by your token/key
for model in client.models.list():
    # Shows the model name (used in the 'model=' parameter) and supported methods
    print(f"🤖 Model: {model.name}")
    print(f"   Description: {model.description}")
    print("-" * 60)