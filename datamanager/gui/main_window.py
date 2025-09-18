from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QPushButton
)

# from datamanager.gui import *
from .video_widget import VideoSetupGroup
from .usv_widget import USVSetupGroup
from .meta_widget import MetaSetupGroup
from .rfid_widget import RFIDSetupGroup
from .custom_widget import QFileSelector, QSpinBox_inline
from .utils_gui import error2messagebox
from ..processing import utils_log as ul


class DataManagerGUI(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setWindowTitle("Data Manager GUI")
        self.root_dir = ""
        
        self.init_ui(**kwargs)
    
    def init_ui(self, **kwargs):
        
        layout_tot = QHBoxLayout()
        layout = QVBoxLayout()
    
        # set root directory
        self.gb_root = QGroupBox("Project Directory Setting")
        layout_root = QVBoxLayout()
        self.file_selector = QFileSelector("Project Directory", is_dir=True,
                                           default_path=kwargs.get("root_dir", None))
        layout_root.addWidget(self.file_selector)
        self.gb_root.setLayout(layout_root)
        layout.addWidget(self.gb_root, stretch=1)
        
        # set video 
        self.gb_video = VideoSetupGroup("Video Setup",
                                        default_path=kwargs.get("video_path", None))
        layout.addWidget(self.gb_video, stretch=2)
        
        # USV input
        self.gb_usv = USVSetupGroup("USV Setup") #, default_str=kwargs.get("usv_path", None))
        layout.addWidget(self.gb_usv, stretch=4)
        
        # RFID input
        self.gb_rfid = RFIDSetupGroup("RFID Setup")
        layout.addWidget(self.gb_rfid, stretch=1)
        
        # Organize dataset
        self.button_arrange = QPushButton("Organize dataset")
        self.button_arrange.clicked.connect(self.organize_files)
        
        layout_tot.addLayout(layout, stretch=1)
        
        layout_meta = QVBoxLayout()
        self.gb_meta = MetaSetupGroup("Meta Data")
        layout_meta.addWidget(self.gb_meta)
        
        layout_meta.addWidget(self.button_arrange, stretch=1)
        layout_tot.addLayout(layout_meta, stretch=1)
        
        self.setLayout(layout_tot)
    
    @error2messagebox(to_warn=True)
    def organize_files(self, event):
        if not self.file_selector.is_selected():
            return
        self.root_dir = self.file_selector.file_name
        
        # construct meta data
        self.gb_meta.meta.is_video = self.gb_video.check_fill()
        self.gb_meta.meta.is_usv  = self.gb_usv.check_fill()
        self.gb_meta.meta.is_rfid = self.gb_rfid.check_fill()
        
        t_dur = self.gb_video.video_info.duration # minutes (int)
        encoding_info = self.gb_video.read_encoding_info()
        self.gb_meta.update_duration(t_dur)  # update duration
        self.gb_meta.meta.set_videoinfo(encoding_info)
        print("encoding info:", encoding_info)
        print("meta info:", self.gb_meta.meta.encoding_info)
        
        # build meta dataset and generate project_directory
        self.gb_meta.run(self.root_dir)
        project_dir = self.gb_meta.meta.project_dir
        self._log_default_settings(project_dir)        
        
        # video encoding
        t0_set = self.gb_video.run(project_dir, self.gb_meta.meta.recording_start, 
                                   encoding_info, copy_raw_video=True)
        
        # arrange usv files
        self.gb_usv.run(self.gb_meta.meta, t0_set)
        
        # arrange RFID dataset
        self.gb_rfid.run(self.gb_meta.meta, t0_set)
        
        # 
        
        # split directories first
        # dur_set, encode_info = self.gb_video.encode_video(self.root_dir, t_seg)
        # self.gb_meta.meta.set_videoinfo(encode_info)
        
        # generate 
        
        # split videos
        
        
        # execute meta data setting
        # meta_subset = self.gb_meta.run(self.root_dir, dur_set)
        # self.gb_video.run(self.root_dir, meta_subset)
        
        # meta_subset = self.gb_meta.run(self.root_dir, t_seg)
        # self.gb_video.run(self.root_dir, t_seg, meta_subset)
        # self.gb_usv.run(meta_subset)
        
    def _log_default_settings(self, project_dir):
        ul.add_file_logger(project_dir + "/log.txt")
        ul.dm_logger.info("Project directory: %s", project_dir)
        ul.dm_logger.info("VIDEO: %s", self.gb_meta.meta.is_video)
        ul.dm_logger.info("USV: %s", self.gb_meta.meta.is_usv)
        ul.dm_logger.info("RFID: %s", self.gb_meta.meta.is_rfid)
