from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, 
    QLabel, QToolButton, QFileDialog, QSizePolicy, QMessageBox,
    QGroupBox,
    QScrollArea, QPushButton
)

from typing import List

from .base import BaseWidget
from .custom_widget import QFileSelector
from ..processing import usv_arranger as ua


class USVSetupGroup(QGroupBox, BaseWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_usv = 0
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_container = QWidget()
        self.layout_sel_usv = QVBoxLayout()
        self.scroll_container.setLayout(self.layout_sel_usv)
        self.scroll_area.setWidget(self.scroll_container)
        layout.addWidget(self.scroll_area)
        
        self.usv_selector = []
        while self.num_usv < 4:
            self.add_usv_selector()
            # sel = QFileSelector("USV log#%d"%(i+1), is_dir=False, file_types="Log Files (*.log);;All Files (*)")
            # sel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            # sel.setFixedHeight(30)
            # self.layout_sel_usv.addWidget(sel)
            # self.usv_selector.append(sel)
        
        layout_sub = QHBoxLayout()
        layout.addLayout(layout_sub)
        self.add_button = QPushButton("Add USV")
        self.add_button.clicked.connect(self.add_usv_selector)
        layout_sub.addWidget(self.add_button)
        
        self.del_button = QPushButton("Delete USV")
        self.del_button.clicked.connect(self.del_usv_selector)
        layout_sub.addWidget(self.del_button)
        
        self.setLayout(layout)
    
    def add_usv_selector(self):
        sel = QFileSelector("USV log#%d"%(self.num_usv+1), is_dir=False, file_types="Log Files (*.log);;All Files (*)")
        self.layout_sel_usv.insertWidget(self.layout_sel_usv.count(), sel)
        sel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sel.setFixedHeight(42)
        self.usv_selector.append(sel)
        self.num_usv += 1
    
    def del_usv_selector(self):
        if self.num_usv == 0:
            QMessageBox.warning(self, "Warning", "Empty USV slot")
            return
        
        self.layout_sel_usv.removeWidget(self.usv_selector.pop())
        self.num_usv -= 1
        
    def check_fill(self):
        is_fill = True
        for n in range(self.num_usv):
            is_fill = is_fill and self.usv_selector[n].is_selected()
        return is_fill
            
    def run(self, meta_subset: List):
        usv_files = []
        for n in range(self.num_usv):
            if self.usv_selector[n].is_selected():
                usv_files.append(self.usv_selector[n].file_name)
        
        if len(usv_files) == 0:
            return 
        
        ua.organize_usv_files(usv_files, meta_subset)
