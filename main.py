import sys
import random
from cdc_test.sqlhelper import SQLHelper

rng = int(sys.argv[1])

print(f"Будет произведено транзакций: {rng}")

helper = SQLHelper()

helper.init()

functions = [
    helper.insert_row,
    # helper.delete_row,
    # helper.update_row
]

for _ in range(0, rng):
    random.choice(functions)()

print("Транзакции были проведены успешно.")