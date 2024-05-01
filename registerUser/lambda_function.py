import boto3
import json
import logging


cognito_client = boto3.client('cognito-idp',region_name='eu-north-1')
dynamodb = boto3.resource('dynamodb')

USER_POOL_ID = 'eu-north-1_y9V0mjfKH'
CLIENT_ID = '7gstac2jdrmg11ujvvsuqnlsc5'
DYNAMODB_TABLE = 'User'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    event_body = json.loads(event['body'])
    
    username = event_body['username']
    password = event_body['password']
    email = event_body['email']
    groupId = event_body['groupId']
    
    if groupId is  None:
        return {
            'statusCode': 400,
            'body': json.dumps({'error':'Groupid should not be None'})
        }
    try:
        cognito_response = cognito_client.sign_up(
            ClientId=CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
                
            ]
        )
    except Exception as e:
        logger.error(e)
        # DynamoDB write failed, delete the user from Cognito
        try:
            cognito_client.admin_delete_user(
                UserPoolId=USER_POOL_ID,
                Username=username
            )
            return_msg = 'DynamoDB write failed, user deleted from Cognito.'
        except cognito_client.exceptions.ClientError as e:
            # Handle failure to delete user from Cognito
            logger.error(e)
            return_msg = 'DynamoDB write failed, and unable to delete user from Cognito.'

        return {
            'statusCode': 500,
            'body': json.dumps({'error': return_msg})
        }
    
    
    sub_id = cognito_response['UserSub']
    
    # check the existence of gourpId in Points table
    # TODO: Concurrency Conflicts may exist when creating new entry in the Points table
    points_table = dynamodb.Table('Points')
    response = points_table.get_item(Key={'group_id': groupId})
    if 'Item' not in response:
        try:
            points_table.put_item(
                Item={
                    'group_id': groupId,
                    'total_points': 0
                }
            )
            logger.info(f"Created new points record for group {groupId}")
        except Exception as e:
            logger.error(e)
            # If creation failed due to existence of the gourpId, just skip it
    table = dynamodb.Table(DYNAMODB_TABLE)
    try:
        dynamo_response = table.put_item(
            Item={
                'group_id': groupId,  # Partition Key
                'user_id': sub_id,    # Sort Key, using Cognito UserSub
                'username': username,
                'email': email
            }
        )
    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Could not save user to DynamoDB.'})
        }
    
    

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'User created successfully.', 'userSub': sub_id})
    }
