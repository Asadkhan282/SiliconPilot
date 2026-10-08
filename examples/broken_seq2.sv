module broken_seq2 (
    input  logic       clk,
    input  logic       reset,
    input  logic [7:0] data_in,
    output logic [7:0] data_out,
    output logic [7:0] counter
);

always_ff @(posedge clk) begin
    if (reset) begin
        data_out <= 8'd0;
        counter  <= 8'd0;
    end
    else begin
        data_out = data_in;
        counter = counter + 1'b1;
    end
end

endmodule