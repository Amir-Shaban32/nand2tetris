// Fill.asm
// Blacken screen if any key pressed, else clear it

(START)

    @KBD
    D=M
    @NO_KEY
    D;JEQ        // if no key pressed -> jump to NO_KEY

    // --- Key pressed: fill screen black ---
    @SCREEN
    D=A
    @addr
    M=D          // addr = SCREEN

(FILL)
    @addr
    A=M
    M=-1         // blacken 16 pixels

    @addr
    M=M+1        // addr++

    @KBD
    D=A          // D = 24576
    @addr
    D=D-M        // D = KBD - addr
    @FILL
    D;JGT        // if addr < KBD, keep filling

    @START
    0;JMP


(NO_KEY)
    // --- No key pressed: clear screen ---
    @SCREEN
    D=A
    @addr
    M=D          // addr = SCREEN

(CLEAR)
    @addr
    A=M
    M=0          // whiten 16 pixels

    @addr
    M=M+1        // addr++

    @KBD
    D=A
    @addr
    D=D-M        // D = KBD - addr
    @CLEAR
    D;JGT        // if addr < KBD, keep clearing

    @START
    0;JMP
