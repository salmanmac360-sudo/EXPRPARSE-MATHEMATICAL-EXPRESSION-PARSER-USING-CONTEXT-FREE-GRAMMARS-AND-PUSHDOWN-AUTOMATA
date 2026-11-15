
"""Fixed and generated tests for ExprParse."""

import random
import ast
from fractions import Fraction
from exprparse import calculate


def fixed_tests():
    cases = [
        ("2+3*4", "ok", Fraction(14)),
        ("(2+3)*4", "ok", Fraction(20)),
        ("18/3+2", "ok", Fraction(8)),
        ("2*(3+4)", "ok", Fraction(14)),
        ("10-3-2", "ok", Fraction(5)),
        ("((2+3)*4)", "ok", Fraction(20)),
        ("7/2", "ok", Fraction(7, 2)),
        ("2+3*(4-1)", "ok", Fraction(11)),
        ("2+", "syntax-error", None),
        ("+2", "syntax-error", None),
        ("(2+3", "syntax-error", None),
        ("2**3", "syntax-error", None),
        ("2+*3", "syntax-error", None),
        ("()", "syntax-error", None),
        ("2 3", "syntax-error", None),
        ("3/(1-1)", "div-zero", None)
    ]

    failures = []

    for source, expected_status, expected_value in cases:
        status, value, _ = calculate(source)

        if status != expected_status or (
            expected_value is not None and value != expected_value
        ):
            failures.append(source)

    print(
        f"Fixed tests: {len(cases) - len(failures)}/"
        f"{len(cases)} passed"
    )

    return not failures


def generated_value_tests():
    random.seed(2026)

    def expression(depth=0):
        if depth > 3 or random.random() < 0.3:
            return str(random.randint(0, 99))

        if random.random() < 0.25:
            return "(" + expression(depth + 1) + ")"

        return (
            expression(depth + 1)
            + random.choice("+-*/")
            + expression(depth + 1)
        )

    def reference_value(node):
        if isinstance(node, ast.Expression):
            return reference_value(node.body)

        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return Fraction(node.value)

        if isinstance(node, ast.BinOp):
            left = reference_value(node.left)
            right = reference_value(node.right)

            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise ZeroDivisionError
                return left / right

        raise ValueError("Unsupported generated expression")

    matched = 0

    for _ in range(1500):
        source = expression()
        status, value, _ = calculate(source)

        try:
            reference = reference_value(
                ast.parse(source, mode="eval")
            )
            expected_status = "ok"

        except ZeroDivisionError:
            reference = None
            expected_status = "div-zero"

        if status == expected_status and (
            reference is None or value == reference
        ):
            matched += 1

    print(
        f"Generated arithmetic checks: {matched}/1500 matched"
    )

    return matched == 1500


if __name__ == "__main__":
    result1 = fixed_tests()
    result2 = generated_value_tests()

    raise SystemExit(0 if result1 and result2 else 1)
