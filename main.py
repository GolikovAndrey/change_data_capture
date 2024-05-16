import argparse
from cdc_test.sqlhelper import SQLHelper

argParser = argparse.ArgumentParser()
argParser.add_argument("--insert", type=int, default=0, help="Кол-во операций INSERT")
argParser.add_argument("--update", type=int, default=0, help="Кол-во операций UPDATE")
argParser.add_argument("--delete", type=int, default=0, help="Кол-во операций DELETE")
args = argParser.parse_args()

helper = SQLHelper(args.insert, args.update, args.delete)
helper.run_transactions()