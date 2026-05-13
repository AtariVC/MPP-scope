from bytes_parser.frame import Frame
from bytes_parser.row import Row

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
    ],
    byte_order="little",
)

mpp_ddii_unyt: Frame = Frame('typeMPPDDIIUnyt', [
    Row("TmpCount", 2),       # +6
    Row("ACQ1_Peak", 2),      # +7
    Row("ACQ2_Peak", 2),      # +8
    Row("DDIN_Peak", 2),      # +9
    Row("BinNum", 2),         # +10
    *[Row(f"threshold_el_th_{i}", 2) for i in range(6)],    # +11..16
    *[Row(f"threshold_el_max_{i}", 2) for i in range(2)],   # +17..18
    *[Row(f"threshold_p1_th_{i}", 2) for i in range(4)],    # +19..22
    *[Row(f"threshold_p2_th_{i}", 2) for i in range(4)],    # +23..26
    *[Row(f"threshold_p3_th_{i}", 2) for i in range(4)],    # +27..30
    *[Row(f"threshold_p4_th_{i}", 2) for i in range(4)],    # +31..34
    *[Row(f"threshold_p5_th_{i}", 2) for i in range(4)],    # +35..38
    *[Row(f"threshold_p6_th_{i}", 2) for i in range(4)],    # +39..42
    Row("res2", 2),           # +43
    Row("particle_electron_0_1", 4),                        # +44..45
    Row("particle_electron_0_5", 4),                        # +46..47
    Row("particle_electron_0_8", 4),                        # +48..49
    Row("particle_electron_1_6", 4),                        # +50..51
    Row("particle_electron_3", 4),                          # +52..53
    Row("particle_electron_5", 4),                          # +54..55
    Row("particle_proton_10", 2),                            # +56
    Row("particle_proton_30", 2),                            # +57
    Row("particle_proton_60", 2),                            # +58
    Row("particle_proton_100", 2),                           # +59
    Row("particle_proton_200", 2),                           # +60
    Row("particle_proton_500", 2),                           # +61
    Row("particle_HCP_1", 2),                                # +62
    Row("particle_HCP_5", 2),                                # +63
    Row("particle_HCP_10", 2),                               # +64
    Row("particle_HCP_20", 2),                               # +65
    Row("particle_HCP_45", 2),                               # +66
],
    byte_order="little",
)
