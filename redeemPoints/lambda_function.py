import json
import boto3
from uuid import uuid4
from datetime import datetime
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    
    # Connect to database table
    dynamodb = boto3.resource('dynamodb') 
    points_table = dynamodb.Table('Points')
    discounts_table = dynamodb.Table('Discounts')

    # Extract data from event
    group_id = event['group_id']
    user_id = event['user_id']
    points_to_redeem = event['points']
    store_id = event['store_id']
    discount_id = str(uuid4())

    try:
        # Redeem points if possible
        response = points_table.update_item(
            Key={'group_id': group_id},
            UpdateExpression='SET total_points = total_points - :val',
            ConditionExpression='total_points >= :val',
            ExpressionAttributeValues={':val': points_to_redeem},
            ReturnValues='UPDATED_NEW'
        )
        # Register discount
        response = discounts_table.put_item(
            Item={
                'group_id': group_id,
                'user_id': user_id,
                'discount_id': discount_id,
                'discount_points': -points_to_redeem,
                'store_id': store_id,
                'timestamp': str(datetime.now())
            }
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 200,
                'body': json.dumps({ 'status': 'failed', 'msg': 'Insufficient points' })
            }
        else:
            raise

    return {
        'statusCode': 200,
        'body': json.dumps({ 'status': 'success', 'msg': 'Points redeemed successfully' })
    }
