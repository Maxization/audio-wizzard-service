import json
import boto3

sqs = boto3.resource('sqs')

def account_handler(event):
    options = event['data']['options']
    action = options[0]['name']
    account_event = {
        "appId": event['appId'],
        "data": event['data'],
        "user": event['user'],
        "token": event['token']
    }
    
    user_queue = sqs.get_queue_by_name(QueueName="user_queue")
    
    return user_queue.send_message(MessageBody=json.dumps(account_event))


def review_handler(event):
    options = event['data']['options']
    content = options[0]['value']
    
    songRatesQueue = sqs.get_queue_by_name(QueueName="song_rates_queue")

    analyze_event = {
        "appId": event['appId'],
        "message": content,
        "user": event['user'],
        "token": event['token']
    }

    return songRatesQueue.send_message(MessageBody=json.dumps(analyze_event))


def recommend_handler(event):
    number = 0
    if 'options' in event['data']:
        number = event['data']['options'][0]['value']
    else:
        number = 1
    
    recommendationQueue = sqs.get_queue_by_name(QueueName="recommendation_queue")
    
    recommendation_event = {
        "appId": event['appId'],
        "number": number,
        "user": event['user'],
        "token": event['token']
    }
    
    return recommendationQueue.send_message(MessageBody=json.dumps(recommendation_event))


def lambda_handler(event, context):
    command = event['data']['name']
    
    result = 200
    
    if command == 'account':
        result = account_handler(event)
    elif command == 'review':
        result = review_handler(event)
    elif command == 'recommend':
        result = recommend_handler(event)
    
    return result
