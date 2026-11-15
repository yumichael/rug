# The positive-valuation polynomial union for no-pre XOR

The existing conditional polynomial samplers extend to an exact uniform sampler over **all positive exponent valuations**. Each productive valuation contributes a disjoint set of shift classes; all later valuations contribute one identical shared tail. Choose among these finitely many sets in proportion to their exact class counts, then use the existing conditional sampler. The same sampler is uniform over order classes because these families fill their numerical value grids.

This resolves a gap explicitly left in [November 2, Section 13](../2026-11-02-xor-polynomial-period/2026-11-02-xor-polynomial-period.md#13-what-has-been-resolved-and-what-remains-separate) and [November 4, Section 6.3](../2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#63-valid-same-valuation-polynomial-sums). Those reports supply the conditional coordinates, counts, period condition, and shift/order equivalence. The cross-valuation separation theorem and the resulting union construction are the new results here.

## 1. Scope, coordinates, and terminology

Fix an operand modulus $C=2^c\ge8$ and displayed side $N=C/2$. Use no pre-operation and XOR. The reference is horizontal checkerboard-opposite sampling at displayed origin $(0,0)$: original operand-grid positions are $(a,b)=(i+j+1,i-j)$ for displayed column $i$ and row $j$, reduced modulo $C$ before XOR. It selects all original-grid pairs with opposite parity, with the stated phase and orientation. Both native checkerboard orientations are checked below. The scalar class result also applies to the older full-grid diagonal XOR layout whenever the same complete odd input set is reached; each layout retains its own coordinate map.

Every odd combined input $z=1,3,\ldots,C-1$ occurs. Fix a positive integer $v$ and allow every finite integer polynomial of the form

$$
H(z)=b+\sum_{u\text{ positive and odd}}a_u z^{2^v u},\qquad M_v=C2^v,\qquad \sum_u a_u\equiv1\pmod2.
$$

Thus all nonconstant exponents have exactly the same positive valuation. The coefficients can be arbitrary integers; only their nonconstant sum must be odd. The constant $b$ is unrestricted. This is the user’s intended **odd coefficient sum**, corresponding to the gallery’s “even sum” label. The gallery’s “odd sum” label means odd exponents, with $v=0$, which is outside this union. A polynomial mixing exponent valuations is a different family.

The existing period theorem gives exact least horizontal and vertical periods $N$. It also makes $M_v$ the minimum power-of-two post-modulus for the particular polynomial: a relevant half-period changes the output by $M_v/2$, and reduction modulo $M_v/2$ erases every such change. Every smaller modulus therefore loses the requested period too.

Put $Q=C/4$ and $d_v=2^{v+2}$, so $M_v=d_vQ$. Compare normalized classes through the anchored integer table

$$
F_v(z)=\frac{H(z)-H(1)}{d_v}\pmod Q.
$$

The numerator is divisible by $d_v$ on odd inputs, so this is well-defined. A numerical channel value is $F_v(z)/Q$ modulo one. Let $\mathcal S_v$ be the set of these tables. Spatial translations, reflections, rotations, and odd output multipliers remain distinct unless the anchored tables actually coincide. A shift class removes a common circular output phase; an order class records the anchored circular rank table, retaining ties. The existing grid-filling theorem says that every member here attains all $Q$ values. Consequently its rank table recovers $F_v$ exactly, and order equivalence equals shift equivalence across the whole union.

## 2. A three-input invariant separates the productive rows

For a table in the union, define

$$
\Delta(F)=F(25)-2F(5)+F(1)\pmod Q,\qquad q=c-2.
$$

Use inputs 5 and 25 reduced modulo $C$ when necessary. This is valid because each allowed power is periodic modulo $C$ on odd inputs at its balanced modulus $M_v$. Since the coefficients in this difference sum to zero, changing the output phase does not change it. Set $\nu_2(0)=\infty$.

In the reference horizontal checkerboard layout, these three inputs occur at displayed cells $(0,0)$, $(2,2)$, and $(12,12)$, with coordinates reduced modulo $N$. Thus the invariant is also a constant-size diagnostic on the anchored rank data.

**Theorem.** Every $F\in\mathcal S_v$ satisfies

$$
F(5)\text{ is odd},\qquad \boxed{\min\bigl(\nu_2(\Delta(F)),q\bigr)=\min(v+2,q).}
$$

**Proof.** For each allowed exponent $p=2^v u$, the odd-input lifting identity gives $\nu_2(5^p-1)=v+2$. Thus $(5^p-1)/d_v$ is odd, and its coefficient-weighted sum is odd because $\sum a_u$ is odd. This proves the first assertion.

For the second, use the integer identity

$$
25^p-2\cdot5^p+1=(5^p-1)^2.
$$

After dividing by $d_v$, each summand has valuation exactly $v+2$. Factoring out $2^{v+2}$ leaves an odd integer for every odd $u$. Their coefficient-weighted sum remains odd. Hence the unreduced difference has valuation exactly $v+2$; reducing modulo $Q=2^q$ gives the stated truncated valuation. This applies to every polynomial in the family, regardless of degree or coefficient size.

**Consequence.** Set

$$
V=\max(1,c-4)=\max(1,\log_2N-3).
$$

For $1\le v<V$, the invariant is nonzero with valuation $v+2$. Different such valuations give disjoint class sets, and none intersects any row with $v\ge V$, where the invariant vanishes. For a table already known to belong to this union, a nonzero invariant recovers its unique valuation as $\nu_2(\Delta)-2$. A zero invariant identifies the shared-tail category; this invariant alone is not a membership test for arbitrary polynomial patterns.

For example, take $C=64$, $Q=16$, and the two minimum-modulus polynomials

$$
H_1(z)=11(z^2-1)\pmod{128},\qquad H_2(z)=7(z^4-1)\pmod{256}.
$$

Both have $F(5)=1$. The first has $F(25)=10$ and $\Delta=8$, whereas the second has $F(25)=2$ and $\Delta=0$. They are different shift classes and different order classes despite their shared equality geometry. The invariant’s valuation also survives odd output multiplication, so even that broader identification cannot merge these two rows.

## 3. All later rows are exactly the same tail

Every odd residue modulo $C$ has a unique expression $z=\epsilon5^j$ with $\epsilon\in\{1,-1\}$ and $j\pmod Q$. Define $L(z)=j$. Even exponents ignore the sign.

To see the representation directly, $\nu_2(5^{2^k}-1)=k+2$, so 5 has order $Q$ modulo $C$. Its powers fill the entire class 1 modulo four, and their negatives fill the class 3 modulo four. This proves existence and uniqueness of the stated sign and exponent. This standard odd-unit structure is also recorded in [Conrad, Theorem 2.3](https://kconrad.math.uconn.edu/blurbs/gradnumthy/primepowerunitsandGLnQ.pdf).

**Theorem.** For every $v\ge V$,

$$
\boxed{\mathcal S_v=\{aL\pmod Q:a\text{ odd modulo }Q\}.}
$$

Thus the tail contains exactly $Q/2=C/8$ classes, independently of how large $v$ becomes.

**Proof.** Put $s=2^v$, $r=5^s$, and $\eta_v=(r-1)/d_v$, which is odd. For any odd positive $u$, the geometric-sum identity gives, as an integer identity before modular reduction,

$$
\frac{5^{suj}-1}{d_v}=\eta_v\sum_{k=0}^{uj-1}r^k.
$$

Since $v\ge V$, $r\equiv1\pmod Q$. The right side is therefore $\eta_v u j\pmod Q$. Every allowed polynomial becomes $aL$ with $a=\eta_v\sum a_u u$ odd. Conversely, the single power $z^s-1$ multiplied by an appropriate odd integer realizes every odd $a$, because $\eta_v$ is invertible modulo $Q$. This proves equality of the whole sets, rather than pointwise equality of one unadjusted power at different valuations.

Combining Sections 2 and 3 gives the complete disjoint union

$$
\boxed{\bigcup_{v\ge1}\mathcal S_v=\mathcal S_1\sqcup\cdots\sqcup\mathcal S_V.}
$$

For $C=8,16,32$, $V=1$ and the whole positive-valuation union is already the shared tail. For every larger power-of-two domain, the cutoff is sharp: row $V-1$ has a nonzero invariant and is distinct from the tail.

There are two stabilization thresholds to distinguish. The existing conditional theorem says each individual row becomes cyclic already at $v\ge\max(1,c-5)$. Cross-valuation equality begins one row later, at $V=\max(1,c-4)$. The last cyclic row before the tail and the tail have the same count but different class sets whenever $C\ge64$.

The dedicated `xor_valuation_catalogue` already uses the latter cutoff through `xor_valuation_tail(C)`. The broader polynomial gallery’s label “even sum tail” instead selects $v=\max(5,c-5)$ in the inspected code. At $C\ge1024$, that selects the last distinct cyclic row before the shared tail. Its conditional draws remain valid and uniform within that row, but the label must not be used to deduplicate the whole positive-valuation union. This research leaves gallery behavior unchanged.

## 4. The uniform union sampler

Let $D_v$ be the number of independent valid bits from the existing exact conditional coordinate construction, so $n_v=2^{D_v}=\lvert\mathcal S_v\rvert$. Compute these only for $v=1,\ldots,V$, and set

$$
T(C)=\sum_{v=1}^V2^{D_v}.
$$

Choose row $v$ with probability $2^{D_v}/T(C)$, then sample uniformly within its conditional space. Every union class receives probability $1/T(C)$ because the rows are disjoint. Every omitted higher valuation is already represented by row $V$.

Equivalently, draw one uniform integer rank $r\in\{0,\ldots,T(C)-1\}$. Lay out consecutive blocks of sizes $2^{D_1},\ldots,2^{D_V}$, select its block, and decode the remaining conditional rank with the existing cyclic coordinates. The [prototype](union_sampler.py) implements this exact bijection. Its output specifies $C$, $v$, $M_v$, and coefficients of the finite factored spanning list from November 2; it can also expand them into ordinary integer monomial coefficients.

The conditional decoder chooses a character-one cyclic generator of smallest order, subtracts it from the other character-one generators, makes its own coefficient odd, and ranges all remaining coordinates independently. It then converts back through the stored polynomial column transformation. This is the existing coordinate proof expressed as deterministic rank decoding. No output-table catalogue, membership rejection, or cross-row deduplication is needed when drawing a class. Preparing the historical evaluation matrices scales with the input domain and spanning-list length, rather than the total number of classes; this prototype retains those matrices and has not been optimized as an app implementation.

Use unbiased bounded-integer sampling for the global rank. At $C=4096$, for example, $T=98{,}304$ is not a power of two, so reducing a fixed uniform bit word modulo $T$ introduces bias. `Random.randrange(T)` in the prototype supplies bounded draws from a pseudorandom stream; seeded runs provide reproducibility. The mathematical uniformity statement assumes uniform random bits and does not claim that a finite set of seeds enumerates classes uniformly.

## 5. Exact counts and weighting at practical domains

The counts below use the proved historical modular coordinate algorithm for each conditional row and the new disjoint-union theorem. They are exact finite computations, without enumeration of all classes. Coordinate domain $C$ is twice displayed side $N$ for the reference checkerboard.

|      C | Displayed side N | Shared tail starts at v | Polynomial union classes | Single-power union classes | Ratio |
| -----: | ---------------: | ----------------------: | -----------------------: | -------------------------: | ----: |
|      8 |                4 |                       1 |                        1 |                          1 |     1 |
|     16 |                8 |                       1 |                        2 |                          2 |     1 |
|     32 |               16 |                       1 |                        4 |                          4 |     1 |
|     64 |               32 |                       2 |                       16 |                         16 |     1 |
|    128 |               64 |                       3 |                       64 |                         64 |     1 |
|    256 |              128 |                       4 |                      256 |                        256 |     1 |
|    512 |              256 |                       5 |                    1,024 |                      1,024 |     1 |
|  1,024 |              512 |                       6 |                    4,096 |                      4,096 |     1 |
|  2,048 |            1,024 |                       7 |                   16,384 |                     16,384 |     1 |
|  4,096 |            2,048 |                       8 |                   98,304 |                     65,536 |   3/2 |
|  8,192 |            4,096 |                       9 |                  655,360 |                    262,144 |   5/2 |
| 16,384 |            8,192 |                      10 |                4,980,736 |                  1,048,576 |  19/4 |
| 32,768 |           16,384 |                      11 |               38,797,312 |                  4,194,304 |  37/4 |
| 65,536 |           32,768 |                      12 |              576,716,800 |                 16,777,216 | 275/8 |

Single-power counts include odd output multipliers and quotient the common phase, matching the shift-class comparison; the old odd-affine quotient is a different count. For $C\ge32$, the existing single-power union has $C^2/256$ classes. The first three small domains have the direct tail counts above. Since every single-power class is already a member of the polynomial union, equality of the finite counts through $C=2048$ proves equality of those entire class sets. Polynomials first enlarge this union at the next power-of-two domain, $C=4096$.

At $C=1024$, the six disjoint row counts are 2,048; 1,024; 512; 256; 128; and 128. Their selection probabilities are $1/2$, $1/4$, $1/8$, $1/16$, $1/32$, and $1/32$. The last entry represents every valuation at least six.

At $C=4096$, the eight row counts are 65,536; 16,384; 8,192; 4,096; 2,048; 1,024; 512; and 512. Their probabilities are $2/3$, $1/6$, $1/12$, $1/24$, $1/48$, $1/96$, $1/192$, and $1/192$. The fixed-valuation-one count doubles relative to its single-power space, while the complete union grows by a factor of $3/2$. These are different comparisons.

## 6. What the visual observation means

Every valid member has precisely the same equality partition on the reachable odd inputs: $z$ and $C-z$ agree, and there are no other mergers. The existing same-valuation isometry theorem proves this because the pre-image power identifies exactly those pairs and the odd coefficient sum preserves its difference valuations. Every positive valuation therefore retains the same positions of equal-valued cells under the fixed coordinate map. That common geometry can make their fabric motifs look very similar.

The ranks assigned to those groups still vary. Sections 2 and 3 show that different productive rows cannot give the same anchored rank table, despite the shared equality partition; the explicit domain-64 example demonstrates the difference. Uniformity over classes is therefore a precise numerical and order statement, rather than a guarantee of uniform perceptual variety. This investigation establishes the union sampler without claiming that all its rows are visually distinct families.

## 7. Reproducible evidence and boundaries

The [verification script](verify.py) regenerates [results.json](results.json), including source hashes for the new code and the historical coordinate implementation. It checks every global rank and every independent conditional binary setting at $C=8,16,32,64,128,256$. It independently compares affine-module intersections through $C=4096$, including an extra tail valuation. Larger-domain checks cover every power of two through $C=65536$, random conditional draws, independently generated integer polynomials with odd coefficient sum, and complete pointwise logarithmic tail identities at three tail valuations.

With `--native`, it additionally checks ordinary expanded post-polynomials against the factored recipes in the workbench’s real XOR engine, both checkerboard orientations, exact axis periods, loss of the target period after halving the modulus, and shift/order signatures. It also checks existing gallery draws against the new invariant. The results file records the exact check totals and finite coverage. The general claims come from the proofs, rather than extrapolation from these runs.

The recorded native run completed **205,997 exact checks**, including 122 affine-module intersection tests, 640 seeded conditional draws, 72 native fields, and 36 draws from the existing gallery sampler. In the smallest domain, halving the post-modulus makes the pattern constant; the period check therefore requires loss of the target, allowing a drop by more than a factor of two.

The union includes arbitrary degrees and integer coefficients within each single positive valuation. It does not include mixed-valuation sums, the broader “even only” gallery style, valuation zero, or the unrestricted pseudo-square polynomial family from November 12. Those larger spaces have different overlap and shift/order questions. An independently restored color offset can be sampled after selecting the class; it does not alter the union weights.
