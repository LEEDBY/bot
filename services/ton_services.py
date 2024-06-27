import requests
from config import TON_API_KEY, TONCONSOLE_API_KEY
import random
import asyncio
import re
import time
import aiohttp
import config
from typing import Dict, Any
from TonTools.Providers.TonCenterClient import TonCenterClient
from datetime import datetime

balance_cache = {}
last_update_time = {}

client = TonCenterClient(key=config.TON_API_KEY, base_url=config.TON_API_URL)

# Создаем глобальный кеш для хранения балансов и времени последнего обновления
BALANCE_CACHE = {}

async def send_xgr(from_address, to_address, amount):
    url = f"{config.TON_API_URL}/sendJetton"
    data = {
        "from": from_address,
        "to": to_address,
        "amount": int(amount * 10**9),  # Конвертация в нанотоны
        "jetton": config.XGR_JETTON_MASTER_ADDRESS,
        "api_key": config.TON_API_KEY
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()

async def check_transaction_status(address, memo):
    url = f'https://toncenter.com/api/v2/getTransactions?address={address}&api_key={config.TON_API_KEY}&limit=50'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            transactions = await response.json().get('transactions', [])

            for tx in transactions:
                if tx.get('in_msg', {}).get('message', '') == memo:
                    return tx
            return None

def get_jetton_balance(account_id, jetton_id, token):
    url = f"https://tonapi.io/v2/accounts/{account_id}/jettons/{jetton_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'balance' in data and data['balance']:
            return int(data['balance'])
        else:
            return 0
    else:
        raise Exception(f"Ошибка: {response.status_code}, {response.text}")

def generate_memo():
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])

def validate_address_format(address):
    # Регулярное выражение для проверки адреса TON
    pattern = r'^[Uu][Qq][A-Za-z0-9_-]{48}$'
    match = re.match(pattern, address)
    print(f"Validation result for {address}: {match is not None}")
    return bool(match)

async def update_giver_balances(givers, address_key):
    current_time = time.time()
    cache_duration = 60  # Длительность кеширования в секундах

    for giver in givers:
        address = giver[address_key]
        if address in BALANCE_CACHE and (current_time - BALANCE_CACHE[address]['timestamp']) < cache_duration:
            giver['balance'] = BALANCE_CACHE[address]['balance']
            print(f"Using cached balance for giver {address}: {giver['balance']}")
        else:
            print(f"Updating balance for giver: {address}")
            try:
                balance = get_jetton_balance(address, config.XGR_JETTON_MASTER_ADDRESS, config.TONCONSOLE_API_KEY)
                giver['balance'] = balance / 10**9  # Convert balance from nanoton to ton
                BALANCE_CACHE[address] = {'balance': giver['balance'], 'timestamp': current_time}
                print(f"Updated balance for giver {address}: {giver['balance']}")
            except Exception as e:
                print(f"Error updating jetton wallet: {e}")
                giver['balance'] = 0
                BALANCE_CACHE[address] = {'balance': 0, 'timestamp': current_time}

async def update_all_giver_balances():
    await update_giver_balances(config.GIVERS, 'new_address')

async def periodic_update_balances():
    while True:
        try:
            print("Starting periodic update of giver balances...")
            await update_giver_balances(config.GIVERS, 'new_address')  # Изменено: добавлен аргумент 'address_key'
            print("Periodic update completed.")
        except Exception as e:
            print(f"Error during periodic update: {e}")
        await asyncio.sleep(60)
