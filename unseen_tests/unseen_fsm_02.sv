module unseen_fsm_02 (
    input  logic        clk,
    input  logic        reset,
    input  logic        start,
    input  logic [15:0] data_a,
    input  logic [15:0] data_b,

    output logic [7:0]  result,
    output logic        busy,
    output logic        done
);

typedef enum logic [1:0] {
    IDLE,
    EXECUTE,
    COMPLETE
} state_t;

state_t state;
state_t next_state;

always_comb begin

    busy = 1'b0;
    done = 1'b0;

    case (state)

        IDLE: begin
            if (start)
                next_state = EXECUTE;
            else
                next_state = IDLE;
        end

        EXECUTE: begin
            busy = 1'b1;
            result = data_a + data_b;
            next_state = COMPLETE;
        end

        COMPLETE: begin
            done = 1'b1;
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