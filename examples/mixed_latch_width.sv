module mixed_latch_width (
    input  logic        enable,
    input  logic [15:0] a,
    input  logic [15:0] b,
    output logic [7:0]  result
);

always_comb begin
    if (enable)
        result = a + b;
end

endmodule