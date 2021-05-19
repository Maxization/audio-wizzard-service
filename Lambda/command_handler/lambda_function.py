import json
import boto3

def lambda_handler(event, context):
    print("debug")
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(FunctionName='chat_service',
                         InvocationType='Event',
                         Payload=json.dumps(event))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
