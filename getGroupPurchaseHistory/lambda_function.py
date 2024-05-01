import boto3
from boto3.dynamodb.conditions import Key
import json
from decimal import Decimal

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError

def lambda_handler(event, context):
    """
    AWS Lambda function to fetch all purchase records for a given group_id from the 'Purchases' DynamoDB table.
    Converts Decimal to string to prevent precision loss during JSON serialization.

    Parameters:
    event (dict): A dictionary that must contain the key 'group_id' with a string value.

    Returns:
    dict: A response object containing the statusCode and the body with a list of purchase records.
    """
    req_body = json.loads(event['body'])
    group_id = req_body.get('group_id')
    if not group_id:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing "group_id" in the request.')
        }

    table = dynamodb.Table('Purchases')

    try:
        response = table.query(
            KeyConditionExpression=Key('group_id').eq(group_id)
        )
        items = response.get('Items', [])

        items_json = json.dumps(items, default=decimal_default)

        return {
            'statusCode': 200,
            'body': items_json
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Internal server error')
        }
