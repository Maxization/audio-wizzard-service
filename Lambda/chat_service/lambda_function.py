import json
import requests

def lambda_handler(event, context):
    # TODO implement
    url = f"https://discord.com/api/v8/webhooks/{event['appId']}/{event['token']}"
    json = {
        "tts": "false",
        "content": "Pls work !",
        "embeds": [],
        "allowed_mentions": []
    }
    
    r = requests.post(url, json=json)
    print(r)
    return {
        'statusCode': 200
    }
