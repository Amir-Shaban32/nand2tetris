import re
from typing import List, Tuple

class JackTokenizer:
    """
    Simple Jack Tokenizer: turns Jack source into (type, value) pairs
    """

    token_specification = [
        ("keyword", r"\b(class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)\b"),
        ("symbol", r"[{}()\[\].,;+\-*/&|<>=~]"),
        ("integerConstant", r"\d+"),
        ("stringConstant", r"\".*?\""),
        ("identifier", r"[A-Za-z_]\w*"),
        ("skip", r"\s+|//.*|/\*.*?\*/"),
    ]

    def __init__(self, source: str):
        self.tokens: List[Tuple[str, str]] = self.tokenize(source)
        self.current = 0

    def tokenize(self, text: str) -> List[Tuple[str, str]]:
        pattern = "|".join(f"(?P<{name}>{regex})" for name, regex in self.token_specification)
        regex = re.compile(pattern, re.DOTALL)
        tokens = []
        for match in regex.finditer(text):
            kind = match.lastgroup
            value = match.group()
            if kind == "skip":
                continue
            tokens.append((kind, value))
        return tokens

    def has_more_tokens(self) -> bool:
        return self.current < len(self.tokens)

    def advance(self) -> Tuple[str, str]:
        tok = self.tokens[self.current]
        self.current += 1
        return tok

    def peek(self) -> Tuple[str, str]:
        if self.has_more_tokens():
            return self.tokens[self.current]
        return ("", "")
