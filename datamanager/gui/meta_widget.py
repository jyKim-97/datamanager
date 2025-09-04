
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QLineEdit, QDateTimeEdit, QLabel, QPlainTextEdit, QFormLayout
from PyQt5.QtCore import QDateTime

# from ..processing.video_encoder import VideoInfo
from collections import defaultdict
from datamanager.gui.base import BaseWidget

from .base import BaseWidget
from ..processing import meta
from datetime import datetime
from typing import List


def editable_datetime():
    
    default_str = datetime.strftime(meta.default_datetime, "%Y-%m-%d %H:%M")
    default_dt = QDateTime.fromString(default_str, "yyyy-MM-dd HH:mm")
    
    dobj = QDateTimeEdit(QDateTime.currentDateTime())
    dobj.setDisplayFormat("yyyy-MM-dd HH:mm")
    dobj.setCalendarPopup(True)  # enables date picker
    dobj.setDateTime(default_dt)

    return dobj


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
        # default_str = datetime.strftime(meta.default_datetime, "%Y-%m-%d %H:%M:%S")
        # default_dt = QDateTime.fromString(default_str, "yyyy-MM-dd HH:mm:ss")

        # self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        # self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        # self.datetime_edit.setCalendarPopup(True)  # enables date picker
        # self.datetime_edit.setDateTime(default_dt)

        self.date_start = editable_datetime()
        # self.date_top = editable_datetime()
        layout_form.addRow("recording start (KST)", self.date_start)    
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
        m.recording_start = self.date_start.dateTime().toPyDateTime()
        m.update_endtime(self.dur)
        
        # print("="*50)
        # print("Recording start: ", m.recording_start)
        # print("Recording stop: ", m.recording_end)
        # print("="*50)
        
        return m
        
    def update_duration(self, dur: float):
        self.dur = dur
        self.meta.update_endtime(dur)
        
    def check_fill(self):
        return self.meta.validate()
    
    def run(self, root_dir: str):
        if self.dur is None:
            raise ValueError("Load video file first (or run 'update_duration' method first)")
        self.meta = self.build_meta()
        print(self.meta)
        
        # make directory for the video
        self.meta.make_project_dir(root_dir)
        
        # print(self.meta.project_dir)
