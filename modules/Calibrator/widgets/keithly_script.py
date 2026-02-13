import json
from pydantic import BaseModel, Field, model_validator, create_model
from keithley2600 import Keithley2600, log_to_screen, ResultTable
from keithley2600.result_table import ResultTablePlot
from dataclasses import dataclass, field
import asyncio
from loguru import logger 
from pathlib import Path
import sys
from typing import List, Optional


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

class MPConf(BaseModel):
    name: str
    calibrate_mode: bool # Включить режим калибровки 
                         # (Нужно прописать настройки ModBus)
    modbus_settings: ModBusSettings
    current_limit: float # Задать ограничение по току
    loop: bool # позволяет зациклить измерение
    save_table: bool
    save_plot: bool


class MeasureProcess():
    def __init__(self, k: Keithley2600):
        self.k = k
    
    def dict_to_pydentic(self, mp_conf: dict):
        for key, value in mp_conf.items():
            if isinstance(value, dict):
                mp_conf
                setattr(self, key, key)

    def load_config(self, json_conf: str):
        with open(json_conf,  'r', encoding='utf-8') as jsn:
            mp_conf = json.load(jsn)
        try:
            self.dict_to_pydentic(mp_conf)
                
        except Exception as e:
            logger.error(e)

if __name__ == "__main__":
    address = '10.6.1.222'
    logger = log_init()
    json_conf = 'modules\Calibrator\widgets\keithly_script.json'
    try:
        k: Keithley2600|None = Keithley2600(f'TCPIP0::{address}::INSTR') # type:ignore
        logger.debug(f'Connected: TCPIP0::{address}::INSTR')
    except Exception as e:
        k = None
        logger.error(f"Error connection keithley: {e}")
    try:
        if k:
            mp: MeasureProcess = MeasureProcess(k)
            mp.update_config(json_conf)
    except Exception as e:
        logger.error(e)

    
