# Exact odd-odd equality and order sampling

At sufficiently high pre-precision, either MULT or CLMUL distinguishes every unordered pair of odd operand classes. With arbitrary integer post-polynomials, every merger of those pairs and every circular order of the resulting groups is attainable at sufficiently high post-precision. This gives a direct sampler for the full-period merger classes of any selected combiner subset containing a product combiner. The [notebook gallery](../../interactive/notebooks/explore.py) also compares the raw equality and order spaces, where distinctions made by the combiner are retained.

## Domain and finite raw family

Use an even pre-power $q=2^w u$ with $w\ge1$ and $u$ odd. The shared twist is $f(z)=z+2z(z-1)Q(z)$ for an arbitrary integer polynomial $Q$. The displayed side is $N=2^r\ge8$. Set $T=N/2=2^t$, $s=w+2$, $S=2^s$, and $K=2N2^w=ST$. Odd-odd selects original-grid coordinates $(2i+1,2j+1)$ using straight coordinates. A powered and twisted operand is $1+SA$ with $A$ in $[0,T)$.

Negating an odd coordinate modulo $2N$ preserves its pre-value. The odds in $[1,N)$ represent the $T$ sign classes. For two distinct representatives $x,y$, exactly one of $x-y$ and $x+y$ has valuation one and the other has valuation at most $r$. Lifting gives $\nu_2(x^q-y^q)=\nu_2(x-y)+\nu_2(x+y)+w-1<\log_2 K$. Thus the representatives give every code exactly once. Along either displayed axis the remaining half mirrors the first. A half-side shift exchanges representative $i$ with $T-1-i$, which toggles the code's top bit by the same lifting identity applied to $x$ and $x+N$. The twist preserves this because it is a 2-adic isometry. Every combiner here is symmetric, so a triangular array of $T(T+1)/2$ positions uniquely determines the whole spatial pattern. Two partitions are equal when their first-occurrence labels on this triangle agree.

Write a raw value as $z=C+SB$. Let $A,D$ be the two operand codes, $\oplus$ be XOR, and $\star$ be carryless multiplication. The formulas use ordinary nonnegative integer values before the post-modulus.

| Combiner | $C$ | $B$                             |
| -------- | --- | ------------------------------- |
| AND      | 1   | Bitwise AND of $A$ and $D$      |
| OR       | 1   | Bitwise OR of $A$ and $D$       |
| XOR      | 0   | $A\oplus D$                     |
| ADD      | 2   | $A+D$                           |
| ABSDIFF  | 0   | $\lvert A-D\rvert$              |
| MULT     | 1   | $A+D+SAD$                       |
| CLMUL    | 1   | $(A\oplus D)\oplus S(A\star D)$ |

The [previous work](../2026-11-19-monomial-first-pass/direct-sampling.md#direct-coordinates-for-pre-twists) gives direct finite ranks for all pre-maps at fixed $s$. Rows with $s<t$ are disjoint, and at $s\ge t$ the same odd linear maps in the original unit-logarithm coordinate occur at every valuation. For AND, OR, XOR, ADD and ABSDIFF, $B$ is independent of $S$. Their raw partition families are therefore complete through $s=\max(3,t)$. For MULT, $S\ge2T$ separates the sum and product into distinct parts. The pair is the unordered root set, with multiplicities, of the polynomial specified by its sum and product. For CLMUL, $S\ge T$ separates the XOR sum and carryless product, and the same root argument applies over the integral domain $\mathbb{F}_2[X]$. In either case the common partition in that regime is the unordered pair partition. Including $s=\max(3,t+1)$ gives both complete product families. Every raw partition retains the full axis periods. Fix the other operand at code zero for six combiners, or at code $T-1$ for AND, to expose the distinct operand values.

## Raw equality and nonmerging order draws

For a single AND, OR, ADD, or ABSDIFF draw, each distinct pre-map gives a distinct raw partition. For AND and OR, the diagonal gives the relabeling between two pre-maps with the same partition. It must preserve meet or join throughout the Cartesian table. A Boolean lattice automorphism permutes the singleton bits, and the relabeling is a 2-adic isometry fixing zero, so the valuation of each singleton fixes its position. For ADD or ABSDIFF, the axis with other operand zero gives the relabeling $h$ on codes, with $h(0)=0$. Equalities between $(i,1)$ and $(i+1,0)$ for ADD force $h(i+1)=h(i)+h(1)$. For ABSDIFF the pairs $(i,i+1)$ all have distance one, so $h(i+1)$ is at distance $h(1)$ from $h(i)$. The first step ascends, and a reversal would revisit the previous value. In both cases the permutation is the identity. Consequently each of these four scopes can draw directly by pre-map rank. Its group count is fixed at $T$, or $2T-1$ for ADD.

Other raw scopes deduplicate the finite tables by their spatial partition, including cross-combiner matches in the union. For example, the union stores the high-precision unordered pair partition only once. At side 64 there are 369 distinct raw partitions across the seven combiners. The individual counts in combiner order AND, OR, XOR, ADD, ABSDIFF, MULT, CLMUL are 64, 64, 16, 64, 64, 49, and 49.

For equality sampling, give each partition weight one. A partition with $k$ groups supports $(k-1)!$ circular orders. For nonmerging order sampling, use this weight and a uniform group permutation, anchored at the center cell. Distinct partitions have disjoint nonmerging order supports because a circular order determines its underlying partition. The sampler uses the existing IID, equal-spacing, Dirichlet-gap and cell-mass placement rules. IID placement draws distinct values from a grid of $2^{53}$ positions. Spacing and independent color rotation leave the class probabilities intact.

## Polynomial mergers and the product shortcut

Let $z_1,\ldots,z_k$ be distinct raw integer labels. For each label choose a target numerator $a_i$ at dyadic precision $L$ and set $D=\max_i\nu_2(\prod_{j\ne i}(z_i-z_j))$. Modulo $2^D L$, prescribe $2^D a_i$. In the Lagrange basis, the factor $2^D$ clears the power of two in every denominator, and the remaining odd part has a modular inverse. The resulting integer-coefficient polynomial realizes the chosen levels with fractions $a_i/L$. This proves attainability for every equality partition coarsening the raw partition and for every circular order of the new groups. Both the pre-modulus that distinguishes unordered pairs and the post-polynomial chosen for the target matter. The argument uses arbitrary finite integer polynomials. The [single-power analysis](../2026-11-19-monomial-first-pass/direct-sampling.md) studies a more restricted family.

Every raw partition of every requested combiner is a coarsening of the unordered pair partition. Since that finest partition is attainable by either product combiner, coarsenings in any selected subset containing MULT or CLMUL are exactly the coarsenings of that one partition. Equivalently, any equality pattern respecting both operand reflections and exchange of operands is attainable, and its groups can be placed in any circular order. The gallery conditions these draws on retaining both full axis periods.

To count that condition, put an edge between the labels of each pair of cells exchanged by the axis half-shift. The two axes yield the same constraints by symmetry. A coarsening loses the full period exactly when the assignment is constant on all $c$ connected components of this graph. If $k$ is the raw group count, the full-period equality count is the difference of the Bell numbers at $k$ and $c$. For circular orders, use the difference of $\sum_j {k\brace j}(j-1)!$ and its counterpart at $c$. For the finest partition, $k=T(T+1)/2$ and $c=(T/2)(T/2+1)/2$, since contracting both coordinate half-shifts replaces each operand by its two-element orbit. At side 8 this gives 115,970 full-period equality classes and 14,174,516 circular orders, including both merged and raw classes. The sampler draws a uniform set partition by the Stirling recurrence, adds a uniform circular order when requested, and rejects a lost period.

In a selection without either product combiner, more than one raw partition can support a merged result. Choose a raw partition weighted by its eligible class count. After drawing within it, accept with the reciprocal of the number of raw partitions on which the resulting field is constant within each raw group. Every eligible occurrence has the same proposal probability, so acceptance is uniform over distinct classes.

**Minimum M** uses the [existing component-order sampler](../2026-11-12-2-checkerboard-head-tail/sampling.md). At the minimum period-preserving modulus of a fixed polynomial, every half-shift edge has either equal or antipodal outputs and at least one edge is antipodal. Conversely, component placements with this property lift by the same interpolation argument, with full period at their chosen precision and with the half-shift restored one bit below it. The ordered placement depends on the visible field, so the same finest-partition shortcut and reciprocal multiplicity rule apply. The lookup records normalized interpolation levels. The described minimum is for the representative polynomial realizing those levels.

## Isometric equality and order weighting

A 2-adic isometry gives equal outputs at modulus $2^m$ exactly where the two raw inputs agree modulo $2^m$. The identity polynomial witnesses every such equality partition. Enumerate the full-period residue partitions up to the first modulus distinguishing all raw groups, then deduplicate them across maps, precisions, and combiners. Beyond $s=\max(3,t+1)$, the five simpler combiners retain the same code partitions after removing their common scale. The products have separated low and high parts. A low-bit projection then tests either a prefix of the sum or XOR, or the entire low part together with a prefix of the product. Increasing $s$ only adds zero positions between parts, so the same finite valuation cutoff suffices for isometric equality. At side 64, the union has 1,416 full-period residue partitions.

**Isometric equality union** uses the identity's color spacing at a retained modulus. **Residue partitions / uniform circular orders** instead applies the factorial weight to those same partitions and assigns freely permuted levels. Those orders have unrestricted polynomial witnesses. Sampling only orders of isometric post-polynomials on the merged residue partitions remains open here.

## Gallery and verification

Each draw is sampled with replacement from the deduplicated union for the selected side and combiner subset. The notebook defaults to side 64 and the deduplicated raw equality union. Preview and export use `cmr.emergency`, an independent circular rotation, and the original coordinate $(1,1)$ at the center. The exact lookup in each specification reproduces the preview's values and rotation. Choose Catalogue to retain the draw's precision.

The default enumeration budget is 16 million triangular cell comparisons, and merger samplers accept up to 768 raw groups. At these defaults the full raw union runs through side 128, and the full residue and merger unions run through side 64. The four single-combiner direct raw samplers avoid the enumeration limit. A scope that exceeds a limit shows an unavailable panel.

[verify.py](verify.py) checks the complete raw and residue sets per combiner and in union through side 64, using native operand operations and the earlier independent twist enumerator at extra valuations. It checks all 127 nonempty combiner subsets at side 16, reproduces the side-8 merger counts by enumerating set partitions, and verifies sampled fields against native evaluation and axis periods.

```sh
MPLCONFIGDIR=/private/tmp/rug-odd-mpl PYTHONDONTWRITEBYTECODE=1 research/interactive/.venv/bin/python research/theory/2026-11-21-odd-odd-samplers/verify.py
```
