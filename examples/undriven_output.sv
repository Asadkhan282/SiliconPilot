module undriven_output (
    input  logic       enable,
    input  logic [7:0] data_in,
    output logic [7:0] data_out,
    output logic       valid
);

always_comb begin
    data_out = 8'd0;

    if (enable)
        data_out = data_in;
end

endmodule