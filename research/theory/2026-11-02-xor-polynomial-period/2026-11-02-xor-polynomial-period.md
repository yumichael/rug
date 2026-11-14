# Constructing XOR polynomial patterns with the full repetition period

This investigation derives new results for the no-pre-operation XOR rug construction. It starts from the [earlier explanation](../2026-10-25-pattern-space/2026-11-01-xor-post-operations-explained.md) and resolves the distinction between a complete enumeration procedure and a direct, nonredundant recipe for full-period patterns.

The most useful result concerns sums of powers that all have the same valuation and therefore the same derived modulus: **the smallest axis periods remain unchanged exactly when the sum of the nonconstant coefficients is odd**. This condition can be built into a set of independent binary controls, so no rejection or pattern-table catalogue is needed after constructing the controls.

Arbitrary post-polynomials at the same modulus form a broader space. They also have explicit independent polynomial coordinates. Their period criterion is a small derivative test in the usual valuation range, and an exact finite-difference test at every valuation. Their full-period subset need not have a power-of-two size.

## 1. Scope and the two polynomial spaces

Fix a coordinate domain $C=2^c\ge8$, a valuation parameter $v\ge0$, and

$$
M=C2^v=2^m,\qquad m=c+v,\qquad R=C/2.
$$

We study one numerical channel before color conversion, cropping, or stretching. The spatial origin and orientation are fixed. We require the least horizontal period and least vertical period to be exactly $R$; smaller oblique translation lattices are a separate question.

The **same-valuation space** consists of

$$
H(z)=b+\sum_{u\text{ positive and odd}}a_u z^{2^vu}\pmod M,
$$

with finitely many nonzero integer coefficients. Its exponents all have valuation $v$. Coefficients can be even or odd; odd post-multipliers are included, and unrestricted integer sums supply the other coefficients too.

The **arbitrary-polynomial space** consists of all integer polynomials $H(z)$ evaluated modulo that same $M$. Here $v$ fixes precision rather than restricting the exponents. A polynomial containing only even powers is another restriction, not the same as fixing one valuation.

Throughout, a **shift class** identifies normalized channel patterns differing by a common circular phase. At fixed $M$, subtracting $H(1)$ gives a unique anchored table for that class. Every odd input $z=1,3,\ldots,C-1$ occurs, so equality of those anchored tables is exactly equality of the shift classes under the chosen construction. Each anchored result has exactly $M$ unanchored versions, obtained by restoring the constant value at input 1.

We cover both the original full-grid diagonal XOR and the additional checkerboard sampling studied previously. The binary constructions below do not assert the same guarantees for arbitrary sampling rules.

## 2. What a half-period displacement does to the XOR input

The original coordinates are $a=y-x-1$ and $b=y+x$, reduced modulo $C$ before XOR. Write their combined value as $Z(x,y)$. It is always odd. A shift by $R$ toggles the top bit of both operands and leaves their XOR unchanged, so $R$ is a period before any post-operation.

Put $h=C/2$. A half-period spatial displacement is $R/2=C/4$. It leaves every combined-input bit unchanged except possibly the top bit. More precisely:

| Construction and displacement         | Effect on the combined input                                                           |
| ------------------------------------- | -------------------------------------------------------------------------------------- |
| Full grid, horizontal half-period     | Toggle the top bit if the next-to-top bit is zero; otherwise leave the input unchanged |
| Full grid, vertical half-period       | Toggle the top bit if the next-to-top bit is one; otherwise leave the input unchanged  |
| Checkerboard, either axis half-period | Toggle the top bit for every input                                                     |

Here toggling the top bit sends $z$ to $z\mathbin{\mathrm{XOR}}h$, equivalently $z+h$ or $z-h$ within the raw input range.

**Proof for the full grid.** Separate each operand into its low $c-2$ bits and its top two-bit digit. A horizontal half-period subtracts one from the first top digit and adds one to the second, modulo four. Both low bits of those digits toggle, so their XOR cancels that toggle. Their top-bit toggles differ exactly when the XOR of their low bits is zero. This is the next-to-top bit of $z$. For the vertical displacement both top digits increase by one, so the top-bit toggles differ exactly when that XOR bit is one. Every opposite-parity operand pair occurs, so every input pair specified in the table is attained.

**Proof for the checkerboard.** The established input formula is $Z=C-1-2(i\mathbin{\mathrm{XOR}}j)$ with displayed coordinates reduced modulo $R$. Adding $R/2$ to either displayed coordinate toggles that bit of its XOR, and therefore toggles bit $C/2$ of $Z$.

Consequently, any post-function has exact axis periods $R$ precisely under these tests:

| Construction | Necessary and sufficient condition                                                                          |
| ------------ | ----------------------------------------------------------------------------------------------------------- |
| Full grid    | The difference between inputs separated by C/2 is nonzero somewhere in each of the two lower input quarters |
| Checkerboard | That difference is nonzero somewhere in the lower input half                                                |

In formulas, define $D_H(z)=H(z+h)-H(z)\pmod M$ for odd $1\le z<h$. For the full grid, require one nonzero $D_H(z)$ with $z<C/4$ and another with $z>C/4$. For checkerboard, require any nonzero $D_H(z)$ in the lower half. If a half-period is excluded, every smaller axis period is excluded because $R$ is a power of two. This proves the tests for every $v$, without evaluating a complete rug grid.

## 3. The parity theorem for same-valuation sums

**Theorem.** In the same-valuation space, both established constructions have exact axis periods $R$ if and only if

$$
\boxed{\sum_u a_u\text{ is odd}.}
$$

The constant $b$ does not affect this condition. If individual terms are written with odd post-multipliers, those multipliers count as odd factors in the coefficients. In particular, selecting an odd number of such terms with binary inclusion coefficients preserves the full period; selecting an even number loses it. This latter statement does not guarantee distinct outputs from distinct selections.

**Proof.** For odd integers separated by $h=C/2$ and every $p=2^vu$ with $u$ odd,

$$
(z+h)^p-z^p\equiv M/2\pmod M.
$$

For odd $p$, the difference has valuation $c-1$. For even $p$, the odd-input lifting formula gives valuation $(c-1)+1+v-1=m-1$, since $2z+h$ has valuation one. This also follows from the earlier power-congruence results. A difference with valuation $m-1$ is exactly $M/2$ modulo $M$. Reversing the pair gives the same residue.

Every toggled input pair in Section 2 therefore changes the polynomial output by

$$
D_H(z)\equiv\frac M2\sum_u a_u\pmod M.
$$

If the coefficient sum is odd, every toggled pair changes value. Both full-grid axes have such pairs, and both checkerboard axes toggle all pairs. Neither half-period survives. If the sum is even, every pair is unchanged, so both half-periods survive. This proves both directions.

This improves on a generic generate-and-filter method: period preservation is one coefficient-parity condition, independent of the size of the displayed table. The parity is intrinsic to the resulting pattern. If two polynomial descriptions give the same table, their difference is zero and the argument forces the same coefficient parity.

## 4. Why valid same-valuation patterns admit independent binary controls

Anchor every table at input 1. All anchored same-valuation sums form a finite additive group $V$. Define a bit $\chi(F)$ to be the coefficient parity from Section 3. The proof shows that it is well-defined on output tables, is additive modulo two, and takes both values. For example, $z^{2^v}-1$ has value one.

The full-period patterns are exactly the tables with $\chi(F)=1$. Thus they are one translate of the period-losing subgroup with $\chi(F)=0$, and

$$
\boxed{\text{number of full-period shift classes}=|V|/2.}
$$

There is a direct binary recipe for the whole valid set, not merely a large valid subset. First obtain independent cyclic generators $G_j$, with unique coefficients ranging from 0 through $2^{\ell_j}-1$. Section 5 gives a short constructive way to obtain them.

Choose a generator $G_*$ with $\chi(G_*)=1$ whose order exponent $\ell_*$ is smallest among those with character one. Subtract $G_*$ from every other character-one generator. This is an invertible change of cyclic coordinates: the chosen generator's order divides the order of every generator being adjusted. All other resulting generators have character zero, and the only period condition is that the coefficient of $G_*$ be odd.

Write that coefficient as $1+2t$. Every full-period pattern now has a unique expression consisting of the fixed base $G_*$ plus binary on/off additions. The additions are $2G_*,4G_*,\ldots,2^{\ell_*-1}G_*$ and $G_j,2G_j,\ldots,2^{\ell_j-1}G_j$ for every other generator. There are exactly

$$
\boxed{D=\sum_j\ell_j-1}
$$

independent bits, giving all $2^D$ valid shift classes. Every bit setting retains the period and distinct settings give distinct outputs. Uniform independent bits give uniform shift classes.

These switches are anchored integer-polynomial patterns, but the switches themselves have character zero and need not have full period. Their additions preserve the fixed base's character one. This is why the construction succeeds where arbitrary subsets of individually full-period patterns can cancel. The binary encoding is not linear over the two-element field; it is a unique digit encoding of modular coordinates.

## 5. A short polynomial spanning list for every valuation

Put $w=z^{2^v}$. The same-valuation polynomials are exactly $b+wA(w^2)$ for integer polynomials $A$. Set

$$
e=3\quad(v=0),\qquad e=v+3\quad(v\ge1).
$$

As the odd input $z$ varies below $C$, the values $w^2\pmod M$ cover exactly the congruence class $1\pmod{2^e}$. For $v=0$ this is the odd-square image; for positive $v$ it follows from the odd-unit power image. The earlier congruence lemma ensures that restricting the input from all odd residues modulo $M$ to odd residues below $C$ loses no power values. These use the unit-group and lifting results already established in the earlier research.

Define

$$
P_k(z)=w\prod_{j=0}^{k-1}\bigl(w^2-(1+2^e j)\bigr),\qquad P_0(z)=w.
$$

Only keep indices satisfying

$$
ek+\nu_2(k!)<m.
$$

The anchored generators are $P_0-1$ and $P_k$ for the retained positive indices. Each $P_k$ is a simple factored integer polynomial using only allowed odd powers of $w$; positive-index generators vanish at input 1. Their coefficient-sum characters are zero, while $P_0-1$ has character one.

**Spanning proof.** Integer Newton products with nodes $1,1+2^e,1+2\cdot2^e,\ldots$ are related to monomials by an integer unitriangular change of basis. For $w^2=1+2^e t$, the product in $P_k$ equals $2^{ek}(t)_k$, always divisible by $2^{ek}k!$. Thus every omitted product vanishes modulo $M$. The retained products span every $A(w^2)$, and multiplication by the odd unit $w$ preserves this conclusion. The first omitted index is at most the number of values in the congruence class, so the factorial divisibility also supplies the claimed cutoff for all later products.

Anchoring can create relations between these columns, so the list is a spanning list, not a claim of independence. Form its evaluation matrix on the actual odd inputs and diagonalize it modulo $M$, retaining the polynomial column operations. The result is an independent cyclic generator list with orders $2^{\ell_j}$. The script implements this by repeatedly choosing an entry of minimum valuation, removing its odd factor, and eliminating its row and column. All operations are invertible modulo $M$; transformed columns recover explicit polynomial generators.

This is a small-matrix construction rather than enumeration of patterns. It starts with only as many columns as satisfy the displayed cutoff. The practical cases in the results use a handful of such columns, even though the resulting number of patterns can be enormous. An elementary closed formula for all the positive-valuation cyclic orders is not claimed here.

## 6. A closed coordinate formula for odd-power sums

For $v=0$, the cyclic coordinates have an explicit form, with no matrix diagonalization needed. Let

$$
G_0(z)=z-1,\qquad G_k(z)=z\prod_{j=0}^{k-1}\bigl(z^2-(1+8j)\bigr)\quad(k\ge1).
$$

Keep the positive indices with $3k+\nu_2(k!)<c$. Every anchored odd-power sum has a unique representation

$$
H(z)=a_0G_0(z)+\sum_{k\ge1}a_kG_k(z)\pmod C,
$$

with coefficient orders

$$
0\le a_0<2^{c-1},\qquad0\le a_k<2^{c-3k-\nu_2(k!)}.
$$

It has full period exactly when $a_0$ is odd. Therefore the exact number of valid shift classes is $2^D$, where

$$
\boxed{D=c-2+\sum_{k\ge1}\max\bigl(0,c-3k-\nu_2(k!)\bigr).}
$$

**Uniqueness proof.** Before anchoring, the polynomials $P_k=z\prod_{j<k}(z^2-(1+8j))$ have independent coefficient ranges of sizes $2^{c-3k-\nu_2(k!)}$, including size $2^c$ for $k=0$. Evaluate successively at roots of square values $1+8k$. Each Newton diagonal has valuation $3k+\nu_2(k!)$, giving uniqueness in its stated range. Earlier columns whose coefficients reach their range boundary vanish as complete functions, so this triangular argument is valid modulo $C$.

Anchoring identifies precisely the constant functions in this odd-polynomial space. Such a constant must equal its own negative under $z\mapsto-z$, so it is either zero or $C/2$. Both occur: $(C/2)z$ is the constant $C/2$ on odd inputs. Only the coefficient of $P_0$ changes, by $C/2$, under this identification. This halves its range and leaves the others unchanged, proving the anchored coordinate formula. Section 3 supplies the period condition.

## 7. Explicit recipes at domain size 256

For odd-power sums, $C=256$, $v=0$, and $M=256$, every full-period shift class is represented exactly once by

$$
H(z)=(1+2A)(z-1)+Bz(z^2-1)+Ez(z^2-1)(z^2-9)\pmod{256},
$$

where $A=0,\ldots,63$, $B=0,\ldots,31$, and $E\in\{0,1\}$. These are six, five, and one independent bits, respectively: **12 bits and 4,096 patterns**, all with least axis periods 128. A phase can be added afterward.

For valuation one, $M=512$. Put $w=z^2$. The short spanning list is $w-1$ and $w(w^2-1)$. A convenient independent replacement is

$$
G_0=z^2-1,\qquad G_1=z^6-91z^2+90.
$$

The second generator factors as $(w-1)(w-9)(w+10)$. Its minimum valuation is seven: write $w=1+8t$, giving $64t(t-1)(11+8t)$, with the last factor odd. Its order modulo 512 is therefore four. The first generator has order 64. At $w=9$, $G_1=0$ and $G_0=8$, so a vanishing combination first forces the first coefficient to be zero modulo 64, then the second to be zero modulo four. This proves independence.

Every full-period shift class in this valuation-one space is therefore represented exactly once by

$$
H(z)=(1+2A)(z^2-1)+B(z^6-91z^2+90)\pmod{512},
$$

with $A=0,\ldots,31$ and $B=0,\ldots,3$. That is **seven independent bits and 128 patterns**. Every setting has the full period. Here polynomial combinations introduce no additional full-period shift classes beyond the corresponding valuation-one power-and-multiplier family; at larger domains they can introduce additional classes.

## 8. High valuations and practical same-valuation counts

There is another closed case. For $v\ge\max(1,c-5)$, the anchored same-valuation space is generated by $z^{2^v}-1$ alone. It has order $C/4$, and exactly $C/8=2^{c-3}$ full-period shift classes.

**Proof.** Put $d=2^{v+2}$ and $w=1+dt$. Only $P_0$ and $P_1$ from Section 5 can remain nonzero in this range. Subtract $(1+d)(2+d)(w-1)$ from $P_1=w(w^2-1)$. The remainder is

$$
(w-1)(w-1-d)(w+2+d).
$$

Its minimum valuation is $2(v+2)+1$, at least $m$ under the stated bound, so it vanishes. The remaining generator $w-1$ has minimum valuation $v+2$ and hence order $2^{m-v-2}=C/4$. Its odd coefficients give the claimed full-period half.

For the field sizes discussed previously, the following table gives **independent valid bits** for each fixed valuation. Each entry $D$ means exactly $2^D$ full-period shift classes; these are computed by the proved short-matrix construction, not inferred from a fitted formula.

| Field dimensions in cells    | Coordinate domain | Valuation 0 | Valuation 1 | Valuation 2 | Valuation 3 | Valuation 4 |
| ---------------------------- | ----------------: | ----------: | ----------: | ----------: | ----------: | ----------: |
| 512 × 256                    |             1,024 |          18 |          11 |          10 |           9 |           8 |
| 1,024 × 512                  |             2,048 |          22 |          13 |          12 |          11 |          10 |
| 2,048 × 512 or 2,048 × 1,024 |             4,096 |          26 |          16 |          14 |          13 |          12 |

For example, at $C=4096$, valuation zero gives 67,108,864 full-period shift classes and valuation one gives 65,536. The counts are conditional on a fixed valuation. Spaces at different valuations use different moduli and can overlap after normalized comparisons, so summing rows or columns is not a joint classification across valuations.

These field-to-domain conversions assume fresh or adapted references, with $C$ twice the longer field side in cells. Pixel enlargement does not increase the counts; retained references can preserve a different domain.

## 9. Independent polynomial coordinates for the unrestricted space

For all integer post-polynomials at fixed $C$ and $M$, use Newton products directly on the actual odd inputs:

$$
B_k(z)=\prod_{j=0}^{k-1}\bigl(z-(1+2j)\bigr),\qquad B_0=1.
$$

Let $n=C/2$. Every polynomial output table on those inputs has a unique representation using indices $0\le k<n$ with $k+\nu_2(k!)<m$, and coefficient ranges

$$
0\le a_k<2^{m-k-\nu_2(k!)}.
$$

For shift classes, drop $k=0$: all other products already vanish at input 1. Put

$$
\ell_k=m-k-\nu_2(k!),\qquad S=\sum_{\substack{1\le k<n,\,\ell_k>0}}\ell_k.
$$

There are exactly $2^S$ anchored polynomial tables before filtering period. Their cyclic coordinates are explicit polynomials, with no matrix decomposition needed for this first step.

**Proof.** Division by the monic product $B_n$ reduces every integer polynomial to degree below $n$ without changing any input value. Newton expansion at the integer nodes then gives integer coefficients. At input $z=1+2t$, $B_k(z)=2^k(t)_k$, divisible by $2^k k!$, and its value at $t=k$ attains that valuation. Coefficients can therefore be reduced to the stated ranges. Evaluation at successive nodes proves uniqueness. Terms whose displayed exponent is nonpositive vanish as complete tables.

This restricted-input normal form can be smaller than the earlier normal form on every residue modulo $M$. It directly answers which integer polynomials are distinguishable on the XOR input set.

## 10. A derivative criterion in the usual valuation range

**Theorem.** Suppose $C\ge32$ and $0\le v\le c-4$. For any integer polynomial $H$, both established constructions have exact axis periods $R$ if and only if

$$
\boxed{H'(r)\not\equiv0\pmod{2^{v+1}}\text{ for at least one odd residue }r.}
$$

Only $2^v$ residues need to be tested, independent of $C$. For valuation zero this is a single parity condition; for valuation one the derivative is tested modulo four.

**Proof.** Write $h=C/2$. Taylor expansion of each monomial, with integer binomial coefficients, gives

$$
H(z+h)-H(z)\equiv hH'(z)\pmod M.
$$

All terms with at least two factors of $h$ are divisible by $2^{2c-2}$, which is divisible by $M$ in the stated range. The difference is zero modulo $M$ exactly when $H'(z)$ is zero modulo $2^{v+1}$.

Polynomial evaluation modulo $2^{v+1}$ depends only on the input residue. Each lower input quarter contains every odd residue modulo that number because $C/4$ is a multiple of $2^{v+1}$. Thus a nonzero derivative value supplies witnesses in both full-grid quarters, and also supplies a checkerboard witness. If every derivative value is zero, all half-period pairs are unchanged. Section 2 completes the proof.

The derivative test is invariant under the polynomial description on the actual input set. If an integer polynomial vanishes on that entire set, its half-pair differences vanish, and the argument forces its derivative values in this test to vanish as well.

At $v=0$, the derivative at any odd input has parity equal to the sum of the odd-degree coefficients. At $v=1$, it is constant on odd inputs modulo four: odd powers of the input have even derivative coefficients, and even powers of the input are 1 modulo four. At $v=2$, the derivative functions modulo eight have the form $a+2bz$ and give 16 distinct value tables. These yield derivative-image sizes 2, 4, and 16, respectively; arbitrary $a$ and the required coefficient of $z$ are supplied by derivatives of linear and quadratic polynomials.

## 11. Counts and sampling for arbitrary polynomials

The derivative vectors of the independent generators from Section 9 generate a finite image of size $2^\delta$ modulo $2^{v+1}$. Compute $\delta$ by diagonalizing the small matrix whose column for $B_k$ is its derivative evaluated on those odd residues. The period-losing tables are exactly the kernel of this map. Every image value has the same number of preimages, so

$$
\boxed{N_{\mathrm{valid}}=2^S-2^{S-\delta}=(2^\delta-1)2^{S-\delta}.}
$$

For $C=256$, the first values are:

| Valuation | Modulus | Bits before period filtering | Derivative image size | Full-period shift classes |
| --------: | ------: | ---------------------------: | --------------------: | ------------------------: |
|         0 |     256 |                           17 |                     2 |                    65,536 |
|         1 |     512 |                           22 |                     4 |                 3,145,728 |
|         2 |   1,024 |                           27 |                    16 |               125,829,120 |

These are the unrestricted polynomial spaces, not the smaller same-valuation spaces. For example, the valuation-one unrestricted space allows odd and even degrees at modulus 512, whereas the same-valuation space allows degrees 2, 6, 10, and so on, plus the constant.

For the unrestricted space, uniformly sample the independent coefficients from Section 9 and reject only when the derivative vector is zero. Since those coordinates enumerate tables uniquely, accepted results are uniform full-period shift classes. The acceptance probability is $1-2^{-\delta}$, at least one half because the derivative of $z$ is 1. This avoids deduplication and grid scans, though it is a rejection sampler rather than the rejection-free same-valuation binary construction.

The valid count need not be a power of two: the valuation-one count contains a factor of three. Therefore a fixed number of independent unbiased binary switches cannot cover every valid output exactly once in general. A variable-length random stream or an additional nonbinary choice can represent the distribution instead.

## 12. Exact unrestricted results at every valuation

For larger $v$, retain the exact finite-difference criterion of Section 2 rather than assuming the derivative simplification. Section 9 still gives explicit independent polynomial coordinates for every $v$.

For the full grid, form two matrices: their columns are $B_k(z+C/2)-B_k(z)$ modulo $M$, evaluated on odd $z$ in the first and second lower quarters, respectively. Let their image sizes be $2^{d_x}$ and $2^{d_y}$, and let the vertically stacked matrix have image size $2^{d_{xy}}$. Then the exact number of full-period shift classes is

$$
\boxed{N_{\mathrm{valid}}=2^S-2^{S-d_x}-2^{S-d_y}+2^{S-d_{xy}}.}
$$

**Proof.** Half-period invariance is the kernel of the corresponding difference map. Its kernel has size $2^{S-d_x}$ or $2^{S-d_y}$. Both half-periods hold precisely in the kernel of the stacked map, of size $2^{S-d_{xy}}$. Inclusion–exclusion gives the formula. All image sizes are obtained by modular diagonalization of the explicit polynomial columns, without enumerating output tables.

For checkerboard, both axes use the same complete lower-half difference map. If its image size is $2^d$, the count is $2^S-2^{S-d}$. The derivative theorem shows why the two constructions' unrestricted counts agree in the usual valuation range. Their exact period constraints need not be identified outside that range.

For an even-only polynomial style, the same difference-map construction works after replacing the unrestricted spanning columns by integer polynomial generators in $z^2$ and finding their independent anchored image coordinates. The unrestricted count table above does not claim to count that restricted style.

## 13. What has been resolved and what remains separate

The same-valuation problem now has an exact coefficient criterion, a complete finite polynomial spanning list, a constructive independent-coordinate procedure, and a rejection-free binary recipe for all valid shift classes. Odd-power sums and sufficiently high valuations additionally have closed coordinate/count formulas. The practical intermediate-valuation counts use exact small-matrix calculations.

The arbitrary-polynomial problem has an explicit independent normal form on the actual odd inputs, an exact finite-difference characterization for every valuation, and a derivative criterion and efficient uniform rejection sampler in the usual valuation range. A general elementary expression for the derivative-image size as a function of valuation is not claimed; the finite matrix determining it is specified and implemented.

Uniformity here is over anchored numerical shift classes at fixed domain, modulus, and polynomial family. Restoring an offset multiplies each count by $M$ at that fixed precision. These results do not establish uniform visual variety, identical color behavior across moduli, cross-period consistency of the new polynomial coordinates, or a joint deduplication across different valuations. They do not alter the application.

## 14. Reproducible verification

The [script](xor_polynomial_period.py) uses Python integer arithmetic and the standard library. Run it from the repository root:

```sh
python3 research/theory/2026-11-02-xor-polynomial-period/xor_polynomial_period.py
```

It writes [results.json](results.json), including independent coordinate orders, period characters, valid counts, derivative-image orders, and coverage. The run accompanying this report completed **59,463 exact checks**. Proofs establish the general results; these checks verify the implementation and explicit examples over finite ranges.

| Check                                                                | Coverage                                                                                                                                                            |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Literal grid versus derived half-shift input pairs                   | C = 8, 16, 32, 64; full grid and checkerboard; both axes                                                                                                            |
| Short same-valuation coordinates versus independent monomial closure | C = 8, 16, 32, 64; valuations 0 through 3; all obtainable anchored tables                                                                                           |
| Independent binary controls                                          | Every switch setting in those 16 spaces; uniqueness and exact periods for both constructions                                                                        |
| Odd-input Newton normal form versus independent monomial enumeration | All 4,096 four-coefficient descriptions modulo eight                                                                                                                |
| Unrestricted polynomial counts and period tests                      | Complete anchored spaces at C = 8, valuations 0–3; C = 16, valuations 0–2; C = 32, valuations 0–1; C = 64, valuation 0                                              |
| Derivative congruence and full-grid quarter witnesses                | 480 seeded degree-at-most-11 polynomials across C = 32 through 512 and all productive valuations                                                                    |
| General finite-difference counts versus derivative counts            | 18 construction/precision cases at C = 32, 64, 128                                                                                                                  |
| Explicit recipes and displayed size counts                           | All 8,192 and 256 anchored coefficient settings of the two displayed recipes, including literal-grid period tests; exact size calculations recorded in results.json |

The source basis computations use all reachable odd inputs. The script retains polynomial column transformations, so its independent generators can be reconstructed from the short factored spanning list. It does not create a production UI or benchmark interactive generation at the largest app sizes.

## Sources and relationship to earlier work

- [October 13 XOR theory](../2026-10-13-post-power/2026-10-13-xor-post-power-theory.md), Sections 3.1–3.5: odd-input power congruences, input coverage, and the balanced period witnesses. These support the new coefficient-parity theorem.
- [October 25 pattern-space theory](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md), Sections 7.5, 9.1, and 10: checkerboard input formula, polynomial normal forms, image modules, and generic exact-period filtering. This report specializes and extends those methods into the results proved above.
- [XOR post-operation explanation](../2026-10-25-pattern-space/2026-11-01-xor-post-operations-explained.md): the single-channel model, affine versus shift equivalence, practical domain sizes, and the discussion motivating this investigation.
