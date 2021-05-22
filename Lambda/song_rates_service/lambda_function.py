import boto3
import json
import uuid
import time

client = boto3.client('comprehend')
sqs = boto3.resource('sqs')

personalize_events = boto3.client(service_name='personalize-events')

responseQueue = sqs.get_queue_by_name(QueueName="chat_service_queue")


def add_user_to_personalize(event):
    user_properties = {
        "age": 22,  # TODO: Read from database
        "gender": "male"  # TODO: Read from database
    }

    personalize_events.put_users(
        datasetArn='arn:aws:personalize:eu-central-1:043035977035:dataset/user-songs-group/USERS',
        users=[{
            'userId': event['user']['id'],
            'properties': json.dumps(user_properties)
        }]
    )


def add_user_song_rating(event):
    interaction_properties = {
        "rating": 50  # TODO: Calculate with Comprehend
    }

    personalize_events.put_events(
        trackingId='1d2eb1be-2cef-4569-8c3b-12ba7d3cbc08',
        userId=event['user']['id'],
        sessionId=uuid.uuid4(),
        eventList=[{
            'sentAt': time.time(),
            'eventType': 'eventTypePlaceholder',
            'itemId': '35iwgR4jXetI318WEWsa1Q',  # TODO: Read from database
            'properties': json.dumps(interaction_properties)
        }]
    )


def lambda_handler(event, context):
    print(event)
    data = json.loads(event['Records'][0]['body'])
    text = data['message']
    sentiment = client.detect_sentiment(Text=text, LanguageCode='en')

    sentiment_event = {
        "appId": data['appId'],
        "message": sentiment['Sentiment'],
        "user": data['user'],
        "token": data['token']
    }

    # TODO: Chek if user exsists in database
    # if not invoke add_user_to_personalize

    return responseQueue.send_message(MessageBody=json.dumps(sentiment_event))
