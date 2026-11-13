# Pre-power families under sampling

This report refines the visual observations about even pre-powers with optional twists. It uses $N = 2^r \ge 8$, $q = 2^w u$ with $u$ odd, and the shared family

$$
f(t)=t+2t(t-1)Q(t),\qquad P(x)=f(x^q).
$$

The existing [November 4 report, Section 3](../2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#3-a-shared-pre-modulus-for-useful-even-pre-polynomial-families) proves that $f$ preserves every difference valuation and $\nu_2(f(t)) = \nu_2(t)$. In particular $f(0) = 0$ and $f(1) = 1$. The original-grid sampling maps are those in [sampling.py](../../interactive/ruglab/sampling.py), with the vertical checkerboard orientation.

Two fields have the same equality geometry if their cells form the same equal-value partition, allowing arbitrary bijective recoloring. Their anchored order tables agree only when their ascending value-group orders agree as well. Statements about a value-preserving post assume it is injective on the reachable combined values. [Minimum-period precision](precision-policy.md) alone does not generally imply that condition.

## 1. Adaptive pre-moduli and decomposition

For the four combiners OR, XOR, ADD, and ABSDIFF, the gallery's pre-moduli are $N\cdot 2^w$ on the full and opposite-checkerboard grids, $2N\cdot 2^w$ on the four Cartesian selections except even/even, and $2^q N\cdot 2^w$ on even/even. OR's same checkerboard also uses $N\cdot 2^w$. Same-checkerboard XOR has its separate factor of two. These adjustments retain the selected branch's displayed period; separately generated panels can therefore use different arithmetic constructions.

At fixed arithmetic and coloring, the full operand grid is the interlacing of its two checkerboards, and the same checkerboard interlaces even/even with odd/odd. Separately computed panels need not have the same post-modulus or rank palette, so the literal color-interlacing statement requires those choices to be held fixed.

With an untwisted pre-power, the even/even operands at its enlarged modulus are $2^q$ times the full operands at their modulus. Bitwise OR commutes with a common binary shift. A monomial post-operation scales similarly, including its distinction-preserving modulus, so the rank patterns agree. For a twist the effective pre-function becomes $f(2^q t)/2^q$, and for a mixed post it becomes $H(2^q z)$. These generally alter the comparison. At $N = 8$, $q = 2$, post $z+z^2$ changes the ordering; $Q = 1$ with identity post changes the equality geometry.

## 2. Zero occupancy

Put $k = r+w$ and $a = \lceil k/q\rceil$. On the full field, $P(x)$ is zero exactly when $x$ is divisible by $2^a$. Thus the fraction of zero OR cells is $2^{-2a}$. Conditioning on the same-parity checkerboard doubles it to $2^{1-2a}$, because every zero pair has even/even parity. They reach $1/4$ and $1/2$ once the even branch vanishes.

Opposite-checkerboard and odd/odd OR have no zeros before post-processing: each pair contains an odd pre-value. These fractions survive value- and zero-preserving posts. Arbitrary posts at minimum-period precision can introduce new zeros or mergers. The exact fractions were checked on 280 fields.

## 3. Opposite-checkerboard tail geometry

At $K = 2^{r+w}$, every even pre-input vanishes if and only if

$$
\boxed{q\ge r+w.}
$$

The twist preserves the condition. On each opposite-parity pair, OR then returns its odd pre-value. For odd operands $a,b$, the lifting formula gives

$$
\nu_2(a^q-b^q)=\nu_2(a-b)+\nu_2(a+b)+w-1.
$$

One of $a-b$ and $a+b$ has valuation one. Equality modulo $K$ is therefore equivalent to $a = \pm b$ modulo $N$. The twist's isometry preserves that equivalence. Thus all powers satisfying the boxed inequality have the same equality geometry, with $N/4$ groups, each containing $4N$ cells, before a value-preserving post. Their numerical values and color orders can differ.

When $q < r+w$, $P(2)$ is nonzero and $P(1) = 1$. Pairing odd input one with even inputs zero and two splits an equality group of the erased-even-branch field. Thus the nonvanishing even branch changes that geometry.

The first even pre-power after which every subsequent even exponent satisfies the inequality is:

|              N | First pre-power of the persistent tail |
| -------------: | -------------------------------------: |
|        8,16,32 |                                      6 |
| 64,128,256,512 |                                     10 |
|           1024 |                                     12 |
|      2048,4096 |                                     14 |

For identity twist and identity post, the sweep through pre-power 64 has one, two, and four distinct rank tables within this tail at $N = 8,16,32$. The complete $q = 2,4,\ldots,64$ partition/order groupings through $N = 256$ are in [results.json](results.json). Earlier exact comparisons also checked the opposite-checkerboard partition through $N = 1024$.

Pre-powers six and eight share $q-w-2 = 3$. Once the odd pre-operand's common fixed bits are removed, the even branch begins at the same relative bit in both cases. This explains their related coarse structure; it does not identify their complete arrays or define an aesthetic equivalence class.

## 4. Four combiners become the same field

On the opposite checkerboard, the vanished even branch leaves operands zero and $v \ge 0$. Consequently

$$
\boxed{0\mathbin{\mathrm{OR}}v=0\mathbin{\mathrm{XOR}}v=0+v=|0-v|=v.}
$$

This equality precedes the post-operation and holds for every integer $Q$ in the shared family, not only the displayed twists. Matching post-settings and modulus policy therefore give identical numerical fields for OR, XOR, ADD, and ABSDIFF. This specializes the erased-variation observation in the earlier report, Section 4.5, and connects it to the adaptive catalogue threshold above.

At $N = 128$, $q = 10$ uses $K = 256$, so all even tenth powers vanish; every subsequent even $q$ also meets the condition. At $N = 1024$, $q = 10$ uses $K = 2048$ and input two has nonzero powered residue 1024, so the four can differ. Pre-power twelve restores the collapse. At this same $K$, AND, MULT, and CLMUL give zero; a style that raises $K$ to retain their even branch is a different comparison.

## 5. Odd/odd decomposition and frequencies

Here $K = 2^{r+w+1}$. Odd pre-values fill the class 1 modulo $S = 2^{w+2}$. Writing them as $1+SA_i$, the $A_i$ fill all residues modulo $T = N/2$ exactly twice. The isometry $f$ permutes that same complete class. Thus

$$
\boxed{Z(i,j)=1+S(A_i\mathbin{\mathrm{OR}}A_j).}
$$

There are exactly $N/2$ combined-value groups. The group at normalized value $b$ has $4\cdot 3^{\mathrm{popcount}(b)}$ cells: at each one-bit of $b$ there are three operand-bit choices giving OR one, at each zero-bit there is one, and each operand code has two preimages. This count is independent of $q$ and $Q$; the groups' spatial locations change.

This is the algebraic content of the observed purified odd/odd texture. Suitability as a large rug field remains an aesthetic observation, rather than a theorem inferred from the count.

## 6. The catalogue post family

For the derivative formulas below, the catalogue post family is the following fixed set. Let $d = \nu_2(H'(1))$ and $\beta$ be the odd part $H'(1)/2^d$.

| Index | H(z)    |    d |    β |
| ----: | ------- | ---: | ---: |
|     0 | z       |    0 |    1 |
|     1 | z+z²    |    0 |    3 |
|     2 | z³      |    0 |    3 |
|     3 | z+3z³   |    1 |    5 |
|     4 | z²+z³   |    0 |    5 |
|     5 | 3z+z⁴   |    0 |    7 |
|     6 | z²+3z⁵  |    0 |   17 |
|     7 | z+z³+z⁷ |    0 |   11 |
|     8 | z⁷      |    0 |    7 |
|     9 | z¹⁴     |    1 |    7 |

For $a,b = 1$ modulo $S$ with $S \ge 8$, the difference quotient of $H$ is $H'(1)$ plus a multiple of $S$. Since $d \le 1$, it has valuation exactly $d$. Thus these $H$ preserve difference valuations after adding $d$. Also $H(1)$ is between one and four, below $S$, so none of these odd/odd outputs can reduce to zero at the relevant modulus. Since the combined values fill a complete class, all three selections, Catalogue, Distinct outputs, and Minimum period, give

$$
M=K2^d.
$$

A half-period toggles the top bit of one odd pre-operand. Choosing the other pre-value one exposes that toggle under OR, giving a post-difference of valuation $\log_2 K-1+d$. This proves the minimum-period part of the assertion. The same argument applies to the opposite-checkerboard erased-even-branch tail, using its complete odd pre-value class. The [explicit selector theorem](precision-policy.md#4-all-three-selectors-agree-in-the-opposite-checkerboard-tail) states that tail result for all four surviving combiners, proves it for every positive post-power as well, and gives an outside-catalogue counterexample.

## 7. Exact valuation stabilization

Fix the odd part $u$. Define, for odd $x$,

$$
L_w(x)=\frac{x^{2^w}-1}{2^{w+2}}\pmod T.
$$

Squaring gives

$$
L_{w+1}(x)=L_w(x)+2^{w+1}L_w(x)^2\pmod T.
$$

Hence $L_w$ stabilizes once $w \ge r-2$. When $w = r-3$, the last correction flips the top retained bit conditional on the low bit. For $r \ge 4$ this changes the OR equality geometry: the shear $\sigma(a) = a \mathbin{\mathrm{XOR}} ((a \bmod 2)\cdot T/2)$ sends the equal-OR pairs $(1,T/2)$ and $(1+T/2,0)$ to pairs with different ORs. Every operand code is attained, so this supplies actual cells witnessing the difference. At $N = 8$ the first allowed even-power valuation is already the threshold $w = 1$.

Once $w \ge r-2$, higher powers in the odd exponent $u$ and in $f$ contribute multiples of $T$ after normalization. Put

$$
\alpha=f'(1)u=(1+2Q(1))u\pmod T,\qquad
L_i=L_{r-2}(2i+1).
$$

The exact anchored rank table for a catalogue post is

$$
\boxed{R(i,j)=\beta\left[(\alpha L_i\bmod T)\mathbin{\mathrm{OR}}(\alpha L_j\bmod T)\right]\bmod T.}
$$

The first displayed odd/odd operands are one, so anchoring subtracts $H(1)$. To see the post simplification, expand $H(1+Sb) = H(1)+S H'(1)b+S^2R_H(b)$. At $w \ge r-2$, $S \ge 2T$ and $d \le 1$, so the nonlinear part vanishes modulo $S\cdot 2^d\cdot T$. Dividing by $S\cdot 2^d$ leaves $\beta b$ modulo $T$. Every residue $b$ is attained, so these normalized residues are exactly the anchored ranks.

Thus the twist survives only through $f'(1)$, before OR, and the post only through its odd derivative part $\beta$, after OR. For example $Q = 1$ and $Q = t$ agree in this tail. Posts $z+z^2$ and $z^3$ agree in rank, as do $z^7$ and $z^{14}$. The scalar expansion does not move the rug's spatial origin.

For powers of two, all 160 catalogue twist/post pairs were checked to have exact rank stabilization at $w = 1,2,3,4,5,6$ for $N = 8,16,32,64,128,256$. In particular the exact thresholds at $N = 32,64,128$ are 3,4,5, one beyond the visual estimates 2,3,4. The last bit correction explains the preceding case's resemblance without identifying it with the tail.

Valuation alone does not classify the tail: $u$ remains in $\alpha$. At $N = 16$, powers 16,32,64 have $u = 1$ and agree, whereas power 48 has $u = 3$ and can differ. The derivative formula was checked on 1,920 combinations covering $N = 16,32,64,128$, all 16 twists, all ten posts, and $u = 1,3,5$.

## 8. General posts can delay or change this simplification

The catalogue condition $d \le 1$ matters. For a general $H$ with nonzero $H'(1)$, divide its anchored expansion by $S\cdot 2^d$:

$$
\frac{H(1+Sb)-H(1)}{S2^d}=\beta b+\sum_{j\ge2}\frac{S^{j-1}h_j}{2^d}b^j.
$$

Here $h_j$ are the integer Taylor coefficients at one. In the range where the displayed division is integral, each higher term disappears modulo $T$ when its coefficient is divisible by $T$. A large $d$ can postpone that event. If $H'(1) = 0$, a higher derivative supplies the leading behavior, so its odd first-derivative part is undefined.

A concrete extension is $H(z) = 62z+z^2$, with $H'(1) = 64$. At $N = 32$, $u = 1$ and $Q = 0$, the underlying operand table stabilizes at $w = 3$, but the post rank table stabilizes only at $w = 8$, or pre-power 256. For $w \ge 5$, the minimum and catalogue moduli agree and the remaining post action is

$$
b\longmapsto b+2^{w-4}b^2\pmod{16}.
$$

This is a permutation because the quadratic coefficient is even. It changes between $w = 5,6,7,8$ and becomes $b$ at $w = 8$ and thereafter. At $w = 3$ an accidental match with the final rank table occurs, but the intervening changes mean that is not stabilization. The [results](results.json) include both catalogue and minimum-period signatures through $w = 10$.
