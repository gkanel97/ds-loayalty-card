import json
import boto3

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Points')
    group_id = event['group_id']
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
