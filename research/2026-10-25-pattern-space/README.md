# Pattern-space research

Read [the report](2026-10-25-pattern-space-theory.md) for proofs, sampling recommendations, symmetry classifications, and scope. This is a continuation of the October 13 post-power research, based on repository commit `e1fde1ca97c9644511d4b4e9a264f532a75b1090`.

For a concrete introduction to the existing XOR algorithm, read [Understanding XOR post-power, multiplier, and offset](2026-11-01-xor-post-operations-explained.md). It follows the discussion through numerical examples, structural versus exact output families, the growing-modulus tail, and the current sampler.

Run the exact checks and regenerate figures from the repository root:

```sh
python3 research/2026-10-25-pattern-space/pattern_space.py --figures
```

Dependencies are Python 3, NumPy, and Matplotlib. The verified run used NumPy 2.3.5 and Matplotlib 3.10.8. Without `--figures`, the script runs the integer checks and writes `results.json`; with the flag it also adds scale metrics, generates `lag-metrics.json`, and regenerates all three PNG figures.

The script completes 62,130 assertions. Exact arithmetic supplies the classifications; floating point supplies entropy, phase diagnostics, and figures. All output files are written beside the script. No application settings or Git state are changed.

The package contains only this research folder. Add it at `research/2026-10-25-pattern-space/` to keep the documented command and relative figure links valid.
