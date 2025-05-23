
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QLineEdit, QDateTimeEdit, QLabel, QPlainTextEdit, QFormLayout
from PyQt5.QtCore import QDateTime

# from ..processing.video_encoder import VideoInfo
from collections import defaultdict
from datamanager.gui.base import BaseWidget

from .base import BaseWidget
from ..processing import meta
from datetime import datetime
from typing import List


class MetaSetupGroup(QGroupBox, BaseWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = meta.ExperimentMetaClass.get_field()
        self.dur = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.meta = meta.ExperimentMetaClass()
        
        self.forms = defaultdict()
        layout_form = QFormLayout()
        for f in self.fields:
            if "note" in f:
                continue
            if "version" in f:
                continue
            if "recording" in f:
                continue
            if "project" in f:
                continue
            if "is" in f:
                continue
            if "encoding_info" in f:
                continue
            else:
                self.forms[f] = QLineEdit()
                self.forms[f].setText(getattr(self.meta, f))
                layout_form.addRow(f, self.forms[f])
                
        # recording start
        # default_str = "2025-01-01 00:00:00"
        default_str = datetime.strftime(meta.default_datetime, "%Y-%m-%d %H:%M:%S")
        default_dt = QDateTime.fromString(default_str, "yyyy-MM-dd HH:mm:ss")

        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.datetime_edit.setCalendarPopup(True)  # enables date picker
        self.datetime_edit.setDateTime(default_dt)

        layout_form.addRow("recording start (KST)", self.datetime_edit)    
        layout.addLayout(layout_form)
        
        layout.addWidget(QLabel("Note"))
        self.note = QPlainTextEdit("")
        layout.addWidget(self.note)
        
        self.setLayout(layout)
        
    def build_meta(self):
        m = meta.ExperimentMetaClass()
        for k, v in self.meta.__dict__.items():
            setattr(m, k, v)
        
        for k, v in self.forms.items():
            setattr(m, k, v.text())
    
        m.note = self.note.toPlainText()
        m.recording_start = self.datetime_edit.dateTime().toPyDateTime()
        m.update_endtime(self.dur)
        return m
        
    def update_duration(self, dur: float):
        self.dur = dur
        self.meta.update_endtime(dur)
        
    def check_fill(self):
        return self.meta.validate()
    
    def run(self, root_dir: str, dur_set: List):
        """
        collect typed meta information
        """
        if self.dur is None:
            raise ValueError("Load video file first (or run 'update_duration' method first)")
        
        # encoding_info = self.meta.encoding_info
        self.meta = self.build_meta()
        # self.meta.encoding_info = encoding_info
        
        meta_subset = self.meta.split(dur_set)
        for meta_sub in meta_subset:
            meta_sub.make_project_dir(root_dir)
        
        return meta_subset
