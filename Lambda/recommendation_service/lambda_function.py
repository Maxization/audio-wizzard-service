import json
import boto3
from boto3.dynamodb.conditions import Key

personalizeRt = boto3.client('personalize-runtime')

sqs = boto3.resource('sqs')
responseQueue = sqs.get_queue_by_name(QueueName="chat_service_queue")

dynamodb = boto3.resource('dynamodb')


def query_users(user_id):
    table = dynamodb.Table('DynamoDBTableUsersName')
    response = table.query(
        KeyConditionExpression=Key('USER_ID').eq(user_id)
    )

    return response['Items']


def send_no_account_message(event):
    response_event = {
        "appId": event['appId'],
        "message": "Create your account with /account set",
        "user": event['user'],
        "token": event['token']
    }

    return responseQueue.send_message(MessageBody=json.dumps(response_event))


def query_users(userId):
    table = dynamodb.Table('DynamoDBTableUsersName')
    response = table.query(
        KeyConditionExpression=Key('USER_ID').eq(userId)
    )
    
    return response['Items']


def send_no_account_message(event):
    response_event = {
        "appId": event['appId'],
        "message": "Create your account with /account set",
        "user": event['user'],
        "token": event['token']
    }
    
    return responseQueue.send_message(MessageBody=json.dumps(response_event))

    
def get_recommendation(event):
    number = event['number']

    if number <= 0 or number > 25:
        number = 1

    response = personalizeRt.get_recommendations(
        campaignArn='arn:aws:personalize:eu-central-1:043035977035:campaign/audio_wizzard_service',
        userId=event['user']['id'],
        numResults=number
    )

    table = dynamodb.Table('DynamoDBTableSongsName')
    result = ""
    i = 0
    for item in response['itemList']:
        i += 1

        query_result = table.query(KeyConditionExpression=Key('ITEM_ID').eq(item['itemId']))
        result += f"**{i}.** " + query_result['Items'][0]['ARTISTS'] + "```" + query_result['Items'][0]['NAME'] + "```"

    return result


def lambda_handler(event, context):
    data = json.loads(event['Records'][0]['body'])

    user = query_users(data['user']['id'])

    if not user:
        return send_no_account_message(data)

    result = get_recommendation(data)

    response_event = {
        "appId": data['appId'],
        "message": result,
        "user": data['user'],
        "token": data['token']
    }

    return responseQueue.send_message(MessageBody=json.dumps(response_event))
