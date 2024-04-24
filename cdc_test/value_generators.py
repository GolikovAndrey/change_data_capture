import json
import string
import random as r
from datetime import datetime

def generate_int_value():
    return r.randint(0, 100)

def generate_str_value():
    return ''.join(
        r.choice(
            string.ascii_uppercase 
            + string.digits 
            + string.ascii_lowercase 
            + string.ascii_letters
        ) for _ in range(r.randint(5, 20))
    )

def generate_double_value():
    return round(r.random() * r.randint(10, 100), 2)

def generate_timestamp_value():
    return (
        datetime
        .fromtimestamp(
            r.randint(
                1200000000, 
                1700000000
            )
        ).strftime('%Y-%m-%d %H:%M:%S')
    )

def genarate_array():
    return json.dumps([r.randint(0, 10) for _ in range(1, r.randint(2, 10))])