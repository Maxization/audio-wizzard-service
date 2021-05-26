import json
import requests


def lambda_handler(event, context):
    data = json.loads(event['Records'][0]['body'])
    text = data['message']

    if len(text) > 2000:
        text = "Your list contains too many characters to be displayed.\n"
        text += "You can manage the issue by providing less number of songs."

    url = f"https://discord.com/api/v8/webhooks/{data['appId']}/{data['token']}"
    response = {
        "tts": "false",
        "content": text,
        "embeds": [],
        "allowed_mentions": []
    }

    response = requests.post(url, json=response)