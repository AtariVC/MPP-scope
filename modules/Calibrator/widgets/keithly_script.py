import asyncio
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from keithley2600 import Keithley2600, ResultTable, log_to_screen
from keithley2600.result_table import ResultTablePlot
from loguru import logger
from pydantic import BaseModel, Field, create_model, model_validator

src_path = Path(__file__).resolve().parent.parent.parent.parent
# Добавляем папку src в sys.path
sys.path.append(str(src_path))

from src.log_config import log_init

# k = Keithley2600(f'TCPIP0::{address}::INSTR')


class ConvinceMeasure(BaseModel):
    vg_lst: list
    step_delay_s: float


class LinspaceMeasure(BaseModel):
    vg_start: float
    vg_stop: float
    vg_step: int
    step_delay_s: float


class ConstMeasure(BaseModel):
    vg_cnst: float


class MeasureSettings(BaseModel):
    convince_msr: ConvinceMeasure
    linspace_msr: LinspaceMeasure
    const_msr: ConstMeasure


class ModBusSettings(BaseModel):
    id: int
    bodrate: int


class MPModel(BaseModel):
    name: str
    calibrate_mode: bool  # Включить режим калибровки
    # (Нужно прописать настройки ModBus)
    modbus_settings: ModBusSettings | None = None
    measure_settings: MeasureSettings
    current_limit: float  # Задать ограничение по току
    loop: bool  # позволяет зациклить измерение
    save_table: bool
    save_plot: bool

    @classmethod
    def pydentic_model_init(cls, data: dict) -> Dict[str, "MPModel"]:
        return {
            name: cls.model_validate(conf)
            for name, conf in data.items()
        }

class MeasureProcessing:
    def __init__(self, k: Keithley2600 | None = None):
        # self.k = k
        self.mp_models: Dict[str, MPModel] = {}

    def load_config(self, json_conf: str):
        with open(json_conf, "r", encoding="utf-8") as jsn:
            raw = json.load(jsn)
        try:
            self.mp_models = MPModel.pydentic_model_init(raw)
        except Exception as e:
            logger.error(e)
    
    def run_measure(self, mp_name: str):
        mp_conf = self.mp_models.get(mp_name)
        if not mp_conf:
            logger.error(f"Measure config '{mp_name}' not found")
            return
        logger.debug(f"Running measure: {mp_conf.name}")
        # Здесь должна быть логика выполнения измерения в зависимости от настроек mp_conf
        # Например, если mp_conf.calibrate_mode == True, то выполняем калибровку
        # Если mp_conf.loop == True, то зацикливаем измерение и т.д.

if __name__ == "__main__":
    address = "10.6.1.222"
    logger = log_init()
    json_conf = Path("modules/Calibrator/widgets/keithly_script.json")
    try:
        k: Keithley2600 | None = Keithley2600(f"TCPIP0::{address}::INSTR")  # type:ignore
        logger.debug(f"Connected: TCPIP0::{address}::INSTR")
    except Exception as e:
        k = None
        logger.error(f"Error connection keithley: {e}")
    try:
        # if k:
        mp: MeasureProcessing = MeasureProcessing()
        mp.load_config(json_conf)
    except Exception as e:
        logger.error(e)
