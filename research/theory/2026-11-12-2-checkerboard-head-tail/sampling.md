# Uniform sampling with general post-polynomials

Use the general scope and connected half-period components in [theory.md](theory.md). All claims here concern exact numerical or order classes before palette quantization. Choosing a measure on aesthetically distinct fabrics is a separate design decision.

## 1. Which spaces admit uniform sampling

At a fixed dyadic modulus and fixed pre-function, the polynomial numerical table space is finite. Uniform shift-class sampling is therefore well-defined. Restricting it to requested periods, or to polynomials at their own minimum period precision, gives another finite space.

Across all post-polynomials and their own minimum moduli, order classes are finite and admit the direct sampler below. Shift classes are generally infinite. In the present graph formulation they are infinite exactly when the half-period graph has at least two connected components. With one connected component, every admissible minimum-period table has exactly two antipodal values; its finite shift and order spaces coincide and have $2^{n-1}-1$ classes, where $n$ is its number of vertices.

**Proof.** A connected component can use at most one antipodal pair. With one component, every nontrivial binary partition of its vertices is attainable by interpolation; fixing the anchor's side removes the global exchange of the two labels. With at least two components, one can split a component across an antipodal pair and put another component at a third freely movable dyadic position. If a singleton component exists, it can supply the third value; if all components were singletons the target would be unattainable. The present basic fields always have a nontrivial component. Infinitely many choices of that third position preserve order and minimum period and are realized by integer interpolation. This specializes the [earlier infinite-shift theorem](../2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#75-exactly-when-the-unrestricted-polynomial-shift-space-is-finite).

All head and tail styles here have infinitely many such shift classes at $N\ge16$. In the tail at side eight there is one two-vertex component, giving just one shift and one order class. The graph formula handles the remaining small-side exceptions.

A probability distribution assigning equal mass to every member of a countably infinite set does not exist. Therefore a request for uniform unrestricted shift sampling must choose a fixed modulus, a finite precision cap with duplicate normalized tables removed, or an explicitly nonuniform precision distribution. An arbitrary cutoff in polynomial degree is unnecessary for fixed precision.

## 2. Exact shift sampling at a fixed modulus

Let the raw scalar vertices be $z_1,\ldots,z_n$, with reference $z_0$. The anchored columns

$$
g_j=(z_i^j-z_0^j)_i\bmod M,\qquad1\le j<n,
$$

span every integer-polynomial output table up to a constant phase. Monic division by $\prod_i(z-z_i)$ proves that no higher degree is needed. Dyadic elimination gives independent generators of orders $2^{e_j}$; choosing their coefficients independently in $[0,2^{e_j})$ samples every anchored numerical table exactly once.

Let $D$ be the edge-difference map. Ordinary period retention excludes $\ker D$. For minimum-period precision, first restrict to $W=\ker(2D)$ inside the polynomial table space and then exclude $\ker D$. Diagonalizing the coefficient constraint matrix gives a basis for the former kernel; evaluating and diagonalizing that image removes duplicate polynomial descriptions. Each remaining table has equal probability. If the valid set is nonempty, the final rejection accepts at least one half, because the excluded subgroup is proper.

If $B$ is the total number of independent bits in the chosen table subgroup and the edge-difference image has $e$ independent bits, its exact valid count is

$$
2^B-2^{B-e}.
$$

The proof uses the equal sizes of all fibers of a finite group homomorphism. It applies to signed or nonmonotone polynomials and to polynomial collisions. [ShiftSampler](core.py) returns numerical tables; the prototype is not integrated into the notebook or app. Uniform shift draws must not be advertised as uniform order draws, since several numerical spacings can have the same anchored ranks.

From this directory:

```python
from random import Random
from core import Basic, ShiftSampler

basic = Basic(128, 6, (3, -2, 1), 'add')
sampler = ShiftSampler(basic, 2048, minimum=True)
values = sampler.draw(Random(0))
```

The sampler reports an empty space if no polynomial has the target periods at that precision. Setting `minimum=False` instead samples all polynomial tables retaining the target at that fixed modulus.

## 3. Direct order counts for components of any sizes

Write the component sizes as $s_1,\ldots,s_c$. A component that uses both ends of a specified antipodal pair has $w_i=2^{s_i}-2$ possible endpoint assignments. A component using one value can instead join an endpoint group or an unpaired color group. Let $e_b$ denote the elementary symmetric polynomial of degree $b$ in $w_1,\ldots,w_c$, with $e_0=1$.

Let $S(b,k)$ be the Stirling number counting partitions of $b$ labeled objects into $k$ nonempty sets. Define

$$
A_j(n)=n![x^n]\left(\frac{e^x}{2-e^x}\right)^j.
$$

This counts placements of $n$ labeled monochrome components into $j$ specified endpoint groups and $j$ gaps, each gap containing a sequence of unpaired groups. Each component placed in a gap carries all its vertices together.

For exactly $k$ antipodal pairs of output groups, the number of rooted representations is

$$
R_k=\sum_{b=k}^c e_b\,k!S(b,k)\,A_{2k}(c-b).
$$

**Proof.** Choose the $b$ components that actually cross their assigned antipodal pairs, with assignment weight $e_b$. Assign them onto the $k$ ordered pairs, each receiving at least one crossing component, in $k!S(b,k)$ ways. Place the remaining monochrome components in endpoint groups and intervening gaps, counted by $A_{2k}(c-b)$. This construction is unique once the root and first endpoint are specified.

Each anchored circular order has exactly $2k$ rooted representations. Thus the complete number of attainable order classes is

$$
\boxed{T(s_1,\ldots,s_c)=\sum_{k=1}^c\frac{R_k}{2k}.}
$$

All counts use positive integer arithmetic. For computation, put $a_{j,\ell}=[u^\ell]((1+u)/(1-u))^j$. Then

$$
a_{j,0}=1,\quad a_{j,1}=2j,\quad (\ell+1)a_{j,\ell+1}=2j a_{j,\ell}+(\ell-1)a_{j,\ell-1},\qquad A_j(n)=\sum_{\ell=0}^n\ell!S(n,\ell)a_{j,\ell}.
$$

The coefficient recurrence follows by differentiating the generating function and multiplying by $1-u^2$. [fast_sampler.py](fast_sampler.py) uses this univariate formula. [order_sampler.py](order_sampler.py) independently counts and samples by component-type subset recurrences; agreement with it and with exhaustive small ordered partitions is part of the saved verification.

## 4. Uniform draws and polynomial realizations

Choose $k$ with weight $R_k/(2k)$, choose $b$ with its summand weight, choose the crossing component subset with weight equal to the product of its $w_i$, and sample each subsequent finite choice uniformly. Crossing endpoint assignments exclude the two monochrome bit strings. The remaining components are assigned to endpoint groups or ordered gap partitions with their exact combinatorial weights. Finally rotate the color-group order to put the reference cell first.

For one resulting class with $k$ antipodal pairs, the probability is

$$
\frac{R_k/(2k)}{T}\frac{2k}{R_k}=\frac1T.
$$

This proves uniformity over classes, independently of the number of polynomial representatives or their precision. The only local bit-string rejection has acceptance at least one half. Polynomial coefficients need not be generated for a rank-color renderer. The uniformity argument assumes unbiased integer draws with enough entropy; a fixed 64-bit draw cannot uniformly cover a class space larger than $2^{64}$. The seeded examples below demonstrate reproducibility rather than a claim of uniformity over a finite seed set.

```python
from random import Random
from core import Basic
from fast_sampler import OrderSampler
from realize import realize

basic = Basic(256, 6, (3, -2, 1), 'add')
sampler = OrderSampler(basic.components)
rank, structure = sampler.draw(Random(0), anchor=basic.anchor)
# Optional: a polynomial realizing exactly this order at its own minimum M.
H, M, values = realize(basic, structure)
```

The returned rank tuple indexes the distinct raw scalar values. Use `basic.indices` to expand it into the current displayed coordinate map. Interpolation degree is below the number of raw vertices. Its precision can be much larger than another polynomial realization of the same order; this is not a globally smallest-modulus constructor.

In the tail, all component sizes are two and their number is $N/8$. This recovers the earlier matching sampler with half as many input pairs as no-pre-operation pseudo-square XOR at the same displayed side. The tail order counts for sides 8, 16, 32, and 64 are respectively 1, 12, 2,640, and 1,986,611,520. OR and XOR at any pre-power at least four have those same abstract counts for the corresponding side, including in the head.

## 5. Uniform unions over pre-functions and coarse families

Uniform pre-functions followed by uniform conditional order draws generally bias the union of output classes. Different pre-functions can have different numbers of orders, and the same spatial order can belong to several pre-functions or combiners.

There is an exact finite union algorithm for every fixed domain. Enumerate the independent twist coordinates from [the finite-twist theorem](theory.md#5-finite-twist-coordinates-at-every-domain) for the requested head powers and combiners. Keep one base for each distinct spatial raw equality partition. For base $i$, compute its class count $T_i$ with the component sampler. Choose $i$ with probability $T_i/\sum_jT_j$, then choose one of its order classes uniformly. If that spatial order belongs to $b$ retained bases, accept it with probability $1/b$; otherwise repeat.

**Proof.** Each occurrence of a class has probability $1/\sum_jT_j$. A class with multiplicity $b$ is proposed with probability $b/\sum_jT_j$, so the correction makes every union class have the same accepted mass. Membership in another base is exactly constancy on each of its raw value groups: the full-period and antipodal properties already belong to the spatial order itself, and interpolation supplies a post-polynomial on that base. Raw equality partitions may therefore be deduplicated before sampling.

[UnionSampler](union_sampler.py) implements this for an explicit finite base list. Its acceptance is at least the reciprocal of the number of retained bases. At side 64, the complete 208 general twist functions across the four head powers give 832 combiner/pre-function descriptions and 689 distinct raw partitions. The saved run draws from this complete union; it is not limited to the gallery's sixteen twists.

At larger domains, exhaustive enumeration of all twist functions rapidly becomes expensive: pre-power two alone has over eight million functions at side 1024 and over 34 billion at side 4096. The finite union algorithm remains exact, but an efficient complete-union implementation at those sizes is unresolved here. Conditional sampling for a fixed arbitrary twist does not require that enumeration and works across the tested range. Choosing a finite explicit style set and applying the union correction is another exact option, with a correspondingly restricted sample space.

## 6. Measured limits

The saved run checks the structural and twist-coordinate results at every dyadic side from 8 through 4096. Conditional head count construction and order draws are benchmarked through side 1024, using pre-power two, ADD, and the identity twist, which already has mixed component sizes. Approximate count-build times at sides 64, 128, 256, 512, and 1024 were below 1 ms, 2 ms, 17 ms, 0.22 s, and 4.0 s. Subsequent rank draws took milliseconds or less. These timings exclude expanded grids, color rendering, and polynomial interpolation; counts can be reused for another base with the same component sizes.

The side-64 complete-union run built its 689 entries in about 0.24 s and drew 40 accepted spatial rank tables in about 0.15 s total on this machine. These are dated measurements, not a runtime guarantee. Side-2048 and side-4096 conditional samplers were not benchmarked, and their larger exact integer count tables can be expensive. The source hashes, full timings, and all comparison counts are in [results.json](results.json).
