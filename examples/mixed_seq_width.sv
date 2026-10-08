module mixed_seq_width (
    input  logic        clk,
    input  logic        reset,
    input  logic [15:0] a,
    input  logic [15:0] b,
    output logic [7:0]  result,
    output logic [7:0]  count
);

always_ff @(posedge clk) begin
    if (reset) begin
        result <= 8'd0;
        count  <= 8'd0;
    end
    else begin
        result = a + b;
        count = count + 1'b1;
    end
end

endmodule