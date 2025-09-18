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
        self.current_command = ""  

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
        if self.hasMoreLines():  
            self.current_command = self.lines[self.idx]
            self.idx += 1

    def commandType(self):
        """
        Returns the type of the current VM command.
        """
        if not hasattr(self, 'current_command') or not self.current_command:  
            return None
            
        command_parts = self.current_command.split()  
        if not command_parts:  
            return None
            
        first_word = command_parts[0]
        
        if first_word == "push":
            return C_PUSH
        elif first_word == "pop":
            return C_POP
        else:
            return C_ARITHMETIC

    def arg1(self):
        """
        Returns the first argument of the current command.
        For arithmetic commands, returns the command itself.
        Should not be called if the current command is C_RETURN.
        """
        if not hasattr(self, 'current_command') or not self.current_command:  
            return None
            
        command_parts = self.current_command.split()
        if not command_parts:  
            return None
            
        if self.commandType() == C_ARITHMETIC:
            return command_parts[0]
        else:
            if len(command_parts) >= 2:  
                return command_parts[1]
            else:
                return None  

    def arg2(self):
        """
        Returns the second argument of the current command (if any).
        Should be called only if the current command is C_PUSH, C_POP, C_FUNCTION, or C_CALL.
        """
        if not hasattr(self, 'current_command') or not self.current_command:  
            return None
            
        command_parts = self.current_command.split()
        
        if self.commandType() != C_ARITHMETIC:
            if len(command_parts) >= 3:  
                try:
                    return int(command_parts[2])
                except ValueError:  
                    return None
            else:
                return None  
        else:
            return None