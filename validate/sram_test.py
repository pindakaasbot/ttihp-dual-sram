# to load the detector and demoboard modules

from ttboard.boot.demoboard_detect import DemoboardDetect
from ttboard.demoboard import DemoBoard
from ttboard.mode import RPMode

import gc
gc.threshold(10000)


WE = 1 << 7
BANKSEL = 1 << 6

# to first probe the board/breakout
DemoboardDetect.probe()

# and then get a handle to the DemoBoard object
tt = DemoBoard.get()

# setup
tt.shuttle.tt_um_urish_sram_test.enable()
tt.mode = RPMode.ASIC_RP_CONTROL
tt.uio_oe_pico.value = 0xFF


def write(addr, data):
    tt.ui_in.value = BANKSEL
    # top 4 bits of addr
    tt.uio_in.value = addr >> 6
    tt.clock_project_once()
    # set rest of address and data
    tt.ui_in.value = WE | (addr & 0b00111111)
    tt.uio_in.value = data
    tt.clock_project_once()
    print(f"wrote {data:02x} to {addr:02x}")

def read(addr):
    tt.ui_in.value = BANKSEL
    # top 4 bits of addr
    tt.uio_in.value = addr >> 6
    tt.clock_project_once()
    # set rest of addr
    tt.ui_in.value = addr & 0b00111111
    tt.clock_project_once()
    print(f"read {int(tt.uo_out.value):02x} from {addr:02x}")
    return int(tt.uo_out.value)


for addr in range(1024):
    data = 0x00
    write(addr, data)
    assert read(addr) == data
    data = 0xAA
    write(addr, data)
    assert read(addr) == data
    data = 0xFF
    write(addr, data)
    assert read(addr) == data
