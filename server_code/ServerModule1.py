import anvil.server
import json
import csv
import base64
import requests
from datetime import datetime
import time

# Global variables to track progress and result
progress = 0
update_result = ""

@anvil.server.callable
def process_csv_and_update(file):
    """
    Process the uploaded CSV file, convert it into JSON format,
    and update the records through CIN7 API.
    """
    global progress
    progress = 0  # Reset progress
    
    # Read the CSV file
    csv_data = file.get_bytes().decode('utf-8').splitlines()
    csv_reader = csv.DictReader(csv_data)
    data = []

    # Prepare JSON structure
    for rows in csv_reader:
        # Constructing each purchase_order object based on CSV row
        purchase_order = {
            "Id": int(rows["id"]),  # Converting 'id' to integer
            "stage": rows["stage"],  # Mapping 'stage' to 'Status'
            "estimatedArrivalDate": format_date(rows["estimatedArrivalDate"]),  # Correcting date formats
            "estimatedDeliveryDate": format_date(rows["estimatedDeliveryDate"])
        }
        data.append(purchase_order)

    # Convert data to JSON structure expected by CIN7 API
    json_data = json.dumps({"purchase_orders": data}, indent=4)
    
    # Start updating records
    return update_purchase_orders(json_data)

def format_date(date_str):
    """
    Converts date from MM/DD/YYYY format to the ISO 8601 format required by the API.
    """
    try:
        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        return date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        return date_str  # Return original string if format is incorrect

def update_purchase_orders(json_data):
    """
    Sends the JSON data to the CIN7 API to update purchase orders and tracks progress.
    Logs detailed information in case of errors.
    """
    global progress, update_result
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

    # Iterate over each purchase order and send to the API
    for i, order in enumerate(data["purchase_orders"], start=1):
        # Log the current order being processed
        print(f"Updating record {i}/{total_records}: {json.dumps(order, indent=4)}")
        
        # Make the POST request to CIN7 API
        try:
            response = requests.post(endpoint_url, headers=headers, json=order)
            response.raise_for_status()  # Raise error for bad responses
            
            if response.status_code == 200:
                updated_records += 1
        except requests.exceptions.HTTPError as err:
            # Log more details about the error and response
            error_message = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            progress = (i / total_records) * 100
            anvil.server.call('update_progress', progress)
            update_result = (f"HTTP error occurred: {err}\n"
                             f"Error updating record {order['id']}:\n"
                             f"Response Code: {response.status_code}\n"
                             f"Response Message: {json.dumps(error_message, indent=4)}\n"
                             f"Request Payload: {json.dumps(order, indent=4)}")
            print(update_result)
            return update_result
        except Exception as err:
            # Handle any other exceptions
            update_result = f"Other error occurred: {err}"
            print(update_result)
            return update_result
        
        # Update progress after each record
        progress = (i / total_records) * 100
        anvil.server.call('update_progress', progress)
        print(f"Updated {i}/{total_records} records. Progress: {progress}%")

    # Ensure the progress is 100% when done
    progress = 100
    anvil.server.call('update_progress', progress)
    update_result = f"Successfully updated {updated_records}/{total_records} records."
    print(update_result)
    return update_result


@anvil.server.callable
def update_progress(value):
    """
    Function to update the progress of the record update process.
    """
    global progress
    progress = value

@anvil.server.callable
def get_progress():
    """
    Returns the current progress of the update process.
    """
    global progress
    return progress

@anvil.server.callable
def get_update_result():
    """
    Returns the final result message after processing is complete.
    """
    global update_result
    return update_result
