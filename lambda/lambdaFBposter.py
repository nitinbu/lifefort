import json
import os
import requests
import boto3
from datetime import datetime

def lambda_handler(event, context):
    # Load secrets from AWS Secrets Manager
    secrets_client = boto3.client('secretsmanager')
    secret_response = secrets_client.get_secret_value(SecretId="lifefort/fb-openai-secrets")
    secrets = json.loads(secret_response['SecretString'])

    page_token = secrets['facebook_page_token']
    page_id = secrets['page_id']
    openai_api_key = secrets['openai_api_key']

    # Use hardcoded or dynamically pulled blog title/link (in real case: from S3 or API)
    blog_title = "Why Busy Professionals Delay Life Insurance (and Why They Shouldn’t)"
    blog_link = "https://lifefortsolutions.com/why-busy-professionals-delay-life-insurance-and-why-they-shouldnt/"

    # Generate caption using OpenAI
    openai_response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": f"Write a short Facebook caption for a blog post titled '{blog_title}'. Add emojis, 2–3 hashtags, and end with: Read more: {blog_link}"}
            ]
        }
    )
    caption = openai_response.json()['choices'][0]['message']['content']

    # Post to Facebook
    fb_response = requests.post(
        f"https://graph.facebook.com/{page_id}/feed",
        params={
            "message": caption,
            "access_token": page_token
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'facebook_response': fb_response.json(),
            'caption': caption
        })
    }
