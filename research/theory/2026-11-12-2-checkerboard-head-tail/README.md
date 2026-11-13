# Checkerboard head and tail research

This November 12, 2026 investigation follows the [latest substantive personal-notes request](research-request.md) and the [tentative exploration numbered one](../2026-11-12-1-tentative-pattern-explorations/README.md). It studies checkerboard-opposite OR, XOR, ADD, and ABSDIFF with arbitrary integer post-polynomials and arbitrary twists in the shared difference-preserving pre-polynomial family. General statements cover every dyadic side at least eight; verification spans sides 8–4096. The 64×64 examples are specializations, not the scope of the head results.

## Findings

In the erased-even-branch tail, the four combiners agree exactly, including every modulus selector, for each fixed polynomial recipe. Across selectors, arbitrary polynomials can disagree substantially; the exact criterion depends on half-period difference depths, all distinct-output difference depths, and zero preservation. The discrepancy is not universally small.

For every fixed recipe, all dyadic moduli from its minimum upward retain the requested period. ABSDIFF minimum precision is available: throughout the head at sides at least sixteen, every shared twist with identity post has minimum modulus four. Its two output classes encode comparison of the odd and even pre-values. A small side-eight exception is stated explicitly.

For general post-polynomials, a graph of half-period edges gives a complete classification of orders at minimum-period precision. A connected component may use one value or an antipodal pair; the pairs must fit the specified circular order. The new sampler draws these classes uniformly for components of arbitrary sizes. Numerical shift classes are generally infinite across all minimum moduli, so their uniform sampler needs a finite precision boundary.

Every arbitrary polynomial twist reduces to finitely many exact coordinates at a fixed domain; representatives of degree at most seven suffice throughout sides 8–4096. At side 64 the complete head has 208 pre-functions across its four powers, rather than only the gallery's sixteen twists per power. An exact multiplicity-corrected sampler covers their union across all four combiners. Exhaustive twist-union enumeration becomes much larger at higher domains; conditional order sampling avoids that enumeration.

Natural coarser structural groups come from the surviving even-branch layers, their relative bit depth, and the half-period component sizes. Pre-powers six and eight share a coarse scale but diverge as the domain grows. OR and XOR at every pre-power at least four share the same abstract order count as that side's tail; ADD and ABSDIFF have matching abstract counts with different spatial embeddings. None of these count equivalences asserts identical visual texture.

## Reports

| Report                            | Contents                                                                                                                       |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| [General theory](theory.md)       | Exact modulus criteria; general head/tail graph; arbitrary-polynomial order theorem; finite twist coordinates; ABSDIFF minimum |
| [Head families](head-families.md) | Domain-dependent even-branch layers; coarser groups; OR/XOR and ADD/ABSDIFF comparisons; modulus exploration and figures       |
| [Uniform sampling](sampling.md)   | Fixed-modulus shift sampler; complete order counts and direct sampler; uniform unions; practical limits                        |
| [Recorded evidence](results.json) | General-domain checks, module counts, gallery comparisons, native realizations, exhaustive small counts, and timings           |

## Reproduce

Use the existing optional [research environment](../../../README.md#optional-python-research-tools). From the repository root:

```sh
MPLCONFIGDIR=/private/tmp/rug-research-mpl PYTHONDONTWRITEBYTECODE=1 research/interactive/.venv/bin/python research/theory/2026-11-12-2-checkerboard-head-tail/verify.py
```

The command regenerates [results.json](results.json), the [worked head/tail atlas](head-tail-atlas.png), the [modulus ladder](modulus-ladder.png), and the [domain comparison](domain-families.png). Use `--skip-figures` to omit image regeneration or `--output` to write the JSON elsewhere. It performs no Git operations and changes no app or notebook settings.

The recorded run checks 392 reductions of arbitrary high-degree twists over ten domain sizes, all 208 side-64 canonical pre-functions, 2,560 gallery head recipes as a comparison, 288 actual selector fields, 40 native constructed-polynomial realizations, 40 native cases with signed degree-nine posts and degree-eight twists, independent exhaustive order models and a small overlapping union, and exhaustive small numerical polynomial spaces. The general claims rest on the proofs, not only these bounded checks.

| Source                               | Purpose                                                                                            |
| ------------------------------------ | -------------------------------------------------------------------------------------------------- |
| [core.py](core.py)                   | Compressed exact raw tables, modulus formulas, twist coordinates, and fixed-modulus shift sampling |
| [fast_sampler.py](fast_sampler.py)   | Direct uniform order sampler using crossing components and Stirling transforms                     |
| [order_sampler.py](order_sampler.py) | Independent component-type counting and sampling reference                                         |
| [realize.py](realize.py)             | Integer post-polynomial construction at its own minimum-period precision                           |
| [union_sampler.py](union_sampler.py) | Multiplicity-corrected uniform union over an explicit finite base set                              |
| [verify.py](verify.py)               | Reproducible verification, catalogue comparisons, benchmarks, and static figures                   |

## Remaining limits

Uniformity refers to exact mathematical classes. The sampler does not establish uniform perceived variety. The complete all-twist union is practical in the recorded side-64 example; the same exhaustive approach is not claimed practical at the largest domains. A globally smallest polynomial realization modulus for each order remains separate from minimum precision for the constructed polynomial. General pre-polynomials outside the shared twist family require a new analysis. No proposed style or sampler has been integrated into the app or notebook.
