// Behavioral model for RM_IHPSG13_1P_512x32_c2_bm_bist
// 512 words × 32 bits, 9-bit address

`celldefine
module RM_IHPSG13_1P_512x32_c2_bm_bist (
    A_CLK,
    A_MEN,
    A_WEN,
    A_REN,
    A_ADDR,
    A_DIN,
    A_DLY,
    A_DOUT,
    A_BM,
    A_BIST_CLK,
    A_BIST_EN,
    A_BIST_MEN,
    A_BIST_WEN,
    A_BIST_REN,
    A_BIST_ADDR,
    A_BIST_DIN,
    A_BIST_BM
);

    input A_CLK;
    input A_MEN;
    input A_WEN;
    input A_REN;
    input [8:0] A_ADDR;
    input [31:0] A_DIN;
    input A_DLY;
    output [31:0] A_DOUT;
    input [31:0] A_BM;
    input A_BIST_CLK;
    input A_BIST_EN;
    input A_BIST_MEN;
    input A_BIST_WEN;
    input A_BIST_REN;
    input [8:0] A_BIST_ADDR;
    input [31:0] A_BIST_DIN;
    input [31:0] A_BIST_BM;

`ifdef FUNCTIONAL

    SRAM_1P_behavioral_bm_bist #(
        .P_DATA_WIDTH(32),
        .P_ADDR_WIDTH(9)
    ) i_SRAM_1P_behavioral_bm_bist (
        .A_CLK(A_CLK),
        .A_MEN(A_MEN),
        .A_WEN(A_WEN),
        .A_REN(A_REN),
        .A_ADDR(A_ADDR),
        .A_DLY(A_DLY),
        .A_DIN(A_DIN),
        .A_DOUT(A_DOUT),
        .A_BM(A_BM),
        .A_BIST_CLK(A_BIST_CLK),
        .A_BIST_EN(A_BIST_EN),
        .A_BIST_MEN(A_BIST_MEN),
        .A_BIST_WEN(A_BIST_WEN),
        .A_BIST_REN(A_BIST_REN),
        .A_BIST_ADDR(A_BIST_ADDR),
        .A_BIST_DIN(A_BIST_DIN),
        .A_BIST_BM(A_BIST_BM)
    );

`else

    // Timing model placeholder
    SRAM_1P_behavioral_bm_bist #(
        .P_DATA_WIDTH(32),
        .P_ADDR_WIDTH(9)
    ) i_SRAM_1P_behavioral_bm_bist (
        .A_CLK(A_CLK),
        .A_MEN(A_MEN),
        .A_WEN(A_WEN),
        .A_REN(A_REN),
        .A_ADDR(A_ADDR),
        .A_DLY(A_DLY),
        .A_DIN(A_DIN),
        .A_DOUT(A_DOUT),
        .A_BM(A_BM),
        .A_BIST_CLK(A_BIST_CLK),
        .A_BIST_EN(A_BIST_EN),
        .A_BIST_MEN(A_BIST_MEN),
        .A_BIST_WEN(A_BIST_WEN),
        .A_BIST_REN(A_BIST_REN),
        .A_BIST_ADDR(A_BIST_ADDR),
        .A_BIST_DIN(A_BIST_DIN),
        .A_BIST_BM(A_BIST_BM)
    );

`endif

endmodule
`endcelldefine
