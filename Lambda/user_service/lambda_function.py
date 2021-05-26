import json
import boto3
from boto3.dynamodb.conditions import Key

personalize_events = boto3.client(service_name='personalize-events')

sqs = boto3.resource('sqs')
responseQueue = sqs.get_queue_by_name(QueueName="chat_service_queue")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DynamoDBTableUsersName')


def add_user_to_personalize(user):
    user_properties = {}
    if 'AGE' in user:
        user_properties['AGE'] = user['AGE']
    if 'GENDER' in user:
        user_properties['GENDER'] = user['GENDER']

    personalize_events.put_users(
        datasetArn='arn:aws:personalize:eu-central-1:043035977035:dataset/user-songs-group/USERS',
        users=[{
            'userId': user['USER_ID'],
            'properties': json.dumps(user_properties)
        }]
    )


def lambda_handler(event, context):
    data = json.loads(event['Records'][0]['body'])

    query_result = table.query(KeyConditionExpression=Key('USER_ID').eq(data['user']['id']))
    if query_result['Count'] == 0:
        user = {"USER_ID": f"{data['user']['id']}"}
    else:
        user = query_result['Items'][0]

    command_type = data['data']['options'][0]['name']
    message = "Nothing done."

    if command_type == 'delete':
        if query_result['Count'] == 0:
            message = "You cannot delete your account, because it does not exist..."
        else:
            table.delete_item(Key={'USER_ID': data['user']['id']})
            message = "Your account has been deleted..."
    elif command_type == 'set':
        if data['data']['options'][0] == {"name": "set", "type": 1}:
            if query_result['Count'] == 0:
                table.put_item(Item=user)
                add_user_to_personalize(user)
                message = "Account created without details!"
            else:
                message = "Nothing to update."
        else:
            for opt in data['data']['options'][0]['options']:
                user[opt['name'].upper()] = f"{opt['value']}"
            table.put_item(Item=user)
            add_user_to_personalize(user)
            if query_result['Count'] == 0:
                message = "Account created with details!"
            else:
                message = "Details updated!"

    response_event = {
        "appId": data['appId'],
        "message": message,
        "user": data['user'],
        "token": data['token']
    }

    return responseQueue.send_message(MessageBody=json.dumps(response_event))
