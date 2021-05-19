import json


def lambda_handler(event, context):
    # TODO implement
    print("I am just ")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
