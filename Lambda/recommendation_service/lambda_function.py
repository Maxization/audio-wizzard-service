import json
import boto3
from boto3.dynamodb.conditions import Key

sqs = boto3.resource('sqs')

personalizeRt = boto3.client('personalize-runtime')
responseQueue = sqs.get_queue_by_name(QueueName="chat_service_queue")
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DynamoDBTableSongsName')

def get_recommendation(event):
    number = event['number']
    
    if number <= 0 or number > 100:
        number = 1
    
    response = personalizeRt.get_recommendations(
        campaignArn = 'arn:aws:personalize:eu-central-1:043035977035:campaign/audio_wizzard_service',
        userId = event['user']['id'],
        numResults = number
    )
    
    result = ""
    i = 0
    for item in response['itemList']:
        i += 1
        queryResult = table.query(KeyConditionExpression=Key('ITEM_ID').eq(item['itemId']))
        result += f"{i}. " + queryResult['Items'][0]['ARTISTS'] + " - " + queryResult['Items'][0]['NAME'] + "\n"
    return result

def lambda_handler(event, context):
    data=json.loads(event['Records'][0]['body'])

    result = get_recommendation(data)
    
    response_event = {
        "appId": data['appId'],
        "message": result,
        "user": data['user'],
        "token": data['token']
    }
    
    return responseQueue.send_message(MessageBody=json.dumps(response_event))
