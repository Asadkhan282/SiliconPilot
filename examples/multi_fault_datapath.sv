module multi_fault_datapath (
    input  logic        clk,
    input  logic        reset,
    input  logic        enable,
    input  logic [15:0] a,
    input  logic [15:0] b,
    output logic [7:0]  result,
    output logic [7:0]  result_reg
);

always_comb begin
    if (enable)
        result = a + b;
end

always_ff @(posedge clk) begin
    if (reset)
        result_reg <= 8'd0;
    else
        result_reg = result;
end

endmodule