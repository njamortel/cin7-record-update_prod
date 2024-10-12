import anvil.server
import json
import csv
import base64
import requests
from datetime import datetime
import time

# Global variable to store log messages
log_messages = []
progress = 0
update_result = ""

@anvil.server.callable
def process_csv_and_update(file):
    global progress
    progress = 0  # Reset progress
    append_to_log_message_queue("process_csv_and_update called")

    try:
        # Read the CSV file
        csv_data = file.get_bytes().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(csv_data)
        data = []

        # Prepare JSON structure
        for row in csv_reader:
            purchase_order = [{
                "id": int(row["id"]),
                "stage": row["stage"],
                "estimatedArrivalDate": format_date(row["estimatedArrivalDate"]),
                "estimatedDeliveryDate": format_date(row["estimatedDeliveryDate"])
            }]
            data.append(purchase_order)

        json_data = json.dumps({"purchase_orders": data}, indent=4)
        append_to_log_message_queue("CSV file processed successfully")
        return update_purchase_orders(json_data)
    except Exception as e:
        append_to_log_message_queue(f"Error processing CSV: {str(e)}")
        return f"Error processing CSV: {str(e)}"

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        return date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        return date_str

def update_purchase_orders(json_data):
    global progress, update_result
    append_to_log_message_queue("update_purchase_orders called")
    api_key = '4cc465afd3534370bbc4431e770346e1'
    username = 'SignalPowerDelivUS'
    endpoint_url = "https://api.cin7.com/api/v1/PurchaseOrders"
    credentials = base64.b64encode(f'{username}:{api_key}'.encode('utf-8')).decode('utf-8')
    headers = {
        'Authorization': 'Basic ' + credentials,
        'Content-Type': 'application/json'
    }

    data = json.loads(json_data)
    total_records = len(data["purchase_orders"])
    updated_records = 0

    for i, order in enumerate(data["purchase_orders"], start=1):
        append_to_log_message_queue(f"Updating record {i}/{total_records}: {json.dumps(order, indent=4)}")

        try:
            response = requests.post(endpoint_url, headers=headers, json=order)
            response.raise_for_status()

            if response.status_code == 200:
                updated_records += 1
                append_to_log_message_queue(f"Successfully updated record {order['id']}")
            else:
                append_to_log_message_queue(f"Failed to update record {order['id']}")
        except requests.exceptions.HTTPError as err:
            error_message = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            append_to_log_message_queue(f"HTTP error occurred: {err}\n"
                                         f"Error updating record {order['id']}:\n"
                                         f"Response Code: {response.status_code}\n"
                                         f"Response Message: {json.dumps(error_message, indent=4)}\n"
                                         f"Request Payload: {json.dumps(order, indent=4)}")
        except Exception as err:
            append_to_log_message_queue(f"Other error occurred: {err}")

        progress = (i / total_records) * 100
        anvil.server.call('update_progress', progress)
        append_to_log_message_queue(f"Progress updated to {progress}%")

    progress = 100
    anvil.server.call('update_progress', progress)
    update_result = f"Successfully updated {updated_records}/{total_records} records."
    append_to_log_message_queue(update_result)
    return update_result

@anvil.server.callable
def update_progress(value):
    global progress
    progress = value
    append_to_log_message_queue(f"update_progress called with value: {value}")

@anvil.server.callable
def get_progress():
    global progress
    append_to_log_message_queue("get_progress called")
    return progress

@anvil.server.callable
def get_update_result():
    global update_result
    append_to_log_message_queue("get_update_result called")
    return update_result

def append_to_log_message_queue(message):
    global log_messages
    log_messages.append(message)
    print(message)  # Print to server logs for debugging

def process_log_messages():
    global log_messages
    if log_messages:
        messages = log_messages.copy()
        log_messages.clear()
        txt_log_output = anvil.server.get_widget('txtLogOutput')
        for message in messages:
            txt_log_output.text += message + '\n'
