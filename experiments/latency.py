import time
import json
import requests
from tqdm import tqdm
from uuid import uuid4

BASE_URL = 'https://hzsswx6it1.execute-api.eu-north-1.amazonaws.com/prod/'

def record_request_latency(url, payload, timeout=10):
    start = time.time()
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        if response.status_code == 200:
            return time.time() - start
        else:
            return -1
    except Exception as e:
        return -1
    
def measure_latency(url, payload, num_requests=10):
    latencies = []
    pbar = tqdm(total=num_requests)
    for _ in range(num_requests):
        latency = record_request_latency(url, payload)
        if latency != -1:
            latencies.append(latency)
        pbar.update(1)
    pbar.close()
    return latencies

if __name__ == '__main__':

    latencies = {
        'login': [],
        'retrievePoints': [],
        'redeemPoints': [],
        'registerPurchase': [],
        'retrievePurchases': []
    }

    # Measure login latency
    print('Measuring login latency...')
    url = BASE_URL + 'login'
    payload = { 'username': 'cafeuser', 'password': 'cafeUser!1' }
    latencies['login'] = measure_latency(url, payload, num_requests=500)

    # Measure purchase registration latency
    print('Measuring purchase registration latency...')
    url = BASE_URL + 'purchases/register'
    payload = {
        'group_id': 6,
        'user_id': '30d16d7b-592d-486d-a958-38d6fc921508',
        'store_id': 17,
        'purchase_value': 10,
        'purchase_id': str(uuid4())
    }
    latencies['registerPurchase'] = measure_latency(url, payload, num_requests=500)

    # Measure purchase retrieval latency
    print('Measuring purchase retrieval latency...')
    url = BASE_URL + 'purchases/retrieve'
    payload = { 'group_id': 6 }
    latencies['retrievePurchases'] = measure_latency(url, payload, num_requests=500)
    
    # Measure point retrieval latency
    print('Measuring point retrieval latency...')
    url = BASE_URL + 'points/retrieve'
    payload = { 'group_id': 6 }
    latencies['retrievePoints'] = measure_latency(url, payload, num_requests=500)

    # Measure point redemption latency
    print('Measuring point redemption latency...')
    url = BASE_URL + 'points/redeem'
    payload = {
        'group_id': 6,
        'user_id': '30d16d7b-592d-486d-a958-38d6fc921508',
        'points': 5,
        'store_id': 17
    }
    latencies['redeemPoints'] = measure_latency(url, payload, num_requests=500)

    # Save latencies to file
    with open('measurements.json', 'w') as f:
        json.dump(latencies, f)