module mixed_seq_latch (
    input  logic       clk,
    input  logic       reset,
    input  logic       enable,
    input  logic [7:0] data_in,
    output logic [7:0] data_reg,
    output logic [7:0] selected_data
);

always_ff @(posedge clk) begin
    if (reset)
        data_reg <= 8'd0;
    else
        data_reg = data_in;
end

always_comb begin
    if (enable)
        selected_data = data_reg;
end

endmodule