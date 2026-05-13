import asyncio
import datetime
import struct
import sys
from functools import partial
import qasync

# from save_config import ConfigSaver
from pathlib import Path

from PyQt6 import QtGui, QtWidgets
from qtpy.uic import loadUi
import qtmodern.styles

from loguru import logger

root_path = Path(__file__).resolve().parents[4]
modules_path = root_path.joinpath("modules")
# Добавляем папку src в sys.path
sys.path.append(str(root_path))
# sys.path.append(str(modules_path))

from src.async_task_manager import AsyncTaskManager  # noqa: E402
from src.mpp_frames.mpp_frames import mpp_unit, mpp_ddii_unyt  # noqa: E402
from src.table_view.df_table import DfModel
from src.log_config import log_init, log_s  # noqa: E402
from modules.Main_Serial.main_serial_dialog_tcp import SerialConnect  # noqa: E402

class MPPDataWidget(QtWidgets.QDialog):
    """Чтение структуры мпп и вывод данных в таблицу"""

    pushButton_mpp_request: QtWidgets.QPushButton
    tableView_mpp_df: QtWidgets.QTableView

    pushButton_mpp_ddii_request: QtWidgets.QPushButton
    tableView_mpp_ddii_df: QtWidgets.QTableView

    vLayout_ser_connect: QtWidgets.QVBoxLayout
    tabWidget_mpp: QtWidgets.QTabWidget

    def __init__(self, w_ser_dialog: SerialConnect, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        loadUi(Path(__file__).parent.joinpath("mpp_data_widget.ui"), self)
        self.tabWidget_mpp.setCurrentIndex(0)
        self.w_ser_dialog: SerialConnect = w_ser_dialog
        self.cm_cmd, self.mpp_cmd = self.w_ser_dialog.get_commands_interface()
        self.logger = logger

        if __name__ == "__main__":
            log_init()
            self.task_manager = AsyncTaskManager()
            w_ser_dialog.checkBox_mpp_only.setHidden(True)

        self.pushButton_mpp_request.clicked.connect(self.pushButton_mpp_request_hendler)
        self.pushButton_mpp_ddii_request.clicked.connect(self.pushButton_mpp_ddii_request_hendler)

    def _set_df_to_table(self, table: QtWidgets.QTableView, df):
        df = df.drop(columns=["IsOK", "ErrCnt"], errors="ignore")
        header = [str(column) for column in df.columns]

        if isinstance(table, QtWidgets.QTableWidget):
            table.clear()
            table.setRowCount(len(df.index))
            table.setColumnCount(len(header))
            table.setHorizontalHeaderLabels(header)
            for row_idx, row in enumerate(df.itertuples(index=False)):
                for col_idx, value in enumerate(row):
                    table.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(value)))
            table.resizeRowsToContents()
            return

        df_model = DfModel()
        df_model.header_labels = header
        df_model.setColumnCount(len(header))
        for row in df.itertuples(index=False):
            items = [QtGui.QStandardItem(str(value)) for value in row]
            df_model.appendRow(items)
        table.setModel(df_model)
        table.resizeRowsToContents()

    def _raise_for_bad_response(self, data: bytes):
        if data == b"-1":
            raise RuntimeError("MPP не отвечает")

    @qasync.asyncSlot()
    async def pushButton_mpp_request_hendler(self):
        try:
            self.cm_cmd, self.mpp_cmd = self.w_ser_dialog.get_commands_interface()
            data: bytes = await self.mpp_cmd.get_mpp_struct()
            self._raise_for_bad_response(data)
            df = mpp_unit.parse(data)
            self._set_df_to_table(self.tableView_mpp_df, df)
        except Exception as err:
            self.logger.exception(err)
            QtWidgets.QMessageBox.warning(self, "MPP data", f"Не удалось прочитать MPP struct:\n{err}")

    @qasync.asyncSlot()
    async def pushButton_mpp_ddii_request_hendler(self):
        try:
            self.cm_cmd, self.mpp_cmd = self.w_ser_dialog.get_commands_interface()
            data: bytes = await self.mpp_cmd.get_ddii_mpp_struct()
            self._raise_for_bad_response(data)
            df = mpp_ddii_unyt.parse(data)
            self._set_df_to_table(self.tableView_mpp_ddii_df, df)
        except Exception as err:
            self.logger.exception(err)
            QtWidgets.QMessageBox.warning(self, "MPP DDII data", f"Не удалось прочитать MPP DDII struct:\n{err}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    qtmodern.styles.dark(app)
    # light(app)
    log_init()
    w_ser_dialog: SerialConnect = SerialConnect(logger)
    w: MPPDataWidget = MPPDataWidget(w_ser_dialog)
    # add_serial_widget(w.vLayout_ser_connect, w_ser_dialog)
    w.vLayout_ser_connect.addWidget(w_ser_dialog)

    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    w.show()

    with event_loop:
        try:
            event_loop.run_until_complete(app_close_event.wait())
        except asyncio.CancelledError:
            ...
