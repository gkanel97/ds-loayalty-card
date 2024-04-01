import json
import boto3
from uuid import uuid4
from datetime import datetime
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    
    # Connect to database table
    dynamodb_client = boto3.client('dynamodb') 

    # Extract data from event
    group_id = event['group_id']
    user_id = event['user_id']
    points_to_redeem = event['points']
    store_id = event['store_id']
    discount_id = str(uuid4())

    try:
        response = dynamodb_client.transact_write_items(TransactItems=[
            {
                'Update': {
                    'TableName': 'Points',
                    'Key': {'group_id': {'N': str(group_id)}},
                    'UpdateExpression': 'SET total_points = total_points - :val',
                    'ConditionExpression': 'total_points >= :val',
                    'ExpressionAttributeValues': {':val': {'N': str(points_to_redeem)}}
                }
            },
            {
                'Put': {
                    'TableName': 'Discounts',
                    'Item': {
                        'group_id': {'N': str(group_id)},
                        'user_id': {'S': user_id},
                        'discount_id': {'S': discount_id},
                        'discount_points': {'N': str(-points_to_redeem)},
                        'store_id': {'N': str(store_id)},
                        'timestamp': {'S': str(datetime.now())}
                    }
                }
            }
        ]
    )
    except ClientError as e:
        if e.response['Error']['Code'] == 'TransactionCanceledException':
            if 'ConditionalCheckFailed' in e.response['Error']['Message']:
                return {
                    'statusCode': 200,
                    'body': json.dumps({ 'status': 'failed', 'msg': 'Insufficient points' })
                }
            else:
                return {
                    'statusCode': 500,
                    'body': json.dumps({ 'status': 'failed', 'msg': f'Transaction failed: {str(e)}' })
                }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({ 'status': 'failed', 'msg': f'Transaction failed: {str(e)}' })
        }

    return {
        'statusCode': 200,
        'body': json.dumps({ 'status': 'success', 'msg': 'Points redeemed successfully' })
    }
