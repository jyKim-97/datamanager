from datetime import datetime, timedelta
from typing import List
import os
import shutil
import csv
from tqdm import tqdm
import sqlite3
# from utils import strftime_hms
from . import utils
from utils_log import dm_logger

# import sys
# sys.path.append("./")
# import utils

usv_rel_dir = "./usv/"


class USVReader:
    def __init__(self, usv_file: str, device_id: int = -1):
        self.usv_file = usv_file
        self.usv_dir = None
        self.recording_start = None
        self.recording_end = None
        if device_id == -1:
            try:
                device_id = int(os.path.basename(usv_file).split(".")[0].split("ch")[1])
            except:
                device_id = -1
                          
        self.device_id = device_id
        self.recording_time = []
        self.recording_file = []
        self.recording_dur  = []
        
    def read_usv_data(self):
        with open(self.usv_file, 'r') as fp:
            self.usv_dir = fp.readline()[:-1]
            line = fp.readline()
            # n = 0
            while line:
                labels = line.split("\t")
                dt = self.get_recording_time(labels[0], labels[1])
                # print(labels[1], dt)
                # n+=1
                # if n == 2:
                #     raise ValueError("Check USV log file format")
                
                if "Monitoring" in line:
                    if "started" in line:
                        self.recording_start = dt
                    elif "stopped" in line:
                        self.recording_end = dt
                    else:
                        raise ValueError("Unexpected label in USV file")
                else:
                    self.recording_time.append(dt)
                    self.recording_file.append(os.path.join(self.usv_dir, labels[2]))
                    self.recording_dur.append(float(labels[3].strip().split(" ")[0]))
                line = fp.readline()

    @staticmethod
    def get_recording_time(lb_date, lb_time):
        return datetime.strptime(lb_date+"/"+lb_time, "%m/%d/%y/%H:%M:%S.%f")
        

def merge_usv_logs(usv_readers: List[USVReader]):
    merged = []
    for reader in usv_readers:
        for dt, f, dur in zip(reader.recording_time, reader.recording_file, reader.recording_dur):
            merged.append((dt, f, dur, reader.device_id))
    merged.sort(key=lambda x: x[0])
    return merged


def get_aligned_recording_set(file_path_set: List[str]):
    usv_readers = []
    for dev_id, f in enumerate(file_path_set, start=1):
        usv_reader = USVReader(f, dev_id)
        usv_reader.read_usv_data()
        usv_readers.append(usv_reader)    
    return merge_usv_logs(usv_readers)


def move_target_files(t0_set: List, project_dir: str, merged, pbar_obj=tqdm, **kwargs):
    
    usv_dir = os.path.join(project_dir, usv_rel_dir)
    os.makedirs(usv_dir, exist_ok=True)
    summary_path = os.path.join(project_dir, "usv_table.csv")
    
    # search number of dataset
    tmin, tmax = t0_set[0], t0_set[-1]+timedelta(seconds=1)
    num_total = 0
    for t, _, _, _ in merged:
        if tmin <= t < tmax:
            num_total += 1
    
    # write with file
    fp_csv = open(summary_path, "w", newline='')
    writer = csv.writer(fp_csv)
    writer.writerow(["date", "time", "video_id", "time_delta", "duration", "device_id", "filename"])
    
    desc = kwargs.get("desc", "Moving USV files")
    pbar = pbar_obj(total=num_total, desc=desc, ncols=100)
    
    new_id = 0
    video_id = 0
    for t, src_path, dur, dev_id in merged:
        if tmin <= t < tmax:
            filename = "usv_%07d.wav"%(new_id)
            dst_path = os.path.join(usv_dir, filename)
            shutil.move(src_path, dst_path)
            
            # assert ascending order
            if t >= t0_set[video_id+1]:
                video_id += 1
            new_id += 1
            
            assert video_id < len(t0_set)-1
            
            t0 = t0_set[video_id]
            writer.writerow([
                t.strftime("%m/%d/%y"),
                utils.strftime_hms(t),
                video_id,
                utils.timedelta_to_hms(t-t0),
                f"{dur:.1f}",
                f"{dev_id}",
                os.path.join(usv_rel_dir, filename)
            ])
            
            pbar.update(1)
    
    pbar.close()
    fp_csv.close()

    # TODO: convert csv to xlsx
    copy_csv2sql(summary_path)
    
    
        
def copy_csv2sql(summary_path: str):
    
    fp = open(summary_path, 'r', newline='')
    reader = csv.DictReader(fp)
    
    # open db file 
    nid = summary_path.rfind(".csv")
    db_path = summary_path[:nid] + ".sqlite"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usv_events (
            date TEXT,
            time TEXT,
            video_id INTEGER,
            time_delta TEXT,
            duration REAL,
            device_id INTEGER,
            filename TEXT
        )
    """)
    
    for row in reader:
        cursor.execute(
            "INSERT INTO usv_events (date, time, video_id, time_delta, duration, device_id, filename) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (row['date'], row['time'], int(row["video_id"]), row['time_delta'], float(row['duration']), int(row['device_id']), row['filename'])
        )
    
    fp.close()
    conn.commit()
    conn.close()
        
        
def read_usv_sqlite(db_path):
    conn = sqlite3.connect(db_path)
    # print(conn, db_path, os.path.exists(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usv_events")
    rows = cursor.fetchall()
    for row in rows:
        print(row)  # or convert to dict, etc.
    conn.close()
    
                
# def timedelta_to_str(dt_delta):
#     total_seconds = dt_delta.total_seconds()
#     hours = int(total_seconds // 3600)
#     minutes = int((total_seconds % 3600) // 60)
#     seconds = int(total_seconds % 60)
#     milliseconds = int((total_seconds % 1) * 1000)
#     return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"


# def organize_usv_files(usv_logs, meta_subset, pbar_obj=tqdm):
#     merged = get_aligned_recording_set(usv_logs)
#     for n, meta_sub in enumerate(meta_subset, start=1):
#         dt_start = meta_sub.recording_start
#         dt_end = meta_sub.recording_end
#         target_dir = os.path.join(meta_sub.project_dir, "usv")
#         os.mkdir(target_dir)
#         move_target_files(dt_start, dt_end, target_dir, merged,
#                           pbar_obj=pbar_obj, desc="Move usv#%d"%(n))

def organize_usv_files(usv_logs: List, t0_set: List, project_dir, pbar_obj=tqdm):
    merged = get_aligned_recording_set(usv_logs)
    # target_dir = os.path.join(project_dir, usv_rel_dir)
    # os.makedirs(target_dir, exist_ok=False)
    move_target_files(t0_set, project_dir, merged, 
                      pbar_obj=pbar_obj, desc="Move usv files")
    dm_logger.info("USV files are moved to %s", os.path.join(project_dir, "usv"))    
    
if __name__ == "__main__":
    from pprint import pprint

    merged = get_aligned_recording_set(["../../testdata/ch1.log"])
    
    move_target_files(merged[2][0], merged[20][0], "../../testdata/usv", merged)    
    read_usv_sqlite("../../testdata/usv/usv_table.sqlite")