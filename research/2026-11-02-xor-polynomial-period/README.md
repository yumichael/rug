# XOR polynomials with an exact repetition period

Read [the report](2026-11-02-xor-polynomial-period.md) for new proofs, explicit polynomial recipes, independent binary controls, and counts. It continues the [XOR explanation](../2026-10-25-pattern-space/2026-11-01-xor-post-operations-explained.md) and the earlier pattern-space research.

The central result for sums of same-valuation powers is simple: the full axis period survives exactly when the sum of the nonconstant coefficients is odd. A constructive coordinate system removes duplicate descriptions and turns that criterion into independent binary choices around a fixed base pattern. The report also gives an exact characterization for arbitrary post-polynomials, with a derivative test in the usual valuation range.

Run the reproducible checks from the repository root:

```sh
python3 research/2026-11-02-xor-polynomial-period/xor_polynomial_period.py
```

The script uses only the Python standard library. It writes [results.json](results.json) beside itself and prints the check count and selected numerical results. It does not change application settings or Git state. The report distinguishes proved statements, formula-based calculations, and finite verification coverage.
