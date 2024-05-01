import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    client = boto3.client('cognito-idp', region_name='eu-north-1')

    username = event['username']
    password = event['password']

    # response = client.admin_confirm_sign_up(
    #     UserPoolId='eu-north-1_y9V0mjfKH',
    #     Username=username
    # )

    try:
        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password
            },
            ClientId='7gstac2jdrmg11ujvvsuqnlsc5'
        )
    
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # 如果你想要更严格的控制，这里可以替换成具体的源
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"token": response['AuthenticationResult']['IdToken']})
        }
    
    except client.exceptions.NotAuthorizedException:
        return {
            "statusCode": 401,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": 'Password is incorrect'})
        }
    
    except client.exceptions.UserNotFoundException:
        return {
            "statusCode": 404,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": 'Username does not exist'})
        }
    
    except ClientError as e:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": str(e)})
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": 'An unexpected error occurred'})
        }