import requests
import os

from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv('APP_ID')
BOT_TOKEN = os.getenv('BOT_TOKEN')

url = f"https://discord.com/api/v8/applications/{APP_ID}/commands"


def register_command(reg_url, reg_headers, reg_json):
    response = requests.post(reg_url, headers=reg_headers, json=reg_json)
    if response.ok:
        print("Registered!")
    else:
        print("Failed!")


json_account = {
    "name": "account",
    "description": "Manage your account",
    "options": [
        {
            "name": "delete",
            "description": "Delete information about you",
            "type": 1,
            "required": False
        },
        {
            "name": "set",
            "description": "set params value",
            "type": 1,
            "required": False,
            "options": [
                {
                    "name": "age",
                    "description": "set age",
                    "type": 4,
                    "required": False,
                },
                {
                    "name": "listening-behaviour",
                    "description": "todo",
                    "type": 3,
                    "required": False,
                    "choices": [
                        {
                            "name": "1",
                            "value": "behaviour_1"
                        },
                        {
                            "name": "2",
                            "value": "behaviour_2"
                        }
                    ]
                }
            ],
        }
    ]
}

json_recommend = {
    "name": "recommend",
    "description": "Recommend a song",
    "options": [
        {
            "name": "number-of-songs",
            "description": "Number of songs to recommend",
            "type": 4,
            "required": False
        },
    ]
}

json_review = {
    "name": "review",
    "description": "Review a song",
    "options": [
        {
            "name": "content",
            "description": "Your review with title like *song title*",
            "type": 3,
            "required": True
        },
    ]
}


# For authorization, you can use either your bot token
headers = {
    "Authorization": f"Bot {BOT_TOKEN}"
}

register_command(url, headers, json_account)
register_command(url, headers, json_recommend)
register_command(url, headers, json_review)
