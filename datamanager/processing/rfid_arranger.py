from datetime import datetime, timedelta
from typing import List
from pathlib import Path
import csv
from tqdm import tqdm
from . import utils
# import sys
# sys.path.append("./")
# import utils


row_strings = ("zone_label", "uid", "tag_no", "timestamp", "weight")


class RFIDReader:
    def __init__(self, rfid_file: str):
        self.rfid_file = Path(rfid_file)
    
    def _parse_line(self, line):
        lb = line[0]
        uid = line[1]
        tag_no = line[2]
        t = datetime.strptime(line[3], "%Y-%m-%d_%H:%M:%S.%f")
        return lb, uid, tag_no, t        
            
    def build(self, t0_set: List[datetime], project_dir: str, pbar_obj=tqdm, **kwargs):
        tmin = t0_set[0]
        tmax = t0_set[-1] + timedelta(seconds=1)
        summary_file = Path(project_dir) / "rfid_table.csv"
        
        # get file nlength
        with self.rfid_file.open("r", newline='') as f:
            num_rfid = sum(1 for _ in f) - 1
        
        video_id = 0
        fp_csv = summary_file.open("w", newline='')
        writer = csv.writer(fp_csv)
        writer.writerow(["date", "time", "video_id", "time_delta", "zone_label", "uid", "tag_no"])
        
        with self.rfid_file.open("r", newline='') as f:
            reader = csv.reader(f)
            desc = kwargs.get("desc", "Read RFID files")
            pbar = pbar_obj(total=num_rfid, desc=desc, ncols=100)
            for n, row in enumerate(tqdm(reader)):
                if n == 0: 
                    if tuple(row) != row_strings:
                        raise ValueError("Unexpected labels found in rfid raw data")
                    continue

                lb, uid, tag_no, t = self._parse_line(row)
                pbar.update(1)
                if tmin < t <= tmax:
                    # assert ascending order
                    if t >= t0_set[video_id+1]:
                        video_id += 1
                    
                    if video_id > len(t0_set)-1:
                        print(video_id)
                        raise ValueError("video ID exceeds the number of videos")
                    t0 = t0_set[video_id]
                    # print("\n", t, t0, t-t0)
                    writer.writerow([
                        t.strftime("%m/%d/%y"),
                        utils.strftime_hms(t),
                        video_id,
                        utils.timedelta_to_hms(t-t0),
                        lb,
                        uid,
                        tag_no
                    ])
                    
                    # if n == 5:
                    #     raise ValueError("")

        pbar.close()
        fp_csv.close()
                    
                
                    
                
                
                
                
                
