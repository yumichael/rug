# Uniform order classes across all minimum moduli

This research prototype samples the complete union of attainable anchored order classes over minimum-period post-moduli. It uses no pre-operation, operand modulus $K = 2N$, the current opposite-checkerboard phase, and target least horizontal and vertical periods $N$, where $N$ is a power of two at least four. Pseudo-square means $H(2N-z) \equiv H(z)\pmod M$ on odd inputs. It does not quotient spatial rotations, translations, or reflections. Orders identify common circular color shifts through an anchored rank signature, as in the workbench.

The interpolation and minimum-period criteria come from the checked-in November 4 research report, Sections 2.2 and 7. The combinatorial classification, counts, and direct sampler below are a new extension developed in this chat. The scripts in this folder preserve that prototype for further review.

## 1. Relationship to existing results

The [November 3 companion](../2026-11-02-xor-polynomial-period/2026-11-03-xor-polynomial-examples.md)'s no-increase/2× table fixes one exponent valuation $v$ and the modulus $C\cdot 2^v$. For $v = 1$, the single-power and polynomial counts are 2,048 and 2,048 at $C = 1024$; 8,192 and 8,192 at $C = 2048$; and 32,768 and 65,536 at $C = 4096$. It explicitly does not count the union over valuations, much less all arbitrary pseudo-square post-polynomials. In the current notation $C = 2N$.

The [November 4 report](../2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md), Sections 6.1–6.3, proves shift/order equivalence for balanced monomials and valid same-valuation sums because their distinct values fill a complete evenly spaced grid. Section 6.4 explains why arbitrary polynomial classes need not share that property. Section 7.5 proves that unrestricted polynomial shift classes at minimum-period precision are infinite whenever an attainable table has at least three output groups. Apply that theorem to the fixed feature $(z-N)^2$, whose polynomial functions give the whole pseudo-square family. For $N \ge 8$ the infinite-shift obstruction applies. A uniform probability distribution assigning equal mass to each of these countably infinitely many shift classes does not exist.

A concrete counterexample already uses ordinary even polynomials at one fixed modulus. At $N = 8$, $K = 16$, $M = 512$, let $F(z) = z^4+30z^2-31$. Its outputs on $z = 1,3,\ldots,15$ are $(0,320,320,256,256,320,320,0)$. The polynomial $3F$ gives $(0,448,448,256,256,448,448,0)$. Both tables are complement-symmetric; both have axis periods $(8,8)$, becoming $(4,4)$ modulo 256. They have identical anchored ranks, but distinct normalized spacings, namely $\{0,1/2,5/8\}$ and $\{0,1/2,7/8\}$.

Uniform order-class sampling over all minimum moduli is nevertheless finite and can be done directly, without choosing a modulus or polynomial first.

## 2. Complete combinatorial description

Complement symmetry identifies $z$ with $2N-z$, leaving $n = N/2$ scalar input classes. Represent them by the positive odd magnitudes $|z-N|$. Half-period translations connect each magnitude $x$ to $N-x$. These form $p = N/4$ disjoint pairs of input classes. The prototype labels the two nodes in pair $i$ by $2i$ and $2i+1$, corresponding to magnitudes $2i+1$ and $N-2i-1$.

At a minimum-period modulus, each such input pair must receive either equal output values or values separated by exactly one half of the normalized color circle. At least one pair must receive distinct values. Complement symmetry links the two grid axes, so their half-period exclusions are equivalent and minimum precision makes both disappear modulo $M/2$.

An order class is therefore a partition of the $n$ labeled input classes into color groups, together with a circular order of those groups, anchored at the group containing one fixed reference input. Its validity has two exact tests:

1. Each color group has at most one distinct partner reached by a nontrivial half-period edge. Thus the graph on color groups, ignoring loops, is a nonempty matching.
1. The endpoints of those matching edges admit antipodal positions in the stated circular order. Remove the unpaired color groups. The remaining cyclic list must be an ordered list of paired groups followed by their partners in the same order.

These conditions are sufficient: choose dyadic positions for the paired groups in one half-circle and place their partners one half-turn later; insert the unpaired groups in their required gaps. The interpolation theorem realizes these values with an integer polynomial in $(z-N)^2$ at a sufficiently large power-of-two modulus. Every half-period difference is zero or $M/2$, with a nonzero difference, so that modulus is the minimum giving the requested periods for the resulting formula.

## 3. Counting and uniform sampling

Group the $p$ labeled input pairs into components. A component is either a single color group containing both endpoints of each of its input pairs, or two antipodal color groups with at least one input pair crossing between them. A component containing $a$ input pairs has $4^a-2^a$ ordered assignments to the two antipodal groups: all endpoint assignments except those in which every input pair stays together.

Let $F_j$ count ordered set partitions of $j$ labeled input pairs. Then $F_0 = 1$ and

$$
F_j=\sum_{s=1}^j\binom js F_{j-s}.
$$

A rooted double block consists of an ordered pair of antipodal color groups, a sequence of unpaired color groups following its first endpoint, and another such sequence following its second endpoint. Define

$$
D_j=\sum_{b=0}^j\binom jb F_bF_{j-b},\qquad
Y_s=\sum_{a=1}^s\binom sa(4^a-2^a)D_{s-a}.
$$

Let $R_{p,k}$ count ordered sequences of $k$ rooted double blocks using all $p$ labeled input pairs. Its recurrence is

$$
R_{0,0}=1,\qquad
R_{p,k}=\sum_{s=1}^{p-k+1}\binom ps Y_sR_{p-s,k-1}.
$$

An order class with $k$ antipodal group pairs has exactly $2k$ rooted representations, one for each choice of paired color group as the first endpoint. Consequently the total number of order classes is

$$
T_p=\sum_{k=1}^p\frac{R_{p,k}}{2k}.
$$

The sampler chooses $k$ with weight $R_{p,k}/(2k)$, then samples an ordered rooted representation uniformly by the recurrence. Within a representation, subset choices and endpoint assignments are uniform. It forms the circular group order by listing all first endpoints and their intervening unpaired groups, then all second endpoints and their intervening groups, and finally rotates to the fixed reference group.

For any one order class with $k$ pairs, its probability is

$$
\frac{R_{p,k}/(2k)}{T_p}\cdot\frac{2k}{R_{p,k}}=\frac1{T_p}.
$$

This proves exact uniformity. The implementation uses integer counts and rejection-free weighted integer draws for the combinatorial choices. The only local rejection draws an endpoint assignment with at least one crossing input pair; its acceptance probability is at least one half.

## 4. Counts and checks

| Side N | Input pairs p | Order classes |
| -----: | ------------: | ------------: |
|      4 |             1 |             1 |
|      8 |             2 |            12 |
|     16 |             4 |         2,640 |
|     32 |             8 | 1,986,611,520 |

Independent exhaustive enumeration of ordered partitions agrees with the counts, including the count for each number of antipodal pairs, through $N = 16$. The auxiliary enumeration also checks the abstract matching model with three input pairs; that model is not itself a power-of-two Rug domain.

For $N = 4,8,16,32$, twenty-five sampled classes at each size were realized as explicit integer post-polynomials. Native workbench evaluation matched every prescribed output cell; all had least periods $(N,N)$, and reducing $M$ by two lost that target. The shift/order counterexample above was also checked with native signatures and period scans.

On this machine, building the exact count tables for $N = 1024$ took about 2.3 seconds, and drawing one order table took about 8 milliseconds. This excludes polynomial realization and rendering. The count has 2,302 bits. Tables are reused for subsequent draws at the same side length.

## 5. Usage and representative precision

The sampler uses only the standard library. From this research directory:

```python
from random import Random
from sampler import Sampler

N = 1024
sampler = Sampler(N // 4)
rank, structure = sampler.draw(Random(0))
```

The returned rank tuple has $N/2$ entries in the paired-node convention of Section 2. `count_orders.py` independently enumerates small order spaces. `realize.py` uses the research environment's ruglab package to construct polynomial representatives and verify exact grid values and periods.

The interpolation representative can have a much larger modulus than another polynomial realizing the same order class. It is at minimum-period precision for its own formula. Finding the globally smallest modulus among all polynomial representatives of a sampled order class is a separate canonicalization problem; the existing finite-bound search remains available. This does not change uniformity over sampled order classes.

For a renderer that colors by rank, the rank table can be used directly as a lookup after XOR and complement identification, so sampling need not wait for interpolation. The prototype is a mathematical sampler and verifier, not integrated app or notebook code.
