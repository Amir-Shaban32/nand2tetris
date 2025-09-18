// Mult.asm
// Computes R0 * R1 and stores in R2

    @R2
    M=0        // R2 = 0 (result)

    @R1
    D=M
    @counter
    M=D        // counter = R1

(LOOP)
    @counter
    D=M
    @END
    D;JEQ      // if counter == 0, jump to END

    @R0
    D=M
    @R2
    M=D+M      // R2 = R2 + R0

    @counter
    M=M-1      // counter--

    @LOOP
    0;JMP      // repeat

(END)
    @END
    0;JMP      // infinite loop to stop
