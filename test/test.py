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
    """Read a byte at addr_low (using current config).
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

    # --- Test all 8 byte lanes in memory 0 ---
    for byte_idx in range(8):
        dut._log.info(f"mem0, byte {byte_idx}: write/read")
        await set_config(dut, addr_high=0, byte_sel=byte_idx, mem_sel=0)
        test_val = 0x10 + byte_idx
        await write_byte(dut, 8, test_val)
        val = await read_byte(dut, 8)
        assert val == test_val, f"byte {byte_idx}: Expected 0x{test_val:02x}, got 0x{val:02x}"

    # --- Verify all bytes are still intact ---
    dut._log.info("verify all bytes at addr 8")
    for byte_idx in range(8):
        await set_config(dut, addr_high=0, byte_sel=byte_idx, mem_sel=0)
        val = await read_byte(dut, 8)
        expected = 0x10 + byte_idx
        assert val == expected, f"byte {byte_idx}: Expected 0x{expected:02x}, got 0x{val:02x}"

    # --- Test memory 1 ---
    dut._log.info("mem1: write/read bytes 0 and 7")
    await set_config(dut, addr_high=0, byte_sel=0, mem_sel=1)
    await write_byte(dut, 8, 0xA0)
    val = await read_byte(dut, 8)
    assert val == 0xA0, f"Expected 0xA0, got 0x{val:02x}"

    await set_config(dut, addr_high=0, byte_sel=7, mem_sel=1)
    await write_byte(dut, 8, 0xA7)
    val = await read_byte(dut, 8)
    assert val == 0xA7, f"Expected 0xA7, got 0x{val:02x}"

    # --- Verify memory 0 not affected ---
    dut._log.info("verify mem0 byte 0 addr 8 unchanged")
    await set_config(dut, addr_high=0, byte_sel=0, mem_sel=0)
    val = await read_byte(dut, 8)
    assert val == 0x10, f"Expected 0x10, got 0x{val:02x}"

    # --- Test bank switching (addr_high) ---
    dut._log.info("test bank switching: write to bank 5")
    await set_config(dut, addr_high=5, byte_sel=0, mem_sel=0)
    await write_byte(dut, 10, 0xEE)
    val = await read_byte(dut, 10)
    assert val == 0xEE, f"Expected 0xEE, got 0x{val:02x}"

    # Switch back to bank 0 and verify byte 0 unchanged
    dut._log.info("switch back to bank 0, verify addr 8")
    await set_config(dut, addr_high=0, byte_sel=0, mem_sel=0)
    val = await read_byte(dut, 8)
    assert val == 0x10, f"Expected 0x10, got 0x{val:02x}"

    # --- Test overwrite ---
    dut._log.info("test overwrite at mem0 byte 0 addr 8")
    await write_byte(dut, 8, 0x99)
    val = await read_byte(dut, 8)
    assert val == 0x99, f"Expected 0x99, got 0x{val:02x}"

    # --- Test write blocked during bank_select ---
    dut._log.info("verify writes blocked during bank_select")
    dut.ui_in.value = WE | BANKSEL | 8
    dut.uio_in.value = 0x00  # cfg: addr_high=0, byte_sel=0, mem_sel=0
    await ClockCycles(dut.clk, 1)
    val = await read_byte(dut, 8)
    assert val == 0x99, f"Expected 0x99 (write should be blocked), got 0x{val:02x}"

    dut._log.info("all good!")
