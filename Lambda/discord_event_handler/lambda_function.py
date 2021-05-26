import json
import boto3

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

PING_PONG = {"type": 1}
RESPONSE_TYPES = {
    "PONG": 1,
    "ACK_NO_SOURCE": 2,
    "MESSAGE_NO_SOURCE": 3,
    "MESSAGE_WITH_SOURCE": 4,
    "ACK_WITH_SOURCE": 5
}


def get_public_key():
    secretsmanager = boto3.client('secretsmanager')
    result = secretsmanager.get_secret_value(
        SecretId="DiscordPublicKey"
    )['SecretString']
    return json.loads(result)['DiscordPublicKey']


PUBLIC_KEY = get_public_key()


def verify_signature(event):
    raw_body = event.get("rawBody")
    auth_sig = event['params']['header'].get('x-signature-ed25519')
    auth_ts = event['params']['header'].get('x-signature-timestamp')

    message = auth_ts.encode() + raw_body.encode()
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    verify_key.verify(message, bytes.fromhex(auth_sig))  # raises an error if unequal


def ping_pong(body):
    if body.get("type") == 1:
        return True
    return False


def lambda_handler(event, context):
    print(f"event {event}")  # debug print

    # verify the signature
    try:
        verify_signature(event)
    except Exception as e:
        raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")

    # check if message is a ping
    body = event.get('body-json')
    if ping_pong(body):
        return PING_PONG

    command_event = {
        "appId": body['application_id'],
        "data": body['data'],
        "user": body['member']['user'],
        "token": body['token']
    }

    lambda_client = boto3.client('lambda')
    response = lambda_client.invoke(FunctionName='command_handler',
                                    InvocationType='Event',
                                    Payload=json.dumps(command_event))

    return {
        "type": RESPONSE_TYPES['ACK_WITH_SOURCE']
    }
