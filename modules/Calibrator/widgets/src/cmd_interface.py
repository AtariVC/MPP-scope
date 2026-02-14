from serial import Serial
from src.serial_interface import open_serial, is_connect, ser_close, open_serial_mb
import time
import struct
from src.log_config import log_init, log_s
from pymodbus.client import ModbusSerialClient
from pymodbus.pdu import ModbusResponse
from src.env_var import EnvironmentVar
from src.modbus_worker import ModbusWorker
from src.pars_util import pars_16b, pars_32b
from loguru import logger

env = EnvironmentVar()
mw = ModbusWorker()


def mb_ecpt():
    def decorator(func):
        def _wraper(*args, **kwargs):
            client: ModbusSerialClient = args[0]
            try:
                res = func(*args, **kwargs)
                log_s(mw.send_handler.mess)
                return res
            except Exception as e:
                logger.error(e)
                return b'-1'
        return _wraper
    return decorator


####### stm32f405 -- gen impulse #######
@is_connect()
def f405_set_pulse(client: Serial, pulse: list[int]):
        #       /*  in:   byte0 - cmd
        #             byte1 - DAC1 level hi byte
        #             byte2 - DAC1 level lo byte
        #             byte3 - DAC2 level hi byte
        #             byte4 - DAC2 level lo byte
        #             byte5 - DIN[4:0]
        #             byte6 - pulse width in us
        #       out:  byte0 - cmd echo
        #   */
    CMD_GP_SET_PARAMS = 1
    trans = [CMD_GP_SET_PARAMS,
             (pulse[0] >> 8) & 0xFF,  
             pulse[0] & 0xFF, 
             (pulse[1] >> 8) & 0xFF,  
             pulse[1] & 0xFF,
             sum([val*2**index&0x1F for index, val in enumerate(pulse[2:])]),
             1]
    client.write(bytes(trans))
    # for byte in trans:
    #     client.write(struct.pack('<B', byte))
    t0 = time.time()
    echo = b''
    while (echo != bytes([CMD_GP_SET_PARAMS])):
        echo = client.read(1)
        if time.time() - t0 >= 0.5:
            logger.error(f"{client.port} not response")
            ser_close(client)
            break

@is_connect()
def f405_gen_pulse(client: Serial):
    CMD_GP_GENERATE = 2
    trans = [CMD_GP_GENERATE]
    client.write(bytearray(trans))
    echo = b'0'
    t0 = time.time()
    while (echo != bytes([CMD_GP_GENERATE])):
        echo = client.read(1)
        if time.time() - t0 >= 0.5:
            logger.error(f"{client.port} not response")
            ser_close(client)
            break
##################################################

####### mpp cmd interface #######

#### === get === #### 
@mb_ecpt()
def get_hist32(client: ModbusSerialClient) -> bytes:
    result: ModbusResponse = client.read_holding_registers(env.MPP_REG_HIST_32, 
                                                            12,
                                                            env.MPP_ID)
    return result.encode()[1:]

@mb_ecpt()
def get_hist16(client: ModbusSerialClient) -> bytes:
    result: ModbusResponse = client.read_holding_registers(env.MPP_REG_HIST_16, 
                                                            6,
                                                            env.MPP_ID)
    return result.encode()[1:]

@mb_ecpt()
def get_bin_num(client: ModbusSerialClient) -> bytes:
    result: ModbusResponse = client.read_holding_registers(env.MPP_REG_BIN_NUM, 
                                                            1,
                                                            env.MPP_ID)
    return result.encode()[1:]



@mb_ecpt()
def get_ddin(client: ModbusSerialClient) -> bytes:
    result: ModbusResponse = client.read_holding_registers(env.MPP_REG_DDIIN_PEAK, 
                                                            1,
                                                            env.MPP_ID)
    return result.encode()[1:]
    
@mb_ecpt()
def get_tmp_cnt(client: ModbusSerialClient) -> bytes:
    result: ModbusResponse = client.read_holding_registers(env.MPP_REG_COMMAND, 
                                                            1,
                                                            env.MPP_ID)
    return result.encode()[1:]

@mb_ecpt()
def get_acq1_peak(client: ModbusSerialClient) -> bytes:
    result: ModbusResponse = client.read_holding_registers(env.MPP_REG_ACQ1_PEAK, 
                                                            1,
                                                            env.MPP_ID)
    return result.encode()[1:]

@mb_ecpt()
def get_acq2_peak(client: ModbusSerialClient) -> bytes:
    result: ModbusResponse = client.read_holding_registers(env.MPP_REG_ACQ2_PEAK, 
                                                            1,
                                                            env.MPP_ID)
    return result.encode()[1:]

@mb_ecpt()
def get_hh(client: ModbusSerialClient) -> bytes:
    result: ModbusResponse = client.read_holding_registers(env.MPP_REG_HH, 
                                                            32,
                                                            env.MPP_ID)
    return result.encode()[1:]

#### === set === #### 
# @mb_ecpt()
# def set_lvl(client: ModbusSerialClient, cmd: int):
#     result: ModbusResponse = client.write_registers(env.MPP_REG_LEVEL, 
#                                                     cmd,
#                                                     env.MPP_ID)
    
@mb_ecpt()
def set_hh(client: ModbusSerialClient, cmd: list[int]):
    result: ModbusResponse = client.write_registers(env.MPP_REG_HH, 
                                                    cmd,
                                                    env.MPP_ID)

@mb_ecpt()
def set_clear_hist(client: ModbusSerialClient):
    result: ModbusResponse = client.write_registers(env.MPP_REG_HIST_32, 
                                                    [0]*18,
                                                    env.MPP_ID)

@mb_ecpt()
def set_clear_reg_mes(client: ModbusSerialClient):
    result: ModbusResponse = client.write_registers(env.MPP_REG_ACQ1_PEAK, 
                                                    [0]*4,
                                                    env.MPP_ID)

#### === cmd === #### 
@mb_ecpt()
def cmd_set_level(client: ModbusSerialClient, cmd: int):
    result: ModbusResponse = client.write_registers(env.MPP_REG_COMMAND, 
                                                    [env.MPP_CMD_SET_LEVEL, cmd],
                                                    env.MPP_ID)
    
@mb_ecpt()
def cmd_start_meas(client: ModbusSerialClient):
    result: ModbusResponse = client.write_registers(env.MPP_REG_COMMAND, 
                                                    env.MPP_CMD_START_MEASURE,
                                                    env.MPP_ID)

@mb_ecpt()
def cmd_stop_meas(client: ModbusSerialClient):
    result: ModbusResponse = client.write_registers(env.MPP_REG_COMMAND, 
                                                    env.MPP_CMD_STOP_MEASURE,
                                                    env.MPP_ID)
    
@mb_ecpt()
def cmd_set_hh(client: ModbusSerialClient):
    result: ModbusResponse = client.write_registers(env.MPP_REG_COMMAND, 
                                                    env.MPP_CMD_SET_HH,
                                                    env.MPP_ID)
    
@mb_ecpt()
def cmd_trig_cnt_clr(client: ModbusSerialClient):
    result: ModbusResponse = client.write_registers(env.MPP_REG_COMMAND, 
                                                    env.MPP_CMD_TRIG_COUNT_CLEAR,
                                                    env.MPP_ID)

##################################################


