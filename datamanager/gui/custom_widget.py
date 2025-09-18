from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QToolButton, 
    QFileDialog, QSizePolicy, QMessageBox,
    QSpinBox
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFontMetrics, QFont


class QFileSelector(QWidget):
    
    file_selected = pyqtSignal(str)
    
    def __init__(self, label_text, file_types=None, is_write=False, is_dir=False, default_path=None):
        super().__init__()
        if is_dir: assert not is_write
        self.label_text = label_text
        if file_types is None:
            file_types = "All Files (*)"
        self.file_types = file_types
        self.is_write = is_write
        self.is_dir = is_dir
        self.file_name = ""
        self.init_ui()
        self.set_default(default_path)
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        self.label = QLabel(self.label_text)
        self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_file = QLabel(self.file_name)
        self.label_file.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.button = QToolButton()
        self.button.setText("📁")
        self.button.clicked.connect(self.browse_file)
        self.button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        layout.addWidget(self.label)
        layout.addWidget(self.label_file)
        layout.addWidget(self.button)
        self.setLayout(layout)
        
    def set_default(self, default_path: None):
        if default_path is not None:
            self.file_name = default_path
            self.update_text()
            self.file_selected.emit(self.file_name)
        
    def browse_file(self):
        options = QFileDialog.Options()
        if self.is_dir:
            file_name = QFileDialog.getExistingDirectory(self, "Select Directory", "", options=options)
        else:
            if self.is_write:
                file_name, _ = QFileDialog.getSaveFileName(self, "Type file name", "", self.file_types, options=options)
            else:
                file_name, _ = QFileDialog.getOpenFileName(self, "Select file", "", self.file_types, options=options)

        if file_name:
            self.file_name = file_name
            self.update_text()
            self.file_selected.emit(self.file_name)
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_text()
        
    def update_text(self):
        font = QFont("Arial", 10)
        metrics = QFontMetrics(font)
        elided = metrics.elidedText(self.file_name, Qt.ElideLeft, self.label_file.width())
        self.label_file.setText(elided)
        
    def is_selected(self):
        if self.file_name == "":
            # QMessageBox.warning(self, "Warning", "Label %s: no file selected"%(self.label_text))
            return False
        else:
            return True 
        
        
class QSpinBox_inline(QSpinBox):
    def __init__(self, min_value=0, max_value=100, default_value=0, step=1):
        super().__init__()
        self.setRange(min_value, max_value)
        self.setValue(default_value)
        self.setSingleStep(step)
        self.setFixedWidth(100)