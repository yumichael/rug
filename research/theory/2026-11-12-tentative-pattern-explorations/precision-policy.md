# Precision policy and the gallery observations

This note distinguishes mathematical modulus policies and records the bounded gallery comparisons obtained in the chat. The workbench snapshot now exposes `catalogue`, `distinct_outputs`, and `minimum_period` selections. The original observations were made before those choices were separated in the UI. All numerical comparisons below name their policy explicitly; they do not prescribe future generator behavior.

## 1. Value preservation versus minimum-period precision

Fix K, the sampling, the pre-function, and the integer post-polynomial. Let U(t) be the resulting integer output on a complete periodic torus. A distinction-preserving modulus keeps distinct integer U values distinct after reduction. The original OR study additionally adjoined zero when choosing its modulus, keeping every nonzero output separate from zero. Its catalogue polynomials are strictly increasing on nonnegative combined inputs, so preserving their outputs also preserves all combined-input groups.

A minimum-period modulus only requires the requested least horizontal and vertical periods. It permits groups to merge and permits nonzero integer outputs to become zero when those changes leave the target periods intact.

**Upper-bound result.** A distinction-preserving modulus is an upper bound on the minimum modulus attaining the target, whenever the target is attainable for the fixed construction. Above that modulus, the equality partition has already stabilized to the integer U partition. If the target occurs there or at a larger modulus, it already occurs at that modulus; if it occurs only after mergers, it occurs at a smaller modulus. This statement assumes the supplied table is a complete torus or complete reachable value set, rather than a crop.

Consequently a value-preserving catalogue can overestimate the precision needed for repetition. It inherits the integer output's symmetries and periods. A pattern with insufficient integer period cannot acquire a larger period through reduction.

## 2. Concrete OR differences

Use N = 8, pre-power two, no twist, and post-cube H(z) = z³:

| Sampling              | Catalogue M | Minimum-period M | Least periods at the minimum |
| --------------------- | ----------: | ---------------: | ---------------------------- |
| Full                  |         128 |               16 | (8,8)                        |
| Checkerboard-same     |         128 |               16 | (8,8)                        |
| Checkerboard-opposite |          16 |               16 | (8,8)                        |

In the full field, combined inputs zero and four give cubes zero and 64. They merge modulo 16 while the target periods survive. There are six groups before reduction and five at the minimum.

For opposite-checkerboard sampling with the same pre-operation, choose H(z) = 3z+z⁴. The catalogue chooses M = 256, while the minimum-period modulus is 16. At 16 all four combined groups remain distinct, but H(5) = 640 becomes zero. Thus zero preservation alone can impose extra precision, separately from preserving distinctions between reachable values.

The current odd/odd study family and its ten post-polynomials have matching catalogue and minimum-period moduli, as proved in [the pre-power report](pre-power-families.md). The same holds inside its opposite-checkerboard erased-even-branch tail. The overshoot examples do not invalidate those tail results.

## 3. XOR gallery precision

The single-power and valid same-valuation sum strata use balanced minimum-period moduli for the reference opposite checkerboard. The broader even-only and unrestricted strata select a precision and test the target period there. That acceptance test does not establish that the selected modulus is minimum.

At N = 1024, seed zero, and 24 draws per stratum, exact checks give:

| Stratum    | Precision parameter v in M = 2N·2^v | Excess-precision draws | Rank changes on reduction |
| ---------- | ----------------------------------: | ---------------------: | ------------------------: |
| Even only  |                                   1 |                      0 |                         0 |
| Even only  |                                   2 |                     16 |                        16 |
| Even only  |                                   4 |                     23 |                        23 |
| Any powers |                                   0 |                      0 |                         0 |
| Any powers |                                   1 |                     19 |                        19 |
| Any powers |                                   2 |                     21 |                        21 |
| Any powers |                                   4 |                     24 |                        24 |

The other eight strata each have zero excess-precision draws. Overall 103 of the 360 draws change their anchored rank arrays when reduced to their minimum-period modulus.

The even-only strata initially have 24,8,1 complement-symmetric draws at v = 1,2,4. Every one of the 39 failures gains that symmetry after reduction, leaving all 72 even-only draws symmetric. This is explained by the general bound M_min ≤ 2N² in [the XOR symmetry report](xor-symmetry.md), not only by the finite observations.

These counts concern the reference opposite-checkerboard XOR sampling. A polynomial drawn for that reference may have different minimum periods or insufficient precision under another sampler or combiner; those constructions require their own period test. The [results](results.json) record the precise counts and source hashes used in the rerun.
