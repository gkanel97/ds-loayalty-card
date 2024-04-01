import json
import boto3
from datetime import datetime
from decimal import Decimal
import uuid

# TODO: add exception handler for unexisted store_id.
def lambda_handler(event, context):
    """
    Handles a purchase event by saving a purchase record to the DynamoDB 'Purchases' table.
    Automatically generates a unique purchase_id and the current timestamp as purchase_date.
    Validates the purchase value to ensure it's not negative and verifies the existence of the user in the 'User' table.

    Parameters:
    event (dict): An event containing purchase information, including group_id, user_id, purchase_value, and store_id.
    context: Provides information about the invocation, function, and execution environment.

    Returns:
    dict: A response object with a statusCode and a body indicating the outcome of the operation.
    """
    
    # Initialize the DynamoDB client and resource
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_resource = boto3.resource('dynamodb')
    
    # Connect to the 'User' table
    user_table_name = 'User'
    user_table = dynamodb_resource.Table(user_table_name)

    # Extract group ID and user ID and purchase value from the event
    user_id = event.get('user_id')
    group_id = event.get('group_id')
    purchase_value = Decimal(event.get('purchase_value', 0))

    # Check if the purchase value is negative
    if purchase_value < 0:
        return {
            'statusCode': 400,
            'body': json.dumps('Error: Purchase value cannot be negative.')
        }

    # Check the existence of the user
    try:
        user_response = user_table.get_item(Key={'group_id': group_id, 'user_id': user_id})
        if 'Item' not in user_response:
            return {
                'statusCode': 404,
                'body': json.dumps(f'Error: User with group_id {group_id} \t user_id {user_id} does not exist.')
            }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error: Failed to retrieve user information.')
        }

    # Automatically generate purchase_id and purchase_date
    purchase_id = str(uuid.uuid4())
    purchase_date = datetime.now().isoformat()

    # Extract additional purchase record data from the event
    store_id = event.get('store_id')

    # Attempt to save the new purchase and update the user's total points in an atomic transaction
    try:
        response = dynamodb_client.transact_write_items(
            TransactItems=[
                {
                    'Put': {
                        'TableName': 'Purchases',
                        'Item': {
                            'group_id': {'N': str(group_id)},
                            'purchase_id': {'S': purchase_id},
                            'purchase_date': {'S': purchase_date},
                            'purchase_value': {'N': str(purchase_value)},
                            'store_id': {'N': str(store_id)},
                            'user_id': {'S': user_id}
                        }
                    }
                },
                {
                    'Update': {
                        'TableName': 'Points',
                        'Key': {
                            'group_id': {'N': str(group_id)}
                        },
                        'UpdateExpression': 'SET total_points = total_points + :val',
                        'ExpressionAttributeValues': {
                            ':val': {'N': str(purchase_value)}
                        },
                        'ReturnValuesOnConditionCheckFailure': 'ALL_OLD'
                    }
                }
            ]
        )
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error: Failed to save purchase record and update group points.')
        }

    # Successfully saved the record
    return {
        'statusCode': 200,
        'body': json.dumps('Purchase record saved successfully.')
    }
