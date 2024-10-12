from ._anvil_designer import Form_MainTemplate
from anvil import *
import anvil.server
import anvil.media

class Form_Main(Form_MainTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.csv_file = None
        self.progress = 0
        self.timer_1.interval = 1  # Set the timer interval to 1 second

    def file_loader_1_change(self, file, **event_args):
        self.csv_file = file
        self.txtProgress.text = "File uploaded successfully."
        self.rich_text_Log.content += "File uploaded successfully.\n"

    def start_process_click(self, **event_args):
        if self.csv_file:
            self.txtProgress.text = "Processing started..."
            self.rich_text_Log.content += "Processing started...\n"
            try:
                anvil.server.call('process_csv_and_update', self.csv_file)
                self.timer_1.enabled = True  # Start the timer to track progress
            except Exception as e:
                self.txtProgress.text = f"Error: {str(e)}"
                self.rich_text_Log.content += f"Error: {str(e)}\n"
        else:
            self.txtProgress.text = "Please upload a CSV file first."
            self.rich_text_Log.content += "Please upload a CSV file first.\n"

    def timer_1_tick(self, **event_args):
        try:
            self.progress = anvil.server.call('get_progress')
            self.txtProgress.text = f"Progress: {self.progress:.2f}%"
            self.rich_text_Log.content += f"Progress: {self.progress:.2f}%\n"

            if self.progress >= 100 or self.progress == 0:
                self.timer_1.enabled = False
                result = anvil.server.call('get_update_result')
                self.txtProgress.text = result
                self.rich_text_Log.content += result + "\n"
        except Exception as e:
            self.txtProgress.text = f"Error: {str(e)}"
            self.rich_text_Log.content += f"Error: {str(e)}\n"
            self.timer_1.enabled = False
