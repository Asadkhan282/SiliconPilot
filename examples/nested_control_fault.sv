module nested_control_fault (
    input  logic       mode,
    input  logic       enable,
    input  logic [7:0] data_a,
    input  logic [7:0] data_b,
    output logic [7:0] result,
    output logic       valid
);

always_comb begin

    if (mode) begin
        if (enable) begin
            result = data_a;
            valid = 1'b1;
        end
    end
    else begin
        result = data_b;
        valid = 1'b0;
    end

end

endmodule