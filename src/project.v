/*
 * Copyright (c) 2024 Uri Shaked
 * SPDX-License-Identifier: Apache-2.0
 *
 * Dual 512x64 SRAM test — two memories using
 * RM_IHPSG13_1P_512x64_c2_bm_bist macros.
 * Byte-level read/write through 8-bit Tiny Tapeout interface.
 */

`default_nettype none

module tt_um_urish_sram_test (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  assign uio_oe  = 8'b0;  // All bidirectional IOs are inputs
  assign uio_out = 8'b0;

  // --- Pin mapping ---
  // ui_in[5:0] : lower 6 address bits
  // ui_in[6]   : bank_select (latches config register when high)
  // ui_in[7]   : write enable
  //
  // When bank_select=1: uio_in latches config:
  //   [2:0] = addr_high[2:0]  (address bits [8:6])
  //   [5:3] = byte_sel[2:0]   (which byte of 64-bit word, 0-7)
  //   [6]   = mem_sel          (which memory, 0 or 1)
  //
  // When bank_select=0: uio_in[7:0] = write data
  // uo_out[7:0] = read data (selected byte)

  wire       wen = ui_in[7];
  wire       bank_select = ui_in[6];
  wire [5:0] addr_low = ui_in[5:0];

  // Config register (latched on bank_select)
  reg [2:0] addr_high_reg;
  reg [2:0] byte_sel_reg;
  reg       mem_sel_reg;

  always @(posedge clk) begin
    if (~rst_n) begin
      addr_high_reg <= 0;
      byte_sel_reg  <= 0;
      mem_sel_reg   <= 0;
    end else if (bank_select) begin
      addr_high_reg <= uio_in[2:0];
      byte_sel_reg  <= uio_in[5:3];
      mem_sel_reg   <= uio_in[6];
    end
  end

  wire [2:0] addr_high = bank_select ? uio_in[2:0] : addr_high_reg;
  wire [2:0] byte_sel  = bank_select ? uio_in[5:3] : byte_sel_reg;
  wire       mem_sel   = bank_select ? uio_in[6]   : mem_sel_reg;
  wire [8:0] addr = {addr_high, addr_low};

  // Write enable per memory (active when writing & not bank_select)
  wire write_active = wen && !bank_select;
  wire wen_mem0 = write_active && !mem_sel;
  wire wen_mem1 = write_active &&  mem_sel;

  // Write data replicated across all byte lanes
  wire [7:0] wdata = uio_in;

  // Bit mask decode — enable only the targeted byte
  wire [63:0] bm = (byte_sel == 3'd0) ? 64'h00000000_000000FF :
                    (byte_sel == 3'd1) ? 64'h00000000_0000FF00 :
                    (byte_sel == 3'd2) ? 64'h00000000_00FF0000 :
                    (byte_sel == 3'd3) ? 64'h00000000_FF000000 :
                    (byte_sel == 3'd4) ? 64'h000000FF_00000000 :
                    (byte_sel == 3'd5) ? 64'h0000FF00_00000000 :
                    (byte_sel == 3'd6) ? 64'h00FF0000_00000000 :
                    (byte_sel == 3'd7) ? 64'hFF000000_00000000 : 64'h0;

  // --- Memory 0 ---
  wire [63:0] dout0;

  RM_IHPSG13_1P_512x64_c2_bm_bist sram0 (
      .A_CLK(clk), .A_MEN(rst_n),
      .A_WEN(wen_mem0), .A_REN(~wen),
      .A_ADDR(addr), .A_DIN({8{wdata}}), .A_DLY(1'b1),
      .A_DOUT(dout0), .A_BM(bm),
      .A_BIST_CLK(1'b0), .A_BIST_EN(1'b0), .A_BIST_MEN(1'b0),
      .A_BIST_WEN(1'b0), .A_BIST_REN(1'b0),
      .A_BIST_ADDR(9'b0), .A_BIST_DIN(64'b0), .A_BIST_BM(64'b0)
  );

  // --- Memory 1 ---
  wire [63:0] dout1;

  RM_IHPSG13_1P_512x64_c2_bm_bist sram1 (
      .A_CLK(clk), .A_MEN(rst_n),
      .A_WEN(wen_mem1), .A_REN(~wen),
      .A_ADDR(addr), .A_DIN({8{wdata}}), .A_DLY(1'b1),
      .A_DOUT(dout1), .A_BM(bm),
      .A_BIST_CLK(1'b0), .A_BIST_EN(1'b0), .A_BIST_MEN(1'b0),
      .A_BIST_WEN(1'b0), .A_BIST_REN(1'b0),
      .A_BIST_ADDR(9'b0), .A_BIST_DIN(64'b0), .A_BIST_BM(64'b0)
  );

  // --- Output mux ---
  wire [63:0] sel_word = mem_sel ? dout1 : dout0;

  reg [7:0] dout_byte;
  always @(*) begin
    case (byte_sel)
      3'd0: dout_byte = sel_word[7:0];
      3'd1: dout_byte = sel_word[15:8];
      3'd2: dout_byte = sel_word[23:16];
      3'd3: dout_byte = sel_word[31:24];
      3'd4: dout_byte = sel_word[39:32];
      3'd5: dout_byte = sel_word[47:40];
      3'd6: dout_byte = sel_word[55:48];
      3'd7: dout_byte = sel_word[63:56];
    endcase
  end

  assign uo_out = dout_byte;

endmodule
