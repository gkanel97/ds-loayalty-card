import time
import requests
from uuid import uuid4

TOKEN = None
BASE_URL = 'https://hzsswx6it1.execute-api.eu-north-1.amazonaws.com/prod/'

def login_user(username, password):
    url = BASE_URL + 'login'
    payload = {
        'username': username,
        'password': password
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            TOKEN = response.json()['token']
            return response.json()
        else:
            return { 'status': 'failed', 'msg': f'Failed to login: {response.json()}' }
    except Exception as e:
        return { 'status': 'failed', 'msg': f'Failed to login: {str(e)}' }
    
def exponential_backoff_request(url, payload, max_retries=3, backoff_factor=2, timeout=10):
    for retry in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return { 'status': 'failed', 'msg': f'Request failed: {response.json()}' }
        except requests.exceptions.RequestException as e:
            if retry < max_retries - 1:
                time.sleep(backoff_factor * (2 ** retry))
            else:
                return { 'status': 'failed', 'msg': f'Request failed: {str(e)}' }
            
def retrieve_group_points(group_id):
    url = BASE_URL + 'points/retrieve'
    payload = { 'group_id': group_id }
    return exponential_backoff_request(url, payload, timeout=5)

def redeem_points(group_id, user_id, points, store_id):
    url = BASE_URL + 'points/redeem'
    payload = {
        'group_id': group_id,
        'user_id': user_id,
        'points': points,
        'store_id': store_id,
        'discount_id': str(uuid4())
    }
    return exponential_backoff_request(url, payload, timeout=5)

def register_purchase(group_id, user_id, value, store_id):
    url = BASE_URL + 'points/purchase'
    payload = {
        'group_id': group_id,
        'user_id': user_id,
        'store_id': store_id,
        'purchase_value': value,
        'purchase_id': str(uuid4())
    }
    return exponential_backoff_request(url, payload, timeout=5)

def retrieve_purchase_history(group_id, user_id):
    url = BASE_URL + 'points/purchase/history'
    payload = {
        'group_id': group_id,
        'user_id': user_id
    }
    return exponential_backoff_request(url, payload, timeout=10)
