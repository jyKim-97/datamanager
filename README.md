# Install program
1. Install python package
- 코드가 존재하는 디렉토리로 이동 (해당 디렉토리에는 datamanger 폴더와 setup.py 파일, README.md 파일이 존재해야 함)
```
>>> pip install .
```

2. Install ffmpeg ([reference](https://angelplayer.tistory.com/351))
    1) ffmpeg 사이트로 이동 (https://ffmpeg.org/)
    2) Download 버튼 클릭
    3) windows 선택
    4) 하단에 windows build from gyan.dev 클릭
    5) ffmpeg-git-full.7z 파일 다운로드
    6) 다운로드 후 압축 해제 
    6) 환경변수 편집으로 들어가서 PATH에 압축해제한 경로 입력
        - 예를 들어 Desktop에 풀어두었다면 Desktop/ffmpeg/bin/ 폴더 추가

3. 비디오 인코딩 GPU 가속 (h264_nvenc 코덱 사용)
    1) https://www.nvidia.com/ko-kr/drivers/ 에서 GPU 버전에 맞는 NVIDIA display driver 설치

# Run program & functions
- Open windows terminal
```
>>> python -m datamanager
```
아래와 같은 창 생성 (빨간 선 제외)

![GUI MAIN](figures/gui_functions.png)

1) Root directory 선택 (항상 동일)
2) Video 파일 선택 (단일 파일 선택 가능)
3) Video encoding 옵션 선택
    - Bitrate (kbps): 높일수록 화질이 좋아지지만 비례햐여 용량이 커짐 (2000-5000 사이의 값을 추천)
    - Segment duration (min): 영상을 자르는 시간 단위; 원본 영상의 fps가 항상 동일하지는 않기에 수초 정도의 차이가 있을 수 있음.
4) Video metadata (video 파일 선택 시 자동으로 popup)
5) USV 파일 선택
    - log file을 선택 필요 (e.g. ch1.log)
    - 기본 4개 선택이 가능하며, 원하면 추가하거나 (Add USV) 뺄 수 있음 (Delete USV).
6) RFID 파일 선택
    - RFID recording 데이터 (csv파일) 선택
7) Experiment metadata (실험자가 입력)
    - experiment_name: 실험 이름 (e.g. Global STEAM Project)
    - experimenter: 실험자 이름 (e.g. John Doe)
    - experiment_place: 실험 장소 (e.g. 순천향대)
    - recording_start: recording 시작 시간 (!**video 시간 기준으로 적어줄 것**)
    - note: 기타 특이사항
8) Arrange
    - 모든 셋팅을 확인 후, 파일 정렬 시작


# File structure
- 전체적인 파일 구조는 다음과 같음.
```tree
root_dir
├───summary.xlsx
├───RAW_VIDEO
    ├───raw_250206T1430.avi
    ├───...
├───Data_250206T1430-250207T1430
    ├───meta.json
    ├───usv_table.csv // video ID가 encoding된 video의 number
    ├───usv_table.sqlite
    ├───rfid_table.csv
    ├───video
        └───encoded_000.avi // segment duration 간격으로 잘림
        └───encoded_001.avi    
        └───encoded_002.avi    
        └───...
    ├───usv
        └───usv_0000000.wav
        └───usv_0000001.wav
        └───usv_0000002.wav
        └───usv_0000003.wav
        ...
```

## RAW_VIDEO
- 원본 영상 파일이 복사됨. 기존의 영상도 보존되기에 실행 전에 반드시 저장장치 용량 확인 필요
- raw뒤의 숫자는 날짜-시간으로 예를 들어 250206T1430은 25년 2월 6일 14시 30분에 해당 (KST)

## summary.xlsx
- 전체 데이터셋에 대한 summary가 저장됨 (time_start, time_end, directory, is_video, is_usv, is_rfid, note)

## Data directory
### meta.json
- GUI에 입력한 정보가 각 데이터 폴더에 저장됨.

```bash
{
    "experiment_name": "Global STEAM Project",
    "experimenter": "Jungyoung Kim",
    "experiment_place": "KIST",
    "recording_start": "2025-02-06T14:30:00",
    "recording_end": "2025-02-06T15:31:03.360000",
    "note": "",
    "structure_version": "0.1.0",
    "is_video": true,
    "is_usv": false,
    "is_rfid": false,
    "project_dir": "Data_250206T1430-250206T1531",
    "encoding_info": {
        "width": 1920,
        "height": 1080,
        "fps": 25,
        "duration": 120.1,
        "codec": "h264",
        "bitrate": 2
    }
}
```

### encoded video (encoded_*)
- 잘린 원본 영상을 선택한 encoding option으로 인코딩된 영상

### usv
- 여러 채널에서 Recording된 USV데이터들을 비디오 시간에 맞춰 정렬시킴
#### usv_table.csv
- date: USV 측정 날짜 (절대시간 기준)
- time: USV 측정 시간 (절대시간 기준)
- video_id: 해당 event가 recording된 video ID (video/encoded_*에 해당)
- time_delta: 해당 event의 recording video ID 기준 시간 (video_ID=1, 10초인 경우, video/encoded_001.avi파일의 10초에 해당)
- device_id: 해당 USV가 recording된 USV device ID
- filename: 해당하는 usv 파일 위치 (상대경로)
#### usv_table.sqlite
- usv_table.xlsx와 같은 정보를 담고 있는 sql 파일

### RFID
#### rfid_table.csv
- date: RFID 측정 날짜 (절대시간 기준)
- time: RFID 측정 시간 (절대시간 기준)
- video_id: 해당 event가 recording된 video ID (video/encoded_*에 해당)
- time_delta: 해당 event의 recording video ID 기준 시간 (video_ID=1, 10초인 경우, video/encoded_001.avi파일의 10초에 해당)
- zone_label: RFID zone label
- uid: RFID 개체 ID
- tag_no: RFID tag number