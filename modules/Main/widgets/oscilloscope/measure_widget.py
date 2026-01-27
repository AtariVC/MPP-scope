import asyncio
import datetime
import struct
import sys
from functools import partial

# from save_config import ConfigSaver
from pathlib import Path

from PyQt6 import QtWidgets
from qtpy.uic import loadUi

# from src.write_data_to_file import write_to_hdf5_file

####### импорты из других директорий ######
# /src
src_path = Path(__file__).resolve().parent.parent.parent.parent
modules_path = Path(__file__).resolve().parent.parent.parent
# Добавляем папку src в sys.path
sys.path.append(str(src_path))
sys.path.append(str(modules_path))
from modules.Main.widgets.oscilloscope.graph_widget import GraphWidget  # noqa: E402
from modules.Main_Serial.main_serial_dialog_tcp import SerialConnect  # noqa: E402
from src.async_task_manager import AsyncTaskManager  # noqa: E402
from src.event.event import Event  # noqa: E402
from src.filters_data import FiltersData  # noqa: E402

class MeasureWidget(QtWidgets.QDialog):
    """Управление окном run_meas_widget.ui
    Запуск измерения, запуск тестовых импульсов, запись логфайла всех измерений.
    Опрос гистограмм МПП.

    Args:
        QtWidgets (_type_): _description_Базовый класс виджетов
    """

    lineEdit_max_a: QtWidgets.QLineEdit
    lineEdit_min_a: QtWidgets.QLineEdit
    lineEdit_pk_a: QtWidgets.QLineEdit

    lineEdit_max_b: QtWidgets.QLineEdit
    lineEdit_min_b: QtWidgets.QLineEdit
    lineEdit_pk_b: QtWidgets.QLineEdit

    def __init__(self) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath("measure_widget.ui"), self)


    def update_widget_ca_a(self, max, min, pk):
        self.lineEdit_max_a.setText(str(max))
        self.lineEdit_min_a.setText(str(min))
        self.lineEdit_pk_a.setText(str(pk))

    def update_widget_ca_b(self, max, min, pk):
        self.lineEdit_max_b.setText(str(max))
        self.lineEdit_min_b.setText(str(min))
        self.lineEdit_pk_b.setText(str(pk))
