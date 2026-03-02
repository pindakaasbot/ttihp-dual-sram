# SPDX-FileCopyrightText: © 2024 Uri Shaked
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

BANKSEL = 1 << 6
WE = 1 << 7


async def set_config(dut, addr_high=0, byte_sel=0, mem_sel=0):
    """Set config register via bank_select."""
    cfg = (addr_high & 0x7) | ((byte_sel & 0x7) << 3) | ((mem_sel & 0x1) << 6)
    dut.ui_in.value = BANKSEL
    dut.uio_in.value = cfg
    await ClockCycles(dut.clk, 1)


async def write_byte(dut, addr_low, data):
    """Write a byte at addr_low (using current config for addr_high/byte_sel/mem_sel)."""
    dut.ui_in.value = WE | (addr_low & 0x3F)
    dut.uio_in.value = data & 0xFF
    await ClockCycles(dut.clk, 1)


async def read_byte(dut, addr_low):
    """Read a byte at addr_low (using current config for addr_high/byte_sel/mem_sel).
    Returns the read value."""
    dut.ui_in.value = addr_low & 0x3F
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)
    return int(dut.uo_out.value)


@cocotb.test()
async def test_dual_sram(dut):
    """Test basic read/write to both memories across all byte lanes."""
    dut._log.info("start")
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    dut._log.info("reset")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)

    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # All bidirectional ports should be inputs
    assert int(dut.uio_oe.value) == 0

    # --- Test memory 0, byte 0 (from 512x32, lowest byte) ---
    dut._log.info("mem0, byte 0: write/read")
    await set_config(dut, addr_high=0, byte_sel=0, mem_sel=0)

    await write_byte(dut, 8, 0x55)
    await write_byte(dut, 9, 0x66)

    val = await read_byte(dut, 8)
    assert val == 0x55, f"Expected 0x55, got 0x{val:02x}"
    val = await read_byte(dut, 9)
    assert val == 0x66, f"Expected 0x66, got 0x{val:02x}"

    # --- Test memory 0, byte 3 (from 512x32, highest byte) ---
    dut._log.info("mem0, byte 3: write/read")
    await set_config(dut, addr_high=0, byte_sel=3, mem_sel=0)

    await write_byte(dut, 8, 0xAA)
    val = await read_byte(dut, 8)
    assert val == 0xAA, f"Expected 0xAA, got 0x{val:02x}"

    # --- Test memory 0, byte 4 (from 512x16, low byte) ---
    dut._log.info("mem0, byte 4: write/read")
    await set_config(dut, addr_high=0, byte_sel=4, mem_sel=0)

    await write_byte(dut, 8, 0xBB)
    val = await read_byte(dut, 8)
    assert val == 0xBB, f"Expected 0xBB, got 0x{val:02x}"

    # --- Test memory 0, byte 5 (from 512x16, high byte) ---
    dut._log.info("mem0, byte 5: write/read")
    await set_config(dut, addr_high=0, byte_sel=5, mem_sel=0)

    await write_byte(dut, 8, 0xCC)
    val = await read_byte(dut, 8)
    assert val == 0xCC, f"Expected 0xCC, got 0x{val:02x}"

    # --- Test memory 0, byte 6 (from 512x8) ---
    dut._log.info("mem0, byte 6: write/read")
    await set_config(dut, addr_high=0, byte_sel=6, mem_sel=0)

    await write_byte(dut, 8, 0xDD)
    val = await read_byte(dut, 8)
    assert val == 0xDD, f"Expected 0xDD, got 0x{val:02x}"

    # --- Verify earlier bytes are still intact ---
    dut._log.info("verify byte 0 at addr 8 is still 0x55")
    await set_config(dut, addr_high=0, byte_sel=0, mem_sel=0)
    val = await read_byte(dut, 8)
    assert val == 0x55, f"Expected 0x55, got 0x{val:02x}"

    # --- Test memory 1 ---
    dut._log.info("mem1, byte 0: write/read")
    await set_config(dut, addr_high=0, byte_sel=0, mem_sel=1)

    await write_byte(dut, 8, 0x11)
    await write_byte(dut, 9, 0x22)

    val = await read_byte(dut, 8)
    assert val == 0x11, f"Expected 0x11, got 0x{val:02x}"
    val = await read_byte(dut, 9)
    assert val == 0x22, f"Expected 0x22, got 0x{val:02x}"

    # --- Test memory 1, byte 6 ---
    dut._log.info("mem1, byte 6: write/read")
    await set_config(dut, addr_high=0, byte_sel=6, mem_sel=1)

    await write_byte(dut, 8, 0x33)
    val = await read_byte(dut, 8)
    assert val == 0x33, f"Expected 0x33, got 0x{val:02x}"

    # --- Verify memory 0 is not affected by memory 1 writes ---
    dut._log.info("verify mem0 byte 0 addr 8 unchanged")
    await set_config(dut, addr_high=0, byte_sel=0, mem_sel=0)
    val = await read_byte(dut, 8)
    assert val == 0x55, f"Expected 0x55, got 0x{val:02x}"

    # --- Test bank switching (addr_high) ---
    dut._log.info("test bank switching: write to bank 3")
    await set_config(dut, addr_high=3, byte_sel=0, mem_sel=0)

    await write_byte(dut, 10, 0xEE)
    val = await read_byte(dut, 10)
    assert val == 0xEE, f"Expected 0xEE, got 0x{val:02x}"

    # Switch back to bank 0 and verify byte unchanged
    dut._log.info("switch back to bank 0, verify addr 8")
    await set_config(dut, addr_high=0, byte_sel=0, mem_sel=0)
    val = await read_byte(dut, 8)
    assert val == 0x55, f"Expected 0x55, got 0x{val:02x}"

    # --- Test overwrite ---
    dut._log.info("test overwrite at mem0 byte 0 addr 8")
    await write_byte(dut, 8, 0x99)
    val = await read_byte(dut, 8)
    assert val == 0x99, f"Expected 0x99, got 0x{val:02x}"

    # --- Test write blocked during bank_select ---
    dut._log.info("verify writes blocked during bank_select")
    # Try to write while bank_select is high (targeting mem0/byte0/addr_high=0)
    dut.ui_in.value = WE | BANKSEL | 8
    dut.uio_in.value = 0x00  # cfg: addr_high=0, byte_sel=0, mem_sel=0
    await ClockCycles(dut.clk, 1)
    # Read back — should still be 0x99 (write_active is blocked when bank_select=1)
    val = await read_byte(dut, 8)
    assert val == 0x99, f"Expected 0x99 (write should be blocked), got 0x{val:02x}"

    dut._log.info("all good!")
