// Synthesis stub for RM_IHPSG13_1P_512x64_c2_bm_bist
// The actual macro is provided as GDS/LEF during hardening.

`default_nettype none

module RM_IHPSG13_1P_512x64_c2_bm_bist (
    input  wire        A_CLK,
    input  wire        A_MEN,
    input  wire        A_WEN,
    input  wire        A_REN,
    input  wire [8:0]  A_ADDR,
    input  wire [63:0] A_DIN,
    input  wire        A_DLY,
    output wire [63:0] A_DOUT,
    input  wire [63:0] A_BM,
    input  wire        A_BIST_CLK,
    input  wire        A_BIST_EN,
    input  wire        A_BIST_MEN,
    input  wire        A_BIST_WEN,
    input  wire        A_BIST_REN,
    input  wire [8:0]  A_BIST_ADDR,
    input  wire [63:0] A_BIST_DIN,
    input  wire [63:0] A_BIST_BM
);

  assign A_DOUT = 64'b0;

endmodule
