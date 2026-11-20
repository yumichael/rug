# Single-power parameterizations at minimum precision

The [selector and pre-twist extension](modulus-and-twists.md) compares Minimum period, Distinct outputs, and Catalogue for the full shared twist family.

Identity pre-twist and one post-power already give finite, exactly sampleable equality and circular order families for both requested samplings. At minimum precision, checkerboard-opposite OR, XOR, ADD, and ABSDIFF always use equally spaced distinct colors. So do odd-odd AND, OR, ADD, MULT, and CLMUL. Odd-odd XOR and ABSDIFF have finite circular order spaces but infinitely many numerical shift classes. Two paired examples below show what a larger post-modulus and a pre-twist can add.

This first pass builds on the [fixed-base odd-input post-power theorem](../2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#54-an-unbounded-power-theorem-for-odd-valued-basic-tables), the [checkerboard head and tail analysis](../2026-11-12-2-checkerboard-head-tail/theory.md), and the [odd-odd OR valuation theorem](../2026-11-12-1-tentative-pattern-explorations/pre-power-families.md#7-exact-valuation-stabilization). In particular, the previous precision-policy report gives the [checkerboard tail's common modulus](../2026-11-12-1-tentative-pattern-explorations/precision-policy.md#4-all-three-selectors-agree-in-the-opposite-checkerboard-tail). The extensions here are the complete color grids in the checkerboard head, a finite union across its pre-power groups, and the modulus and class results for the remaining odd-odd combiners.

## Scope and class definitions

Use a displayed side $N=2^r\ge16$, an even pre-power $q=2^w u$ with $u$ odd, and a positive post-power $p=2^v j$ with $j$ odd. Reduce each operand power modulo the pre-modulus $K$ before applying the combiner. Use the least power-of-two post-modulus $M$ giving both least axis periods $N$ for the chosen recipe. The post is $a z^p+b\pmod M$, with $a$ odd. An odd multiplier and a common offset preserve all equality and period tests.

The checkerboard uses original coordinates $(x+y,y-x-1)$, and odd-odd uses $(2x+1,2y+1)$. The class comparisons anchor at the first displayed cell. Equality classes retain which visible cells agree, order classes retain the circular order of those groups, and shift classes retain their normalized positions around the circle up to a common offset. Spatial positions remain fixed. The catalogue chooses one witness per class and samples classes uniformly within the requested group. It restores a uniform independent color rotation on the witness's modular grid.

## Checkerboard-opposite

Set $K=N2^w$, $s=\min(q,w+2)$, and $T=K/2^s$. Use the previous partition of head powers by $q-w-2$ and the erased-even-branch tail $q\ge r+w$. At side 64 the groups are 2, 4, {6, 8}, and tail. These are structural groups used for comparison.

| Combiner and case       | Minimum modulus | Distinct colors |
| ----------------------- | --------------: | --------------: |
| OR, XOR, ADD            |          $K2^v$ |             $T$ |
| ABSDIFF, head, odd $p$  |             $4$ |             $2$ |
| ABSDIFF, head, even $p$ |          $K2^v$ |             $T$ |
| ABSDIFF, tail           |          $K2^v$ |             $T$ |

Every row fills a complete equally spaced color grid. Consequently an anchored circular order determines the normalized shift class, including across different bases. Equality still forgets the circular ordering.

**Proof.** Write $O$ and $E$ for the odd and even pre-values. Every opposite-parity pair is reached modulo the operand period $N$. Under either axis half-shift the odd pre-value toggles the top bit of $K$ and the even pre-value is fixed, by the existing half-period lemma. For OR, XOR, and ADD every change is therefore congruent to zero or $K/2$ modulo $K$. Pairing with $E=0$ exposes $K/2$. All raw values are $1$ modulo $2^s$, with $s\ge2$, so powering adds $v$ to the valuation of each nonzero difference by lifting the exponent.

For even post-powers, ABSDIFF has the same outputs as the signed difference $O-E$ raised to that power. The signed table has the same half-shift congruences, and its values are also $1$ modulo $2^s$. In each of these unit-valued cases, the odd pre-values alone fill the required coset when $s=w+2$. The other case is $q=2$. There, choosing $E=0$ or $4$ fills both of the cosets $1$ and $5$ modulo eight in each combiner. Thus the complete raw coset is reached modulo $K$. The powered coset follows from the unit calculation below. In the head ABSDIFF with odd $p$, the earlier comparison witness gives minimum $4$ for $p=1$. Odd powering on odd inputs preserves every difference valuation, so the same witness and both output groups survive for every odd $p$. In the tail $E=0$ and all four combiners coincide.

## Odd-odd

Set $K=2N2^w$, $S=2^{w+2}$, and $T=N/2=2^t$. The pre-values are $1+SA_i$, with $A_i$ covering all residues modulo $T$ and toggling the top bit under the corresponding axis half-shift. The pre-value 1 occurs at the origin.

| Combiner and case    | Minimum modulus | Color structure at the minimum         |
| -------------------- | --------------: | -------------------------------------- |
| AND, OR, MULT, CLMUL |          $K2^v$ | $T$ equally spaced colors              |
| ADD                  |    $K2^{p-1+v}$ | $T$ equally spaced colors              |
| XOR                  |      $S^p T2^v$ | Powers of $0,\ldots,T-1$ modulo $T2^v$ |
| ABSDIFF, even $p$    |      $S^p T2^v$ | Powers of $0,\ldots,T-1$ modulo $T2^v$ |
| ABSDIFF, odd $p$     |         $4 S^p$ | Four colors if $p=1$, otherwise three  |

For AND and OR the high code is the corresponding bitwise operation on $A_i,A_j$. For MULT it is $A_i+A_j+SA_i A_j$, and for CLMUL it is $(A_i\mathbin{\mathrm{XOR}} A_j)\mathbin{\mathrm{XOR}}(S\,\mathrm{CLMUL}(A_i,A_j))$. For ADD, factor the raw value as $2(1+(S/2)(A_i+A_j))$. In each case the high codes modulo $T$ attain all residues. Fix the other code at zero, or at $T-1$ for AND. The same choices expose a change of $T/2$ modulo $T$ along each half-axis. All other changes are multiples of $T/2$, since each operation respects reduction to lower bits. This proves the first two minimum-modulus rows by lifting the exponent and accounting for the factor $2^p$ for ADD.

XOR and ABSDIFF are $S$ times a basic value $B$ in $[0,T)$, and each $B$ occurs by setting the other input code to zero. Let $H=T/2$. For XOR a shifted pair of basic values differs by $H$ in absolute value. For ABSDIFF the shifted value, up to sign, differs by $H$. For an odd $B$ and even $p$, one of the sum and difference of the shifted values has valuation $\nu_2(H)=t-1$, and the other has valuation one. Thus the powered difference has valuation $t-1+v$. For two values of common valuation $d<t-1$, factoring out $2^d$ and applying the same lifting bound to the two odd parts gives a lower bound of $pd+(t-1-d)+v$. This also holds when $t-1-d=1$, since the sum and difference of two odd numbers have total valuation at least three. For the remaining pair $0,H$, the powered difference has valuation $p(t-1)\ge t-1+v$. An odd $B$ paired against the zero operand attains the bound for both combiners. Odd $p$ for XOR preserves the depth $t-1$ on odd $B$, and even $B$ cannot lower it. Odd $p$ for ABSDIFF preserves parity under the half-shift, but the subtraction can cross zero and take a basic value from 1 to $H-1$, whose difference has valuation one. These witnesses work along either axis. Multiplication by $S^p$ restores the scale in the table. Modulo four, odd powers preserve 1 and 3, and send 2 to zero once $p\ge3$.

## Finite enumeration without a post-power cutoff

For the equally spaced cases, the core calculation uses a unit $1+2^sB$ and its normalized power at precision $T=2^t$. The formula below uses $U_0(B)=B$.

$$
U_v(B)=\frac{(1+2^sB)^{2^v}-1}{2^{s+v}}\pmod T,\qquad U_{v+1}(B)=U_v(B)+2^{s+v-1}U_v(B)^2\pmod T.
$$

The numerator is divisible by $2^{s+v}$. Lifting gives a bijection on the $T$ possible codes, so a complete raw coset gives the complete post-color coset. The recurrence stabilizes pointwise for $v\ge\max(0,t-s+1)$. Raising to the remaining odd exponent only needs its residue modulo $T$, since the subgroup $1+2^{s+v}\mathbb Z$ modulo $2^{s+v+t}$ has exponent dividing $T$. Keep one representative for each odd part and each valuation up to the stabilization bound. For the even-only head ABSDIFF case keep valuation one even when stabilization starts at zero. Separately keep the single binary comparison for odd powers.

For the pre-power reduction, the odd input first squares into $1+8\mathbb Z$ and then uses the same recurrence with $s=3$ and valuation $w-1$. On the erased checkerboard branch, the surviving odd pre-code is modulo $N/4$. Keep $w$ through $\max(1,r-3)$ and one pre-power per odd part modulo $N/4$ in each row, chosen large enough to satisfy $q\ge r+w$. The post also stabilizes with respect to $w$ in this range because the unit exponent $s=w+2$ is already large enough at its endpoint. This covers every erased pre-power. The head is finite by its defining inequality.

For odd-odd the pre-code is modulo $N/2$. It stabilizes for fixed odd part when $w\ge r-2$, and the MULT and CLMUL cross terms then vanish modulo $T$. The fixed-post normalized field is also stable from there, except for ADD which has a smaller unit exponent $s=w+1$. For ADD, $w\ge r-1$ removes the final quadratic correction in the fixed-post table. At $w=r-2$ that correction is itself a linear odd multiplier, since $2^{t-1}B^2=2^{t-1}B\pmod T$. The class space after allowing all odd multipliers therefore already stabilizes in the preceding row. The catalogue keeps the extra ADD row to show the fixed-post distinction.

### Even-valued basic tables

For odd-odd XOR and ABSDIFF, remove the common factor $S^p$ and use normalized modulus $2^m$. For a fixed post valuation $v$, $m=t+v$ except for odd-post ABSDIFF, where $m=2$. Before $p\ge m$, enumerate the transient exponents. After that threshold every even basic value vanishes, while the cycle of the odd exponent part divides $2^{\max(1,m-2-v)}$.

For all $v\ge t$, the even values have already vanished and the powered odd values have the form $1+2^{v+2}L(B)\pmod{2^{t+v}}$ before applying the odd exponent part. The code $L(B)$ modulo $2^{t-2}$ is independent of $v$ in this range by the squared-unit recurrence. The odd exponent part multiplies the code modulo $2^{t-2}$, since the higher terms vanish at this precision. Write the multiplier as $a_0+2^{v+2}k$ with $0<a_0<2^{v+2}$ odd. After normalization the odd groups have positions

$$
\frac{(k+a_0j L(B))\bmod 2^{t-2}+a_0/2^{v+2}}{2^{t-2}}.
$$

Zero is present and fixes the circular order origin. The fractional part is positive and common, so the order depends only on $k\bmod 2^{t-2}$ and the odd residue $a_0j\bmod 2^{t-2}$. These range independently already at $v=t$. This gives one finite representative row for every higher valuation. The shift space is nevertheless infinite, since the field contains fixed cells with basic values 0 and 1 and their normalized difference for $a=1$ is $1/2^{t+v}$. Uniform sampling over all numerical shift classes is unavailable. Uniform circular order sampling remains exact.

## Gallery comparisons

At side 64 the checkerboard identity-twist groups have 449, 33, 42, and 16 distinct circular orders in pre-power group order. These counts include every positive post-power at its minimum modulus. The broader all-twist gallery samples substantially more spatial partitions in the head, and the paired witness below shows one such partition explicitly.

- [Checkerboard atlas](checkerboard.png) shows a uniform seeded order draw per head group and combiner. The four tail columns use independent draws from the common tail.
- [Odd-odd atlas](odd-odd.png) compares the first and stabilized pre-valuations at representative fixed powers, including both post-power one and two. It illustrates texture changes across combiners. The exact catalogue contains many more tables than these panels.
- [Paired comparisons](comparisons.png) vary one choice at a time. For checkerboard OR at side 64 and pre-power two, the twist $t+2t(t-1)$ splits a raw equality of each of the four identity-twist bases in that group. The pair of cells can depend on the base. Every scalar post-operation preserves the equalities of its own raw input, so no such operation on those four identity bases can reproduce this twisted partition. For odd-odd ABSDIFF at side 64 and pre-power two, raising $M$ from 32 to 256 with post-power one increases the color count from 4 to 32 and drops the largest cell group from 26.6% to 6.1%. Both settings retain the same least axis periods.

Equal color spacing describes the distinct levels. A large share of cells can still occupy one level, as the OR and AND panels illustrate. The paired comparisons give separate reasons to try a larger modulus for ABSDIFF and a pre-twist for some checkerboard head textures. They establish added coverage without deciding which textures belong in the app.

## Reproduction

[study.py](study.py) constructs serializable native recipes and deduplicates exact class signatures. [verify.py](verify.py) checks the formulas against the native engine, verifies representative substitutions and periods, compares the pre-valuation tails, and regenerates [results.json](results.json) and the atlases. Side 64 class counts enumerate every representative in the proved finite spaces. The field checks use sides 16, 32, 64, and 128. Enumeration is a research tool for modest sides. A scalable direct sampler at larger sides and a notebook integration remain follow-up work.

Run from the repository root.

```sh
MPLCONFIGDIR=/private/tmp/rug-research-mpl PYTHONPATH=research/interactive PYTHONDONTWRITEBYTECODE=1 research/interactive/.venv/bin/python research/theory/2026-11-19-monomial-first-pass/verify.py
```
