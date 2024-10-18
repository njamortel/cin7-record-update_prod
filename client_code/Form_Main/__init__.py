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
    """Triggered when a file is uploaded"""
    self.csv_file = file
    self.txtProgress.text = "File uploaded successfully."

  def start_process_click(self, **event_args):
    """Triggered when the 'start_process' button is clicked"""
    if self.csv_file:
      self.txtProgress.text = "Processing started..."
      anvil.server.call('process_csv_and_update', self.csv_file)
      self.timer_1.enabled = True  # Start the timer to track progress
    else:
      self.txtProgress.text = "Please upload a CSV file first."

  def timer_1_tick(self, **event_args):
    """Triggered every second to update progress"""
    self.progress = anvil.server.call('get_progress')  # Retrieve progress from server
    self.update_client_progress(self.progress)  # Call the client-side function to update UI

    if self.progress >= 100 or self.progress == 0:  # Stop when complete or failed
      self.timer_1.enabled = False
      result = anvil.server.call('get_update_result')
      self.txtProgress.text = result

  def btnProcess_click(self, **event_args):
    """Triggered when the "Process" button is clicked"""
    file = self.file_loader_1.file
    if file:
      try:
        result = anvil.server.call('process_csv_and_update', file)
        self.txtLog(result)  # Update the log TextBox
      except Exception as e:
        self.txtLog(f"Error: {str(e)}")

  def txtLog(self, message):
    """Appends a message to the txtLog TextBox"""
    self.txtLogOutput.text += message + '\n'

  @anvil.server.callable  # Ensure the decorator is placed correctly
  def update_client_progress(self, progress_value):
    """Sends progress to the client-side UI"""
    self.txtProgress.text = f"Progress: {progress_value:.2f}%"