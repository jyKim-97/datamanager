import ffmpeg
import subprocess
import sys
import os
import re
from time import strftime, gmtime
from dataclasses import dataclass
import functools
import uuid
from tqdm import tqdm
import shutil
from typing import Dict, List
from copy import deepcopy
from datetime import datetime, timedelta
from utils_log import dm_logger


BAR_WIDTH = 40
TRY_CUDA_FIRST = True

prefix_raw = "raw"
prefix_enc = "encoded"
ext_enc = "avi"


@dataclass
class VideoInfo:
    width: int
    height: int
    fps: float
    duration: float # minutes
    codec: str
    bitrate: int # M
    
    
# def encode_video(root_dir, input_video_files, t_seg, opt_encoding, pbar_obj):
#     enc_directory = None


def encode_video(project_dir, input_file, recording_start: datetime, opt_encoding, pbar_obj=None, copy_raw_video=False):
    
    fenc = os.path.join(project_dir, "video")
    os.makedirs(fenc, exist_ok=False)
    
    # print("duration: ", get_video_duration(input_file))
    # print("encoding duration:", opt_encoding.duration)

    # encode video
    compress_video_with_progress(input_file=input_file,
                                #  output_file=os.path.join(fenc, "%s_%03d.%s"%(prefix_enc, n, ext_enc))
                                 output_file=os.path.join(fenc, "%s_%%03d.%s"%(prefix_enc, ext_enc)),
                                 fps=opt_encoding.fps,
                                 bitrate=f"{opt_encoding.bitrate}M",
                                 resolution=f"{opt_encoding.width}:{opt_encoding.height}",
                                 segment_time=opt_encoding.duration*60, # min -> sec
                                 pbar_obj=pbar_obj, desc="encoding video")
    
    t0_set = [recording_start]
    for f in [f for f in os.listdir(fenc) if ext_enc in f]:
        fsrc = os.path.join(fenc, f)
        dur = get_video_duration(fsrc)
        t0_set.append(t0_set[-1] + timedelta(minutes=dur))
    
    # move file names
    # t0 = recording_start
    # t0 = datetime(25,1,1,0,0,0)
    # for f in [f for f in os.listdir(fenc) if ext_enc in f]:
    #     fsrc = os.path.join(fenc, f)
    #     fdst = os.path.join(fenc, "video_%s.%s"%(t0.strftime("%H%M%S"), ext_enc))
    #     # fdst = os.path.join(fenc, "video_%s.%s"%(t0.strftime("%y%m%dT%H%M"), ext_enc))
    #     # print("move video: %s to %s"%(fsrc, fdst))
    #     shutil.move(fsrc, fdst)

    #     dur = get_video_duration(fdst)
    #     # print("duration: ", dur)
    #     t0 = t0 + timedelta(minutes=dur)
    
    if copy_raw_video:
        # basedir = os.path.dirname(project_dir)
        basename = os.path.basename(project_dir)
        os.makedirs(os.path.join(project_dir, "RAW_VIDEO"), exist_ok=True)
        shutil.copy(input_file, os.path.join(project_dir, "RAW_VIDEO", "video_" + basename[5:]))
        
    return t0_set

    
def move_encoded_files(buf_path, raw_video_dir, meta_subset):
    fnames_raw = [f for f in os.listdir(buf_path) if "raw" in f]
    fnames_raw = sorted(fnames_raw, key=lambda x: int(x.split("_")[-1].split(".")[0]))
    
    assert len(fnames_raw) == len(meta_subset)
    
    for n, meta_sub in enumerate(meta_subset):
        
        src_raw = os.path.join(buf_path, fnames_raw[n])
        src_enc = os.path.join(buf_path, "%s_%03d.%s"%(prefix_enc, n, ext_enc))
        
        time_str = meta_sub.rec2str()
        dst_raw = os.path.join(raw_video_dir, "raw_%s"%(time_str)+os.path.splitext(src_raw)[1])
        dst_enc = os.path.join(meta_sub.project_dir, "encoded_%s"%(time_str)+os.path.splitext(src_enc)[1])
        
        print(f"Moving files from {src_raw} to {dst_raw}")
        print(f"Moving files from {src_enc} to {dst_enc}")
        
        shutil.move(src_raw, dst_raw)
        shutil.move(src_enc, dst_enc)
    
    os.rmdir(buf_path)
    
    
def make_temporal_dir(root_dir: str):
    unique_id = uuid.uuid4().hex[:8]
    buffer_name = f"tmp_{unique_id}"
    buffer_path = os.path.join(root_dir, buffer_name)
    os.makedirs(buffer_path, exist_ok=False)
    return buffer_path
    
    
def format_time(seconds):
    return strftime("%H:%M:%S", gmtime(seconds))


def get_video_info(input_file):
    
    try:
        info = ffmpeg.probe(input_file)
    except Exception as e:
        raise FileExistsError("ffmpeg is not correctly configured. Please type 'ffmpeg --version' to check installation")

    video_stream = [s for s in info['streams'] if s['codec_type'] == 'video']
    if not video_stream:
        raise ValueError("No video stream found in %s"%(input_file))
    
    video = video_stream[0]
    
    return VideoInfo(
        width=int(video['width']),
        height=int(video['height']),
        fps=eval(video['r_frame_rate']),
        duration=float(info['format']['duration'])/60, # min
        codec=video['codec_name'],
        bitrate=int(info['format']['bit_rate']),
    )
    

def get_video_duration(input_file):
    video_info = get_video_info(input_file)
    return video_info.duration


def check_file(strict=True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            input_file = kwargs.get("input_file")
            output_file = kwargs.get("output_file")
            
            if strict:
                if not os.path.exists(input_file):
                    raise FileNotFoundError(f"Input file {input_file} does not exist.")
                
                if os.path.exists(output_file):
                    raise FileExistsError(f"Output file {output_file} already exists. Please remove it or choose a different name.")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def run_with_ffmpeg_progress(duration_func):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def _parse_progress(process):
                input_file = kwargs.get("input_file")
                duration = duration_func(input_file) * 60 # min -> sec
                pbar_obj = kwargs.get("pbar_obj", tqdm)
                desc = kwargs.get("desc", "Encoding video")

                # tqdm bar setup
                error_lines = []
                pbar = pbar_obj(total=int(duration), desc=desc, ncols=100)
                n_prv = 0

                while True:
                    try:
                        line = process.stderr.readline()
                        if not line:
                            break
                        line = line.strip()
                        error_lines.append(line)
                        # print(line)

                        match = re.search(r'time=(\d+):(\d+):(\d+\.?\d*)', line)
                        if match:
                            h, m, s = map(float, match.groups())
                            elapsed_sec = int(h * 3600 + m * 60 + s)
                            n_new = min(elapsed_sec, int(duration))
                            pbar.update(n_new-n_prv)
                            n_prv = n_new                   
                    except: 
                        continue
                pbar.close()

                return_code = process.wait()
                if return_code != 0:
                    print("\n❌ FFmpeg encountered an error:")
                    for line in error_lines[-10:]:
                        print("stderr:", line)
                    raise RuntimeError("FFmpeg failed to process the video.")
                else:
                    print("Done")

            def _build_cmd(cmd):
                return cmd["begin"] + ["-i", cmd["input"]] + cmd["out_opt"] + [cmd["output"]]
            
            cmd = func(*args, **kwargs) # Dict

            cuda_converted = False
            if TRY_CUDA_FIRST and "-c:v" in cmd["out_opt"]: # Use hardware acceleration only for encoding
                cmd_cuda = deepcopy(cmd)
                cmd_cuda["begin"].extend(["-hwaccel", "nvdec", "-hwaccel_output_format", "cuda"])
                # change codec
                idx = cmd_cuda["out_opt"].index("-c:v")
                cmd_cuda["out_opt"][idx+1] = "h264_nvenc" # change from lib264 -> h264_nvenc
                # change vf option
                if "-vf" in cmd_cuda["out_opt"]:
                    for n, opt in enumerate(cmd_cuda["out_opt"]):
                        if "scale" in opt:
                            cmd_cuda["out_opt"][n] = opt.replace("scale", "scale_cuda")

                cmd_build = _build_cmd(cmd_cuda)
                cuda_converted = True
            else:
                cmd_build = _build_cmd(cmd)
            try:
                dm_logger.info(cmd_build)
                process = subprocess.Popen(cmd_build, stderr=subprocess.PIPE, universal_newlines=True)
                _parse_progress(process)
            except RuntimeError as e:
                if cuda_converted:
                    dm_logger.error("="*50+"\nFailed to use CUDA encoder\n"+"="*50)
                    cmd_build = _build_cmd(cmd)
                    dm_logger.info(cmd_build)
                    process = subprocess.Popen(cmd_build, stderr=subprocess.PIPE, universal_newlines=True)
                    _parse_progress(process)
                else:
                    raise e
            
        return wrapper
    return decorator


@run_with_ffmpeg_progress(duration_func=lambda input_path: get_video_duration(input_path))
@check_file(strict=False)
def compress_video_with_progress(input_file=None, output_file=None, fps=30, bitrate='2M', resolution=None, histeq=False, segment_time=-1, **kwargs)->Dict:

    cmd = dict(
        begin=["ffmpeg", "-y"],
        input=input_file, # will be used with -i option
        out_opt=["-c:v", "libx264", "-b:v", bitrate, "-r", "%d"%(fps), "-an"],
        output=output_file
    )
    
    # WILL NOT BE USED
    vf_parts = []
    if resolution:
        vf_parts.append(f"scale={resolution}")
    if histeq:
        raise ValueError("Histogram normalization method has not been tested")
        vf_parts.append(f"histeq=strength=0.5:intensity=0.6:antibanding=1")
    if vf_parts:
        cmd["out_opt"] += ["-vf", ",".join(vf_parts)]
        
    if segment_time > 0:
        cmd["out_opt"] += [
            "-f", "segment",
            "-segment_time", str(segment_time),
            "-reset_timestamps", "1",
            "-map", "0:v:0",
            "-segment_format", "avi",
        ]

    return cmd
    
    
@run_with_ffmpeg_progress(duration_func=lambda input_path: get_video_duration(input_path))
@check_file(strict=False)
def cut_raw_video(input_file=None, output_file=None, segment_time=-1, **kwargs):
    if segment_time == -1:
        return
    
    ext = os.path.splitext(input_file)[1]

    cmd = dict(
        begin=["ffmpeg", "-y"],
        input=input_file,
        out_opt=[
            "-c", "copy",
            "-map_metadata", "0",
            "-map", "0",
            "-f", "segment",
            "-segment_time", str(segment_time*60), # min -> sec
            "-reset_timestamps", "1",
        ],
        output=output_file+"_%03d"+ext
    )

    return cmd
    

if __name__ == "__main__":
    pass


