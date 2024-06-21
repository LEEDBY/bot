import requests
from config import TON_API_KEY
import random
import re
import time
import aiohttp
import config

async def get_balance(address: str) -> int:
    async with aiohttp.ClientSession() as session:
        url = f"https://tonapi.io/v1/account/getBalance?address={address}"
        headers = {
            'Authorization': f'Bearer {config.TON_API_KEY}',
        }
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return int(data['balance'])
            else:
                return 0

async def send_toncoins(from_address, secret, to_address, amount, memo):
    url = 'https://toncenter.com/api/v2/sendTransaction'
    data = {
        'from': from_address,
        'to': to_address,
        'value': amount,
        'api_key': TON_API_KEY,
        'secret': secret,
        'comment': memo
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()

async def check_transaction_status(address, memo):
    url = f'https://toncenter.com/api/v2/getTransactions?address={address}&api_key={TON_API_KEY}&limit=50'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            transactions = await response.json().get('transactions', [])

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

async def update_giver_balances(givers):
    for giver in givers:
        giver['balance'] = await get_balance(giver['address'])
