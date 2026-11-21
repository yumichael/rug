# Spatial sampler comparison

The **Compare checkerboard samplers** section of [explore.py](../../interactive/notebooks/explore.py) implements the newest personal-notes request. It compares distributions over spatial classes, independently of formula multiplicity. This report separates existing results, new finite-space arguments, finite-precision color choices, and unresolved scope. The implementation is [sampler_comparison.py](../../interactive/ruglab/sampler_comparison.py); [tests](../../interactive/tests/test_sampler_comparison.py) supply reproducible checks.

## Scope and groups

Use the vertical checkerboard-opposite map or its doubled checkerboard-opposite layout on a power-of-two side $N\ge8$, shared pre-twist $f(t)=t+2t(t-1)Q(t)$, arbitrary finite integer polynomial $Q$, and combiners OR, XOR, ADD, ABSDIFF. The head powers satisfy $q<\log_2N+\nu_2(q)$. Group them by the exact relative depth $d=q-\nu_2(q)-2$, then add the erased-branch tail. At side 64 these groups are 2, 4, {6, 8}, and tail. Higher domains introduce additional depth groups; lower domains omit absent groups. The grouping uses the existing bit-structure result, not an assertion that it is a proved aesthetic taxonomy.

The [finite-twist theorem](../2026-11-12-2-checkerboard-head-tail/theory.md#5-finite-twist-coordinates-at-every-domain) gives independent finite coordinates for every distinct pre-function, including arbitrary-degree and signed twists. For the head, the gallery enumerates this entire finite image for each listed pre-power, then deduplicates actual spatial equality tables. The common raw tail partition uses one canonical representative; the separate finite-window strategy enumerates its full twist image. It does not use the notebook's three sample twists. Canonical partition labels follow first spatial occurrence. At side 64 the head groups contain 416, 224, and 49 distinct raw partitions, respectively, from 512, 256, and 64 formula descriptions.

For unrestricted post-polynomial order classes, the [tail theorem](../2026-11-12-2-checkerboard-head-tail/theory.md#3-what-is-exact-in-the-tail) identifies every erased pre-power and twist with the same class space. Thus the canonical tail pre-power is complete for the unrestricted minimum-precision and all-precision strategies. Its raw equality table is also common. For the complete isometric strategies, the finite tail reduction below covers all erased exponents and twists. The extra finite-window strategy instead concerns all twists of the canonical tail pre-power; it is explicitly a bounded-precision comparison.

A class is a partition or circular order of scalar values at visible cell positions, before colormap quantization, without identifying rotations, reflections, or translations of the field. Full period means least horizontal and vertical periods $(N,N)$; oblique periods are not excluded. Circular color rotation is quotiented out by anchoring and restored by an independent seeded uniform offset. Repeated formula descriptions never contribute extra probability. Each distribution is conditional on its power group and checked combiners. With a subset selected, build the union from that subset before deduplicating spatial classes, correcting for overlap, or applying order weights. Every tail combiner has the same surviving operand, so the tail reductions can use any checked combiner as a witness.

## Implemented strategies

| Strategy                                  | Exact discrete target                                                                            | Output placement                                                                            |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| Polynomial order union, minimum M         | Existing minimum-precision order union, including allowed mergers                                | Existing interpolation values and modulus                                                   |
| Uniform raw equalities, IID               | Distinct raw spatial partitions                                                                  | Independent finite-precision uniform positions                                              |
| Uniform nonmerging orders, IID            | All circular permutations of each distinct raw partition                                         | IID positions                                                                               |
| Uniform raw equalities, equal             | Same equality target                                                                             | Randomly permuted exact equal spacing                                                       |
| Uniform nonmerging orders, equal          | Same order target                                                                                | Randomly permuted exact equal spacing                                                       |
| Uniform raw equalities, Dirichlet         | Same equality target                                                                             | Randomly permuted Dirichlet circular gaps                                                   |
| Uniform nonmerging orders, Dirichlet      | Same order target                                                                                | Same gap law                                                                                |
| Isometric equalities                      | All distinct full-period residue partitions across all post-moduli, on the listed bases          | Identity isometry at a witnessing modulus                                                   |
| Isometric orders                          | All attainable full-period isometric circular orders across all post-moduli, on the listed bases | Exact low-precision witness or high-precision construction below                            |
| Cell-mass spacing                         | Uniform raw equalities                                                                           | Random group order with group value at the midpoint of an arc proportional to its cell mass |
| Isometric finite window                   | Distinct isometric orders over explicitly chosen precision offsets                               | Exact witness at its enumerated precision                                                   |
| Polynomial order union, all precisions    | All full-period circular ordered coarsenings of any raw partition                                | Integer-polynomial interpolation-compatible level scaling                                   |
| Polynomial equality union, all precisions | All full-period coarsenings of any raw partition                                                 | Random circular order and interpolation-compatible level scaling                            |

The minimum-precision sampler is the existing multiplicity-corrected component sampler. It is not the same target as unrestricted precision: full period at a polynomial's smallest modulus forces each connected half-period component to occupy at most one antipodal pair. The all-precision additions remove that restriction and are explicitly separate strategies.

Synthetic color placements in the raw-equality and nonmerging-order strategies are lookup colors, not claims that those exact levels are minimum-modulus integer polynomials. Their equality and order targets are attainable at unrestricted precision by the interpolation construction below. Stored specifications use exact lookup tables and preserve native evaluation and export. Equal spacing can require a non-dyadic lookup modulus; it remains exact as a color assignment. M-selection is fixed to Catalogue for this gallery so another selector cannot silently alter a strategy's distribution. Both opposite-checkerboard layouts reuse exactly the same draw, lookup values, modulus, and color offset. The doubled layout copies opposite-parity source cells into their horizontal neighbors; its source-coordinate projection preserves the class information and cell multiplicities of the checkerboard view.

## Uniform unions and nonmerging orders

For a raw partition with $k$ groups, the number of anchored circular orders with no merger is $(k-1)!$. Different raw partitions have disjoint nonmerging order spaces because their equality signatures differ. Therefore choose a raw partition uniformly for equality targeting, or with weight $(k-1)!$ for nonmerging order targeting, followed by a uniform circular permutation. IID exchangeable levels, randomly permuted equal levels, and randomly permuted exchangeable Dirichlet gaps all induce a uniform circular order. They differ in spacing, not this discrete order law.

For unions that allow mergers, use the [existing union correction](../2026-11-12-2-checkerboard-head-tail/sampling.md#5-uniform-unions-over-pre-functions-and-coarse-families): weight each retained base by its conditional class count, draw uniformly in that base, and accept with reciprocal multiplicity. A candidate belongs to another base exactly when its spatial table is constant on every raw group of that base. Each occurrence has the same proposal mass, so reciprocal multiplicity makes every accepted spatial class equiprobable. The interpolation spacing for a minimum-precision class can depend on the chosen witness base; uniformity is over the discrete class, not over its continuum of numerical spacings.

### New all-precision counts

Let $n$ be the number of raw vertices and $c$ the number of connected half-period components. Put $B(n)=\sum_k S(n,k)$ and $F(n)=\sum_k S(n,k)(k-1)!$, where $S$ denotes Stirling numbers of the second kind. The numbers of full-period equality and circular order classes on one base, at unrestricted precision, are respectively

$$
B(n)-B(c),\qquad F(n)-F(c).
$$

Proof: any finite assignment can be realized up to a common dyadic scale by integer interpolation. An assignment loses the required half-period exactly when it is constant on every half-period component. Such assignments are partitions or circular ordered partitions of the $c$ components. Subtracting these from the unconstrained partitions of $n$ vertices proves both formulas. Both axis half-period graphs coincide for the present checkerboard bases, by the existing research. Uniform set partitions are sampled by the Stirling recurrence, ordered by a uniform group permutation when needed, and conditioned on full period. The resulting sampler uses these exact counts in the same union correction.

For realization, let $D$ be the largest 2-adic valuation of a Lagrange denominator on the actual raw nodes. Multiply target rank levels by $2^D$, and multiply a power-of-two color denominator by the same factor. Every scaled Lagrange coefficient is integral modulo that dyadic modulus because each denominator's remaining odd part is invertible. This proves realizability without expanding the coefficients in previews. This construction need not be at its own minimum precision.

## Isometric equality classes

A 2-adic isometry preserves every difference valuation. At post-modulus $2^m$, two raw nodes therefore have equal outputs exactly when their input difference is divisible by $2^m$. These residue partitions do not depend on which isometric polynomial was used. The first usable $m$ is one greater than the smallest valuation of a nonzero half-edge difference. Enumerate all larger $m$ until the raw nodes are distinct modulo $2^m$; beyond that no new equality partition occurs. Canonicalizing visible tables across bases and moduli gives a finite complete equality union. The identity polynomial witnesses every retained partition. Selecting uniformly from this deduplicated union proves equality uniformity; there is no attempt to make its conditional orders uniform.

## Isometric order classes at fixed precision

An integer polynomial is a global 2-adic isometry exactly when its linear coefficient is odd, the sum of its positive even-degree coefficients is even, and the sum of its odd-degree coefficients above degree one is even. Necessity follows from its derivatives at zero and one being odd and from opposite parities remaining distinct. Conversely these conditions give a bijection modulo four and an odd derivative everywhere. Lifting one bit at a time gives a permutation at every dyadic modulus and hence an isometry.

Thus anchored isometric output tables form an affine module: start with $z$, add integer combinations of $2z,2z^2,2z^3$, the even-degree differences $z^j-z^2$ for $j\ge4$, and the odd-degree differences $z^j-z^3$ for $j\ge5$, with each generator anchored at the reference. Finite evaluation followed by the existing dyadic diagonalization gives independent coordinate ranges. Enumerate that finite affine image, canonicalize the spatial circular ranks, and retain one witness per class.

This is complete at fixed $2^m$ with degrees below the first $L\ge4$ for which $\nu_2(L!)\ge m$. Division by the monic falling factorial of degree $L$ reduces every integer polynomial to that degree bound without changing its values modulo $2^m$. The discarded term is zero modulo four and has even derivative at every integer, so the isometry conditions are preserved. The finite-window strategy takes the deduplicated union over explicitly selected offsets from each base's first period-preserving bit, not a uniform mixture of moduli.

### New reduction for all post-precisions

Every nonmerging circular order of a fixed finite raw node set is attained by a global isometric integer polynomial at sufficiently high precision. To see this, let $D$ be the maximum denominator valuation above, and choose $S$ divisible by $2^{D+2}$ and larger than the raw value span. For arbitrary distinct ranks $r_i$, prescribe

$$
H(z_i)=z_i+Sr_i\pmod{2^m}
$$

with $2^m$ larger than all prescribed values. The Lagrange interpolation of $Sr_i$ has every coefficient divisible by four, by the denominator argument. Therefore $H(z)=z+4P(z)$ modulo $2^m$ for an integer polynomial $P$. Any integer lift is globally isometric. The stride ensures that the prescribed rank order is realized. Translating the reference to zero preserves the isometry and circular order.

If $b$ is the largest valuation of any nonzero raw node difference, all $m>b$ have no mergers, and their order classes are already in that symbolic nonmerging union. Only the finitely many full-period moduli with $m\le b$ need explicit enumeration. Remove any enumerated coarse class whose equality partition is already a raw partition in the base union, because all its orders are covered by the symbolic part. Deduplicate the remaining coarse orders. Sample the symbolic raw partitions with weights $(k-1)!$ and each extra coarse order with weight one. The two supports are disjoint, proving uniformity over all post-precisions on the listed bases.

This theorem does not say that a randomly chosen isometric polynomial typically gives those high-precision spacings. It provides a witness for each order class. The preview can show how uneven those particular witness spacings are.

### New finite isometric tail reduction

Write $N=2^r$, $q=2^wu$ with odd $u$, and $S=2^{w+2}$. In the tail a raw value is an odd operand value in $1\pmod S$, and the common raw equality partition is independent of $q$ and $Q$. All nonmerging orders are therefore already covered by the preceding theorem. Only merging post-precisions require a reduction.

Every merging post-modulus divides the pre-modulus $K=N2^w$, since distinct raw values lie below $K$. At such precision the shared twist is an invertible global polynomial isometry; its inverse modulo the post-modulus is a polynomial, obtained by iterating a finite permutation. It can consequently be absorbed into the post-isometry. An odd exponent part can also be absorbed. On odd residues modulo $2^m$, odd powers have odd-power inverses. For odd $u>1$, the polynomial $z^u+z(z^{2^m}-1)$ agrees with $z^u$ on those residues and satisfies the global isometry parity conditions; $u=1$ uses the identity. Thus odd exponent parts do not change the attainable merging order union at fixed $w$.

After writing raw values as $1+St$, a post-polynomial has normalized Taylor form $a_1t+Sa_2t^2+S^2a_3t^3+\cdots$ with $a_1$ odd. At any merging precision its normalized modulus is at most $N/8$. Therefore higher Taylor terms vanish for $w\ge r-5$. The normalized powered-input motifs themselves stabilize up to odd multipliers at $w\ge\max(1,r-4)$ by the existing [whole-row valuation theorem](../2026-10-13-post-power/2026-10-13-xor-post-power-theory.md#6-stronger-valuation-result-the-whole-high-v-tail-repeats), applied with coordinate domain $N$. Those multipliers are absorbed by the affine post-isometry. Hence only

$$
1\le w\le\max(1,r-4)
$$

need representatives for the complete merging union. For each $w$, choose any odd $u$ large enough that $2^wu\ge r+w$. No twist enumeration is needed for these tail representatives. At $N=8$ there are no full-period merged tail partitions; at $N=16$ their normalized precision is at most two, and direct square lifting gives the same valuation-one representative. These cover the small cases outside the whole-row theorem's stated range. The tests compare these reductions against extra valuations, odd exponent parts, and signed twists.

## Spacing and limits

IID positions are sampled without replacement on a $2^{53}$ grid, the finite-precision approximation to distinct independent continuous uniform points. Equal levels use exact integer ranks modulo the number of groups. Dirichlet gaps are generated with gamma variates at the chosen positive concentration, then quantized to positive integer gaps. Very small concentrations have a one-quantum floor and should not be interpreted as exact continuum draws. The ideal symmetric Dirichlet law has mean gap $1/k$ and gap variance $(k-1)/(k^2(k\alpha+1))$. Concentration one matches the ideal IID circular gap law; larger concentrations approach equal spacing. Every strategy applies a separate uniform circular offset, shared across matching seed/group/draw comparisons but independent of its internal draw choices.

Cell-mass spacing assigns an arc of length $p_i$ to a group occupying fraction $p_i$ of visible cells and puts its color at that arc's midpoint. Coupling uniform mass in each arc to that midpoint moves it by at most $\max_i p_i/2$ around the circle. This is a simple additional comparison of pixel-weighted color spread; it does not change the uniform raw-equality target.

The complete twist count is checked before enumerating; the default limit is 4,096 descriptions per group. A separate retained-grid work bound is 16 million cells, and deduplicated isometric spatial signatures have a 64 MiB budget. Isometric affine tables are enumerated only if the complete job fits the configurable table limit. Failed feasibility checks are cached so an unavailable row does not repeat the calculation for every draw. A limit produces an unavailable panel; it never changes the target to a partial or curated subset. Larger field sizes remain selectable, but some exact unions are computationally unavailable. Raising limits can be costly. The isometric all-precision reduction removes the infinite modulus axis, not the potential cost of its finite coarse part.

## Validation

The [recorded inventory](results.json), regenerated with [verify.py](verify.py), lists exact base and equality counts and the availability of finite isometric enumerations. The checked-in tests compare small circular partition counts with exhaustive enumeration; verify exact reciprocal-multiplicity masses on a small union; compare isometry coordinates with brute-force parity-constrained polynomials; confirm side-64 complete twist and partition counts; and round-trip all strategies through native evaluation with the requested axis periods. They also exercise exact-limit failures and dynamic catalogue construction. These are bounded checks of the implementation alongside the arguments above, not a visual ranking of the strategies.

Run from `research/interactive`:

```sh
MPLCONFIGDIR=/private/tmp/rug-mpl .venv/bin/python -m pytest tests/test_sampler_comparison.py -q
```

Regenerate the inventory from the repository root:

```sh
MPLCONFIGDIR=/private/tmp/rug-mpl research/interactive/.venv/bin/python research/theory/2026-11-15-sampler-comparison/verify.py
```
