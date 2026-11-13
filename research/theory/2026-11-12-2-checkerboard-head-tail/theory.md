# General checkerboard head and tail theory

This report answers the [research request](research-request.md) for arbitrary integer post-polynomials and arbitrary polynomial twists in the shared family. The [previous exploration](../2026-11-12-1-tentative-pattern-explorations/README.md) supplies the tail cutoff and catalogue-specific derivative results. The new results below give exact selector criteria, a general half-period component classification, finite twist coordinates, and domain-dependent head families. Proofs are separate from the bounded checks in [results.json](results.json).

## Scope

Fix $N=2^r\ge8$, a positive even pre-power $q=2^wu$ with $u$ odd, and $K=N2^w=2^k$. Let $Q\in\mathbb Z[t]$ have arbitrary finite degree and coefficients, and put

$$
f(t)=t+2t(t-1)Q(t),\qquad P(x)=f(x^q)\bmod K.
$$

The scalar $P(x)$ is always its representative in $[0,K)$. Use the current vertical checkerboard-opposite map $a=i+j$, $b=j-i-1$. Let $Z(i,j)$ be OR, XOR, ADD, or ABSDIFF applied to $P(a),P(b)$. ADD is the integer sum, without an extra reduction modulo $K$; ABSDIFF is the nonnegative absolute difference. The displayed field is $H(Z(i,j))\bmod M$, where $H\in\mathbb Z[z]$ is arbitrary and $M=2^m$.

The target is least horizontal and vertical periods $N$. Classes are anchored at displayed cell $(0,0)$. Numerical shift classes identify a common circular output offset after division by $M$; order classes retain the circular ascending ranks after that anchoring. Spatial translations and reflections remain distinct. These results concern ordinary checkerboard-opposite sampling, not doubled checkerboard-opposite.

The admissible twist family is essential: an unrestricted pre-polynomial outside this family need not preserve valuations, the chosen pre-modulus, or the head/tail structure. No coefficient or degree restriction is imposed on $Q$ or $H$ within the stated construction.

## 1. One half-period graph controls both axes

The shared-twist isometry and pre-period lemmas are proved in [the November 4 report, Section 3](../2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#3-a-shared-pre-modulus-for-useful-even-pre-polynomial-families). With $h=N/2$, they give

$$
P(x+N)=P(x),\qquad P(x+h)=P(x)\quad(x\text{ even}),\qquad P(x+h)=P(x)\mathbin{\mathrm{XOR}}(K/2)\quad(x\text{ odd}).
$$

For odd $x$, lifting gives valuation $k-1$ for the change before reduction; the isometry preserves it, so the two residues differ by exactly the top bit. For even $x$, the change is divisible by $K$. In the displayed sample, horizontal and vertical half-shifts change the second operand by $-h$ and $h$, which agree modulo the pre-period $N$. Consequently, for every allowed combiner and post-polynomial,

$$
Z(i+h,j)=Z(i,j+h),\qquad F(i+h,j)=F(i,j+h).
$$

Thus both least axis periods are equal, and a simultaneous half-axis translation is always a period. This is a statement about translations, not an assertion of square reflection symmetry.

Form a graph whose vertices are the distinct integer values attained by $Z$. For each cell, join its raw value to the value at its half-shift; loops are allowed. Every opposite-parity operand pair modulo $N$ is reached, so the same graph can be built from the complete odd and even pre-value sets without materializing an $N\times N$ tile. Write its connected components as $C_1,\ldots,C_c$.

For a fixed $H$, define

$$
d=\min_{\{z,t\}\text{ an edge}}\nu_2(H(z)-H(t)),\qquad \nu_2(0)=\infty.
$$

If $d=\infty$, the target is unattainable at every modulus. Otherwise the complete answer for all dyadic moduli is

$$
\boxed{M_{\min}=2^{d+1},\qquad\text{the requested periods hold exactly when }m\ge d+1.}
$$

**Proof.** All $N$-shifts already preserve the integer raw table. A half-shift is a period modulo $2^m$ exactly when every edge difference is divisible by $2^m$, equivalently $m\le d$. On a dyadic torus, excluding the half-shift excludes every smaller axis period. There is no upper precision cutoff for retaining the target of this fixed formula.

## 2. Exact meaning of the three modulus selectors

Let $V=\{H(z):z\text{ a raw vertex}\}$ be the distinct integer outputs, allowing polynomial collisions. Set

$$
s=\max_{v\ne t\in V}\nu_2(v-t),\qquad b=\max_{v\in V\setminus\{0\}}\nu_2(v),
$$

with the maximum of an empty set defined as $-1$. Then

$$
M_{\mathrm{distinct}}=2^{s+1},\qquad M_{\mathrm{catalogue}}=2^{1+\max(s,b)}.
$$

These generalize the gallery policies to signed, nonmonotone, constant, and collision-producing polynomials. Distinct outputs preserves the equality partition of integer post-outputs. Catalogue additionally keeps nonzero integer outputs separate from zero. Neither can separate two inputs that already have identical integer post-outputs.

**Proof.** Two unequal integers remain distinct modulo $2^m$ exactly when their difference has valuation below $m$. A nonzero output remains nonzero exactly when its own valuation is below $m$. Taking the maximum gives both formulas.

Whenever the target is attainable, $d\le s$, hence

$$
M_{\min}\le M_{\mathrm{distinct}}\le M_{\mathrm{catalogue}}.
$$

All three agree exactly when $s=d$ and $b\le d$. The first two value policies agree exactly when $b\le s$. These are exact criteria for the word “almost”; there is no universal agreement theorem for arbitrary $H$. Adding a constant to $H$ leaves the minimum-period and distinction-preserving selectors unchanged but can change the catalogue selector. Catalogue precision is therefore sensitive to circular phase and is not an invariant of a numerical shift class.

## 3. What is exact in the tail

The tail condition is $q\ge k=r+w$. It erases every even pre-value. All four combiners then return the same surviving odd pre-value as an equality of integers. Therefore, for the same $N,q,Q,H$, every selector returns exactly the same result across OR, XOR, ADD, and ABSDIFF. If the target is unattainable, it is unattainable for all four. There is no “almost” between these combiners in the tail.

Agreement between different selectors is a separate question. At $N=64$, $q=10$, and $Q=0$:

| Post-polynomial | Catalogue M | Distinct outputs M | Minimum-period M |
| --------------- | ----------: | -----------------: | ---------------: |
| z               |         128 |                128 |              128 |
| z+127           |         256 |                128 |              128 |
| z²+6z           |        2048 |               2048 |             1024 |
| 7               |           2 |                  1 |     Unattainable |

These are exact computations reproduced by [verify.py](verify.py). The linear offset example isolates zero preservation; the quadratic isolates equality mergers at minimum period. More generally, taking $H(z)=z+2^J-1$ with $2^J\ge K$ makes the catalogue modulus $2^{J+1}$ while the other two remain $K$. Thus even positive linear posts can make the discrepancy arbitrarily large.

The odd pre-values fill $1\pmod S$, where $S=2^{w+2}$, with $T=N/4$ values. Equality of tail cells is equivalent to equality of their odd original operands up to sign modulo $N$. This partition is independent of $q$ and $Q$ in the tail, as proved in [the previous pre-power report](../2026-11-12-1-tentative-pattern-explorations/pre-power-families.md#3-opposite-checkerboard-tail-geometry). Half-shifts pair its $T$ classes without fixed points. The graph therefore has $N/8$ components, each of size two.

With arbitrary post-polynomials and the union over their own minimum moduli, all tail exponents and twists give exactly the same family of spatial order tables. Their individual numerical moduli can differ. The [sampling report](sampling.md) gives the common uniform sampler.

## 4. The full minimum-period order classification

**Theorem.** An anchored circular order of a partition of the raw vertices is realizable by an integer post-polynomial at its own minimum-period modulus if and only if each graph component uses at most two output groups, every used pair is an antipodal pair consistent across components, at least one component uses both partners, and those partner pairs admit antipodal positions in the prescribed circular order.

The last condition has a purely combinatorial test. Delete groups without a partner from the circular list. The remaining list must be a sequence of one endpoint of each pair followed by the corresponding partners in the same order. Pair identities must form a matching: one group cannot have two distinct partners.

**Necessity.** At $M/2$ both half-periods return. Each edge difference modulo $M$ is therefore zero or $M/2$. Following a connected path shows that all values of one component lie in one antipodal pair. Exact period requires at least one nonconstant component. Distinct group positions around the output circle imply the matching and ordering conditions.

**Sufficiency.** Place the paired groups at distinct dyadic positions in the first half-circle and their partners one half-turn later. Insert the unpaired groups into their required gaps. The [integer interpolation theorem](../2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#71-interpolation-with-a-power-of-two-divisibility-allowance) realizes these labels after a common power-of-two scaling. Every edge is then zero or half the resulting modulus, with at least one nonzero edge. This modulus is minimal for that polynomial.

Only connected components matter; their internal edges impose no further restrictions. Component sizes determine the number of abstract order classes, while the components' spatial incidence determines their appearance. Polynomial realization is implemented in [realize.py](realize.py). The construction may use a larger modulus than another polynomial representing the same order; it does not solve global canonical minimum precision.

## 5. Finite twist coordinates at every domain

Define

$$
a=\max\left(0,\left\lceil\frac{k-1}{q}\right\rceil-1\right),\qquad b=\max\left(0,\left\lceil\frac{k-1}{w+2}\right\rceil-1\right).
$$

**Theorem.** Every integer polynomial $Q$ gives exactly the same pre-function modulo $K$ as a polynomial of degree below $a+b$. If $a+b=0$, every twist gives the identity pre-twist on the actual powered inputs.

**Proof.** Divide $Q$ by the monic integer polynomial $A(t)=t^a(t-1)^b$. At an even powered input, $\nu_2(t)\ge q$, so $2t(t-1)A(t)$ has valuation at least $1+(a+1)q\ge k$. At an odd powered input, $\nu_2(t-1)\ge w+2$, giving valuation at least $1+(b+1)(w+2)\ge k$. The multiple removed by monic division therefore changes no pre-value. Integer coefficients are preserved by the division.

This is a spanning-degree bound, not unique coefficient ranges. For exact unique coordinates, evaluate the columns $2t(t-1)t^j$ on the powered inputs for $0\le j<a+b$, and diagonalize their image modulo $K$. Independent coefficient ranges of sizes $2^{e_j}$ then enumerate every distinct pre-function once. [core.py](core.py) implements this with the dyadic elimination method from the November 2 report.

For sides 8–4096, degree at most seven suffices for every head pre-power. The finite space can nevertheless be large:

| Side N | Head pre-powers    | Persistent tail starts | Distinct twists at pre-power two |
| -----: | ------------------ | ---------------------: | -------------------------------: |
|      8 | 2, 4               |                      6 |                                2 |
|     16 | 2, 4               |                      6 |                                8 |
|     32 | 2, 4               |                      6 |                               32 |
|     64 | 2, 4, 6, 8         |                     10 |                              128 |
|    128 | 2, 4, 6, 8         |                     10 |                            1,024 |
|    256 | 2, 4, 6, 8         |                     10 |                           16,384 |
|    512 | 2, 4, 6, 8         |                     10 |                          262,144 |
|   1024 | 2, 4, 6, 8, 10     |                     12 |                        8,388,608 |
|   2048 | 2, 4, 6, 8, 10, 12 |                     14 |                      536,870,912 |
|   4096 | 2, 4, 6, 8, 10, 12 |                     14 |                   34,359,738,368 |

The counts are exact module calculations, checked independently against complete explicit representatives at side 64. The general cutoff inequality is proved in the previous exploration; the head lists and twist coordinates are recomputed here across all ten sides.

At side 64 there are especially short complete representatives: for pre-power two take $Q(t)=C+(B-C)t^2$ with $0\le B<8$, $0\le C<16$; for pre-power four take $Q(t)=A+(B-A)t$ with $0\le A,B<8$; for pre-powers six and eight take $Q(t)=B$ with $0\le B<8$. They give respectively 128, 64, 8, and 8 distinct pre-functions.

**Proof of this specialization.** Odd powered inputs are $1+Sx$, and the twist acts there only through $Q(1)\bmod8$. At pre-power two, inputs of valuation one are $4+32x$; their twisted values depend only on $Q(4)\bmod16$. The inputs of valuation two reduce to 16, whose twisted value depends only on $Q(0)\bmod4=Q(4)\bmod4$; the remaining nonzero even layer is fixed at 64. Thus the two displayed parameters are sufficient and independent. At pre-power four the only nonzero even pre-value is the twist of 16, controlled by $Q(0)\bmod8$ independently of $Q(1)\bmod8$. At six and eight the even value is fixed at $K/2$, leaving only the odd-branch parameter.

## 6. Lower bounds on the modulus and the ABSDIFF exception

For OR, XOR, and ADD, every nontrivial raw half-edge has difference $K/2$ in absolute value. The even operand zero supplies at least one such edge. Integer polynomial congruence preservation therefore gives the universal lower bound $M\ge K$ for any attainable post-polynomial. The identity post attains it. Thus the globally lowest attainable modulus for each of these fixed pre-functions is exactly $K$.

For ABSDIFF, every raw value is odd, so every polynomial is constant modulo two. In the head, however, the identity post often detects the comparison between the operands at modulus four:

$$
|O-E|\equiv1\pmod4\quad(O>E),\qquad |O-E|\equiv3\pmod4\quad(O<E),
$$

where $O$ is odd and $E$ even. The comparison has full requested period whenever some nonzero even pre-value lies strictly between the smallest and largest odd pre-values, namely 1 and $K-S+1$. For $q\ge4$, every even pre-value is a multiple of $S$, so any nonzero one satisfies that condition. For $q=2$ and $N\ge16$, the pre-input four has a nonzero pre-value of valuation four, also inside the interval. Hence, throughout the head for every $N\ge16$ and every $Q$,

$$
\boxed{M_{\min}(H(z)=z,\mathrm{ABSDIFF})=4.}
$$

**Why the comparison changes.** Odd pre-values fill their whole congruence class; pairing a value in the lower half with its top-bit toggle produces intervals whose union runs from 1 to $K-S+1$. A fixed even value inside that interval lies between some toggled pair. The corresponding cell distinguishes both half-periods. Modulo two the field is constant, proving minimality.

At side eight, pre-power two has a small exception: an even constant term of $Q$ gives minimum four, while an odd one gives minimum 16. The even pre-value is respectively 4 or 12; in the latter case all raw half-edge differences are eight. Pre-power four at side eight still has minimum four. ABSDIFF minimum precision is therefore mathematically available, although a particular $H$ can erase the period. The 64×64 gallery comparison found no unavailable targets among its 640 ABSDIFF head recipes. Actual selector calls and native evaluation confirm representative cases; this investigation does not identify which earlier UI state produced the reported unavailability.
