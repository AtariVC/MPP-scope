import asyncio
import sys
from pathlib import Path

import qasync
import qtmodern.styles
from pymodbus.client import AsyncModbusSerialClient
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QDoubleValidator, QFont, QIntValidator
from PyQt6.QtWidgets import (
    QGroupBox,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from qtmodern.windows import ModernWindow
from qtpy.uic import loadUi

####### импорты из других директорий ######````
# /src
src_path = Path(__file__).resolve().parent.parent.parent
modules_path = Path(__file__).resolve().parent.parent

# Добавляем папку src в sys.path
sys.path.append(str(src_path))
sys.path.append(str(modules_path))

# from Engine.widgets.oscilloscope.flux_widget import FluxWidget  # noqa: E402
from Engine.widgets.oscilloscope.graph_widget import GraphWidget  # noqa: E402
# from Engine.widgets.oscilloscope.run_flux_widget import RunFluxWidget  # noqa: E402
from Engine.widgets.oscilloscope.run_meas_widget import RunMeasWidget  # noqa: E402
# from Engine.widgets.viewer.explorer_hdf5_widget import ExplorerHDF5Widget  # noqa: E402
# from Engine.widgets.viewer.graph_viewer_widget import GraphViewerWidget  # noqa: E402
from Main_Serial.main_serial_dialog_tcp import SerialConnect  # noqa: E402

from src.craft_custom_widget import add_serial_widget
from src.ddii_command import ModbusCMCommand, ModbusMPPCommand  # noqa: E402
from src.log_config import log_init, log_s  # noqa: E402
from src.main_window_maker import clear_left_widget, create_split_widget, create_tab_widget_items
from src.modbus_worker import ModbusWorker  # noqa: E402
from src.parsers import Parsers  # noqa: E402
from src.parsers_pack import LineEditPack, LineEObj  # noqa: E402
from modules.Engine.widgets.oscilloscope.measure_widget import MeasureWidget


class Engine(QtWidgets.QMainWindow):
    gridLayout_main_split: QtWidgets.QGridLayout

    coroutine_get_client_finished = QtCore.pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath("engine.ui"), self)
        self.resize(1300, 800)
        self.mw: ModbusWorker = ModbusWorker()
        self.parser: Parsers = Parsers()
        self.logger = log_init()

        # self.init_QObjects()
        # self.config = ConfigSaver()
        self.init_widgets()

    def widget_model(self):
        spacer_v = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return {
            "Осциллограф": {
                "Меню запуска": self.run_meas_widget,
                "Измерение": self.measure_widget,
                # "Счетчик частиц": self.flux_widget,
                "spacer": spacer_v,
                "Подключение": self.w_ser_dialog,
            }
        }

    def on_tab_widget_handler(self, index: int):
        tab_text: str = self.tab_widget.tabText(index)
        if tab_text == "Вьюер":
            clear_left_widget(self.w_graph_widget, self.graph_viewer_widget)

        if tab_text == "Осциллограф":
            clear_left_widget(self.graph_viewer_widget, self.w_graph_widget)

        if tab_text == "Вьюер":
            self.current_left_widget = self.graph_viewer_widget
        elif tab_text == "Осциллограф":
            self.current_left_widget = self.w_graph_widget

    def init_widgets(self) -> None:
        # Виджеты
        self.w_graph_widget: GraphWidget = GraphWidget()
        self.w_ser_dialog: SerialConnect = SerialConnect(self.logger)
        for i in range(self.w_ser_dialog.tabWidget_serial.count()):
            if self.w_ser_dialog.tabWidget_serial.tabText(i).strip().lower() == "tcp":
                self.w_ser_dialog.tabWidget_serial.removeTab(i)
                break
        self.measure_widget: MeasureWidget = MeasureWidget()
        self.run_meas_widget: RunMeasWidget = RunMeasWidget(self)
        self.client = self.w_ser_dialog.client
        model = self.widget_model()
        self.tab_widget = create_tab_widget_items(model, self.on_tab_widget_handler)
        #### отдельно добавляем SerialConnectWidget
        vLayout_ser_connect = QVBoxLayout()
        # add_serial_widget(vLayout_ser_connect, self.w_ser_dialog)
        spacer_v = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # tab_widget.layout.addItem(spacer_v)
        # tab_widget.layout.addLayout(vLayout_ser_connect)
        create_split_widget(self.gridLayout_main_split, self.w_graph_widget, self.tab_widget)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    qtmodern.styles.dark(app)
    w: Engine = Engine()
    mw: ModernWindow = ModernWindow(w)
    mw.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, False)  # fix flickering on resize window
    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    mw.show()

    with event_loop:
        try:
            event_loop.run_until_complete(app_close_event.wait())
        except asyncio.CancelledError:
            ...
