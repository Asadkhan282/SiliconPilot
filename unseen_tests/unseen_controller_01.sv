module unseen_controller_01 (
    input  logic        clk,
    input  logic        reset,
    input  logic        enable,
    input  logic [15:0] data_a,
    input  logic [15:0] data_b,
    input  logic [1:0]  opcode,

    output logic [7:0]  result,
    output logic        valid
);

logic [7:0] result_reg;

always_comb begin
    valid = 1'b0;

    case (opcode)

        2'b00: begin
            if (enable) begin
                result = data_a + data_b;
                valid = 1'b1;
            end
        end

        2'b01: begin
            if (enable) begin
                result = data_a - data_b;
                valid = 1'b1;
            end
        end

        2'b10: begin
            result = data_a & data_b;
            valid = 1'b1;
        end

        default: begin
            valid = 1'b0;
        end

    endcase
end


always_ff @(posedge clk) begin
    if (reset)
        result_reg <= 8'd0;
    else
        result_reg = result;
end

endmodule