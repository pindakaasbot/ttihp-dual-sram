// Synthesis stub for RM_IHPSG13_1P_512x8_c3_bm_bist

`default_nettype none

module RM_IHPSG13_1P_512x8_c3_bm_bist (
    input  wire       A_CLK,
    input  wire       A_MEN,
    input  wire       A_WEN,
    input  wire       A_REN,
    input  wire [8:0] A_ADDR,
    input  wire [7:0] A_DIN,
    input  wire       A_DLY,
    output wire [7:0] A_DOUT,
    input  wire [7:0] A_BM,
    input  wire       A_BIST_CLK,
    input  wire       A_BIST_EN,
    input  wire       A_BIST_MEN,
    input  wire       A_BIST_WEN,
    input  wire       A_BIST_REN,
    input  wire [8:0] A_BIST_ADDR,
    input  wire [7:0] A_BIST_DIN,
    input  wire [7:0] A_BIST_BM
);

  assign A_DOUT = 8'b0;

endmodule
