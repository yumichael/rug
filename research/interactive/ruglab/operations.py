"""Exact integer operations extracted and adapted from the symbols experiments."""

import math

import numpy as np


def elementwise(function, *arrays):
    return np.frompyfunc(function, len(arrays), 1)(*arrays)


def clmul(a, b):
    a, b = int(a), int(b)
    if min(a, b) < 0:
        raise ValueError("clmul requires nonnegative operands")
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result


def combine(name, a, b):
    if isinstance(name, dict):
        if name.get("name") != "clmul_low" or int(name.get("width", 0)) < 1:
            raise ValueError("Width-specific combiner requires clmul_low and width>=1")
        mask = (1 << int(name["width"])) - 1
        return elementwise(lambda x, y: clmul(x & mask, y & mask) & mask, a, b)
    functions = {
        "and": lambda x, y: x & y,
        "or": lambda x, y: x | y,
        "xor": lambda x, y: x ^ y,
        "add": lambda x, y: x + y,
        "mult": lambda x, y: x * y,
        "absdiff": lambda x, y: abs(x - y),
        "clmul": clmul,
        "gcd": math.gcd,
        "min": min,
        "max": max,
        "subtract": lambda x, y: x - y,
        "xor0": lambda x, y: (x ^ y) if x and y else 0,
    }
    if name not in functions:
        raise ValueError("Unknown combiner: " + name)
    return elementwise(functions[name], a, b)


def operation(values, name, arg=0, *, width=None, modulus=None):
    if name == "poly":
        out = np.zeros_like(values, dtype=object)
        for coefficient in reversed(arg):
            out = out * values + int(coefficient)
            if modulus:
                out %= modulus
        return out
    if name == "self" and isinstance(arg, str):
        arg = {"identity": 0, "negative": 1}[arg]
    if isinstance(arg, float) and not arg.is_integer():
        raise ValueError("Integer operations require integer arguments")
    arg = int(arg)
    if name == "pow":
        if arg < 0:
            raise ValueError("Negative powers are not integer operations")
        return elementwise(
            lambda x: pow(int(x), arg, modulus) if modulus else pow(int(x), arg), values
        )
    if name == "expo":
        return elementwise(
            lambda x: pow(arg, int(x), modulus) if modulus else pow(arg, int(x)), values
        )
    if name == "add":
        return values + arg
    if name == "mult":
        return values * arg
    if name == "mod":
        return values % arg
    if name == "xor":
        return values ^ arg
    if name == "xor0":
        return elementwise(lambda x: (x ^ arg) if x and arg else 0, values)
    if name == "binary":
        if width is None:
            raise ValueError("binary requires a bit width")
        return (values >= arg) * ((1 << width) - 1)
    if name == "self":
        if arg not in (0, 1):
            raise ValueError("self accepts identity=0 or negative=1")
        return -values if arg else values.copy()
    if name in ("gray", "bitrev", "rotl", "inv"):
        if width is None or width < 1:
            raise ValueError(name + " requires a positive bit width")
        mask = (1 << width) - 1

        def f(x):
            x = int(x) & mask
            if not arg:
                return x
            if name == "gray":
                return (x ^ (x >> arg)) & mask
            if name == "bitrev":
                return int(f"{x:0{width}b}"[::-1], 2)
            if name == "rotl":
                k = arg % width
                return ((x << k) | (x >> (width - k))) & mask
            return pow(x, -1, 1 << width) if x & 1 else 0

        return elementwise(f, values)
    raise ValueError("Unknown operation: " + name)


def steps(values, instructions, *, modulus=None, width=None):
    # Reduction can pass through ordinary integer polynomial operations only.
    for i, item in enumerate(instructions):
        name, arg = item if not isinstance(item, dict) else (item["op"], item["value"])
        safe = all(
            (s[0] if not isinstance(s, dict) else s["op"]) in ("add", "mult", "pow", "poly", "self")
            for s in instructions[i:]
        )
        future = modulus if safe else None
        if name == "pow" and future is None:
            for following in instructions[i + 1 :]:
                op, val = (
                    following
                    if not isinstance(following, dict)
                    else (following["op"], following["value"])
                )
                if op == "mod":
                    future = int(val)
                    break
                if op not in ("add", "mult", "pow", "poly", "self"):
                    break
        values = operation(values, name, arg, width=width, modulus=future)
        if future:
            values %= future
    return values % modulus if modulus else values
