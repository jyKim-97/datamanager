from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel, QSizePolicy
)

import os
from ..processing.video_encoder import get_video_info, process_video, move_encoded_files
from .utils_gui import error2messagebox
from .custom_widget import QFileSelector, QSpinBox_inline
from .base import BaseWidget
from typing import List
from .utils_gui import tqdm_qt
from copy import deepcopy


class VideoSetupGroup(QGroupBox, BaseWidget):
    def __init__(self, *args, default_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.video_info = None
        self.video_path = None
        self.init_ui(default_path=default_path)
        
    def init_ui(self, default_path=None):
        layout = QVBoxLayout()
        
        # Load video file
        self.video_selector = QFileSelector("Video file", is_dir=False, file_types="Video Files (*.mp4 *.mkv *.avi *.mov);;All Files (*)",
                                            default_path=default_path)
        self.video_selector.file_selected.connect(self.update_videoinfo)
        layout.addWidget(self.video_selector)
        
        ## set video options
        layout_opt = QHBoxLayout()
        layout.addLayout(layout_opt)
        
        gb1 = self.setup_opt_groupbox()
        layout_opt.addWidget(gb1, stretch=1)
        
        gb2 = self.setup_raw_groupbox()
        layout_opt.addWidget(gb2, stretch=1)

        self.setLayout(layout)
        
    def setup_opt_groupbox(self):
        gb = QGroupBox("Encoding option")
        layout = QFormLayout()
        gb.setLayout(layout)
        
        self.spin_fps = QSpinBox_inline(min_value=1, max_value=60, default_value=25)
        self.spin_bitrate = QSpinBox_inline(min_value=1000, max_value=16000, default_value=2000, step=500)
        self.spin_seg = QSpinBox_inline(min_value=1, max_value=1440, default_value=60, step=60)
        
        for obj in [self.spin_fps, self.spin_bitrate, self.spin_seg]:
            obj.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            obj.setFixedHeight(25)
        
        layout.addRow("FPS", self.spin_fps)
        layout.addRow("Bitrate [kbps]", self.spin_bitrate)
        layout.addRow("Segment duration [min]", self.spin_seg)
        
        return gb
    
    def setup_raw_groupbox(self):
        gb = QGroupBox("Video metadata")
        layout = QFormLayout()
        gb.setLayout(layout)
        
        self.raw_fps = QLabel("")
        self.raw_bitrate = QLabel("")
        self.raw_duration = QLabel("")
        
        for obj in [self.raw_fps, self.raw_bitrate, self.raw_duration]:
            obj.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            obj.setFixedHeight(25)
        
        layout.addRow("FPS", self.raw_fps)
        layout.addRow("Bitrate [kbps]", self.raw_bitrate)
        layout.addRow("Duration [min]", self.raw_duration)
        
        return gb
        
    def check_fill(self):
        return self.video_selector.is_selected()
    
    @error2messagebox(to_warn=True)
    def update_videoinfo(self, file_path):
        self.video_info = get_video_info(file_path)
        self.video_path = file_path
        
        # update video info
        self.raw_fps.setText("%.f"%(self.video_info.fps))
        self.raw_bitrate.setText("%.2f"%(self.video_info.bitrate/1000))
        self.raw_duration.setText("%.2f"%(self.video_info.duration))
        
    def encode_video(self, root_dir: str, t_seg: int=0):
        
        encode_info = deepcopy(self.video_info)
        encode_info.fps = int(self.spin_fps.value())
        encode_info.bitrate = int(self.spin_bitrate.value()) // 1000
        encode_info.duration = int(self.spin_seg.value()) * 60
        
        self.buf_path, dur_set = process_video(root_dir, self.video_path, 
                                               t_seg, encode_info, pbar_obj=tqdm_qt)
        
        return dur_set, encode_info
                
    def run(self, root_dir: str, meta_subset: List):
        raw_video_dir = os.path.join(root_dir, "RAW_VIDEO")
        if not os.path.exists(raw_video_dir):
            os.mkdir(raw_video_dir)
            
        move_encoded_files(self.buf_path, raw_video_dir, meta_subset)
        
        # raw_video_dir = os.path.join(root_dir, "RAW_VIDEO")
        # if not os.path.exists(raw_video_dir):
        #     os.mkdir(raw_video_dir)

        # encode_info = deepcopy(self.video_info)
        # encode_info.fps = int(self.spin_fps.value())
        # encode_info.bitrate = int(self.spin_bitrate.value()) // 1000
        
        # process_video(root_dir, raw_video_dir, meta_subset,
        #               self.video_path, t_seg, encode_info, pbar_obj=tqdm_qt)
        
