from bytes_parser.frame import Frame, Row

def time_to_sec(field: Row):
    sec = int.from_bytes(field.raw_val, "big")*25*10**-9
    # sec = int.from_bytes(field.raw_val, "big")
    return sec

mpp_unit: Frame = Frame('typeMPPUnit',[
    Row("ChanID", 2),
    Row("AcqTime ", 8),
    Row("WidthTime", 4, '.4f', parser=time_to_sec),
    Row("ZeroCount", 2),
    Row("Peak", 2, '.3f'),
    Row("Power", 4),
    Row("Mean", 2),
    Row("Noise", 2),
    Row("CRC", 2, 'X')
    ]
)

