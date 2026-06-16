#!/usr/bin/env python3

# Generates daily Instagram post content about "obvious things" using Gemini.
# Builds post text (short sentence, caption, rating) while avoiding repeated themes.
# Creates an image with Imagen and stores both image and JSON metadata in posts/<date>/.
# Accepts an optional --date (YYYY-MM-DD); defaults to today's date when omitted.

import dotenv
import json
import os
from typing import List
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError
from pydantic import BaseModel, Field
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import argparse

EXISTING_POSTS_FILE = "existing-posts.txt"

def generate_post(client, historical_sentences: List[str]):
    prompt = """
You are a social media creator. Your task is to generate creative sentences in Portuguese for an Instagram
post about obvious things. The sentences should be catchy, engaging, and suitable for a wide audience. 
They should also reflect the theme of "obvious things" in a fun and relatable way.

Examples of "obvious things" could include:
- The sky is blue.
- Water is wet.
- The sun rises in the east.
- If the light is red, stop.

For each sentence, also generate an image prompt that will be used to create an image with an image generator (like Imagen 3). 
The image prompt should be detailed and in English, describing a scene that visually represents the "obvious thing" in a creative and humorous way. 
And the image should include the sentence itself as part of the scene. It can be just text on top of a background, or the sentence can be integrated
into the scene in a clever way.

Create a creative caption in Portuguese for the Instagram post that includes relevant hashtags to increase engagement.

Finally, rate each post from 0 to 100 on how you evaluate how good the post will be.

CRITICAL: You cannot repeat any theme, central concept, or approach that resembles the sentences listed below.
    They represent posts that have already been published. Be original and seek new angles.
    
    ---
    EXCLUSION LIST (DO NOT REPEAT THESE THEMES/SENTENCES):
    {historical_sentences}
    ---
    """

    class PostInstagram(BaseModel):
        image_prompt: str = Field(description="The detailed prompt (in English) for the image generator (Imagen 3).")
        short_sentence: str = Field(description="A short and catchy sentence in Portuguese that represents an 'obvious thing'.")
        caption: str = Field(description="A creative caption in Portuguese for the Instagram post, including relevant hashtags.")
        rate: int = Field(description="A rating from 0 to 100 indicating how good this post idea is, with 100 being the best.")

    class PostList(BaseModel):
        posts: List[PostInstagram] = Field(description="A list containing the generated post ideas.")

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PostList,
            temperature=0.7 
        ),
    )

    validated_data = PostList.model_validate_json(response.text)

    print("\n--- Resultado Validado com Sucesso! ---\n")

    for i, post in enumerate(validated_data.posts, start=1):
        print(f"📌 POST #{i}")
        print(f"✍️ Short Sentence: {post.short_sentence}")
        print(f"🎨 Image Prompt: {post.image_prompt}")
        print(f"📝 Caption: {post.caption}")
        print(f"⭐ Rating: {post.rate}/100")
        print("-" * 40)
        
    best = max(validated_data.posts, key=lambda p: p.rate)
    return best

def generate_image(client, prompt: str, folder):

    max_attempts = 3
    delay = 5

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio="1:1", 
                    person_generation="ALLOW_ADULT",
                )            
            )
        except (ClientError, ServerError) as e:
            is_temporary = e.code in [429, 503]
            if is_temporary and attempt < max_attempts:
                print(f"AI model is not responding. Waiting for {delay} seconds...")
                time.sleep(delay)
                delay *= 2
        else:
            raise e

    for i, generated_image in enumerate(response.generated_images):
        image = Image.open(io.BytesIO(generated_image.image.image_bytes))
        image_name = f"post_instagram_{i}.jpg"
        image_path = os.path.join(folder, image_name)
        
        image.save(image_path, format="JPEG")
        return image_path


def save_post_data(post, folder):
    json_file_name = os.path.join(folder, "post_data.json")

    data = post.model_dump()

    with open(json_file_name, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)
        

def load_historical_sentences(existing_posts_file: str, posts_root: str = "posts") -> List[str]:
    historical_sentences: List[str] = []

    if os.path.exists(existing_posts_file):
        with open(existing_posts_file, "r", encoding="utf-8") as file:
            historical_sentences.extend(line.strip() for line in file if line.strip())

    if os.path.isdir(posts_root):
        for folder_name in sorted(os.listdir(posts_root)):
            folder_path = os.path.join(posts_root, folder_name)
            if not os.path.isdir(folder_path):
                continue

            post_data_path = os.path.join(folder_path, "post_data.json")
            if not os.path.exists(post_data_path):
                continue

            try:
                with open(post_data_path, "r", encoding="utf-8") as json_file:
                    post_data = json.load(json_file)
                short_sentence = post_data.get("short_sentence")
                if isinstance(short_sentence, str) and short_sentence.strip():
                    historical_sentences.append(short_sentence.strip())
            except (OSError, json.JSONDecodeError):
                # Ignore unreadable or invalid JSON files.
                continue

    # Remove duplicates while preserving insertion order.
    return list(dict.fromkeys(historical_sentences))
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Instagram post content.")
    parser.add_argument("--date", type=str, help="The date for which to generate the post content (format: YYYY-MM-DD). If not provided, today's date will be used.")
    args = parser.parse_args()

    dotenv.load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_TOKEN"))
    historical_sentences = load_historical_sentences(EXISTING_POSTS_FILE)
    
    print(f"{historical_sentences}")

    post_date = datetime.now().strftime('%Y-%m-%d')

    if args.date:
        try:
            datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")
        post_date = args.date

    folder = os.path.join("posts", post_date)
    
    if os.path.exists(folder):
        print(f"The folder '{folder}' already exists. Skipping post generation to avoid overwriting existing content.")
        exit(0)

    os.makedirs(folder, exist_ok=True)

    post = generate_post(client, historical_sentences)

    save_post_data(post, folder)
    print(f"Post data saved to folder: {folder}")

    image_name = generate_image(client, post.image_prompt, folder)
    print(f"Imagem gerada: {image_name}")
