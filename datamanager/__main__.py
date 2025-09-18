from . import DataManagerGUI
import sys
from PyQt5.QtWidgets import QApplication
import argparse


def build_args():
    parser = argparse.ArgumentParser(description="Data Manager GUI")
    parser.add_argument("--root_dir", type=str, default=None)
    parser.add_argument("--video_path", type=str)
    parser.add_argument("--usv_path", type=str)
    return parser
    
    
def main(**kwargs):
    app = QApplication(sys.argv)
    window = DataManagerGUI(**kwargs)
    window.resize(1200, 1000)
    window.move(200, 100)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(**vars(build_args().parse_args()))
    