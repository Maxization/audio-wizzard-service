import json
import boto3


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
    # TODO: Sends to SQS that analyze message
    print(content)


def recommend_handler(event):
    number = 0
    if 'options' in event['data']:
        number = event['data']['options'][0]['value']
    else:
        number = 1
    # TODO: Sends to SQS with recommendations
    print(f"Recommed {number}")


def lambda_handler(event, context):
    command = event['data']['name']

    if command == 'account':
        account_handler(event)
    elif command == 'review':
        review_handler(event)
    elif command == 'recommend':
        recommend_handler(event)

    lambda_client = boto3.client('lambda')
    lambda_client.invoke(FunctionName='chat_service',
                         InvocationType='Event',
                         Payload=json.dumps(event))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
