module broken_alu (
    input  logic        clk,
    input  logic        reset,
    input  logic [7:0]  a,
    input  logic [7:0]  b,
    input  logic [1:0]  op,
    output logic [7:0]  result
);

always_ff @(posedge clk) begin
    if (reset)
        result <= 8'd0;
    else begin
        case (op)
            2'b00: result = a + b;
            2'b01: result = a - b;
            2'b10: result <= a & b;
            default: result = 8'd0;
        endcase
    end
end

endmodule