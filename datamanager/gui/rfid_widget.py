
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox

from .base import BaseWidget
from .custom_widget import QFileSelector


class RFIDSetupGroup(QGroupBox, BaseWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.rfid_file = QFileSelector("RFID Event data file", file_types="Data Files (*.dat);;All Files(*)")
        layout.addWidget(self.rfid_file)
        self.setLayout(layout)
        
    def check_fill(self):
        pass
    
    def run(self, *args, **kwargs):
        pass