module final_multi_fault (
    input  logic        clk,
    input  logic        reset,
    input  logic        enable,
    input  logic        mode,
    input  logic [15:0] a,
    input  logic [15:0] b,

    output logic [7:0]  comb_result,
    output logic [7:0]  registered_result,
    output logic        valid
);

always_comb begin

    if (mode) begin
        if (enable) begin
            comb_result = a + b;
            valid = 1'b1;
        end
    end
    else begin
        comb_result = 8'd0;
        valid = 1'b0;
    end

end


always_ff @(posedge clk) begin
    if (reset)
        registered_result <= 8'd0;
    else
        registered_result = comb_result;
end

endmodule