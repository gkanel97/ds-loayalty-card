import boto3
import json


dynamodb = boto3.resource('dynamodb')
DYNAMODB_TABLE = 'User'

def find_item_by_user_id(user_id,table):
    response = table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('user_id').eq(user_id)
    )
    
    return response['Items']

def lambda_handler(event, context):
    body = json.loads(event['body'])
    user_ids = body['user_ids']
    new_group_id = body['new_group_id']
    
    table = dynamodb.Table(DYNAMODB_TABLE)
    update_failures = []
    
    for user_id in user_ids:
        try:
            items = find_item_by_user_id(user_id, table)
            print("item is ",items)
            for item in items:
                
                new_item = item.copy()  
                new_item['group_id'] = 7
                
                
                table.put_item(
                    Item={
                        'group_id': 6,  # Partition Key
                        'user_id': "30d16d7b-592d-486d-a958-38d6fc921508",    
                        'username': 'testuser5',
                        'email': item['email']
                    }
                )
                
                
                try:
                    table.delete_item(
                        Key={
                            'group_id': item['group_id'],
                            'user_id': item['user_id']
                        }
                    )
                except Exception as delete_error:
                    print(f"Failed to delete original item for user_id {user_id}: {delete_error}")
                    update_failures.append(user_id)
                
        except Exception as e:
            print(f"Failed to update user_id {user_id}: {e}")
            update_failures.append(user_id)
    
    if update_failures:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Failed to update group_id for some users.',
                'failed_user_ids': update_failures
            })
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'User group_ids updated successfully.'})
    }
