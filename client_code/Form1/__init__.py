from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.media

class Form1(Form1Template):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.csv_file = None
        self.progress = 0
        self.timer_1.interval = 1  # Set the timer interval to 1 second

    def file_loader_1_change(self, file, **event_args):
        self.csv_file = file
        self.txtProgress.text = "File uploaded successfully."

    def start_process_click(self, **event_args):
        if self.csv_file:
            self.txtProgress.text = "Processing started..."
            anvil.server.call('process_csv_and_update', self.csv_file)
            self.timer_1.enabled = True  # Start the timer
        else:
            self.txtProgress.text = "Please upload a CSV file first."

    def timer_1_tick(self, **event_args):
        self.progress = anvil.server.call('get_progress')
        self.txtProgress.text = f"Progress: {self.progress}%"
        if self.progress >= 100:
            self.timer_1.enabled = False
            result = anvil.server.call('get_update_result')
            self.txtProgress.text = result
