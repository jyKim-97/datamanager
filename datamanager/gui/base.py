from abc import ABCMeta, abstractmethod
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtCore import QObject


# Dynamically get PyQt5's internal metaclass
PyQtBaseMeta = type(QGroupBox)

# Combined metaclass
class WidgetABCMeta(PyQtBaseMeta, ABCMeta):
    pass


class BaseWidget(metaclass=WidgetABCMeta):

    @abstractmethod
    def init_ui(self):
        ...
        
    @abstractmethod
    def check_fill(self) -> bool:
        ...
    
    @abstractmethod
    def run(self, *args, **kwargs):
        ...
        
        