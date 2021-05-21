import json
import boto3

sqs = boto3.resource('sqs')

personalizeRt = boto3.client('personalize-runtime')
responseQueue = sqs.get_queue_by_name(QueueName="chat_service_queue")


def get_recommendation(event):
    response = personalizeRt.get_recommendations(
        campaignArn='arn:aws:personalize:eu-central-1:043035977035:campaign/audio_wizzard_service',
        userId=event['user']['id'],
        numResults=event['number']
    )

    result = ""
    for item in response['itemList']:
        result += item['itemId'] + ", "
        print(item)

    return result


def lambda_handler(event, context):
    data = json.loads(event['Records'][0]['body'])

    result = get_recommendation(data)

    response_event = {
        "appId": data['appId'],
        "message": result,
        "user": data['user'],
        "token": data['token']
    }

    print(response_event)
    return responseQueue.send_message(MessageBody=json.dumps(response_event))
