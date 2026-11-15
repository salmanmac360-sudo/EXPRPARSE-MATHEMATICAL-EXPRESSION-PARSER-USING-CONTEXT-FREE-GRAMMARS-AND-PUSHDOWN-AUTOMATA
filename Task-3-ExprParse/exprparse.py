
"""ExprParse: Recursive-descent parser for arithmetic expressions.

Grammar:
    E -> T ((+ | -) T)*
    T -> F ((* | /) F)*
    F -> number | (E)

Python 3; no third-party dependencies.
"""

from fractions import Fraction


class SyntaxErr(Exception):
    pass


def tokenize(source):
    tokens, i = [], 0

    while i < len(source):
        char = source[i]

        if char.isspace():
            i += 1

        elif char.isdigit() or char == ".":
            j = i
            while j < len(source) and (
                source[j].isdigit() or source[j] == "."
            ):
                j += 1

            number = source[i:j]

            if number.count(".") > 1 or number == ".":
                raise SyntaxErr("Invalid numeric literal")

            tokens.append(("num", number))
            i = j

        elif char in "+-*/()":
            tokens.append((char, char))
            i += 1

        else:
            raise SyntaxErr(f"Illegal character {char!r}")

    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens + [("$", "$")]
        self.index = 0
        self.depth = 0
        self.max_depth = 0

    def peek(self):
        return self.tokens[self.index][0]

    def eat(self, expected):
        if self.peek() != expected:
            raise SyntaxErr(
                f"Expected {expected}, found {self.peek()}"
            )

        value = self.tokens[self.index][1]
        self.index += 1
        return value

    def expression(self):
        node = self.term()

        while self.peek() in ("+", "-"):
            op = self.eat(self.peek())
            node = (op, node, self.term())

        return node

    def term(self):
        node = self.factor()

        while self.peek() in ("*", "/"):
            op = self.eat(self.peek())
            node = (op, node, self.factor())

        return node

    def factor(self):
        if self.peek() == "num":
            return ("num", self.eat("num"))

        if self.peek() == "(":
            self.eat("(")
            self.depth += 1
            self.max_depth = max(self.max_depth, self.depth)

            node = self.expression()
            self.eat(")")

            self.depth -= 1
            return node

        raise SyntaxErr(f"Unexpected token {self.peek()}")


def parse(source):
    parser = Parser(tokenize(source))
    tree = parser.expression()
    parser.eat("$")
    return tree, parser.max_depth


def evaluate(node):
    if node[0] == "num":
        return Fraction(node[1])

    left = evaluate(node[1])
    right = evaluate(node[2])

    if node[0] == "+":
        return left + right
    if node[0] == "-":
        return left - right
    if node[0] == "*":
        return left * right

    if right == 0:
        raise ZeroDivisionError("division by zero")

    return left / right


def calculate(source):
    try:
        tree, depth = parse(source)
    except SyntaxErr:
        return "syntax-error", None, None

    try:
        return "ok", evaluate(tree), depth
    except ZeroDivisionError:
        return "div-zero", None, depth


def main():
    examples = [
        "2+3*4",
        "(2+3)*4",
        "2+3*(4-1)",
        "2+",
        "3/(1-1)"
    ]

    for expression in examples:
        status, value, depth = calculate(expression)

        print(
            f"{expression!r}: {status}; "
            f"value={value}; maximum nesting={depth}"
        )


if __name__ == "__main__":
    main()
