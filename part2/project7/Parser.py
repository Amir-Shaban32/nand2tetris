from CommandType import *

class Parser:
    """
    Handles parsing of a single .vm file.
    Reads VM commands, removes comments/whitespace, and provides access to command parts.
    """

    def __init__(self, file_path):
        # Read all lines, clean them, and filter out empty lines
        with open(file_path, "r") as file:
            self.lines = [self._clean_line(line) for line in file]
            self.lines = [line for line in self.lines if line]
            self.idx = 0  # Current line index

    def _clean_line(self, line):
        """
        Removes comments and leading/trailing whitespace from a line.
        """
        line = line.strip()
        if "//" in line:
            line = line.split('//')[0].strip()
        return line

    def hasMoreLines(self):
        """
        Returns True if there are more commands in the input.
        """
        return self.idx < len(self.lines)
    
    def advance(self):
        """
        Reads the next command and makes it the current command.
        Should be called only if hasMoreLines() is true.
        """
        self.current_command = self.lines[self.idx]
        self.idx += 1

    def commandType(self):
        """
        Returns the type of the current VM command.
        """
        if self.current_command.split()[0] == "push":
            return C_PUSH
        elif self.current_command.split()[0] == "pop":
            return C_POP
        else:
            return C_ARITHMETIC
        
    def arg1(self):
        """
        Returns the first argument of the current command.
        For arithmetic commands, returns the command itself.
        Should not be called if the current command is C_RETURN.
        """
        if self.commandType() == C_ARITHMETIC:
            return self.current_command
        else:
            return self.current_command.split()[1]
        
    def arg2(self):
        """
        Returns the second argument of the current command (if any).
        Should be called only if the current command is C_PUSH, C_POP, C_FUNCTION, or C_CALL.
        """
        if self.commandType() != C_ARITHMETIC:
            return int(self.current_command.split()[2])
        else:
            return None