'''Описания всех переменных проекта
'''

class EnvironmentVar():
    MPP_ID                          = 14
    
    MPP_REG_COMMAND                 = 0x0000
    MPP_REG_TMP_COUNT               = 0x0006
    MPP_REG_ACQ1_PEAK               = 0x0007
    MPP_REG_ACQ2_PEAK               = 0x0008
    MPP_REG_DDIIN_PEAK              = 0x0009
    MPP_REG_BIN_NUM                 = 0x000A
    MPP_REG_HH                      = 0x000B
    MPP_REG_HIST_32                 = 0x002C
    MPP_REG_HIST_16                 = 0x0038
    MPP_REG_HIST_HCP                = 0x003E
    MPP_REG_LEVEL                   = 0x0079

    REG_CALIBR_ALL_CH               = 0x0050
    REG_OSCILL_CH0                  = 0xA000
    REG_OSCILL_CH1                  = 0xA200

    MPP_CMD_SET_LEVEL               = 0x0001
    MPP_CMD_SET_HH                  = 0x0008
    MPP_CMD_WAVEFORM_RELEASE        = 0x0009
    MPP_CMD_FILTER_BYPASS           = 0x000A
    MPP_CMD_TRIG_COUNT_CLEAR        = 0x000B
    MPP_CMD_START_MEASURE_FORCED    = 0x0051

    MPP_CMD_START_MEASURE: list[int]    = [0x0002, 0x0001]
    MPP_CMD_STOP_MEASURE: list[int]     = [0x0002, 0x0000]




    MB_F_CODE_16                    = 0x10
    MB_F_CODE_3                     = 0x03
    MB_F_CODE_6                     = 0x06
    REG_COMMAND                     = 0


    def __init__(self):
        pass