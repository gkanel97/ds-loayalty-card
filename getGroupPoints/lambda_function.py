import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Points')
    
    body = json.loads(event['body'])
    group_id = int(body.get('group_id'))
    
    try:
        response = table.query(
            KeyConditionExpression='group_id = :group_id',
            ExpressionAttributeValues={
                ':group_id': group_id
            }
        )
        group_points = response['Items'][0]['total_points']
        return {
            'statusCode': 200,
            'body': json.dumps({ 'group_id': group_id, 'total_points': int(group_points) })
        }
    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 500,
            'body': json.dumps({ 'msg': 'An error occured' })
        }
    
