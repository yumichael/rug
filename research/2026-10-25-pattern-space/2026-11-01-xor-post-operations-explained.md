# Understanding XOR post-power, multiplier, and offset

This report records the understanding developed in our discussion of the existing XOR rug algorithm. It explains results from the [October 25 theory report](2026-10-25-pattern-space-theory.md) and its predecessors through concrete numbers. It adds no new classification results. The numerical examples apply those existing results to small cases.

The scope is one numerical channel, with no pre-operation, followed by a positive integer post-power, an odd post-multiplier, and a post-add. We consider complete periodic patterns before color conversion, quantization, cropping, and stretching. Those later stages can hide numerical differences. Polynomial post-operations and powered pre-operations are separate extensions.

The central distinction is between a **structural family**, which sets aside common shifts and odd value rescalings, and an **exact output family**, which retains every distinct numerical result at a specified modulus. This distinction matters especially when the modulus changes.

## 1. What one channel computes

The existing diagonal coordinate construction combines two coordinate values with XOR. Call the resulting number $z$. For a coordinate domain of size $C$, every odd number below $C$ occurs somewhere in the complete pattern, and no even number occurs.

The channel calculation is

$$
F(x,y)=\bigl(\alpha z(x,y)^p+\beta\bigr)\bmod M.
$$

Here $p$ is the post-power, $\alpha$ is an odd post-multiplier, and $\beta$ is the post-add or offset. The channel value passed toward color conversion is $F(x,y)/M$.

For example, an offset increase of one shifts every normalized channel value by $1/M$, wrapping around at 1. An odd multiplier is invertible modulo $M$, so it rearranges numerical values without merging distinct ones. It supplies a particular kind of bijection; it does not supply every possible permutation.

All counts below hold the spatial origin and orientation fixed. Translating or rotating a pattern does not automatically make it the same pattern for these counts.

## 2. Why the power determines the modulus

Every positive post-power can be split into a power of two and an odd number:

$$
p=2^v u,\qquad u\text{ odd}.
$$

The number $v$ counts how many factors of two divide $p$. Its mathematical notation is $v=\nu_2(p)$. For instance, $12=2^2\cdot3$, so its valuation is 2 and its odd part is 3. Odd powers have $v=0$.

The balanced modulus used for this XOR construction is

$$
M=C2^v.
$$

For the domain sizes used in this report, that gives exact horizontal and vertical repetition period

$$
R=C/2.
$$

At $C=256$, the period is 128, but the modulus depends on the power:

| Post-power | Valuation | Odd part | Output modulus |
| ---------: | --------: | -------: | -------------: |
|          3 |         0 |        3 |            256 |
|          2 |         1 |        1 |            512 |
|          6 |         1 |        3 |            512 |
|          4 |         2 |        1 |          1,024 |
|         16 |         4 |        1 |          4,096 |
|         32 |         5 |        1 |          8,192 |

Thus increasing the modulus does not necessarily increase the spatial period: here it compensates for the post-power. The structural classification formulas below assume $C=2^c\ge32$, equivalently $R\ge16$. Smaller domains need separate finite treatment. Power zero is outside this construction.

## 3. What it means for two powers to share a family

Fix a post-power and its modulus. Let the odd multiplier and offset vary through their allowed settings. This produces an exact output family: a set of complete numerical patterns.

Different post-powers can describe the same exact output family at the same modulus. At $C=256$, powers 2 and 18 both use $M=512$, and the research proves

$$
z^{18}\equiv41z^2-40\pmod{512}
$$

for every odd input. These settings therefore give exactly the same output at every coordinate:

| Post-power | Post-multiplier | Post-add | Modulus |
| ---------: | --------------: | -------: | ------: |
|         18 |               1 |        0 |     512 |
|          2 |              41 |      472 |     512 |

The offset 472 represents $-40$ modulo 512. Since 41 is invertible, the compensation works in both directions. Every output available from one power is available from the other through suitable affine adjustments.

A **structural family** goes a step further: it identifies patterns after removing their common normalized phase and compensating for an odd value multiplier. In the formal report this is a primitive odd-affine class. This permits comparing structures whose raw moduli differ.

An exact output family is defined at a specified modulus. A structural family deliberately sets aside phase and multiplier choices. Equal structural families across different moduli need not have equal sets of exact outputs.

## 4. The complete family picture at domain size 256

There are 32 odd-power structural families. Convenient representatives are

$$
p=1,3,5,\ldots,63.
$$

All use $v=0$ and $M=256$. The family represented by power 1 also contains powers 65, 129, and so on; the family represented by power 3 contains 67, 131, and so on. These repeats already have identical powered tables. Allowing multiplier and offset does not merge the 32 odd families further.

There are eight even-power structural families:

| Family | Representative power | Its valuation | Its modulus | Other powers in the family |
| ------ | -------------------: | ------------: | ----------: | -------------------------- |
| A      |                    2 |             1 |         512 | 18, 34, 50, …              |
| B      |                    6 |             1 |         512 | 22, 38, 54, …              |
| C      |                   10 |             1 |         512 | 26, 42, 58, …              |
| D      |                   14 |             1 |         512 | 30, 46, 62, …              |
| E      |                    4 |             2 |       1,024 | 20, 36, 52, …              |
| F      |                   12 |             2 |       1,024 | 28, 44, 60, …              |
| G      |                    8 |             3 |       2,048 | 24, 40, 56, …              |
| H      |                   16 |             4 |       4,096 | 32, 48, 64, 80, …          |

For A through G, all powers within the family have the same valuation and modulus. H is the **tail family**: it contains every positive multiple of 16, whose valuations and moduli can differ. In general, the tail begins at $v=c-4$ and includes all larger valuations.

At a general power-of-two domain size $C\ge32$, the counts are

$$
\text{odd families}=C/8,\qquad\text{even families}=C/32,\qquad\text{total}=5C/32.
$$

These families retain numerical relationships that matter under a fixed color mapping. Merely asking which cells have equal values would give a coarser classification: all odd powers share one equality partition, and all even powers share another.

## 5. How the tail can stay structurally fixed while its modulus grows

The report separates each normalized pattern into a common phase and a table of spatial differences. After its canonical normalization, write the result as

$$
\frac{F_i}{M}\equiv\theta+\frac{aT_i}{Q}\pmod1.
$$

The index $i$ identifies a cell. The table $T_i$ is the canonical structural representative, anchored to zero at a fixed cell. The odd number $a$ adjusts its value arrangement, and $\theta$ is the common phase. The effective denominator $Q$ measures the resolution of the spatial differences. Its value is part of the structure.

For this balanced XOR family,

$$
Q=C/2\text{ for odd powers},\qquad Q=C/4\text{ for even powers}.
$$

At $C=256$, every even family has $Q=64$. Within the tail, the canonical table also stays the same as the power increases. The raw powered tables may require different odd rescalings to reach that canonical table.

The phase still has the raw modulus's resolution. After allowing the offset, it ranges over multiples of $1/M$. Consequently, the same structural family can support increasingly fine phase choices:

| Tail power | Modulus | Phase step | Effective spatial denominator |
| ---------: | ------: | ---------- | ----------------------------: |
|         16 |   4,096 | 1/4096     |                            64 |
|         32 |   8,192 | 1/8192     |                            64 |
|         64 |  16,384 | 1/16384    |                            64 |

The larger-modulus exact output families really are larger. The report counts the distinct outputs at fixed modulus as

$$
M\varphi(Q),
$$

where $\varphi(Q)$ is the number of odd residues modulo the power of two $Q$. Here $\varphi(64)=32$, giving 131,072 exact outputs for the power-16 representative, 262,144 for power 32, and 524,288 for power 64.

Thus the finite structural count does not imply a finite set of all exact outputs across unbounded powers. Choosing one tail representative preserves its structure; preserving every finer phase requires a separate phase-precision policy.

## 6. A complete small example of multiplier rearrangements

Why do larger moduli not continually add new relative rearrangements? In this tail, the reachable powered values become proportionally farther apart as the modulus grows. The number of inputs alone would not establish that result.

Take $C=32$ and compare power 4 modulo 128 with power 8 modulo 256. These are in the same tail structural family. The following table includes every odd input, grouped by identical outputs:

| XOR inputs | Fourth power modulo 128 | Eighth power modulo 256 | Common index |
| ---------- | ----------------------: | ----------------------: | -----------: |
| 1, 31      |                       1 |                       1 |            0 |
| 13, 19     |                      17 |                      33 |            1 |
| 9, 23      |                      33 |                      65 |            2 |
| 11, 21     |                      49 |                      97 |            3 |
| 15, 17     |                      65 |                     129 |            4 |
| 3, 29      |                      81 |                     161 |            5 |
| 7, 25      |                      97 |                     193 |            6 |
| 5, 27      |                     113 |                     225 |            7 |

Writing the common index as $T$, the lower powered values are $1+16T$ and the higher ones are $1+32T$. Their normalized values are

$$
\frac{1+16T}{128}=\frac1{128}+\frac T8,\qquad\frac{1+32T}{256}=\frac1{256}+\frac T8.
$$

After multiplying by any odd $\alpha$ and removing the common phase, both cases reduce to the same rearrangement rule:

$$
T\longmapsto\alpha T\bmod8.
$$

Here are all four possible relative rearrangements:

| Multiplier modulo 8 | Images of indices 0, 1, 2, 3, 4, 5, 6, 7 |
| ------------------: | ---------------------------------------- |
|                   1 | 0, 1, 2, 3, 4, 5, 6, 7                   |
|                   3 | 0, 3, 6, 1, 4, 7, 2, 5                   |
|                   5 | 0, 5, 2, 7, 4, 1, 6, 3                   |
|                   7 | 0, 7, 6, 5, 4, 3, 2, 1                   |

Every raw odd multiplier belongs to one of these groups:

| Relative multiplier | Raw multipliers modulo 128 | Raw multipliers modulo 256 |
| ------------------: | -------------------------- | -------------------------- |
|                   1 | 1, 9, 17, …, 121           | 1, 9, 17, …, 249           |
|                   3 | 3, 11, 19, …, 123          | 3, 11, 19, …, 251          |
|                   5 | 5, 13, 21, …, 125          | 5, 13, 21, …, 253          |
|                   7 | 7, 15, 23, …, 127          | 7, 15, 23, …, 255          |

There are 16 multipliers per group at the lower modulus and 32 at the higher modulus. The extra multipliers provide additional common phases, rather than additional relative rearrangements.

For example, multiplier 9 gives these complete output lists, ordered by the common index:

| Modulus | Original powered outputs          | Outputs after multiplying by 9     |
| ------: | --------------------------------- | ---------------------------------- |
|     128 | 1, 17, 33, 49, 65, 81, 97, 113    | 9, 25, 41, 57, 73, 89, 105, 121    |
|     256 | 1, 33, 65, 97, 129, 161, 193, 225 | 9, 41, 73, 105, 137, 169, 201, 233 |

In each row, this is just an increase of eight in every raw value. The normalized shifts differ: $8/128$ versus $8/256$. Multiplier 3 does rearrange the relative indices, but multiplier 11 gives the same relative rearrangement with a different common phase.

The projection here means removing the common phase, expressing values through their effective index, and reducing the multiplier modulo 8. Simply reducing higher-modulus outputs modulo 128 would merge values and would not perform this projection.

## 7. What uniform sampling means

Uniform structural sampling gives each structural family the same probability. It does not give every exact output the same probability when the exact output families have different sizes.

For example, giving the tail representatives at moduli 4,096 and 8,192 equal probability would not give their individual exact outputs equal probability: the latter family has twice as many outputs. Structural sampling instead counts their common structure once and handles phase separately.

The older proposal to choose valuation and odd part separately needs the same distinction. Suppose that at $C=256$ we choose each productive even valuation, 1 through 4, equally, then choose the odd part uniformly from 1 through 63. There are 128 equally likely parameter pairs, but only eight structural families:

| Valuation | Odd-part choices | Structural families | Old descriptions per family | Old probability per family |
| --------: | ---------------: | ------------------: | --------------------------: | -------------------------- |
|         1 |               32 |                   4 |                           8 | 6.25%                      |
|         2 |               32 |                   2 |                          16 | 12.5%                      |
|         3 |               32 |                   1 |                          32 | 25%                        |
|         4 |               32 |                   1 |                          32 | 25%                        |

Those parameter pairs described distinct coefficient tables under the earlier equivalence. Once adjustable multiplier and offset are included, multiple descriptions merge. Equal probability per old description therefore favors the families with more descriptions.

We can still sample valuation and odd part separately. To make each even structural family equally likely, use this hierarchy instead:

| Valuation | Probability of this valuation | Choose odd part uniformly from | Representative powers |
| --------: | ----------------------------- | ------------------------------ | --------------------- |
|         1 | 1/2                           | 1, 3, 5, 7                     | 2, 6, 10, 14          |
|         2 | 1/4                           | 1, 3                           | 4, 12                 |
|         3 | 1/8                           | 1                              | 8                     |
|         4 | 1/8                           | 1                              | 16                    |

Every representative now has probability $1/8$. If both post-power parities are allowed, uniformity across all 40 structural families gives odd powers total probability $32/40=4/5$ and even powers $8/40=1/5$. An aesthetic preference for either parity can deliberately use different weights.

## 8. A simple sampler, and its resemblance to the current code

For odd powers only, select uniformly from

$$
p\in\{1,3,5,\ldots,C/4-1\}.
$$

For even powers only, select uniformly from

$$
p\in\{2,4,6,\ldots,C/16\}.
$$

The even set has $C/32$ members, one per structural family. At $C=256$, these are powers 2, 4, 6, 8, 10, 12, 14, and 16.

This is the distribution supplied by the report's single-integer index. Let $W=C/32$ and choose $k$ uniformly from 0 through $W-1$. For positive $k$, the valuation formula simplifies directly:

$$
p=2^{1+\nu_2(k)}\frac{k}{2^{\nu_2(k)}}=2k.
$$

For $k=0$, use $p=C/16=2W$, the tail representative. Thus its power set is exactly the consecutive even range above.

The current implementation also chooses a uniform integer and doubles it. For even powers, its relevant calculation in [index.html](../../index.html) is

```js
const qCount = Math.max(1, Math.ceil(N*N/32) - 1);
const q = 1 + randomInteger(rng, qCount);
const power = 2*q;
```

The difference is the range. The compact structural sampler needs only integers 1 through $C/32$. The current code uses integers 1 through $\lceil N^2/32\rceil-1$, apart from its minimum-count safeguard. Here $N$ is the generation-size argument, whereas $C$ is the region's actual coordinate domain. They can differ, especially for borders and retained references.

At $N=C=256$, the current code chooses from 2,047 even powers, 2 through 4,094. Applying the existing classification to that range gives:

| Family represented by power | Current number of descriptions | Compact sampler descriptions |
| --------------------------: | -----------------------------: | ---------------------------: |
|                           2 |                            256 |                            1 |
|                           4 |                            256 |                            1 |
|                           6 |                            256 |                            1 |
|                           8 |                            256 |                            1 |
|                          10 |                            256 |                            1 |
|                          12 |                            256 |                            1 |
|                          14 |                            256 |                            1 |
|                          16 |                            255 |                            1 |

The current sampler is already almost uniform over structural families in this example: seven families have probability $256/2047$ and the tail has $255/2047$. The compact sampler gives each exactly $1/8$.

Uniformly choosing an integer and doubling it is different from uniformly choosing a valuation row and then its odd part. The large bias in Section 7 belongs to the latter proposal. It should not be attributed to the current code.

The smaller range removes redundant structural descriptions. It also changes the sampled raw moduli and phase possibilities, so replacing the old range is a recipe change unless those choices are preserved separately.

For odd powers, the current code uses $p=2q-1$ over the same large integer range. The compact structural range needs only $q=1,\ldots,C/8$. Again, structural completeness and preservation of existing seeded outputs are different requirements.

## 9. Keeping a variation related when the period changes

The report's index $k$ has another purpose beyond uniform sampling. When the domain shrinks, its natural structural projection is

$$
k_{\mathrm{small}}=k_{\mathrm{large}}\bmod(C_{\mathrm{small}}/32).
$$

Doubling the domain doubles the number of even structural families, and the larger index projects consistently to the smaller one. The raw modulus changes from Section 6 instead held the domain fixed; that is a different comparison.

Choosing uniformly among consecutive even powers gives the right distribution at one size. Preserving a stored variation across sizes also requires retaining the index convention, including its special zero case. Equal distributions alone do not guarantee that the same seed or stored integer selects related classes.

The combined odd/even sampler in Section 4.5 of the theory report provides a corresponding construction for both parities. The five-way choice in that sampler requires unbiased bounded sampling; reducing a uniform binary word modulo an arbitrary class count can introduce bias. The current implementation already uses rejection sampling for bounded integer draws.

Applying an identical color style also requires a consistent canonical numerical representative. Equivalent raw powers can differ by an odd rescaling and common phase. Feeding those raw values directly into the same fixed color mapping can produce different colors.

## 10. Full-grid and checkerboard sampling

The original diagonal coordinate construction and an additional checkerboard selection are separate choices. The existing full-grid XOR pattern already has horizontal and vertical reflection symmetry for both odd and even post-powers. Its historical symmetry center is $(-1/2,0)$: one axis lies between cells and the other passes through cells. That does not supply lattice-preserving quarter-turn symmetry.

The extra checkerboard selection has two standard phases. The theory report proves that both produce the same XOR input at every displayed coordinate, before post-processing. They therefore give exactly the same pattern for both post-power parities, with the same multiplier and offset.

For even powers under the balanced modulus rule, the checkerboard pattern has full square symmetry about $(-1/2,-1/2)$: axial and diagonal reflections and quarter-turns. For odd powers, interchange and half-turn remain exact, while the axial reflections negate the powered value modulo $C$. Odd multiplication and an offset turn that into a corresponding value transformation; it is not generally an exact channel-value symmetry.

The checkerboard version still encounters every odd input and retains exact axis period $C/2$. Consequently, the structural family counts and samplers in this report apply to both the full-grid construction and this checkerboard version. These results do not require making checkerboard selection the default for future algorithms or establish the same counts for arbitrary selection rules.

## 11. What a generator can preserve separately

For this established XOR family, the research supports separating three decisions:

1. Choose a structural family at the requested period, using a compact canonical index.
1. Choose its odd relative-value rearrangement and common phase as numerical color controls.
1. Specify the phase precision, including whether to preserve the exact phase possibilities of an older recipe.

This separation explains both conclusions we reached: a finite set of structural families is sufficient at fixed domain size, while retaining every exact output from arbitrarily large tail moduli requires unbounded phase precision. The tail family stays structurally fixed; its exact output sets keep growing.

## Sources

- [October 25 theory report](2026-10-25-pattern-space-theory.md), Sections 2–4: equivalence, normalization, exact output counts, family classification, and sampling; Sections 7.2 and 7.5: full-grid and checkerboard symmetries; Section 12: variation and color contracts.
- [October 13 XOR post-power theory](../2026-10-13-post-power/2026-10-13-xor-post-power-theory.md): balanced period rule, coefficient motifs, and the earlier valuation/odd-part classification.
- [October 11 post-power investigation](../2026-10-11-post-power/2026-10-11-post-power-range.md): the actual domain versus generation-size distinction, inherited sampling range, and changing common phases.
- [Current generator source](../../index.html): `newStyle` samples powers, `channelParameters` selects odd multipliers and offsets, and `colorTable` applies the post-power and modulus. The implementation comparison describes the source inspected on November 1, 2026.
