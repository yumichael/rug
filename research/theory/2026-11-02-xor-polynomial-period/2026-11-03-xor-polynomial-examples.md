# XOR polynomial counts and the extra bit at larger moduli

This companion to the [theory report](2026-11-02-xor-polynomial-period.md) records the subsequent discussion through count comparisons and a concrete polynomial example. The results concern one numerical channel of the no-pre-operation XOR construction, before color conversion, cropping, or stretching.

## 1. What the uniform sampler covers

Fix a coordinate domain $C=2^c$, a specific valuation $v$, and the corresponding modulus and requested axis period:

$$
M=C2^v,\qquad R=C/2.
$$

The same-valuation polynomial set contains integer linear combinations of powers whose exponents have exactly that valuation:

$$
H(z)=b+\sum_{u\text{ odd}}a_u z^{2^vu}\pmod M.
$$

A **shift class** identifies normalized output patterns differing by a common circular shift. Subtracting $H(1)$ anchors one representative of each class. The new research gives a uniform sampler over all such classes whose smallest horizontal and vertical periods remain exactly $R$.

Its period criterion is that the sum of the nonconstant coefficients is odd. The independent-coordinate construction removes duplicate descriptions and builds that oddness into the recipe, giving a fixed base pattern plus independent binary controls. Every setting gives a different valid shift class.

Odd-power polynomials correspond to $v=0$. Even powers form a separate polynomial set for each positive valuation:

| Valuation | Allowed positive exponents |
| --------: | -------------------------- |
|         0 | 1, 3, 5, 7, …              |
|         1 | 2, 6, 10, 14, …            |
|         2 | 4, 12, 20, 28, …           |

Combining every even exponent into one polynomial would mix valuations and require its own common-modulus policy. The comparisons below keep one valuation fixed.

## 2. Odd-power polynomials add substantial variety

For comparison, a **single-power shift class** uses one post-power together with an odd multiplier and an offset. The polynomial set allows integer combinations of those powers. Both columns below ignore common shifts and retain relative multiplier arrangements.

For fresh or adapted field references, the coordinate domain is twice the longer field side in cells. The familiar field sizes give:

| Field dimensions in cells    | Coordinate domain | Single-power affine families | Single-power shift classes | Polynomial shift classes | Increase in shift classes |
| ---------------------------- | ----------------: | ---------------------------: | -------------------------: | -----------------------: | ------------------------- |
| 512 × 256                    |             1,024 |                          128 |                     32,768 |                  262,144 | 8×                        |
| 1,024 × 512                  |             2,048 |                          256 |                    131,072 |                4,194,304 | 32×                       |
| 2,048 × 512 or 2,048 × 1,024 |             4,096 |                          512 |                    524,288 |               67,108,864 | 128×                      |

An affine family is a coarser object than a shift class: it groups the different odd-multiplier arrangements together. The increase column compares shift classes with shift classes, rather than comparing polynomial classes to the coarser affine-family count.

These odd-power polynomial counts correspond to 18, 22, and 26 independent valid bits. They follow the closed odd-power coordinate formula in Section 6 of the theory report.

## 3. Even-power combinations often coincide with the existing space

Each cell below reads **single-power shift classes → polynomial shift classes**, at the specified fixed valuation. All counts require the full smallest period.

|    Valuation |  Domain 1,024 |  Domain 2,048 |    Domain 4,096 |
| -----------: | ------------: | ------------: | --------------: |
|            1 | 2,048 → 2,048 | 8,192 → 8,192 | 32,768 → 65,536 |
|            2 | 1,024 → 1,024 | 4,096 → 4,096 | 16,384 → 16,384 |
|            3 |     512 → 512 | 2,048 → 2,048 |   8,192 → 8,192 |
|            4 |     256 → 256 | 1,024 → 1,024 |   4,096 → 4,096 |
|            5 |     128 → 128 |     512 → 512 |   2,048 → 2,048 |
|            6 |     128 → 128 |     256 → 256 |   1,024 → 1,024 |
|            7 |     128 → 128 |     256 → 256 |       512 → 512 |
| 8 and higher |     128 → 128 |     256 → 256 |       512 → 512 |

Thus, at these dimensions, the even same-valuation polynomial sets usually contain no new full-period shift classes beyond the single-power affine families. The exception in this table is domain 4096 and valuation one, where the count doubles.

For example, at that exceptional entry, the 64 single-power affine families each contain 512 shift classes, giving $64\cdot512=32{,}768$. Polynomial combinations give 65,536 instead.

The intermediate-valuation polynomial counts come from the exact coordinate calculations in [results.json](results.json). The constant counts in the higher-valuation rows also follow the stabilization theorem in Section 8 of the theory report. Different valuations have different moduli and can overlap after normalization, so these rows should not be added to claim a total over all even valuations.

Cell enlargement changes exported pixel dimensions without increasing the underlying space. Retained references can also keep an earlier coordinate domain. These tables concern complete underlying numerical patterns rather than distinct final rendered crops or complete three-channel rugs.

## 4. Why domain 4096 and valuation one cross a threshold

At valuation one, $M=2C$. The relevant comparison is:

| Coordinate domain | Modulus | Single-power shift classes | Polynomial shift classes |
| ----------------: | ------: | -------------------------: | -----------------------: |
|             1,024 |   2,048 |                      2,048 |                    2,048 |
|             2,048 |   4,096 |                      8,192 |                    8,192 |
|             4,096 |   8,192 |                     32,768 |                   65,536 |

The extra variety appears because an additional independent polynomial component becomes distinguishable at modulus 8192. At the smaller moduli, that component is identically zero. It supplies one additional binary choice at the larger modulus.

The independent anchored coordinate sizes show the change directly:

| Coordinate domain | Numbers of settings of the independent anchored controls | Full-period shift classes |
| ----------------: | -------------------------------------------------------- | ------------------------: |
|             1,024 | 256 × 16                                                 |                     2,048 |
|             2,048 | 512 × 32                                                 |                     8,192 |
|             4,096 | 1,024 × 64 × 2                                           |                    65,536 |

Exactly half of each product retains the full period. From domain 1024 to 2048, both existing controls double their ranges. At domain 4096 those ranges double again, and a third two-setting control becomes available. That is why the polynomial count grows eightfold at this step while the single-power count grows fourfold.

This is a precision threshold, rather than a special property unique to the number 4096. Polynomial expressions that were indistinguishable at lower precision can become independent as the modulus grows.

## 5. A concrete polynomial that is invisible at the smaller moduli

Write $w=z^2$ and define

$$
J(z)=(w-1)(w-9)(w-17)(3w^2+81w+520).
$$

Its expansion is

$$
J(z)=3z^{10}-1130z^6+80687z^2-79560.
$$

Only powers 2, 6, and 10 appear, and all have valuation one. The constant is permitted and the expression is anchored at input 1.

Every odd input gives an output divisible by 4096. Consequently, $J$ vanishes modulo 2048 and 4096. Modulo 8192 it can be either zero or 4096:

| Input | Output modulo 4,096 | Output modulo 8,192 |
| ----: | ------------------: | ------------------: |
|     1 |                   0 |                   0 |
|     3 |                   0 |                   0 |
|     5 |                   0 |               4,096 |
|     7 |                   0 |                   0 |
|    11 |                   0 |               4,096 |

After normalization by 8192, this component adds zero at some cells and one half at others. It is therefore a change in the relative arrangement, not a common phase shift.

The divisibility can be seen without checking every input. An odd square has the form $w=1+8t$. Substitution gives

$$
J(z)=2048\,t(t-1)(t-2)(151+174t+48t^2).
$$

The last factor is odd, and the three consecutive integers supply at least one factor of two. Thus every value is divisible by 4096. At $z=5$, $t=3$, and the three-integer product has exactly one factor of two, so the value is nonzero modulo 8192.

## 6. An explicit new full-period pattern

At $C=4096$ and $M=8192$, add this component to the anchored power-2 pattern:

$$
H(z)=z^2-1+J(z)\pmod{8192}.
$$

The sum of the nonconstant coefficients of $J$ is even, whereas that of $z^2-1$ is odd. The parity theorem therefore guarantees that $H$ retains the smallest horizontal and vertical periods $R=2048$.

This particular $H$ cannot be reproduced up to shift by any single valuation-one power and odd multiplier. That claim can be checked over a complete finite set: at domain 4096 the valuation-one affine families have representatives $p=2u$ with $u=1,3,\ldots,127$. For each representative, anchoring removes the offset, and the output difference at input 3 uniquely determines the only possible effective multiplier modulo 1024. None of those 64 candidates agrees with $H$ on all odd inputs.

The example establishes a concrete newly available pattern. It does not assert that switching this component on always converts every single-power pattern into a previously unavailable one. The exact coordinate count establishes the overall doubling; the formula above exhibits one member of the additional space.

The count comparisons are applications of the earlier affine-family formulas and the new same-valuation coordinate calculations. The explicit polynomial identities and table for $J$ were checked with integer arithmetic, including every odd input below 4096. For the main proofs, coordinate construction, and reproducible research checks, see the [theory report](2026-11-02-xor-polynomial-period.md) and [script](xor_polynomial_period.py).
