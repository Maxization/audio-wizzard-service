import boto3
import json
import uuid
import time
from boto3.dynamodb.conditions import Key

personalize_events = boto3.client(service_name='personalize-events')
client = boto3.client('comprehend')

sqs = boto3.resource('sqs')
responseQueue = sqs.get_queue_by_name(QueueName="chat_service_queue")

dynamodb = boto3.resource('dynamodb')


def get_song_title(message):
    start = message.find('*')
    end = message.find('*', start + 1)
    if start == -1 or end == -1:
        return ""
    return message[(start + 1):end]


def query_users(user_id):
    table = dynamodb.Table('DynamoDBTableUsersName')
    response = table.query(
        KeyConditionExpression=Key('USER_ID').eq(user_id)
    )

    return response['Items']


def query_item(title):
    table = dynamodb.Table('DynamoDBTableSongsName')
    response = table.query(
        IndexName="NAME-index",
        KeyConditionExpression=Key('NAME').eq(title)
    )

    return response['Items']


def add_user_song_rating(event, rating, itemId):
    interaction_properties = {
        'rating': str(int(rating)),
        'itemId': itemId
    }

    print(json.dumps(interaction_properties))

    response = personalize_events.put_events(
        trackingId='1d2eb1be-2cef-4569-8c3b-12ba7d3cbc08',
        userId=event['user']['id'],
        sessionId=str(uuid.uuid4()),
        eventList=[{
            'sentAt': time.time(),
            'eventType': 'eventTypePlaceholder',
            'properties': json.dumps(interaction_properties)
        }]
    )


def send_error_message(event, message):
    response_event = {
        "appId": event['appId'],
        "message": message,
        "user": event['user'],
        "token": event['token']
    }
    return responseQueue.send_message(MessageBody=json.dumps(response_event))


def lambda_handler(event, context):
    data = json.loads(event['Records'][0]['body'])

    user = query_users(data['user']['id'])

    if not user:
        return send_error_message(data, "Create your account with /account set")

    text = data['message']
    title = get_song_title(text)

    if not title:
        return send_error_message(data, r"Song title must be like \*title\*")

    songs = query_item(title)

    if not songs:
        return send_error_message(data, f'Cannot find song titled "{title}"')

    item_id = songs[0]['ITEM_ID']

    sentiment = client.detect_sentiment(Text=text, LanguageCode='en')

    rating = 50 + sentiment['SentimentScore']['Positive'] * 50 - 50 * sentiment['SentimentScore']['Negative']
    rating = max(0, min(rating, 100))

    add_user_song_rating(data, rating, item_id)

    response_event = {
        "appId": data['appId'],
        "message": f"Thanks for your {sentiment['Sentiment']} review!",
        "user": data['user'],
        "token": data['token']
    }

    return responseQueue.send_message(MessageBody=json.dumps(response_event))
