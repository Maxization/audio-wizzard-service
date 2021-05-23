import os
import boto3
import json
import uuid
import time
from boto3.dynamodb.conditions import Key

client = boto3.client('comprehend')
sqs = boto3.resource('sqs')
dynamodb = boto3.resource('dynamodb')

personalize_events = boto3.client(service_name='personalize-events')

responseQueue = sqs.get_queue_by_name(QueueName="chat_service_queue")

def query_users(userId):
    table = dynamodb.Table('DynamoDBTableUsersName')
    response = table.query(
        KeyConditionExpression=Key('USER_ID').eq(userId)
    )
    
    return response['Items']

def add_user_to_personalize(event):
    user_properties= {
        "age": 22, # TODO: Read from database
        "gender": "male" # TODO: Read from database
    }
    
    personalize_events.put_users(
        datasetArn = 'arn:aws:personalize:eu-central-1:043035977035:dataset/user-songs-group/USERS',
        users = [{
            'userId': event['user']['id'],
            'properties': json.dumps(user_properties)   
        }]
    )
    
def add_user_song_rating(event):
    interaction_properties= {
        "rating": 50 # TODO: Calculate with Comprehend
    }
    
    personalize_events.put_events(
    trackingId = '1d2eb1be-2cef-4569-8c3b-12ba7d3cbc08',
    userId= event['user']['id'],
    sessionId = uuid.uuid4(),
    eventList = [{
        'sentAt': time.time(),
        'eventType': 'eventTypePlaceholder',
        'itemId': '35iwgR4jXetI318WEWsa1Q' # TODO: Read from database
        }]
    )

def send_no_account_message(event):
    response_event = {
        "appId": event['appId'],
        "message": "Create your account with /account set",
        "user": event['user'],
        "token": event['token']
    }
    
    return responseQueue.send_message(MessageBody=json.dumps(response_event))

def lambda_handler(event, context):
    data=json.loads(event['Records'][0]['body'])
    
    user = query_users(data['user']['id'])
    
    if not user:
        return send_no_account_message(data)
    
    text=data['message']
    sentiment=client.detect_sentiment(Text=text, LanguageCode='en')
    
    sentiment_event = {
        "appId": data['appId'],
        "message": sentiment['Sentiment'],
        "user": data['user'],
        "token": data['token']
    }
    
    return responseQueue.send_message(MessageBody=json.dumps(sentiment_event))
    