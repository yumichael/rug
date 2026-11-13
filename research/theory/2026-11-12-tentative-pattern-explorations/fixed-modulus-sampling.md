# Uniform numerical sampling at a fixed modulus

Fix the no-pre XOR scope and pseudo-square criterion in [the symmetry report](xor-symmetry.md), with displayed side N, input modulus K = 2N, and post-modulus M = 2^m. This report samples distinct numerical tables modulo a constant color offset. The [order sampler](uniform-orders.md) instead covers the union of order classes over all minimum moduli. These are different sample spaces.

## 1. Independent Newton coordinates

The complete centered-square representation uses the n = N/2 distinct integer nodes

$$
t_i=(2i+1)^2,\qquad0\le i<n.
$$

Define

$$
B_0(z)=1,\qquad B_j(z)=\prod_{i=0}^{j-1}\left((z-N)^2-(2i+1)^2\right),
$$

and

$$
d_j=3j+\nu_2(j!)=2j+\nu_2((2j)!).
$$

Keep indices 0 ≤ j < n with d_j < m. Every pseudo-square polynomial output table has exactly one representation

$$
H(z)\equiv\sum_j a_jB_j(z)\pmod M,\qquad0\le a_j<2^{m-d_j}.
$$

For anchored shift classes, fix a₀ = 0. This anchors at either input z = N±1. Changing to another fixed reference, such as the gallery's first cell, is a bijection on anchored classes and does not affect uniformity. An independent uniform a₀ restores absolute circular color phase if that is desired.

**Proof.** Division by the monic polynomial $\prod_{i<n}(t-t_i)$ reduces any integer G(t) to degree below n. The monic Newton products form an integer unitriangular change of basis from those monomials. For odd x = 2s+1,

$$
\prod_{i<j}(x^2-(2i+1)^2)=4^j\prod_{h=s-j+1}^{s+j}h.
$$

The product of 2j consecutive integers is divisible by (2j)!, including negative integer arguments through the integer binomial identity. Hence B_j is always divisible by 2^d_j. At x = 2j+1 its value is exactly 4^j(2j)!, attaining that valuation. Evaluation successively at t₀,t₁,… gives a triangular matrix with those diagonal valuations. The stated coefficient reductions vanish as whole functions; triangular evaluation then proves uniqueness within the reduced ranges.

Consequently uniform independent coefficient draws give uniform distinct numerical tables without deduplication. Only O(log M) columns can survive, capped by N/2. Choosing an arbitrary polynomial degree and unrelated coefficient bounds does not supply this guarantee.

## 2. Period and minimum-precision conditioning

Within the symmetric table space, let Δ(z) = H(z+N)−H(z) modulo M for odd 0 < z < N. Complement symmetry gives Δ(N−z) = −Δ(z), linking the two input quarters. Therefore the requested axis periods are retained exactly when Δ is nonzero somewhere.

At minimum-period precision the exact additional condition is

$$
\boxed{2\Delta(z)=0\pmod M\text{ for every odd }z,\qquad\Delta\ne0.}
$$

All half-period differences are then zero or M/2, and at least one is M/2. The full period survives at M and is lost at M/2. The constraints are linear in the Newton coefficients. One may first sample uniformly in ker(2Δ), using finite modular linear algebra, and reject ker(Δ). If admissible tables exist, this final acceptance probability is at least one half because ker(Δ) is a proper subgroup of ker(2Δ). This is an algebraic construction; the general conditioned coefficient sampler is not integrated into the workbench.

Sampling all coefficient coordinates and then filtering is also exactly uniform conditional on acceptance, but its minimum-precision rejection rate can be poor at large M.

## 3. Lowest possible modulus

Every feature difference across a half-period is divisible by 2N:

$$
z^2-(N-z)^2=N(2z-N),\qquad\nu_2(N(2z-N))=\log_2N+1
$$

on odd z. Integer polynomial congruence preservation therefore rules out the requested periods at M ≤ 2N. The first possible dyadic modulus is M = 4N.

At M = 4N, only B₁ can affect the half-period difference. Every B_j with j ≥ 2 has a difference quotient containing a factor of eight, because its nodes and arguments are all 1 modulo eight. Thus the exact full-period condition is simply a₁ odd. The modulus is automatically minimal. All other retained coordinates are independent unrestricted draws in their ranges.

Moreover, the nodes fill the whole congruence class 1 modulo eight at this modulus. An odd a₁ makes G preserve difference valuations on that class, so the anchored output fills the complete grid of multiples of eight. Numerical shift classes and order classes therefore coincide here.

For N = 1024, M = 4096, only B₁,B₂,B₃ survive. With t = (z−1024)²,

$$
H=a(t-1)+b(t-1)(t-9)+c(t-1)(t-9)(t-25)\pmod{4096},
$$

where a is uniform on {1,3,…,511}, b on {0,…,31}, and c on {0,1,2,3}. These give all 32,768 full-period pseudo-square classes at this fixed M, with 15 independent valid bits. This is broader than the earlier single-valuation polynomial family; its count is not one row of the older valuation table.

## 4. Fixed precision does not generally identify shift and order classes

At N = 8, direct enumeration in the Newton coordinates gives:

|    M | Minimum-period numerical shift classes | Order classes |
| ---: | -------------------------------------: | ------------: |
|   32 |                                      2 |             2 |
|  256 |                                      4 |             4 |
|  512 |                                     12 |             8 |
| 1024 |                                     12 |             8 |
| 2048 |                                     24 |            12 |
| 4096 |                                     48 |            12 |

At M = 512, four order classes have one numerical representative and four have two, so uniform numerical sampling weights some rank appearances twice as heavily. At M = 4096 the corresponding multiplicities are one for six order classes and seven for six others. These fixed-M counts concern minimum precision for each sampled formula. They do not count the entire shift-class union, which is infinite, or identify a globally smallest polynomial modulus for each order class.

The [verification script](verify.py) checks the Newton coordinate uniqueness in these small spaces and checks 100 draws of the 1024×1024 recipe against its complete value grid and half-period differences. The general coordinate and uniformity statements rest on the proofs above.
