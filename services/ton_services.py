import requests
from config import TON_API_KEY
import random
import re

def get_balance(address: str) -> int:
    url = f'https://toncenter.com/api/v2/getAddressBalance?address={address}&api_key={TON_API_KEY}'
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        return 0
    
    try:
        response_json = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Error: Failed to decode JSON response")
        return 0
    
    return int(response_json.get('balance', 0))

def send_toncoins(from_address, secret, to_address, amount, memo):
    url = 'https://toncenter.com/api/v2/sendTransaction'
    data = {
        'from': from_address,
        'to': to_address,
        'value': amount,
        'api_key': TON_API_KEY,
        'secret': secret,
        'comment': memo
    }
    response = requests.post(url, json=data)
    return response.json()

def check_transaction_status(address, memo):
    url = f'https://toncenter.com/api/v2/getTransactions?address={address}&api_key={TON_API_KEY}&limit=50'
    response = requests.get(url)
    transactions = response.json().get('transactions', [])

    for tx in transactions:
        if tx.get('in_msg', {}).get('message', '') == memo:
            return tx
    return None

def generate_memo():
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])

def validate_address_format(address):
    # Регулярное выражение для проверки адреса TON
    pattern = r'^[Uu][Qq][A-Za-z0-9_-]{48}$'
    match = re.match(pattern, address)
    print(f"Validation result for {address}: {match is not None}")
    return bool(match)

def update_giver_balances(givers):
    for giver in givers:
        giver['balance'] = get_balance(giver['address'])
