import json
import requests


def lambda_handler(event, context):
    data = json.loads(event['Records'][0]['body'])
    text = data['message']

    url = f"https://discord.com/api/v8/webhooks/{data['appId']}/{data['token']}"
    response = {
        "tts": "false",
        "content": text,
        "embeds": [],
        "allowed_mentions": []
    }

    response = requests.post(url, json=response)

    return response.status_code
