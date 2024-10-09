#import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

import anvil.server
import csv
import json
import base64
import requests
from datetime import datetime
import pytz
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)

@anvil.server.callable
def process_csv(file):
    csv_file_path = anvil.media.write_to_file(file, 'uploaded.csv')
    json_file_path = 'output.json'
    csv_to_json(csv_file_path, json_file_path)
    return json.load(open(json_file_path))

def csv_to_json(csv_file_path, json_file_path):
    data = []
    with open(csv_file_path, encoding='utf-8') as csvf:
        csv_reader = csv.DictReader(csvf)
        for rows in csv_reader:
            purchase_order = {
                "id": rows["id"],
                "stage": rows["stage"],
                "estimatedArrivalDate": rows["estimatedArrivalDate"],
                "estimatedDeliveryDate": rows["estimatedDeliveryDate"]
            }
            data.append(purchase_order)
    with open(json_file_path, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps({"purchase_orders": data}, indent=4))

