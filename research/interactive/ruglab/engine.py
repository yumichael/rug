"""Exact evaluation, with bounded reuse of immutable basic stages."""

import ast
import json
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

from .operations import combine, steps
from .sampling import coordinates
from .specs import resolve


@dataclass
class Result:
    values: np.ndarray
    modulus: int | None
    spec: dict
    stages: dict = field(default_factory=dict)
    colors: str = "gray"

    def normalized(self, anchored=False):
        a = self.values
        modulus = self.modulus
        if modulus:
            a = (a - int(a.flat[0])) % modulus if anchored else a % modulus
            return np.asarray(np.frompyfunc(lambda x: float(int(x) / modulus), 1, 1)(a), dtype=float)
        if anchored:
            raise ValueError("Anchoring requires a declared modulus")
        return np.asarray(a, dtype=float)


@lru_cache(maxsize=8)
def _basic(key):
    s = json.loads(key)
    a, b = coordinates(s["shape"], s["sampling"], s["origin"], checkerboard_axis=s["checkerboard_axis"])
    width = (s["K"] - 1).bit_length()
    A = steps(a, s["pre"], modulus=s["K"], width=width)
    B = steps(b, s["pre"], modulus=s["K"], width=width)
    names = s["combine"] if isinstance(s["combine"], list) else [s["combine"]]
    stages = {"A": A, "B": B}
    for i, name in enumerate(names):
        stages[f"z{i}"] = combine(name, A, B)
    for value in stages.values():
        value.flags.writeable = False
    return stages


def evaluate(spec):
    s = resolve(spec)
    base = {k: s[k] for k in ("shape", "origin", "sampling", "K", "pre", "combine")}
    base["checkerboard_axis"] = s.get("checkerboard_axis", "horizontal")
    stages = _basic(json.dumps(base, sort_keys=True))
    z = stages["z0"]
    if "expression" in s:
        if any(
            isinstance(node, ast.Div) or (isinstance(node, ast.Constant) and isinstance(node.value, float))
            for node in ast.walk(ast.parse(s["expression"], mode="eval"))
        ):
            raise ValueError(
                "Native expressions use integer arithmetic; use DSL display transforms for fractional values"
            )
        from .dsl import expression

        z = expression(s["expression"], {**stages, "z": z}, modulus=s["M"])
    out = steps(z, s["post"], modulus=s["M"], width=(s["M"] - 1).bit_length())
    out = np.broadcast_to(np.asarray(out, dtype=object), tuple(s["shape"]))
    return Result(out, s["M"], s, dict(stages), s.get("color", "gray"))


def clear_cache():
    _basic.cache_clear()
