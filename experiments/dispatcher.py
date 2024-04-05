import time
import json
import requests

class Dispatcher():

    def __init__(self, max_retries=3, backoff_factor=2, timeout=10):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout

    def exponential_backoff_request(self, url, payload, timeout):
        timeout = self.timeout if timeout is None else timeout
        for retry in range(self.max_retries):
            try:
                response = requests.post(url, json=payload, timeout=timeout)
                if response.status_code == 200:
                    return { 'status': 'success', 'response': response.json() }
                else:
                    return { 'status': 'failed', 'msg': f'Request failed: {response.json()}' }
            except requests.exceptions.RequestException as e:
                if retry < self.max_retries - 1:
                    print(f'Request failed: {str(e)}. Retrying in {self.backoff_factor * (2 ** retry)} seconds.')
                    time.sleep(self.backoff_factor * (2 ** retry))
                else:
                    return { 'status': 'network-error', 'msg': f'Request failed: {str(e)}' }
                
    def wrap_update_request(self, url, payload, timeout=None, allow_local=False):
        resp = self.exponential_backoff_request(url, payload, timeout)
        if resp['status'] == 'network-error' and allow_local:
            # Save request to local storage
            print('Saving request to local storage...')
            with open('local_storage.txt', 'a') as f:
                f.write(f'{url} {json.dumps(payload)}\n')
            return { 'status': 'success', 'response': 'Request saved to local storage.' }
        else:
            # Return failed response
            return resp
        
    def wrap_retrieve_request(self, url, payload, timeout=None):
        return self.exponential_backoff_request(url, payload, timeout)

    def try_saved_requests(self):
        lines = []
        with open('./experiments/local_storage.txt', 'r') as f:
            lines = f.readlines()

        failed_requests = []
        for line in lines:
            url, payload = line.strip().split(' ', 1)
            payload = json.loads(payload)
            resp = self.exponential_backoff_request(url, payload, timeout=5)
            if resp['status'] == 'success':
                print(f'Successfully sent saved request: {resp["response"]}')
            else:
                print(f'Failed to send saved request: {resp["msg"]}')
                failed_requests.append(line)

        with open('local_storage.txt', 'w') as f:
            for line in failed_requests:
                f.write(line)