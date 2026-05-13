from bytes_parser.frame_struct import Frame, Row

mpp_unit: Frame = Frame('typeMPPUnit',[
    Row("ChanID", 2),
    Row("AcqTime ", 8),
    Row("WidthTime", 4, '.4f', parser=time_to_sec),
    Row("ZeroCount", 2),
    Row("Peak", 2, '.3f',
        parser=mpp_formatter, kwargs={"mpp_num": 3}),
    Row("Power", 4),
    Row("Mean", 2),
    Row("Noise", 2),
    Row("CRC", 2, 'X')
    ]
)