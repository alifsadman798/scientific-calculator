from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sympy as sp
import statistics
import re

from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)

app = Flask(__name__)
CORS(app)

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor
)

ALLOWED_NAMES = {
    "x", "y", "z",
    "pi", "e", "E",
    "i", "I",
    "sin", "cos", "tan", "cot",
    "asin", "acos", "atan", "acot",
    "log", "ln", "exp",
    "sqrt", "factorial",
    "abs", "floor", "ceil",
    "oo"
}


def prepare_expression(expr):
    expr = str(expr).strip()

    expr = expr.replace("sin⁻¹", "asin")
    expr = expr.replace("cos⁻¹", "acos")
    expr = expr.replace("tan⁻¹", "atan")
    expr = expr.replace("cot⁻¹", "acot")

    expr = expr.replace("×", "*")
    expr = expr.replace("÷", "/")
    expr = expr.replace("−", "-")
    expr = expr.replace("π", "pi")
    expr = expr.replace("√", "sqrt")
    expr = expr.replace("∞", "oo")

    expr = re.sub(r"sin\s*\^\s*-1", "asin", expr)
    expr = re.sub(r"cos\s*\^\s*-1", "acos", expr)
    expr = re.sub(r"tan\s*\^\s*-1", "atan", expr)
    expr = re.sub(r"cot\s*\^\s*-1", "acot", expr)

    expr = re.sub(r"(\d+(?:\.\d+)?)%", r"(\1/100)", expr)

    for _ in range(5):
        expr = re.sub(
            r"(\([^()]+\))!",
            r"factorial(\1)",
            expr
        )

    expr = re.sub(
        r"(\d+(?:\.\d+)?)!",
        r"factorial(\1)",
        expr
    )

    expr = re.sub(
        r"\b([A-Za-z_][A-Za-z0-9_]*)!",
        r"factorial(\1)",
        expr
    )

    return expr


def validate_expression(expr):
    names = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", expr)

    for name in names:
        if name not in ALLOWED_NAMES:
            raise ValueError(f"Unknown name: {name}")


CURRENT_ANGLE_MODE = "DEG"


def set_angle_mode(mode):
    global CURRENT_ANGLE_MODE

    if mode in ("DEG", "RAD"):
        CURRENT_ANGLE_MODE = mode


def angle_sin(value):
    if CURRENT_ANGLE_MODE == "DEG":
        return sp.sin(sp.pi * value / 180)
    return sp.sin(value)


def angle_cos(value):
    if CURRENT_ANGLE_MODE == "DEG":
        return sp.cos(sp.pi * value / 180)
    return sp.cos(value)


def angle_tan(value):
    if CURRENT_ANGLE_MODE == "DEG":
        return sp.tan(sp.pi * value / 180)
    return sp.tan(value)


def angle_cot(value):
    if CURRENT_ANGLE_MODE == "DEG":
        return sp.cot(sp.pi * value / 180)
    return sp.cot(value)


def angle_asin(value):
    result = sp.asin(value)

    if CURRENT_ANGLE_MODE == "DEG":
        return result * 180 / sp.pi

    return result


def angle_acos(value):
    result = sp.acos(value)

    if CURRENT_ANGLE_MODE == "DEG":
        return result * 180 / sp.pi

    return result


def angle_atan(value):
    result = sp.atan(value)

    if CURRENT_ANGLE_MODE == "DEG":
        return result * 180 / sp.pi

    return result


def angle_acot(value):
    result = sp.acot(value)

    if CURRENT_ANGLE_MODE == "DEG":
        return result * 180 / sp.pi

    return result


def safe_locals():
    return {
        "x": sp.Symbol("x"),
        "y": sp.Symbol("y"),
        "z": sp.Symbol("z"),

        "pi": sp.pi,
        "e": sp.E,
        "E": sp.E,

        "i": sp.I,
        "I": sp.I,

        "sin": angle_sin,
        "cos": angle_cos,
        "tan": angle_tan,
        "cot": angle_cot,

        "asin": angle_asin,
        "acos": angle_acos,
        "atan": angle_atan,
        "acot": angle_acot,

        "log": lambda value: sp.log(value, 10),
        "ln": sp.log,
        "exp": sp.exp,

        "sqrt": sp.sqrt,
        "factorial": sp.factorial,

        "abs": sp.Abs,
        "floor": sp.floor,
        "ceil": sp.ceiling,

        "oo": sp.oo
    }


def parse_calculator_expression(expr):
    expr = prepare_expression(expr)

    if not expr:
        raise ValueError("Expression is empty.")

    validate_expression(expr)

    return parse_expr(
        expr,
        local_dict=safe_locals(),
        transformations=TRANSFORMATIONS,
        evaluate=True
    )


SUPERSCRIPTS = str.maketrans(
    "0123456789+-()",
    "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾"
)


def superscript(value):
    return str(value).translate(SUPERSCRIPTS)


def format_number(value):
    try:
        if isinstance(value, sp.Integer):
            return str(value)

        if isinstance(value, sp.Rational):
            if value.q == 1:
                return str(value.p)
            return f"{value.p}/{value.q}"

        if isinstance(value, sp.Float):
            number = float(value)

            if number.is_integer():
                return str(int(number))

            return f"{number:.12f}".rstrip("0").rstrip(".")

        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))

            return f"{value:.12f}".rstrip("0").rstrip(".")

    except Exception:
        pass

    return str(value)


def format_math_expression(expr):
    if expr is None:
        return ""

    if isinstance(expr, (list, tuple)):
        return "[" + ", ".join(
            format_math_expression(item) for item in expr
        ) + "]"

    if isinstance(expr, dict):
        return str(expr)

    if isinstance(expr, sp.MatrixBase):
        rows = []

        for row in expr.tolist():
            rows.append(
                ", ".join(format_math_expression(item) for item in row)
            )

        return "; ".join(rows)

    if getattr(expr, "is_number", False):
        try:
            if expr.is_real:
                return format_number(expr)

            real_part = sp.re(expr)
            imag_part = sp.im(expr)

            real_text = format_number(real_part)
            imag_text = format_number(abs(imag_part))

            if imag_part == 0:
                return real_text

            if real_part == 0:
                if imag_part == 1:
                    return "i"
                if imag_part == -1:
                    return "-i"
                return f"{imag_text}i" if imag_part > 0 else f"-{imag_text}i"

            sign = "+" if imag_part > 0 else "-"

            if imag_part == 1 or imag_part == -1:
                imag_text = "i"
            else:
                imag_text = f"{imag_text}i"

            return f"{real_text} {sign} {imag_text}"

        except Exception:
            pass

    text = sp.sstr(expr)

    text = text.replace("pi", "π")
    text = text.replace("oo", "∞")
    text = text.replace("E", "e")
    text = text.replace("I", "i")

    text = text.replace("asin", "sin⁻¹")
    text = text.replace("acos", "cos⁻¹")
    text = text.replace("atan", "tan⁻¹")
    text = text.replace("acot", "cot⁻¹")

    text = re.sub(
        r"sqrt\(([^()]+)\)",
        r"√(\1)",
        text
    )

    def replace_power(match):
        base = match.group(1)
        power = match.group(2)
        return base + superscript(power)

    text = re.sub(
        r"([A-Za-z0-9π∞.)]+)\*\*\((-?\d+)\)",
        replace_power,
        text
    )

    text = re.sub(
        r"([A-Za-z0-9π∞.)]+)\*\*(-?[\d.]+)",
        replace_power,
        text
    )

    text = text.replace("**", "·")
    text = text.replace("*", "·")

    return text


def format_result(result):
    return format_math_expression(result)


def friendly_error(error):
    message = str(error)

    if (
        "division by zero" in message.lower()
        or "complex infinity" in message.lower()
        or "zoo" in message.lower()
    ):
        return "Can't divide by zero."

    if "singular matrix" in message.lower():
        return "This matrix has no inverse."

    if (
        "parse" in message.lower()
        or "syntax" in message.lower()
        or "invalid" in message.lower()
    ):
        return "Invalid expression."

    if "unknown name" in message.lower():
        return message

    return message


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/angle", methods=["POST"])
def angle():
    data = request.get_json() or {}

    mode = data.get("angle_mode", "DEG")
    set_angle_mode(mode)

    return jsonify({
        "success": True,
        "angle_mode": CURRENT_ANGLE_MODE
    })


@app.route("/api/normal", methods=["POST"])
def normal_calculation():
    try:
        data = request.get_json() or {}

        expression = data.get("expression", "")
        angle_mode = data.get("angle_mode", "DEG")

        set_angle_mode(angle_mode)

        result = parse_calculator_expression(expression)

        return jsonify({
            "result": format_result(result)
        })

    except Exception as error:
        return jsonify({
            "error": friendly_error(error)
        }), 400


@app.route("/api/complex", methods=["POST"])
def complex_calculation():
    try:
        data = request.get_json() or {}

        operation = data.get("operation", "")
        expression = data.get("expression", "")
        variable = data.get("variable", "x")

        order = int(data.get("order", 1))

        tool = data.get("tool", "simplify")
        matrix_operation = data.get(
            "matrix_operation",
            "determinant"
        )
        statistics_operation = data.get(
            "statistics_operation",
            "mean"
        )

        angle_mode = data.get("angle_mode", "DEG")

        set_angle_mode(angle_mode)

        if operation == "derivative":
            if variable not in ("x", "y", "z"):
                raise ValueError("Invalid variable.")

            if order < 1:
                raise ValueError("Order must be at least 1.")

            expr = parse_calculator_expression(expression)
            symbol = sp.Symbol(variable)

            result = sp.diff(expr, symbol, order)

            return jsonify({
                "result": format_result(result)
            })

        elif operation == "integral":
            if variable not in ("x", "y", "z"):
                raise ValueError("Invalid variable.")

            if order < 1:
                raise ValueError("Order must be at least 1.")

            expr = parse_calculator_expression(expression)
            symbol = sp.Symbol(variable)

            result = expr

            for _ in range(order):
                result = sp.integrate(result, symbol)

            return jsonify({
                "result": format_result(result)
            })

        elif operation == "solve":
            if "=" not in expression:
                raise ValueError(
                    "Please enter an equation using =."
                )

            if variable not in ("x", "y", "z"):
                raise ValueError("Invalid variable.")

            left, right = expression.split("=", 1)

            left_expr = parse_calculator_expression(left)
            right_expr = parse_calculator_expression(right)

            symbol = sp.Symbol(variable)

            equation = sp.Eq(left_expr, right_expr)

            solutions = sp.solve(equation, symbol)

            formatted = []

            for solution in solutions:
                formatted.append(
                    f"{variable} = {format_result(solution)}"
                )

            return jsonify({
                "result": formatted
            })

        elif operation == "algebra":
            expr = parse_calculator_expression(expression)

            if tool == "simplify":
                result = sp.simplify(expr)

            elif tool == "factor":
                result = sp.factor(expr)

            elif tool == "expand":
                result = sp.expand(expr)

            else:
                raise ValueError("Invalid algebra operation.")

            return jsonify({
                "result": format_result(result)
            })

        elif operation == "matrix":
            rows = expression.split(";")

            matrix_data = []

            for row in rows:
                if not row.strip():
                    continue

                values = row.split(",")

                matrix_data.append([
                    parse_calculator_expression(value.strip())
                    for value in values
                ])

            if not matrix_data:
                raise ValueError("Matrix is empty.")

            row_length = len(matrix_data[0])

            for row in matrix_data:
                if len(row) != row_length:
                    raise ValueError(
                        "All matrix rows must have the same length."
                    )

            matrix = sp.Matrix(matrix_data)

            if matrix_operation == "determinant":
                if matrix.rows != matrix.cols:
                    raise ValueError(
                        "Determinant requires a square matrix."
                    )

                result = matrix.det()

            elif matrix_operation == "inverse":
                if matrix.rows != matrix.cols:
                    raise ValueError(
                        "Inverse requires a square matrix."
                    )

                if matrix.det() == 0:
                    raise ValueError("Singular matrix.")

                result = matrix.inv()

            elif matrix_operation == "transpose":
                result = matrix.T

            else:
                raise ValueError("Invalid matrix operation.")

            return jsonify({
                "result": format_result(result)
            })

        elif operation == "statistics":
            values = [
                float(value.strip())
                for value in expression.split(",")
                if value.strip()
            ]

            if not values:
                raise ValueError("Please enter numbers.")

            if statistics_operation == "mean":
                result = statistics.mean(values)

            elif statistics_operation == "median":
                result = statistics.median(values)

            elif statistics_operation == "variance":
                if len(values) < 2:
                    raise ValueError(
                        "At least two values are required."
                    )

                result = statistics.variance(values)

            elif statistics_operation == "stdev":
                if len(values) < 2:
                    raise ValueError(
                        "At least two values are required."
                    )

                result = statistics.stdev(values)

            elif statistics_operation == "min":
                result = min(values)

            elif statistics_operation == "max":
                result = max(values)

            else:
                raise ValueError(
                    "Invalid statistics operation."
                )

            return jsonify({
                "result": format_result(result)
            })

        else:
            raise ValueError("Unknown operation.")

    except Exception as error:
        return jsonify({
            "error": friendly_error(error)
        }), 400


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )