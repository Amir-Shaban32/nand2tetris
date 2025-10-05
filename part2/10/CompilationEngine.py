from JackTokenizer import JackTokenizer

class CompilationEngine:
    """
    Minimal CompilationEngine:
    Parses class, simple functions, let, and return statements.
    """

    def __init__(self, tokenizer: JackTokenizer):
        self.tk = tokenizer
        self.output = []

    def eat(self, expected_type=None, expected_value=None):
        kind, val = self.tk.advance()
        if expected_type and kind != expected_type:
            raise ValueError(f"Expected type {expected_type}, got {kind}")
        if expected_value and val != expected_value:
            raise ValueError(f"Expected value {expected_value}, got {val}")
        self.output.append(f"<{kind}> {val} </{kind}>")

    def compile_class(self):
        self.output.append("<class>")
        self.eat("keyword", "class")
        self.eat("identifier")  # class name
        self.eat("symbol", "{")

        while self.tk.has_more_tokens():
            kind, val = self.tk.peek()
            if val == "}":
                break
            elif val == "function":
                self.compile_subroutine()
            else:
                self.tk.advance()

        self.eat("symbol", "}")
        self.output.append("</class>")

    def compile_subroutine(self):
        self.output.append("<subroutineDec>")
        self.eat("keyword", "function")
        self.eat()  # return type
        self.eat("identifier")  # function name
        self.eat("symbol", "(")
        self.eat("symbol", ")")
        self.eat("symbol", "{")

        while self.tk.has_more_tokens():
            kind, val = self.tk.peek()
            if val == "let":
                self.compile_let()
            elif val == "return":
                self.eat("keyword", "return")
                self.eat("symbol", ";")
            elif val == "}":
                break
            else:
                self.tk.advance()

        self.eat("symbol", "}")
        self.output.append("</subroutineDec>")

    def compile_let(self):
        self.output.append("<letStatement>")
        self.eat("keyword", "let")
        self.eat("identifier")
        self.eat("symbol", "=")
        self.eat("integerConstant")
        self.eat("symbol", ";")
        self.output.append("</letStatement>")

    def get_output(self) -> str:
        return "\n".join(self.output)
