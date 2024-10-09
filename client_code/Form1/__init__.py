#from ._anvil_designer import Form1Template
#from anvil import *
#import anvil.server


#class Form1(Form1Template):
#  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
#    self.init_components(**properties)

import anvil.server
import anvil.media

class Form1(Form1Template):
    def __init__(self, **properties):
        self.init_components(**properties)

    def file_loader_change(self, file, **event_args):
        self.csv_file = file

    def button_click(self, **event_args):
        if hasattr(self, 'csv_file'):
            json_file = anvil.server.call('process_csv', self.csv_file)
            self.text_area.text = json_file
        else:
            self.text_area.text = "Please upload a CSV file first."

    # Any code you write here will run before the form opens.
