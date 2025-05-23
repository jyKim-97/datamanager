from dataclasses import dataclass, asdict, fields, is_dataclass
from typing import Optional, List
import json
from datetime import datetime, timedelta
import os
import pandas as pd


summary_file_name = "summary.xlsx"
default_datetime = datetime(2025, 1, 1, 0, 0, 0)


@dataclass
class ExperimentMetaClass:
    experiment_name: Optional[str] = "Global STEAM Project"
    experimenter: Optional[str] = None
    experiment_place: Optional[str] = None
    recording_start: Optional[datetime] = default_datetime
    recording_end: Optional[datetime] = None
    note: str = ""
    structure_version: Optional[str] = "0.1.0"
    # check recording existence
    is_video: bool = False
    is_usv: bool = False
    is_rfid: bool = False
    # project directory (default: empty)
    project_dir: Optional[str] = None
    encoding_info: dict = None

    def save_json(self, filepath: str):
        with open(filepath, "w") as f:
            json.dump(asdict(self), f, indent=4)
            
    @staticmethod
    def get_field():
        return [f.name for f in fields(ExperimentMetaClass)]
            
    @staticmethod
    def load_json(filepath: str):
        with open(filepath, "r") as f:
            data = json.load(f)
        return ExperimentMetaClass(**data)
    
    def validate(self):
        #TODO: add more validation about recording time
        for field in fields(self):
            if field == "project_dir" or field == "encoding_info":
                continue
            elif field.default is None and getattr(self, field.name) is None:
                raise ValueError(f"Field {field.name} cannot be None")
        if self.recording_start == default_datetime:
            raise ValueError("Field recording_start is not selected")
        
        return True
    
    def split(self, dur_set: List[float])->List["ExperimentMetaClass"]:
        """
        Split the meta data into two parts: general and specific
        - segment: int, the segment time in minutes
        """
        
        dt_start = self.recording_start
        dt_end = self.recording_end
        
        meta_split = []
        dt0 = dt_start
        for dur in dur_set:
            dt_delta = timedelta(minutes=dur)
            meta_split.append(self.get_child(dt0, dt0+dt_delta))
            meta_split[-1].encoding_info = self.encoding_info
            dt0 += dt_delta
            
        if abs(dt0-dt_end) > timedelta(minutes=1):
            raise ValueError("The last segment is not aligned with the end time")

        return meta_split
    
    def get_child(self, dt0: datetime, dt1: datetime):
        """
        Get the child meta data between dt0 and dt1
        """
        assert dt0 < dt1
        meta_sub = ExperimentMetaClass(**self.__dict__)
        meta_sub.recording_start = dt0
        meta_sub.recording_end = dt1
        return meta_sub
    
    def update_endtime(self, dur: float):
        if self.recording_start is not None and dur is not None:
            self.recording_end = self.recording_start + timedelta(minutes=dur)
            
    def set_videoinfo(self, video_info: dataclass):
        self.encoding_info = asdict(video_info)
            
    def make_project_dir(self, root_dir: str):
        make_project_dir(root_dir, self)
        
    def rec2str(self):
        return self.recording_start.strftime("%y%m%dT%H%M")
    
    
def make_project_dir(root_dir: str, meta: ExperimentMetaClass):
    lb1 = meta.recording_start.strftime("%y%m%dT%H%M")
    lb2 = meta.recording_end.strftime("%y%m%dT%H%M")
    d = os.path.join(root_dir, "Data_"+lb1 + "-" + lb2)
    
    if os.path.exists(d):
        raise FileExistsError("Directory %s already exists."%(d))
    
    meta.project_dir = d
    os.mkdir(d)
    _export2json(meta)
    _add_meta_to_summary(root_dir, meta)
    

def _add_meta_to_summary(root_dir: str, meta: ExperimentMetaClass):
    """
    Args:
        root_dir (str): root directory of the project
        meta (ExperimentMetaClass): meta data to be added
    """
    df = pd.DataFrame(dict(
        time_start=[meta.recording_start.strftime("%y/%m/%d %H:%M")],
        time_end=[meta.recording_end.strftime("%y/%m/%d %H:%M")],
        directory=[os.path.basename(meta.project_dir)],
        is_video=[meta.is_video],
        is_usv=[meta.is_usv],
        is_rfid=[meta.is_rfid],
        note=[meta.note]
    ))
    
    fname = os.path.join(root_dir, "summary.xlsx")
    if os.path.exists(fname):
        df_old = pd.read_excel(fname)
        df = pd.concat([df_old, df], ignore_index=True)
    df.to_excel(fname, index=False)


def _export2json(obj: ExperimentMetaClass):
    filepath = os.path.join(obj.project_dir, "meta.json")
    
    data = asdict(obj)
    data["recording_start"] = data["recording_start"].isoformat()
    data["recording_end"] = data["recording_end"].isoformat()
    data["project_dir"] = os.path.basename(obj.project_dir)
    data["encoding_info"] = obj.encoding_info
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    print(ExperimentMetaClass.get_field())