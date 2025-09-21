"""
CommandType.py

Defines constants for VM command types used by the Parser and CodeWriter.
These constants represent the different categories of VM commands in the Hack VM specification.
"""
# Arithmetic and logical commands
C_ARITHMETIC = "C_ARITHMETIC"  # add, sub, neg, eq, gt, lt, and, or, not

# Memory access commands
C_PUSH = "push"                # Push onto stack
C_POP = "pop"                  # Pop from stack

# Program flow commands
C_LABEL = "label"              # Label declaration
C_GOTO = "goto"                # Unconditional jump
C_IF = "if-goto"               # Conditional jump

# Function commands
C_FUNCTION = "function"        # Function declaration
C_RETURN = "return"            # Return from function
C_CALL = "call"                # Function call