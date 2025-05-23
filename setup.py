from setuptools import setup, find_packages
from pathlib import Path
import re


def find_version():
    init_path = Path(__file__).parent / "datamanager" / "__init__.py"
    match = re.search(r'^__version__ = ["\']([^"\']+)["\']', init_path.read_text(), re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Cannot find version in __init__.py")


def setup_package():
    setup(
        name="datamanager",
        version=find_version(),
        author="jungyoung",
        description="A package for managing dataset in global STEAM project",
        packages=find_packages(),
        python_requires=">=3.10",
        install_requires=[
            "ffmpeg-python",
            "pyqt5",
            "pandas",
            "tqdm",
            "openpyxl"
        ],
        entry_points={
            "console_scripts": [
                "datagui = datamanager.__main__:main"
            ],
        },
    )

    
if __name__ == "__main__":
    setup_package()