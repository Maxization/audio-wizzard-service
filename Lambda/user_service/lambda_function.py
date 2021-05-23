import json
import string
import boto3
from boto3.dynamodb.conditions import Key

sqs = boto3.resource('sqs')
responseQueue = sqs.get_queue_by_name(QueueName="chat_service_queue")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DynamoDBTableUsersName')

def lambda_handler(event, context):
    data=json.loads(event['Records'][0]['body'])
    
    queryResult = table.query(KeyConditionExpression=Key('USER_ID').eq(data['user']['id']))
    if queryResult['Count'] == 0:
        user = { "USER_ID": f"\"{data['user']['id']}\"" }
    else:
        user = queryResult['Items'][0]
    
    commandType = data['data']['options'][0]['name']
    message = "Nothing done."
    
    if commandType == 'delete':
        if queryResult['Count'] == 0:
            message = "You cannot delete your account, because it does not exist..."
        else:
            table.delete_item(Key={'USER_ID': data['user']['id']})
            message = "Your account has been deleted..."
    elif commandType == 'set':
        if data['data']['options'][0] == { "name": "set", "type": 1 }:
            if queryResult['Count'] == 0:
                table.put_item(Item=user)
                message = "Account created without details!"
            else:
                message = "Nothing to update."
        else:
            for opt in data['data']['options'][0]['options']:
                user[opt['name'].upper()] = f"{opt['value']}"
            table.put_item(Item=user)
            if queryResult['Count'] == 0:
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
