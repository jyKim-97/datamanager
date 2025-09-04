
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox

from .base import BaseWidget
from .custom_widget import QFileSelector
from ..processing.rfid_arranger import RFIDReader
from .utils_gui import tqdm_qt


class RFIDSetupGroup(QGroupBox, BaseWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.rfid_file = QFileSelector("RFID Event data file", file_types="Data Files (*.csv);;All Files(*)")
        layout.addWidget(self.rfid_file)
        self.setLayout(layout)

    def check_fill(self):
        return self.rfid_file.is_selected()
    
    def run(self, meta, t0_set):
        rfid = RFIDReader(self.rfid_file.file_name)
        rfid.build(t0_set, meta.project_dir, pbar_obj=tqdm_qt)