#!/usr/bin/env python3
"""Exact checks for the November 4 report; Python standard library only."""

from __future__ import annotations

import importlib.util
import itertools
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKS: dict[str, int] = {}


def check(condition: bool, category: str) -> None:
    if not condition:
        raise AssertionError(category)
    CHECKS[category] = CHECKS.get(category, 0) + 1


def valuation(n: int) -> int | float:
    return (abs(n) & -abs(n)).bit_length() - 1 if n else math.inf


def clmul(a: int, b: int) -> int:
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result


COMBINERS = {
    "AND": lambda a, b: a & b,
    "OR": lambda a, b: a | b,
    "XOR": lambda a, b: a ^ b,
    "ADD": lambda a, b: a + b,
    "MULT": lambda a, b: a * b,
    "CLMUL": clmul,
    "ABSDIFF": lambda a, b: abs(a - b),
}


def source(i: int, j: int, method: int) -> tuple[int, int]:
    """Return the selected pair of operands before pre-processing."""
    if method == 1:
        return i, j
    if method in (2, 3):
        return i + j + method - 2, i - j
    ex, ey = divmod(method - 4, 2)
    return 2 * i + ex, 2 * j + ey


def basic_table(k: int, q: int, name: str, method: int,
                twist: tuple[int, ...] = ()) -> list[list[int]]:
    K = 1 << k
    pre = [pow(x, q, K) for x in range(K)]
    if twist:
        pre = [(t + 2 * t * (t - 1) * sum(a * t ** j for j, a in enumerate(twist))) % K
               for t in pre]
    operation = COMBINERS[name]
    result = []
    for i in range(K):
        row = []
        for j in range(K):
            a, b = source(i, j, method)
            row.append(operation(pre[a % K], pre[b % K]))
        result.append(row)
    return result


def edges(table: list[list[int]], h: int, axis: int) -> set[tuple[int, int]]:
    N = len(table)
    if axis == 0:
        return {(table[i][j], table[(i + h) % N][j])
                for i in range(N) for j in range(N)}
    return {(table[i][j], table[i][(j + h) % N])
            for i in range(N) for j in range(N)}


def axis_period(table: list[list[int]], axis: int) -> int:
    h = 1
    while h < len(table):
        if all(a == b for a, b in edges(table, h, axis)):
            return h
        h *= 2
    return h


def translation_basis(table, periods):
    """Lift the subgroup of a least-axis-period rectangle to a lattice basis."""
    width, height = periods
    for bit in range(width.bit_length() - 1):
        dx = 1 << bit
        order = width // dx
        if height % order:
            continue
        step = height // order
        for dy in range(step, height, 2 * step):
            if all(table[i][j] == table[(i + dx) % width][(j + dy) % height]
                   for i in range(width) for j in range(height)):
                return ((dx, dy), (0, height))
    return ((width, 0), (0, height))


def power_depth(a: int, b: int, p: int) -> int | float:
    if a == b:
        return math.inf
    if not a or not b:
        return p * valuation(a or b)
    ta, tb = valuation(a), valuation(b)
    if ta != tb:
        return p * min(ta, tb)
    a0, b0 = a >> int(ta), b >> int(tb)
    depth = p * ta + valuation(a0 - b0)
    if p % 2 == 0:
        depth += valuation(a0 + b0) + valuation(p) - 1
    return depth


def minimum_post_exponent(table: list[list[int]], periods: tuple[int, int],
                          p: int) -> int | None:
    lower, upper = 1, math.inf
    for axis, R in enumerate(periods):
        upper = min(upper, min(power_depth(a, b, p)
                              for a, b in edges(table, R, axis)))
        if R > 1:
            lower = max(lower, 1 + min(power_depth(a, b, p)
                                       for a, b in edges(table, R // 2, axis)))
    return int(lower) if lower <= upper and lower != math.inf else None


def polynomial_period_feasible(table: list[list[int]], R: int) -> bool:
    """Unbounded integer post-polynomials, including minimum-modulus policy."""
    parent = {x: x for row in table for x in row}
    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for axis in (0, 1):
        for a, b in edges(table, R, axis):
            parent[root(a)] = root(b)
    return all(any(root(a) != root(b) for a, b in edges(table, R // 2, axis))
               for axis in (0, 1))


def anchored(values: list[int] | tuple[int, ...], M: int) -> tuple[int, ...]:
    return tuple((x - values[0]) % M for x in values)


def shift_signature(values: list[int] | tuple[int, ...], M: int) -> tuple:
    values = anchored(values, M)
    divisor = math.gcd(M, *values)
    return M // divisor, tuple(x // divisor for x in values)


def order_signature(values: list[int] | tuple[int, ...], M: int) -> tuple[int, ...]:
    values = anchored(values, M)
    ranks = {value: rank for rank, value in enumerate(sorted(set(values)))}
    return tuple(ranks[x] for x in values)


def pre_period_formula(k: int, q: int) -> int:
    if k <= 0:
        return 1
    if q % 2:
        return 1 << k
    w = int(valuation(q))
    if k <= min(q, w + 2):
        return 2
    return 1 << max(2, k - w)


def pure_and_period(k: int, q: int) -> int:
    w = int(valuation(q))
    if q == 2:
        j = k - 1 if k >= 5 else None
    elif k <= q:
        j = None
    elif k <= q + w + 2:
        j = q
    else:
        j = k - 1
    return 1 if j is None else 1 << (j + 1 - w)


def sequence_period(values: list[int]) -> int:
    h = 1
    while h < len(values):
        if all(x == values[(i + h) % len(values)] for i, x in enumerate(values)):
            return h
        h *= 2
    return h


def load_xor_module():
    path = HERE.parent / "2026-11-02-xor-polynomial-period/xor_polynomial_period.py"
    spec = importlib.util.spec_from_file_location("xor_polynomial_period", path)
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def check_pre_families() -> None:
    for k in range(1, 10):
        K = 1 << k
        for q in range(1, 17):
            values = [pow(x, q, K) for x in range(K)]
            check(sequence_period(values) == pre_period_formula(k, q), "pre_period")
            if q % 2 == 0:
                w = int(valuation(q))
                even = values[::2]
                odd = values[1::2]
                even_period = pre_period_formula(k - q, q)
                odd_period = 1 if k <= w + 2 else 1 << (k - w - 1)
                check(sequence_period(even) == even_period, "parity_period")
                check(sequence_period(odd) == odd_period, "parity_period")
    rng = random.Random(20261104)
    for _ in range(200):
        k = rng.randrange(1, 10)
        K = 1 << k
        b, u = rng.randrange(K), 2 * rng.randrange(K) + 1
        coeffs = [rng.randrange(K) for _ in range(5)]
        def f(t):
            return (b + u * t + 2 * sum(a * t ** j for j, a in enumerate(coeffs))) % K
        for _ in range(25):
            s, t = rng.randrange(K), rng.randrange(K)
            check(min(k, valuation(f(s) - f(t))) == min(k, valuation(s - t)),
                  "pre_isometry")


def check_common_pre_moduli() -> list[dict]:
    records = []
    for q in (2, 4, 6):
        w = int(valuation(q))
        for R in (8, 16):
            r = R.bit_length() - 1
            for name in ("OR", "XOR", "ADD", "MULT", "CLMUL", "ABSDIFF"):
                k_min = max(r + w, q + 1) if name in ("MULT", "CLMUL") else r + w
                for twist in ((0,), (1,), (1, 2), (2, 3, 1)):
                    for k in range(1, k_min + 1):
                        table = basic_table(k, q, name, 3, twist)
                        periods = tuple(axis_period(table, a) for a in (0, 1))
                        check((min(periods) >= R) == (k == k_min), "common_pre_minimum")
                    predicted = 1 << (k_min - w)
                    check(periods == (predicted, predicted), "common_pre_period")
                records.append({"pre_power": q, "R": R, "combiner": name,
                                "minimum_K": 1 << k_min, "method": 3,
                                "basic_axis_periods": [predicted, predicted]})
    for q, R, name in itertools.product((2, 4, 6, 8, 10), (8, 16, 32), COMBINERS):
        K = R * (q & -q)
        k = K.bit_length() - 1
        for twist in ((0,), (1,), (1, 2), (2, 3, 1)):
            for trial in (k - 1, k):
                table = basic_table(trial, q, name, 1, twist)
                periods = tuple(axis_period(table, axis) for axis in (0, 1))
                check((min(periods) >= R) == (trial == k), "operand_grid_common_pre_minimum")
            check(periods == (R, R), "operand_grid_common_pre_period")
        records.append({"pre_power": q, "R": R, "combiner": name, "method": 1,
                        "minimum_K": K, "basic_axis_periods": [R, R]})
    for q, R in itertools.product((2, 4, 6), (8, 16)):
        k_min = 1
        while pure_and_period(k_min, q) < R:
            k_min += 1
        for twist in ((0,), (1,), (1, 2), (2, 3, 1)):
            table = basic_table(k_min, q, "AND", 3, twist)
            check(min(axis_period(table, a) for a in (0, 1)) >= R,
                  "common_AND_pre_bound")
        records.append({"pre_power": q, "R": R, "combiner": "AND", "method": 3,
                        "minimum_common_K": 1 << k_min,
                        "individual_minima_can_be_smaller": True})
    return records


def basic_catalogue() -> dict:
    records = []
    for k in (4, 5, 6, 7):
        for q in (2, 4, 6, 8, 10):
            for name in COMBINERS:
                for method in range(1, 8):
                    table = basic_table(k, q, name, method)
                    periods = tuple(axis_period(table, a) for a in (0, 1))
                    if name == "AND" and method == 3:
                        expected = pure_and_period(k, q)
                        check(periods == (expected, expected), "pure_AND_closed_period")
                    n = (1 << k) ** 2
                    zero = sum(x == 0 for row in table for x in row)
                    powers = {str(p): minimum_post_exponent(table, periods, p)
                              for p in (1, 2, 3, 4)}
                    records.append({"K": 1 << k, "pre_power": q, "combiner": name,
                                    "method": method, "axis_periods": periods,
                                    "translation_basis": translation_basis(table, periods),
                                    "zero_fraction": [zero, n],
                                    "minimum_post_m_at_native_period": powers})
                    records[-1]["requested_periods"] = {}
                    for R in (16, 32):
                        if min(periods) >= R:
                            records[-1]["requested_periods"][str(R)] = {
                                "polynomial_feasible": polynomial_period_feasible(table, R),
                                "power_minimum_m": {
                                    str(p): minimum_post_exponent(table, (R, R), p)
                                    for p in (1, 2, 3, 4)},
                            }
                    for p, m in powers.items():
                        if m is None:
                            continue
                        M = 1 << m
                        output = [[pow(x, int(p), M) for x in row] for row in table]
                        check(tuple(axis_period(output, a) for a in (0, 1)) == periods,
                              "post_minimum_period")
                        if m > 1 and periods != (1, 1):
                            output = [[x % (M // 2) for x in row] for row in output]
                            check(tuple(axis_period(output, a) for a in (0, 1)) != periods,
                                  "post_minimum_minimality")
                    if q >= k:
                        # On cells with an even operand, that branch is zero.
                        for i, j in itertools.product(range(1 << k), repeat=2):
                            a, b = source(i, j, method)
                            if (a & b & 1) == 0:
                                expected = 0 if name in ("AND", "MULT", "CLMUL") else pow(a if a & 1 else b, q, 1 << k)
                                check(table[i][j] == expected, "saturated_even_operand")
    minima = []
    for R, q, name, method in itertools.product((16, 32), (2, 4, 6, 8, 10),
                                               COMBINERS, range(1, 8)):
        candidates = [row for row in records
                      if row["pre_power"] == q and row["combiner"] == name
                      and row["method"] == method and str(R) in row["requested_periods"]]
        if candidates:
            row = min(candidates, key=lambda row: row["K"])
            minima.append({"R": R, "pre_power": q, "combiner": name, "method": method,
                           "minimum_K": row["K"], "basic_axis_periods": row["axis_periods"],
                           **row["requested_periods"][str(R)]})
    return {"sampling_methods": {
                1: "full", 2: "checkerboard_same", 3: "checkerboard_opposite",
                4: "even_even", 5: "even_odd", 6: "odd_even", 7: "odd_odd",
            },
            "records": records, "minimum_pre_moduli_found_through_128": minima,
            "missing_minima_mean": "Not found through K=128; not an impossibility claim."}


def finite_power_catalogue(table: list[list[int]], M: int, R: int) -> dict:
    atoms = sorted({x for row in table for x in row})
    anchor = table[0][0]
    atoms.remove(anchor)
    atoms.insert(0, anchor)
    m = M.bit_length() - 1
    even_depths = [valuation(z) for z in atoms if z and z % 2 == 0]
    L = max(1, math.ceil(m / min(even_depths))) if even_depths else 1
    T = 1
    for z in atoms:
        if z % 2:
            order = 1
            while pow(z, order, M) != 1:
                order *= 2
            T = max(T, order)
    shifts, orders = {}, {}
    full_edges = [edges(table, R, axis) for axis in (0, 1)]
    half_edges = [edges(table, R // 2, axis) for axis in (0, 1)]
    for p, a in itertools.product(range(1, L + T), range(1, M, 2)):
        output = {z: a * pow(z, p, M) % M for z in atoms}
        if any(any(output[x] != output[y] for x, y in full)
               or all(output[x] == output[y] for x, y in half)
               for full, half in zip(full_edges, half_edges, strict=True)):
            continue
        values = tuple(output[z] for z in atoms)
        shifts.setdefault(shift_signature(values, M), (p, a))
        orders.setdefault(order_signature(values, M), (p, a))
    return {"transient_start": L, "exponent_cycle": T,
            "shift_classes": len(shifts), "order_classes": len(orders)}


def fixed_precision_catalogues() -> dict:
    result = {}
    for name in COMBINERS:
        for method in range(1, 8):
            table = basic_table(5, 2, name, method)
            result.setdefault(str(method), {})[name] = finite_power_catalogue(table, 64, 16)
    return {"K": 32, "pre_power": 2, "M": 64, "R": 16,
            "complete_positive_power_and_odd_multiplier_catalogues_by_method": result}


def unit_power_catalogue(table: list[list[int]], R: int, brute: bool = False) -> dict:
    """All positive powers and odd multipliers at minimum-period precision."""
    atoms = sorted({x for row in table for x in row})
    check(all(z % 2 for z in atoms), "unit_input")
    anchor = table[0][0]
    atoms.remove(anchor)
    atoms.insert(0, anchor)
    m0 = minimum_post_exponent(table, (R, R), 1)
    m2 = minimum_post_exponent(table, (R, R), 2)
    shifts, orders = {}, {}
    parameters = []
    if m0 is not None:
        cycle = 1 if m0 == 1 else 1 << max(1, m0 - 2)
        parameters.extend((p, m0) for p in range(1, max(2, cycle), 2))
    tail_v = None
    if m2 is not None:
        e = m2 - 1
        tail_v = max(1, e - 3)
        cycle = 1 << max(0, e - 2)
        for v in range(1, tail_v + 1):
            for u in range(1, max(2, cycle), 2):
                parameters.append(((1 << v) * u, e + v))
        for v in range(tail_v + 1, tail_v + 5):
            for u in range(1, 16, 2):
                lower_M, higher_M = 1 << (e + tail_v), 1 << (e + v)
                lower = [pow(z, (1 << tail_v) * u, lower_M) for z in atoms]
                higher = [pow(z, (1 << v) * u, higher_M) for z in atoms]
                check(shift_signature(lower, lower_M) == shift_signature(higher, higher_M),
                      "unit_power_tail")
    order_by_shift = {}
    for p, m in parameters:
        M = 1 << m
        base = [pow(z, p, M) for z in atoms]
        Q = shift_signature(base, M)[0]
        for a in range(1, Q, 2):
            values = [a * z % M for z in base]
            shift = shift_signature(values, M)
            order = order_signature(values, M)
            shifts.setdefault(shift, (p, a, M))
            orders.setdefault(order, (p, a, M))
            order_by_shift[shift] = order
    sizes = {}
    for order in order_by_shift.values():
        sizes[order] = sizes.get(order, 0) + 1
    distribution = {}
    for count in sizes.values():
        distribution[str(count)] = distribution.get(str(count), 0) + 1
    if brute:
        independent = set()
        for p in range(1, 129):
            m = minimum_post_exponent(table, (R, R), p)
            if m is None:
                continue
            M = 1 << m
            base = [pow(z, p, M) for z in atoms]
            Q = shift_signature(base, M)[0]
            for a in range(1, Q, 2):
                signature = shift_signature([a * x % M for x in base], M)
                check(signature in shifts, "unit_catalogue_brute_coverage")
                independent.add(signature)
        check(independent == set(shifts), "unit_catalogue_complete_comparison")
    return {"odd_power_minimum_m": m0, "even_power_m_minus_v": None if m2 is None else m2 - 1,
            "tail_v": tail_v, "shift_classes": len(shifts), "order_classes": len(orders),
            "order_fiber_size_histogram": distribution}


def unit_catalogues() -> dict:
    result = {}
    for name in ("OR", "XOR", "ADD", "ABSDIFF"):
        result[name] = unit_power_catalogue(basic_table(5, 2, name, 3), 16, brute=True)
    # Tail checks on the other sample phases and non-square pre-powers too.
    for k, q, name, method in itertools.product((4, 5, 6), (2, 4, 6),
                                               ("OR", "XOR", "ADD", "ABSDIFF"), range(1, 8)):
        table = basic_table(k, q, name, method)
        periods = tuple(axis_period(table, a) for a in (0, 1))
        # The tail argument also works for rectangular periods. This invocation
        # uses a square target; infeasible parity cases correctly add no members.
        R = min(periods)
        if R > 1 and all(z & 1 for row in table for z in row):
            unit_power_catalogue(table, R)
    return {"K": 32, "pre_power": 2, "method": 3, "R": 16,
            "complete_unbounded_minimum_modulus_catalogues": result}


def check_xor_saturation(xor) -> dict:
    single_counts = []
    for c in range(5, 9):
        C = 1 << c
        for parity in (0, 1):
            shifts, orders = {}, {}
            powers = range(1, C // 4, 2) if parity == 0 else range(2, C // 16 + 1, 2)
            Q = C // (2 if parity == 0 else 4)
            for p in powers:
                M = C << int(valuation(p))
                base = [pow(z, p, M) for z in range(1, C, 2)]
                for a in range(1, Q, 2):
                    values = [(a * x) % M for x in base]
                    sig = shift_signature(values, M)
                    order = order_signature(values, M)
                    check(set(sig[1]) == set(range(Q)), "single_xor_saturated")
                    check(order not in orders or orders[order] == sig, "single_xor_order_injective")
                    shifts[sig] = True
                    orders[order] = sig
            expected = C * C // (32 if parity == 0 else 256)
            check(len(shifts) == len(orders) == expected, "single_xor_count")
            single_counts.append({"C": C, "parity": "odd" if parity == 0 else "even",
                                  "shift_classes": len(shifts), "order_classes": len(orders)})
    polynomial_counts = []
    for C in (8, 16, 32, 64):
        for v in range(4):
            space = xor.same_v_space(C, v)
            base, switches = xor.binary_recipe(space)
            M = space["modulus"]
            Q = C // (2 if v == 0 else 4)
            orders = set()
            for bits in itertools.product((0, 1), repeat=len(switches)):
                values = [(x + sum(bit * g[i] for bit, g in zip(bits, switches))) % M
                          for i, x in enumerate(base)]
                sig = shift_signature(values, M)
                check(set(sig[1]) == set(range(Q)), "polynomial_xor_saturated")
                orders.add(order_signature(values, M))
            check(len(orders) == 1 << len(switches), "polynomial_xor_order_injective")
    for C in (1024, 2048, 4096):
        row = {"C": C, "same_valuation_order_bits": []}
        for v in range(5):
            space = xor.same_v_space(C, v)
            row["same_valuation_order_bits"].append(space["valid_bits"])
        polynomial_counts.append(row)
    return {"single_power_complete_checks": single_counts,
            "practical_same_valuation_counts": polynomial_counts}


def check_interpolation() -> None:
    rng = random.Random(44)
    for n in range(2, 7):
        for _ in range(20):
            nodes = sorted(rng.sample(range(32), n))
            denominators = [math.prod(x - y for y in nodes if y != x) for x in nodes]
            d = max(int(valuation(a)) for a in denominators)
            m = d + 5
            M = 1 << m
            labels = [rng.randrange(32) for _ in nodes]
            for x, label in zip(nodes, labels):
                value = 0
                for z, D, r in zip(nodes, denominators, labels):
                    e = int(valuation(D))
                    factor = (1 << (d - e)) * pow(D // (1 << e), -1, M)
                    value += r * factor * math.prod(x - y for y in nodes if y != z)
                check(value % M == (label << d) % M, "interpolation")


def tight(values: tuple[int, ...], edge_sets: tuple[set, set], M: int) -> bool:
    # Basic target periods already hold; each edge set is a half-period map.
    differences = [{(values[b] - values[a]) % M for a, b in edges_}
                   for edges_ in edge_sets]
    return (all(any(ds) for ds in differences)
            and any(ds <= {0, M // 2} for ds in differences))


def compress_antipodes(values: tuple[int, ...], M: int) -> tuple[tuple[int, ...], int]:
    # Complete the value set under addition by 1/2 before compressing each half.
    lower = sorted({x % (M // 2) for x in values} | {0})
    L = 1 << len(values).bit_length()  # L >= number of values + 1.
    ranks = {x: j for j, x in enumerate(lower)}
    return tuple(ranks[x % (M // 2)] + (L if x >= M // 2 else 0)
                 for x in values), 2 * L


def check_tight_compression() -> None:
    for n in range(2, 5):
        # Two distinct involutions on a cyclic even cell set, plus a loop map.
        if n % 2:
            e0 = {(0, 1), (1, 0), (2, 2)}
            e1 = e0
        else:
            e0 = {(i, i ^ 1) for i in range(n)}
            e1 = {(i, (i + n // 2) % n) for i in range(n)}
        for rest in itertools.product(range(16), repeat=n - 1):
            values = (0,) + rest
            if not tight(values, (e0, e1), 16):
                continue
            compressed, Q = compress_antipodes(values, 16)
            check(order_signature(compressed, Q) == order_signature(values, 16),
                  "order_compression")
            check(tight(compressed, (e0, e1), Q), "tight_compression")


def nonsaturated_examples() -> list[dict]:
    result = []
    for family, M, polynomials in (
        ("arbitrary", 32,
         (lambda z: 2 * (z - 1) + (z - 1) * (z - 3) + (z - 1) * (z - 3) * (z - 5),
          lambda z: 4 * (z - 1))),
        ("even_only", 1024,
         (lambda z: z ** 4 + 18 * z ** 6, lambda z: 3 * z ** 4 + 22 * z ** 6)),
    ):
        values = [tuple(H(z) for z in (1, 3, 5, 7)) for H in polynomials]
        check(order_signature(values[0], M) == order_signature(values[1], M),
              "nonsaturated_order_collision")
        check(shift_signature(values[0], M) != shift_signature(values[1], M),
              "nonsaturated_shift_distinction")
        edge_sets = ({(0, 2)}, {(1, 3)})
        for row in values:
            check(tight(anchored(row, M), edge_sets, M), "nonsaturated_minimum_modulus")
        result.append({"family": family, "C": 8, "M": M,
                       "anchored_values": [anchored(row, M) for row in values],
                       "order_signature": order_signature(values[0], M)})
    return result


def polynomial_order_minima(xor) -> dict:
    result = {}
    for even_only in (False, True):
        nodes = [0, 256, 1024] if even_only else [0, 16, 32]
        d = max(int(valuation(math.prod(x - y for y in nodes if y != x))) for x in nodes)
        bound = d + 1 + len(nodes).bit_length()
        minima = {}
        for m in range(1, bound + 1):
            M = 1 << m
            columns = [[x % M for x in nodes], [(x * x) % M for x in nodes]]
            space = xor.image_coordinates(columns, M)
            for coeffs in itertools.product(*(range(1 << ell) for ell in space["bits"])):
                values = tuple(sum(a * g[i] for a, g in zip(coeffs, space["generators"])) % M
                               for i in range(3))
                if values[2] != M // 2:
                    continue
                signature = order_signature(values, M)
                minima.setdefault(signature, m)
                check(signature in {(0, 1, 2), (0, 2, 1), (0, 0, 1), (0, 1, 1)},
                      "complete_and_polynomial_catalogue")
        expected = {(0, 1, 2): 11 if even_only else 6,
                    (0, 2, 1): 11 if even_only else 6,
                    (0, 0, 1): 19 if even_only else 10,
                    (0, 1, 1): 19 if even_only else 10}
        check(minima == expected, "canonical_polynomial_minima")
        result["even_only" if even_only else "arbitrary"] = {
            "interpolation_d": d, "proved_search_bound_m": bound,
            "minimum_m_by_order_signature": {str(key): value for key, value in minima.items()},
        }
    return result


def check_period_graph() -> None:
    rng = random.Random(123)
    for _ in range(100):
        table = [[rng.randrange(4) for _ in range(4)] for _ in range(4)]
        atoms = sorted({x for row in table for x in row})
        for R in (2, 4):
            possible = False
            for labels in itertools.product((0, 1), repeat=len(atoms)):
                mapping = dict(zip(atoms, labels))
                output = [[mapping[x] for x in row] for row in table]
                if tuple(axis_period(output, axis) for axis in (0, 1)) == (R, R):
                    possible = True
                    break
            check(polynomial_period_feasible(table, R) == possible, "period_graph")


def special_pre_examples() -> dict:
    periods = []
    for k in range(4, 10):
        table = basic_table(k, 4, "AND", 3)
        pair = tuple(axis_period(table, axis) for axis in (0, 1))
        periods.append(pair)
    check(periods == [(1, 1), (8, 8), (8, 8), (8, 8), (8, 8), (128, 128)],
          "pre_period_jump")
    check(not polynomial_period_feasible(table, 16), "jump_target_impossible")
    for q, k in itertools.product((2, 4, 6, 8, 10, 12), range(1, 9)):
        table = basic_table(k, q, "AND", 3)
        expected = pure_and_period(k, q)
        check(tuple(axis_period(table, a) for a in (0, 1)) == (expected, expected),
              "pure_AND_closed_period")
    table = basic_table(4, 2, "AND", 3, (1,))
    check(tuple(axis_period(table, a) for a in (0, 1)) == (8, 8), "and_twisted_pre")
    for name in COMBINERS:
        table = basic_table(5, 2, name, 3)
        N = len(table)
        for i in range(N):
            for j in range(N):
                check(table[i][j] == table[j][(-i - 1) % N], "opposite_checkerboard_square_symmetry")
    return {"fourth_pre_AND_K": [16, 32, 64, 128, 256, 512],
            "method": 3, "axis_periods": periods}


def check_sampling() -> None:
    K = 16
    expected_parities = (
        {(0, 0), (0, 1), (1, 0), (1, 1)}, {(0, 0), (1, 1)}, {(0, 1), (1, 0)},
        {(0, 0)}, {(0, 1)}, {(1, 0)}, {(1, 1)},
    )
    for method, expected in enumerate(expected_parities, 1):
        selected = {tuple(z % K for z in source(i, j, method))
                    for i, j in itertools.product(range(K), repeat=2)}
        exact = {(a, b) for a, b in itertools.product(range(K), repeat=2)
                 if (a % 2, b % 2) in expected}
        check(selected == exact, "operand_sampling")

    for method, expected in ((1, ((32, 32), (0, 64))), (2, ((16, 0), (0, 16))),
                             (3, ((32, 0), (0, 32)))):
        table = [[pow(z, 2, 128) for z in row] for row in basic_table(6, 1, "XOR", method)]
        periods = tuple(axis_period(table, axis) for axis in (0, 1))
        check(translation_basis(table, periods) == expected, "xor_translation_basis")


def and_example() -> dict:
    table = basic_table(6, 2, "AND", 3)
    check(sorted({x for row in table for x in row}) == [0, 16, 32], "and_example")
    for k in range(1, 6):
        smaller = basic_table(k, 2, "AND", 3)
        check(max(axis_period(smaller, a) for a in (0, 1)) < 32, "and_pre_minimum")
    order_set = set()
    for p in range(1, 13):
        m = minimum_post_exponent(table, (32, 32), p)
        check(m == 5 * p + 1, "and_power_minimum")
        # The primitive denominator suffices for every effective odd multiplier.
        Q = 1 << (p + 1)
        for a in range(1, Q, 2):
            order_set.add(order_signature([0, a, a * (1 << p)], Q))
    check(order_set == {(0, 1, 2), (0, 2, 1)}, "and_power_orders")
    polynomial_orders = set()
    # All anchored values on the 3 atoms at precision 6; pure value-label check.
    for b, c in itertools.product(range(64), repeat=2):
        if c != 0 and all((x - y) % 64 in (0, 32)
                          for x, y in ((0, c), (b, b))):
            polynomial_orders.add(order_signature([0, b, c], 64))
    check(polynomial_orders == {(0, 0, 1), (0, 1, 1), (0, 1, 2), (0, 2, 1)},
          "and_polynomial_orders")
    for polynomial in (lambda z: z * (z - 16), lambda z: z * (z - 48)):
        values = [polynomial(z) for z in (0, 16, 32)]
        check(order_signature(values, 1024) in polynomial_orders, "and_polynomial_witness")
        check(valuation(values[2] - values[0]) == 9, "and_polynomial_witness")
    return {"method": 3, "minimum_K": 64, "target_axis_periods": [32, 32],
            "raw_values": [0, 16, 32], "monomial_order_classes": sorted(order_set),
            "polynomial_order_classes": sorted(polynomial_orders)}


def main() -> None:
    xor = load_xor_module()
    check_sampling()
    check_pre_families()
    for a, b, p in itertools.product(range(20), range(20), range(1, 13)):
        check(power_depth(a, b, p) == valuation(a ** p - b ** p), "power_difference")
    check_interpolation()
    check_tight_compression()
    check_period_graph()
    result = {"date": "2026-11-04", "common_pre_modulus_family": check_common_pre_moduli(),
              "basic_catalogue": basic_catalogue(),
              "xor_order_comparison": check_xor_saturation(xor),
              "minimum_pre_modulus_and_example": and_example(),
              "nonsaturated_xor_examples": nonsaturated_examples(),
              "fixed_precision_catalogues": fixed_precision_catalogues(),
              "canonical_AND_polynomial_orders": polynomial_order_minima(xor),
              "pre_period_jump": special_pre_examples(),
              "unbounded_unit_power_catalogues": unit_catalogues()}
    result["checks"] = CHECKS
    result["total_checks"] = sum(CHECKS.values())
    (HERE / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": CHECKS, "total": result["total_checks"]}, indent=2))


if __name__ == "__main__":
    main()
