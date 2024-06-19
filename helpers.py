import re

def validate_address_format(user_address: str) -> bool:
    ton_address_pattern = re.compile(r'^[A-Za-z0-9_-]{48}$')
    match = ton_address_pattern.match(user_address)
    return bool(match)
