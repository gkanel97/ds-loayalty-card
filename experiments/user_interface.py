import requests
from uuid import uuid4
from dispatcher import Dispatcher

BASE_URL = 'https://hzsswx6it1.execute-api.eu-north-1.amazonaws.com/prod/'

class UserInterface:

    def __init__(self, user_id, group_id, store_id=1):
        self.user_id = user_id
        self.group_id = group_id
        self.store_id = store_id
        self.token = None
        self.dispatcher = Dispatcher()
        
    def login_user(self, username, password):
        url = BASE_URL + 'login'
        payload = {
            'username': username,
            'password': password
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                self.token = response.json()['token']
                return response.json()
            else:
                return { 'status': 'failed', 'msg': f'Failed to login: {response.json()}' }
        except Exception as e:
            return { 'status': 'failed', 'msg': f'Failed to login: {str(e)}' }
                
    def retrieve_group_points(self):
        url = BASE_URL + 'points/retrieve'
        payload = { 'group_id': self.group_id }
        return self.dispatcher.wrap_retrieve_request(url, payload, timeout=5)

    def redeem_points(self, points):
        url = BASE_URL + 'points/redeem'
        payload = {
            'group_id': self.group_id,
            'user_id': self.user_id,
            'points': points,
            'store_id': self.store_id,
            'discount_id': str(uuid4())
        }
        return self.dispatcher.wrap_update_request(url, payload, timeout=5, allow_local=False)

    def register_purchase(self, value):
        url = BASE_URL + 'purchases/register'
        payload = {
            'group_id': self.group_id,
            'user_id': self.user_id,
            'store_id': self.store_id,
            'purchase_value': value,
            'purchase_id': str(uuid4())
        }
        return self.dispatcher.wrap_update_request(url, payload, timeout=5, allow_local=True)

    def retrieve_purchase_history(self):
        url = BASE_URL + 'purchases/retrieve'
        payload = {
            'group_id': self.group_id,
            'user_id': self.user_id
        }
        return self.dispatcher.wrap_retrieve_request(url, payload, timeout=10)
