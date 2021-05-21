import json
import boto3

sqs = boto3.resource('sqs')


def set_param(param):
    # TODO: Sends to SQS that set information
    print(param['name'])


def account_handler(event):
    options = event['data']['options']
    action = options[0]['name']
    if action == 'delete':
        # TODO: Sends to SQS that delete information from database
        print("Deleting...")
    elif action == 'set':
        set_options = options[0]['options']
        for param in set_options:
            set_param(param)


def review_handler(event):
    options = event['data']['options']
    content = options[0]['value']

    song_rates_queue = sqs.get_queue_by_name(QueueName="song_rates_queue")

    analyze_event = {
        "appId": event['appId'],
        "message": content,
        "user": event['user'],
        "token": event['token']
    }

    return song_rates_queue.send_message(MessageBody=json.dumps(analyze_event))


def recommend_handler(event):
    number = 0
    if 'options' in event['data']:
        number = event['data']['options'][0]['value']
    else:
        number = 1

    recommendation_queue = sqs.get_queue_by_name(QueueName="recommendation_queue")

    recommendation_event = {
        "appId": event['appId'],
        "number": number,
        "user": event['user'],
        "token": event['token']
    }

    return recommendation_queue.send_message(MessageBody=json.dumps(recommendation_event))


def lambda_handler(event, context):
    command = event['data']['name']

    result = 200

    if command == 'account':
        result = account_handler(event)
    elif command == 'review':
        result = review_handler(event)
    elif command == 'recommend':
        result = recommend_handler(event)

    # lambda_client = boto3.client('lambda')
    # lambda_client.invoke(FunctionName='chat_service',
    #                     InvocationType='Event',
    #                     Payload=json.dumps(event))

    return result
