module broken_logic (
    input  logic       clk,
    input  logic       reset,
    input  logic       en,
    input  logic [7:0] data_in,
    output logic [7:0] data_out,
    output logic       valid
);

always_ff @(posedge clk) begin
    if (reset) begin
        data_out <= 8'd0;
        valid <= 1'b0;
    end
    else begin
        if (en)
            data_out = data_in;

        if (data_in == 8'hFF)
            valid = 1'b1;
    end
end

endmodule