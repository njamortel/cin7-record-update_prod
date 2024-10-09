import anvil.server
import json
import csv
import base64
import requests
from datetime import datetime

progress = 0
update_result = ""

@anvil.server.callable
def process_csv_and_update(file):
    global progress
    progress = 0  # Reset progress
    print("Starting CSV processing...")
    csv_data = file.get_bytes().decode('utf-8').splitlines()
    csv_reader = csv.DictReader(csv_data)
    data = []

    for rows in csv_reader:
        purchase_order = {
            "id": int(rows["id"]),  # Ensure id is an integer
            "stage": rows["stage"],
            "estimatedArrivalDate": format_date(rows["estimatedArrivalDate"]),
            "estimatedDeliveryDate": format_date(rows["estimatedDeliveryDate"])
        }
        data.append(purchase_order)

    json_data = json.dumps({"purchase_orders": data}, indent=4)
    print("CSV processing completed. Starting update...")
    return update_purchase_orders(json_data)

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        return date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        return date_str  # Return the original string if it doesn't match the expected format

def update_purchase_orders(json_data):
    global progress, update_result
    api_key = '7f409f7b9f98499996bc905e83f19cfb'
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
        # Validate JSON structure
        if not isinstance(order, dict) or 'id' not in order or 'stage' not in order:
            update_result = f"Invalid JSON structure for record {i}: {json.dumps(order, indent=4)}"
            print(update_result)
            return update_result
        
        # Print the JSON payload for debugging
        print(f"Updating record {i}/{total_records}: {json.dumps(order, indent=4)}")
        
        # Send the request
        response = requests.post(endpoint_url, headers=headers, json=order)
        
        # Print the response for debugging
        print(f"Request payload: {json.dumps(order, indent=4)}")
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")
        
        if response.status_code == 200:
            updated_records += 1
        else:
            progress = (i / total_records) * 100
            anvil.server.call('update_progress', progress)
            update_result = f"Response status code: {response.status_code}\nUpdating record {i}/{total_records}\nProgress: {progress:.2f}%\nFAILED: Error updating record {order['id']}: {response.text}"
            print(update_result)
            return update_result
        
        progress = (i / total_records) * 100
        anvil.server.call('update_progress', progress)
        print(f"Updated {i}/{total_records} records. Progress: {progress}%")

    progress = 100  # Ensure progress is set to 100% when done
    anvil.server.call('update_progress', progress)
    update_result = f"Successfully updated {updated_records}/{total_records} records."
    print(update_result)
    return update_result

@anvil.server.callable
def update_progress(value):
    global progress
    progress = value

@anvil.server.callable
def get_progress():
    global progress
    return progress

@anvil.server.callable
def get_update_result():
    global update_result
    return update_result
