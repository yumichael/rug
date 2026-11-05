"""The five-section symbols DSL, evaluated through an explicit AST registry."""

import ast
import math
import operator

import numpy as np

from .engine import Result
from .operations import combine, operation
from .sampling import legacy_sample

BIN = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Mod: operator.mod,
    ast.BitXor: operator.xor,
    ast.BitAnd: operator.and_,
    ast.BitOr: operator.or_,
    ast.LShift: operator.lshift,
    ast.RShift: operator.rshift,
    ast.FloorDiv: operator.floordiv,
    ast.Div: operator.truediv,
}


def expression(text, variables, modulus=None):
    tree = ast.parse(text, mode="eval")
    if any(
        isinstance(node, ast.Call)
        or (
            isinstance(node, ast.BinOp)
            and not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Pow))
        )
        for node in ast.walk(tree)
    ):
        modulus = None

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.Name) and node.id in variables:
            return variables[node.id]
        if isinstance(node, (ast.List, ast.Tuple)):
            return [visit(v) for v in node.elts]
        if isinstance(node, ast.UnaryOp):
            f = {ast.USub: operator.neg, ast.UAdd: operator.pos, ast.Invert: operator.invert}.get(
                type(node.op)
            )
            if f:
                return f(visit(node.operand))
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Mod):
                divisor = visit(node.right)
                return expression(ast.unparse(node.left), variables, modulus=int(divisor)) % divisor
            a, b = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow):
                if np.ndim(b):
                    raise ValueError("The exponent must be scalar")
                v = operation(np.asarray(a, dtype=object), "pow", b, modulus=modulus)
            elif type(node.op) in BIN:
                v = BIN[type(node.op)](a, b)
            else:
                raise ValueError("Unsupported expression operator")
            return v % modulus if modulus else v
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
            args = [visit(v) for v in node.args]
            if node.func.id == "abs":
                return abs(args[0])
            if node.func.id in (
                "and",
                "or",
                "xor",
                "add",
                "mult",
                "clmul",
                "absdiff",
                "gcd",
                "min",
                "max",
            ):
                return combine(node.func.id, *args)
        raise ValueError("Unsupported DSL expression: " + ast.dump(node))

    return visit(tree.body)


def channel(text):
    sections = text.split(";")
    if len(sections) != 5:
        raise ValueError("DSL needs n;pre;combine;post;color")
    size, pre, comb, post, color = sections
    n = int(expression(size, {}))
    if not 1 <= n <= 8192:
        raise ValueError("DSL size must be between 1 and 8192")
    s = np.arange(n, dtype=object)
    variables = {"n": n, "s": s, "l": None}

    def apply(z, part, variable, later):
        variables[variable] = z
        try:
            call = ast.parse(part, mode="eval").body
        except SyntaxError:
            call = None
        name = (
            call.id
            if isinstance(call, ast.Name)
            else call.func.id
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
            else None
        )
        args = (
            []
            if isinstance(call, ast.Name)
            else [expression(ast.unparse(a), variables) for a in call.args]
            if name
            else []
        )
        if name in ("diag0", "diag1", "diag1m", "diag1m_1", "ddiag0", "ddiag1", "skip"):
            return legacy_sample(z, name)
        if name in ("map01", "map01cyclic"):
            if not variables["l"]:
                raise ValueError("map01 requires an earlier %modulus")
            values = Result(z, variables["l"], {}).normalized()
            return (
                values
                if name == "map01"
                else np.nextafter(np.sin(values * math.tau) * 0.5 + 0.5, 0.0)
            )
        if name == "binary":
            return (z >= args[0]) * np.nextafter(1.0, 0.0)
        if name == "discrete":
            if args[0] < 2:
                raise ValueError("discrete needs at least two levels")
            return np.floor(z * np.nextafter(float(args[0]), 0)) / (args[0] - 1)
        if name == "power_mod":
            return operation(z, "pow", args[0], modulus=int(args[1]))
        if name in ("gray", "bitrev", "rotl", "inv"):
            return operation(z, name, args[0] if args else 1, width=(n - 1).bit_length())
        if part[0] in "*%&|^/+-" or part.startswith("**"):
            source = variable + part
        elif part[-1] in "*%&|^/+-":
            source = part + variable
        else:
            source = part
        future = None
        # Fuse only polynomial arithmetic up to an explicit modulo.
        for step in [part] + later:
            if step.startswith("%"):
                future = int(expression(step[1:], variables))
                break
            probe = (variable + step) if step[0] in "*+-" else step
            try:
                tree = ast.parse(probe, mode="eval")
            except SyntaxError:
                break
            if any(
                isinstance(v, ast.BinOp)
                and not isinstance(v.op, (ast.Add, ast.Sub, ast.Mult, ast.Pow))
                or isinstance(v, ast.Call)
                for v in ast.walk(tree)
            ):
                break
        value = expression(source, variables, modulus=future)
        if part.startswith("%"):
            variables["l"] = int(expression(part[1:], variables))
        return value

    for source, var in ((pre, "s"), (post, "z")):
        if var == "z":
            x, y = np.meshgrid(s, s, indexing="ij")
            variables.update(x=x, y=y)
            z = expression("x" + comb + "y", variables)
        items = [v for v in source.split(":") if v]
        for i, item in enumerate(items):
            if var == "s":
                s = apply(s, item, var, items[i + 1 :])
            else:
                z = apply(z, item, var, items[i + 1 :])
    floating = np.asarray(z).dtype.kind == "f"
    return Result(np.asarray(z), None if floating else variables["l"], {"dsl": text}, colors=color)


def render(specs):
    from .plotting import colorize

    results = [channel(s) for s in specs]
    if len(results) == 1:
        return colorize(results[0])
    if len(results) != 3:
        raise ValueError("Use one colormap channel or three RGB/HSV/HSL channels")
    space = "".join(r.colors for r in results).lower()
    values = np.stack([r.normalized() for r in results], axis=-1)
    from .plotting import convert_color

    return convert_color(values, space)
