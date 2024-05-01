import json
import boto3
import logging
from uuid import uuid4
from datetime import datetime
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def identify_and_log_error(e):
    ret_msg = None
    if e.response['Error']['Code'] == 'TransactionCanceledException':
        reasons = e.response.get('CancellationReasons', [])
        logger.info(f'Failure reasons: {reasons}')
        for i, reason in enumerate(reasons):
            if reason.get('Code') == 'ConditionalCheckFailed':
                if i == 0:
                    ret_msg = {
                        'statusCode': 200,
                        'body': json.dumps({ 'status': 'failed', 'msg': 'Insufficient points' })
                    }
                elif i == 1:
                    ret_msg = {
                        'statusCode': 200,
                        'body': json.dumps({ 'status': 'duplicate', 'msg': 'Discount ID already exists' })
                    }
        if not ret_msg:
            ret_msg = {
                'statusCode': 500,
                'body': json.dumps({ 'status': 'failed', 'msg': f'Transaction failed: {str(e)}' })
            }
    else:
        ret_msg = {
            'statusCode': 500,
            'body': json.dumps({ 'status': 'failed', 'msg': f'Transaction failed: {str(e)}' })
        }

    return ret_msg

def lambda_handler(event, context):
    
    # Connect to database table
    dynamodb_client = boto3.client('dynamodb') 

    # Extract data from event
    req_body = json.loads(event['body'])
    group_id = req_body['group_id']
    user_id = req_body['user_id']
    points_to_redeem = req_body['points']
    store_id = req_body['store_id']
    discount_id = req_body['discount_id'] if 'discount_id' in req_body else str(uuid4())

    logger.info(f'Redemption {discount_id} | user {user_id} | group {group_id} | {points_to_redeem} points | processing')

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
                    },
                    'ConditionExpression': 'attribute_not_exists(discount_id)'
                }
            }
        ]
    )
    except ClientError as e:
        logger.error(f'Redemption {discount_id} | Client error: {str(e.response['Error'])}')
        return identify_and_log_error(e)
    except Exception as e:
        logger.error(f'Redemption {discount_id} | Exception: {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps({ 'status': 'failed', 'msg': f'Transaction failed: {str(e)}' })
        }

    logger.info(f'Redemption {discount_id}: {points_to_redeem} points redeemed successfully')
    return {
        'statusCode': 200,
        'body': json.dumps({ 'status': 'success', 'msg': 'Points redeemed successfully' })
    }
