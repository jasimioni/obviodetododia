# Óbvio de Todo Dia

An automated Instagram content generator and publisher that creates daily posts about "obvious things" in Portuguese using AI.

📱 **Follow the Instagram account**: [@obviodetododia](https://www.instagram.com/obviodetododia/)

## Overview

This project automates the complete workflow of generating creative Instagram content and publishing it directly to your Instagram account. It uses Google's Gemini API for content generation and Imagen for image creation, then publishes to Instagram via the Meta Graph API.

## How It Works

The project runs two sequential jobs on a schedule or via manual trigger:

### Job 1: Generate Post Content
- Uses Google Gemini to generate creative Portuguese sentences about "obvious things"
- Creates matching image prompts for visual representation
- Generates captions with relevant hashtags
- Rates each post idea and selects the best one
- Uses Imagen 4.0 to generate a 1:1 image
- Stores both image (`post_instagram_0.jpg`) and metadata (`post_data.json`) in `posts/<YYYY-MM-DD>/`
- Commits and pushes changes to the repository

### Job 2: Publish to Instagram
- Runs only after Job 1 succeeds
- Reads the generated post data and image from `posts/<YYYY-MM-DD>/`
- Creates a media container on Instagram
- Publishes to your Instagram feed
- Creates a `done` marker file to prevent re-posting
- Commits and pushes changes to the repository

## Workflow Triggers

The workflow can be triggered in two ways:

1. **Scheduled**: Runs automatically every day at 7:00 AM UTC (cron: `0 7 * * *`)
2. **Manual**: Triggered via GitHub Actions UI with optional `--date` parameter in `YYYY-MM-DD` format

## Required Secrets

Configure these secrets in your GitHub repository settings under **Settings > Secrets and variables > Actions**:

| Secret | Description | Example |
|--------|-------------|---------|
| `GEMINI_API_TOKEN` | Google Gemini API key for content generation | `gsk_...` |
| `META_API_TOKEN` | Meta/Facebook API token for Instagram access | `EAABsbCS...` |
| `PAGE_ID` | Your Instagram Business Account ID | `123456789` |
## Required Variables

Configure these variables in your GitHub repository settings under **Settings > Secrets and variables > Actions > Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `BASE_IMAGE_URL` | Base URL for accessing generated images in the repository | See below |

### About BASE_IMAGE_URL

**Important**: Instagram's API requires a publicly accessible URL to the image file. Since images are generated and stored in this repository, you need to provide a public base URL.

**Options:**

1. **GitHub Raw Content (Recommended for public repos)**:
   ```
   https://raw.githubusercontent.com/YOUR_USERNAME/obviodetododia/main/
   ```
   - The workflow will construct: `https://raw.githubusercontent.com/YOUR_USERNAME/obviodetododia/main/posts/<YYYY-MM-DD>/post_instagram_0.jpg`
   - Only works if your repository is public

2. **GitHub Pages**:
   - Enable GitHub Pages in your repository
   - Set base URL to: `https://YOUR_USERNAME.github.io/obviodetododia/`

3. **Custom CDN or Web Server**:
   - Host the repository contents on a CDN (e.g., Cloudflare, AWS S3)
   - Point `BASE_IMAGE_URL` to your CDN's base path

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/obviodetododia.git
cd obviodetododia
```

### 2. Install Dependencies Locally (Optional for Testing)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create `.env` File (Local Testing)
```bash
GEMINI_API_TOKEN=your_gemini_api_key
META_API_TOKEN=your_meta_api_token
PAGE_ID=your_instagram_page_id
BASE_IMAGE_URL=https://your-base-url/
```

### 4. Add GitHub Secrets
Go to **Settings > Secrets and variables > Actions > Secrets** and add:
- `GEMINI_API_TOKEN`
- `META_API_TOKEN`
- `PAGE_ID`

### 5. Add GitHub Variables
Go to **Settings > Secrets and variables > Actions > Variables** and add:
- `BASE_IMAGE_URL`

### 6. Test Locally (Optional)
```bash
# Generate a post for today
python tools/generate-post-content.py

# Generate a post for a specific date
python tools/generate-post-content.py --date 2026-06-15

# Publish a generated post
python tools/publish-to-instagram.py

# Publish a specific date's post
python tools/publish-to-instagram.py --date 2026-06-15
```

### 7. Trigger Workflow
- **Manual Trigger**: Go to **Actions > Generate And Publish Post > Run workflow**
  - Optionally provide a date in `YYYY-MM-DD` format
- **Automatic**: Workflow runs daily at 7:00 AM UTC

## Project Structure

```
.
├── .github/workflows/
│   └── generate-and-publish-post.yaml    # CI/CD workflow
├── tools/
│   ├── generate-post-content.py          # Content generation script
│   ├── publish-to-instagram.py           # Instagram publishing script
│   └── list-available-models.py          # Utility to list available Gemini models
├── posts/                                # Generated posts organized by date
│   └── YYYY-MM-DD/
│       ├── post_instagram_0.jpg          # Generated image
│       ├── post_data.json                # Post metadata (caption, sentence, rating)
│       └── done                          # Marker file (created after publishing)
├── requirements.txt                      # Python dependencies
├── existing-posts.txt                    # Historical posts to avoid repetition
└── README.md                             # This file
```

## Files

- **generate-post-content.py**: Generates creative post content using Gemini and creates images with Imagen
- **publish-to-instagram.py**: Publishes generated posts to Instagram via Meta Graph API
- **list-available-models.py**: Utility script to list available Gemini models
- **existing-posts.txt**: Text file containing previously published sentences (one per line) to ensure the AI doesn't repeat themes

## Dependencies

- `google-genai`: Google Gemini and Imagen API client
- `python-dotenv`: Environment variable management
- `pydantic`: Data validation
- `Pillow`: Image processing
- `requests`: HTTP library for Meta API

See [requirements.txt](requirements.txt) for pinned versions.

## How the Image URL Flow Works

1. **Generate Job**: Creates `posts/<DATE>/post_instagram_0.jpg` in the repository
2. **Generate Job**: Commits and pushes this file to the repository
3. **Publish Job**: Constructs the full URL: `{BASE_IMAGE_URL}posts/<DATE>/post_instagram_0.jpg`
4. **Publish Job**: Passes this URL to Instagram's API
5. **Instagram**: Fetches the image from the public URL and creates the post

**Note**: The image must be publicly accessible when Instagram's API tries to download it. If using GitHub Raw Content, ensure your repository is public.

## Troubleshooting

### "Image not found" error in publish job
- Ensure the generate job completed successfully
- Check that the image file was created in `posts/<DATE>/post_instagram_0.jpg`
- Verify `BASE_IMAGE_URL` is correct and publicly accessible

### "Post already published" message
- The `done` marker file prevents re-publishing the same date
- Delete the `done` file from `posts/<DATE>/` if you need to republish

### API authentication errors
- Verify all secrets are correctly set in GitHub
- Ensure API tokens have the necessary permissions
- Check token expiration dates

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.
