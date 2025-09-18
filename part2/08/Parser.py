from CommandType import *

class Parser:
    """
    Handles parsing of a single .vm file.
    Reads VM commands, removes comments/whitespace, and provides access to command parts.
    """
    
    def __init__(self, file_path):
        with open(file_path, "r") as file:
            self.lines = [self._clean_line(line) for line in file]
        self.lines = [line for line in self.lines if line]
        self.idx = 0
        self.current_command = ""

    def _clean_line(self, line):
        """
        Removes comments and whitespace from a line.
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
        Reads the next command from the input and makes it the current command.
        Should only be called if hasMoreLines() is True.
        """
        if self.hasMoreLines():
            self.current_command = self.lines[self.idx]
            self.idx += 1

    def commandType(self):
        """
        Returns the type of the current VM command.
        Matches the string constants from CommandType.py
        """
        if not self.current_command:
            return None

        command_parts = self.current_command.split()
        if not command_parts:
            return None

        first_word = command_parts[0]

        if first_word == "push":
            return C_PUSH
        elif first_word == "pop":
            return C_POP
        elif first_word == "label":
            return C_LABEL
        elif first_word == "goto":
            return C_GOTO
        elif first_word == "if-goto":
            return C_IF
        elif first_word == "function":
            return C_FUNCTION
        elif first_word == "call":
            return C_CALL
        elif first_word == "return":
            return C_RETURN
        else:
            return C_ARITHMETIC  # add, sub, neg, eq, gt, lt, and, or, not

    def arg1(self):
        """
        Returns the first argument of the current command.
        For arithmetic commands, returns the command itself.
        Should not be called if the current command is C_RETURN.
        """
        if not self.current_command:
            return None

        command_parts = self.current_command.split()
        ctype = self.commandType()
        
        if ctype == C_ARITHMETIC:
            return command_parts[0]
        elif ctype != C_RETURN and len(command_parts) >= 2:
            return command_parts[1]
        else:
            return None

    def arg2(self):
        """
        Returns the second argument of the current command (if any).
        Should be called only if the current command is C_PUSH, C_POP, C_FUNCTION, or C_CALL.
        """
        if not self.current_command:
            return None

        command_parts = self.current_command.split()
        ctype = self.commandType()

        if ctype in (C_PUSH, C_POP, C_FUNCTION, C_CALL) and len(command_parts) >= 3:
            try:
                return int(command_parts[2])
            except ValueError:
                return None
        return None