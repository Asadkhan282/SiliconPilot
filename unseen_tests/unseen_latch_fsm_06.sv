module unseen_latch_fsm_06 (
    input  logic        clk,
    input  logic        reset,
    input  logic        start,
    input  logic        enable,
    input  logic [1:0]  mode,
    input  logic [15:0] data_a,
    input  logic [15:0] data_b,

    output logic [7:0]  result,
    output logic        valid,
    output logic        busy
);

typedef enum logic [1:0] {
    IDLE,
    RUN,
    DONE
} state_t;

state_t state;
state_t next_state;

always_comb begin
    busy = 1'b0;

    case (state)

        IDLE: begin
            if (start)
                next_state = RUN;
            else
                next_state = IDLE;
        end

        RUN: begin
            busy = 1'b1;

            case (mode)

                2'b00: begin
                    if (enable) begin
                        result = data_a + data_b;
                        valid = 1'b1;
                    end
                end

                2'b01: begin
                    result = data_a & data_b;
                    valid = 1'b1;
                end

                default: begin
                    valid = 1'b0;
                end

            endcase

            next_state = DONE;
        end

        DONE: begin
            valid = 1'b1;
            next_state = IDLE;
        end

        default: begin
            next_state = IDLE;
        end

    endcase
end


always_ff @(posedge clk) begin
    if (reset)
        state <= IDLE;
    else
        state = next_state;
end

endmodule