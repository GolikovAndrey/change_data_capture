import string
import random as r

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