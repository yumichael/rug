# Uniform sampling across positive polynomial valuations

This collection studies the union of the existing no-pre-operation XOR polynomial families with positive exponent valuations and an odd sum of nonconstant coefficients. The [report](report.md) proves that the productive valuation rows are disjoint and that every later row equals one shared tail. This supplies an exact uniform shift-class sampler, also uniform over order classes, using the existing conditional coordinates.

The terminology matters: “odd-sum” here describes coefficient parity. The gallery label “odd sum” instead describes odd exponents, at valuation zero. This project covers the positive-valuation “even sum” families.

The [research prototype](union_sampler.py) implements a global class index and returns a factored integer post-polynomial at its minimum period-preserving modulus. The [verification](verify.py) and [results](results.json) record exact counts, exhaustive small unions, independent overlap checks, larger-domain checks, and comparisons with the native workbench. Application and gallery sampling behavior are unchanged.

Run the standard-library checks from the repository root:

```sh
python3 research/theory/2026-11-14-2-xor-positive-valuation-union/verify.py
```

Include the optional native workbench checks with the existing research environment:

```sh
research/interactive/.venv/bin/python research/theory/2026-11-14-2-xor-positive-valuation-union/verify.py --native
```

Both commands regenerate the results file; its coverage records whether native checks ran. Print an example recipe and the domain-4096 count with:

```sh
python3 research/theory/2026-11-14-2-xor-positive-valuation-union/union_sampler.py
```

Today’s first collection is [Competing visual head-family proposals](../2026-11-14-1-head-family-proposals/report.md). The present collection is the second.
