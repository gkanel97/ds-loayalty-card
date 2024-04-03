import time
import requests
from uuid import uuid4

def login_iam_user(username, password):
    pass

def ui_redeem_points(group_id, user_id, points, store_id):
    url = 'https://uthdag66lrtkln5s6e2tekiyeq0larqh.lambda-url.eu-north-1.on.aws/'
    payload = {
        'group_id': group_id,
        'user_id': user_id,
        'points': points,
        'store_id': store_id,
        'discount_id': str(uuid4())
    }
    max_retries = 3
    backoff_factor = 2

    for retry in range(max_retries):
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                return { 'status': 'failed', 'msg': f'Failed to redeem points: {response.json()}' }
        except requests.exceptions.RequestException as e:
            if retry < max_retries - 1:
                time.sleep(backoff_factor * (2 ** retry))
            else:
                return { 'status': 'failed', 'msg': f'Failed to redeem points: {str(e)}' }            
