# Symmetric rug constructions: repetition, polynomial families, and order classes

This report carries out the investigation specified in [the research brief](research-goal.md), including the clarification that the pre-modulus is selected **after assessing the immediate basic combiner**. It develops new proofs and exact checks. The generator application is unchanged.

The useful conclusions are:

| Generator question                                                                                | Result                                                                                                                                                                                                        |
| ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Where should the pre-modulus be tested?                                                           | On the sampled basic-combiner table, or tuple of such tables, before post-processing. Testing the operands alone is insufficient.                                                                             |
| Can whole families of even pre-polynomials share a minimum pre-modulus?                           | Yes. Section 3 gives an explicit infinite coefficient family. Six combiners have a shared individual minimum; AND has a proved least common sufficient modulus, with possibly smaller member-specific minima. |
| Is checkerboard sampling always a good replacement for the full grid?                             | No. For even pre-powers it usually exposes different periods in the two operand directions. The seven sampling rules require separate period and phase calculations.                                          |
| Does the earlier infinite squared-pre AND example survive the corrected pre-modulus rule?         | Yes. Its minimum pre-modulus is still 64 for target axis periods 32.                                                                                                                                          |
| Can all post-powers be handled without a precision cap for the even-pre OR/XOR/ADD/ABSDIFF cases? | Yes, at a fixed selected pre-modulus. Their odd-valued basic tables have a proved finite normalized tail and complete finite shift/order catalogues.                                                          |
| Do the existing balanced XOR results change under order-class equivalence?                        | Single-power results and valid same-valuation polynomial results do not change: their shift classes and order classes coincide. Arbitrary polynomial results can change.                                      |
| Is there a complete order-class procedure without an arbitrary precision cap?                     | Yes for unrestricted integer post-polynomials, and for even-only post-polynomials of a nonnegative scalar input, at a fixed pre-modulus. Section 7 proves a finite sufficient precision bound.                |
| Is that general procedure suitable for interactive generation?                                    | It is a terminating theoretical fallback. Its worst-case catalogue is enormous; the XOR formulas and the shared pre-polynomial family are the immediately compact results.                                    |

“Integer polynomial” throughout means a polynomial with integer coefficients. Rational-coefficient polynomials that merely take integer values are a different family.

## 1. Arithmetic, coordinates, and what the two minima mean

### 1.1 Four stages and the original domain

The original coordinate-domain label is $C=2^c$. It determines the requested repetition domain through an explicit style convention; it is not an implicit arithmetic reduction. In the historical XOR convention the requested axis period is $R=C/2$. The results below also allow independently specified dyadic axis periods $R_x,R_y$.

Use unwrapped integer coordinates and the historical operand forms

$$
a=y-x-1,\qquad b=y+x.
$$

There is no preliminary reduction modulo $C$. Apply the same pre-function $P$, reduce each result modulo $K=2^k$, and evaluate one or more basic combiners:

$$
A=P(a)\bmod K,\qquad B=P(b)\bmod K,\qquad Z_K=G(A,B).
$$

All seven basic operations use their definitions in [the brief](research-goal.md): AND, OR, XOR, ordinary integer ADD and MULT, the full carryless product CLMUL, and ordinary nonnegative ABSDIFF. In particular, ADD, MULT, and CLMUL have no intermediate output truncation. Each $Z_K$ is nonnegative.

Write the further stage-three expression as $H(Z_K)$, or $H(Z_{K,1},\ldots,Z_{K,s})$ for several symmetric basic outputs. Finally evaluate modulo $M=2^m$. Normalized channel values are the residues divided by $M$. An additive constant supplies an independent circular phase.

Fix the spatial origin, orientation, and a reference cell $t_0$. The anchored normalized output is $((F(t)-F(t_0))\bmod M)/M$. A shift class retains this complete numerical table; an order class retains only which cells have equal anchored values and the ascending order of those groups. Translations and rotations are not identified. Anchoring at a different reference can change an order signature, so use the same reachable reference throughout each comparison.

### 1.2 Minimum pre-modulus: retain the domain after the basic combiner

Fix the pre-function, basic combiner or tuple, sampling, and target periods. Choose the smallest $K$ for which the basic output's least displayed axis periods are **at least** $R_x,R_y$. Then hold $K$ fixed while choosing post-operations. A common family-level $K$ must satisfy this requirement for every admitted member.

This implements “do not shrink the repetition domain.” Requiring the basic table itself to have exactly those periods is a stricter policy, and can fail because its periods skip sizes. For example, with fourth-power pre-operation, AND, and full-grid sampling, its least axis periods are:

|         Pre-modulus K |   16 |   32 |   64 |  128 |  256 |  512 |
| --------------------: | ---: | ---: | ---: | ---: | ---: | ---: |
| Basic AND axis period |    1 |    8 |    8 |    8 |    8 |  128 |

Thus the first pre-modulus that avoids shrinking a target of 16 is 512, whose basic period is 128. A later post-operation must still attain 16 exactly; this first-stage test does not promise that one can. These entries are exact finite calculations, not a proposed formula for every larger $K$.

For integer pre-polynomials the sampled basic table is periodic on a displayed $K\times K$ torus, because integer polynomials preserve congruences. Every axis period is consequently a power of two. The pre-modulus test is therefore just: the translation by $R_x/2$ is not a period on the first axis, and likewise for $R_y/2$, when both targets exceed one. For a tuple, a translation must preserve every component to count as a period.

The subsequent tests assume this finite-torus property. A more general pre-function needs a proved finite operand period first; applying an arbitrary integer-valued function does not guarantee periodicity after reduction.

### 1.3 Minimum post-modulus: attain the exact domain for the chosen expression

At the selected $K$, fix an integer post-expression $H$. Its minimum post-modulus is the smallest $2^m$ giving the exact requested final periods. A failed post-expression is inadmissible at that $K$; it does not silently cause a larger pre-modulus to be selected.

Call an evaluation at its minimum valid post-modulus **minimum-period precision**. This property depends only on the output table at that modulus and the requested translations; Section 2 gives its test. It is distinct from choosing the smallest modulus among all realizations of one order class. Canonical selection first considers evaluations at minimum-period precision, then chooses the smallest modulus available for the selected order class.

Both restrictions matter. An order visible only at an unnecessarily large modulus for a particular expression must not enter the minimum-period catalogue merely because that expression has the right final period there.

## 2. Exact period tests, impossibility, and modulus selection

### 2.1 Difference depths give the complete post-modulus interval

Fix a complete sampled basic table and an integer post-expression. Before the final reduction, let $U(t)$ be its integer output at displayed cell $t$. For a displayed translation $h$, put

$$
d(h)=\min_t\nu_2\bigl(U(t+h)-U(t)\bigr),\qquad \nu_2(0)=+\infty.
$$

Then $h$ is a period modulo $2^m$ exactly when $m\le d(h)$. For targets $R_x,R_y>1$, define

$$
\ell=1+\max\{d((R_x/2,0)),d((0,R_y/2))\},\qquad u=\min\{d((R_x,0)),d((0,R_y))\}.
$$

The valid exponents are exactly the finite integers $m\ge1$ with $\ell\le m\le u$. The minimum is $\ell$ when that interval is nonempty. This is the [earlier difference-depth theorem](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md), Section 6.1, applied after fixing the new pre-modulus and sampling. For a target of one, omit that axis's half-period exclusion.

**Reason.** The upper inequalities make each requested translation a period. Every shorter axis period then divides its requested dyadic period, so it divides its half. The lower inequalities exclude precisely those half-periods. The argument applies to every listed combiner, to polynomials in several intermediate outputs, and to rectangular targets.

Odd multiplication preserves all these depths and any additive constant cancels. For monomials, the exact lifting formulas in the earlier report's Section 6.2 compute the depths without constructing enormous powers. The accompanying script checks those formulas against direct integer powers.

For example, with squared pre-operation, full-grid sampling, and requested periods 32, all seven basic combiners select minimum $K=64$. Their minimum final moduli differ substantially:

| Basic combiner | Post-power 1 | Post-power 2 |
| -------------- | -----------: | -----------: |
| AND            |           64 |        2,048 |
| OR             |           64 |          128 |
| XOR            |           64 |          128 |
| ADD            |           64 |          128 |
| MULT           |          256 |        2,048 |
| CLMUL          |          256 |        2,048 |
| ABSDIFF        |            4 |          128 |

These entries come from exact difference-depth calculations and literal period checks. The small ABSDIFF modulus retains only two distinct values while still attaining period 32. An economical modulus does not guarantee a rich value distribution.

### 2.2 A table test for minimum-period precision

Suppose a table modulo $M$ already has the exact requested periods. It is at minimum-period precision if and only if **at least one** of the two half-period translations changes every cell by either zero or $M/2$, with a nonzero change somewhere.

**Proof.** Each half-period must change some value modulo $M$. The minimum exponent is $m$ precisely when the larger of their difference depths is $m-1$. A depth of $m-1$ says exactly that every difference is zero or $M/2$, with at least one $M/2$. The other half-period need only have some nonzero difference. This explains why the condition says “at least one axis,” not both.

This criterion uses only residues. There is no need to recover the integer coefficients of the expression to determine whether its current modulus is minimal.

### 2.3 Can any polynomial recover the target at this pre-modulus?

There is a complete finite test for arbitrary integer post-polynomials, even when no precision bound has been chosen. Regard each distinct basic output, or distinct tuple of outputs, as one **input group**. All cells in one input group necessarily get the same post-processed value.

Join two input groups whenever cells related by a requested full-period translation encounter those groups. Take the transitive closure. Every admissible post-operation must be constant on each resulting component. Next examine each forbidden half-period translation.

**Theorem.** Some integer post-polynomial attains both exact requested periods if and only if, on each axis, at least one half-period pair belongs to different components. The same criterion applies to even-only post-polynomials when the scalar basic input is nonnegative. A realization can also be required to use minimum-period precision.

**Proof of necessity.** Full-period invariance forces the component identifications, so a half-period entirely inside components cannot be broken by any pointwise post-operation.

**Proof of sufficiency.** Assign each component a binary label. For either half-period, labels making it invariant form a proper linear subspace of the binary label space under the stated condition. Two proper subspaces cannot cover a vector space: if neither contains the other, the sum of a vector in each exclusive part is in neither; if one contains the other, their union is proper. Thus some binary assignment breaks both half-periods. Assign numerical values zero and one half according to these labels. Section 7's interpolation construction realizes this table by an integer polynomial at a sufficiently large power-of-two modulus. Every changed half-period difference is then half the modulus, so that modulus is minimal. Squaring distinct nonnegative input values preserves distinctness and gives the even-only assertion.

This is an impossibility test before attempting polynomial coefficient sampling. It does not say that a single post-power can realize every feasible target.

Applied to fourth-pre-power AND at the minimum pre-modulus 512 for a requested period of 16, this test rules out every integer post-polynomial. The basic period jump does not merely defeat a few selected post-powers. This is an exact finite instance of the component test, not a claim about all larger pre-moduli.

## 3. A shared pre-modulus for useful even pre-polynomial families

### 3.1 An infinite family that preserves numerical distinctions

Fix an even positive integer $q$, and let $Q$ be any integer polynomial. Define

$$
f(t)=t+2t(t-1)Q(t),\qquad P(x)=f(x^q).
$$

This includes $P(x)=x^q$ but allows arbitrarily many higher terms with unrestricted coefficients. For example, $q=2$, $Q=1$ gives $P(x)=2x^4-x^2$.

**Lemma.** For every pair of integers $s,t$, the quotient $(f(s)-f(t))/(s-t)$ is odd when $s\ne t$. Consequently

$$
\nu_2(f(s)-f(t))=\nu_2(s-t).
$$

**Proof.** For any integer polynomial $V$, $V(s)-V(t)$ is divisible by $s-t$. Apply this to $V(t)=t(t-1)Q(t)$. The quotient for $f$ is one plus twice an integer. Also $f(0)=0$, $f(1)=1$, and $f(t)$ has the same valuation as $t$.

Thus applying $f$ changes numerical arrangements without changing the pre-function's periods at any power-of-two modulus. Every member remains functionally even: $P(-x)=P(x)$.

### 3.2 Closed minimum pre-moduli for six combiners

Use the full historical grid, target equal axis periods $R=2^r\ge8$, and put $w=\nu_2(q)$. For the entire family above, the minimum pre-modulus that avoids shrinking the basic-combiner periods is:

$$
\boxed{K_{\min}=2^{r+w}\quad\text{for OR, XOR, ADD, and ABSDIFF},}
$$

$$
\boxed{K_{\min}=2^{\max(r+w,q+1)}\quad\text{for MULT and CLMUL}.}
$$

At these choices the basic periods on both axes are $2^{k-w}$, where $k=\log_2 K_{\min}$. Hence they equal $R$ for the first four combiners. For MULT and CLMUL they can be larger than $R$ when an increased modulus is needed to retain a nonzero even operand. These formulas concern the basic table, not an automatic final post-modulus rule.

**Proof.** The least additive period of $x^q\bmod2^k$ is given in [October 25, Section 8.1](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md). In the present range the odd-input branch has physical period $2^{k-w}$; the even-input branch has period dividing half of that. The lemma preserves both facts for $f(x^q)$. Smaller $k<r+w$ cannot retain period $R$, since the complete pre-function already has a shorter period.

At $k=r+w$, a half-period shift leaves the even branch unchanged but changes the odd branch somewhere. Every opposite-parity operand pair is reachable on the historical grid. Choose the even operand to be zero. OR, XOR, ADD, and ABSDIFF then return the nonnegative odd operand, so each axis has a witness against the half-period. The full requested period already preserves both operands.

MULT and CLMUL vanish if $k\le q$, because the even operand is zero and $f(0)=0$. If $k>q$, choose the even input to be two. Its pre-value is nonzero and is unchanged by the half-period shift. Multiplication by a fixed nonzero integer is injective on integers; multiplication by a fixed nonzero binary polynomial is injective in the polynomial ring over the two-element field. These facts apply to the full, untruncated MULT and CLMUL outputs. Both therefore retain the odd branch's period. The first allowable $k$ is exactly $\max(r+w,q+1)$.

For scale, at a requested period of 512, squaring and sixth powering both have $w=1$ and use $K=1024$ for all six combiners. Fourth and eighth powering use $K=2048$ and $4096$, respectively. Tenth powering uses $K=1024$ for the first four, but MULT and CLMUL need $K=2048$ because the even operand would otherwise vanish. The unrestricted polynomial $Q$ does not alter any of these guarantees.

### 3.3 A closed rule for pure even-pre-power AND

There is also a closed full-grid pre-modulus rule for AND when $P(x)=x^q$ itself. Let $q$ be even and $w=\nu_2(q)$. The bit positions that can survive the AND of an odd and an even pre-powered operand are exactly

$$
J_q=\begin{cases}\{j:j\ge4\},&q=2,\\\{q\}\cup\{j:j\ge q+w+2\},&q\ge4.\end{cases}
$$

At $K=2^k$, let $j$ be the largest member of $J_q$ below $k$. If there is no such member, the basic AND table is zero. Otherwise its two exact full-grid axis periods are

$$
\boxed{2^{j+1-w}.}
$$

For a requested $R=2^r\ge8$, take the smallest $j_*\in J_q$ with $j_*\ge r+w-1$. Then

$$
\boxed{K_{\min}=2^{j_*+1}.}
$$

**Bit-support proof.** Powers of odd inputs have bit zero set, bits one through $w+1$ zero, and can set every individual higher bit. For the last assertion, changing an odd input by $2^{j-w}$ toggles bit $j\ge w+2$ while preserving lower bits, by the lifting formula. An arbitrary integer input is an odd input times a power of two; its power shifts those possible bits by a multiple of $q$. For $q\ge4$, the possible bit positions of an arbitrary $q$th power are therefore $\{0\}\cup\{j\ge w+2\}$. For $q=2$ they are $\{0\}\cup\{j\ge2\}$. Restricting to even inputs shifts these sets by $q$. Intersect with the odd-input bit positions to obtain $J_q$.

**Period proof.** All AND bits above $j$ are identically zero. On the low $j+1$ bits, the odd branch has physical period $2^{j+1-w}$ and the even branch has a period dividing its half. A full shift by that period preserves the output. Choose an even operand with bit $j$ set. A half-period shift leaves that operand's low bits unchanged and toggles bit $j$ of the odd branch; both grid axes permit such a witness. Hence the half-period is excluded and the displayed period formula is exact.

For example, fourth-power AND has possible positions 4 and every position from 8 upward. The absence of positions 5, 6, and 7 explains the period jump in Section 1. At a target period of 512, the minimum pre-moduli for pure pre-powers 2, 4, 6, 8, and 10 are respectively 1,024; 2,048; 1,024; 16,384; and 2,048. Their basic periods are respectively 512; 512; 512; 2,048; and 1,024. The last two overshoot, so their post-operation target still requires the separate feasibility test.

### 3.4 A least common AND pre-modulus for the polynomial family

AND does not reveal the odd operand when the even operand is zero, nor is bitwise AND with a fixed nonzero mask injective. The previous proof therefore supplies no AND guarantee.

The distinction is real. With target period eight, $P=x^2$ first has a nonconstant basic AND table at $K=32$, with periods 16. Replacing it by $P=2x^4-x^2$, a member of the same family, gives periods eight already at $K=16$. For the latter, pre-inputs two and three have residues 12 and 9 modulo 16, whose AND is 8; ordinary squared-pre AND is zero at that modulus. These finite examples show that preserving the pre-function's periods does not preserve the minimum after AND.

Nevertheless, the pure-power minimum in Section 3.3 is exactly the **least common sufficient K for the whole polynomial family**, under the no-shrinking policy. Individual members can use smaller values, but none needs a larger one to retain the domain.

**Proof.** An isometry $f$ maps each complete congruence class $a\pmod{2^h}$ bijectively onto $f(a)\pmod{2^h}$ at every higher modulus. It preserves the class's size and its difference valuations. The odd pre-values therefore still fill $1\pmod{2^{w+2}}$.

For $q\ge4$, even inputs of the form $2t$ with $t$ odd have raw powers filling $2^q\pmod{2^{q+w+2}}$. After $f$, bit $q$ remains set because valuation is preserved, and every individual bit at position $q+w+2$ or higher is still attainable. Thus every position in the pure-power set $J_q$ remains usable by AND. For $q=2$, the even input four gives $f(16)\equiv16\pmod{32}$, guaranteeing position four. Even inputs twice an odd integer fill $4\pmod{32}$ before $f$, so every position from five upward is still attainable afterward. Again all of $J_2$ survives.

At the selected pure-power critical position $j_*$, a half-period shift preserves the even branch's low bits and toggles that odd-branch bit, by the isometry lemma. Choose an even operand with that bit set to obtain the required AND witness on both axes. Hence every member retains periods at least $R$ at the pure-power minimum. No smaller modulus can work for the whole family, because its member $Q=0$ already requires this one.

This yields a consistent pre-modulus for all seven combiners and this entire pre-polynomial family. To find an individual member's smaller AND minimum, the same table test only needs to search up to this proved family bound. The common AND choice may give some members basic periods larger than the target; post-processing still undergoes its separate exact-period test.

### 3.5 Why unrestricted pre-polynomials have no universal finite K

The family $P_s(x)=2^s x^2$ consists entirely of even pre-polynomials. For any proposed fixed $K=2^k$, members with $s\ge k$ are identically zero after the pre-modulus. Every basic output is constant. Consequently no finite $K$ can preserve a nontrivial domain for every integer pre-polynomial with unrestricted coefficients.

Family admissibility is essential. The preceding shared family avoids this obstruction by controlling its difference valuations. More general families may instead impose coefficient conditions or specify a fixed-modulus functional admissibility test.

## 4. The seven sampling rules, symmetry, and erased variation

### 4.1 Exact sample maps

The following maps fix phase, orientation, and displayed axes. The variables $(x,y)$ refer to the original historical grid, while $(i,j)$ are displayed indices before stretch.

| Method | Absolute selection                    | Map from displayed indices |
| -----: | ------------------------------------- | -------------------------- |
|      1 | Whole grid                            | $x=i,\ y=j$                |
|      2 | Same-parity checkerboard sampling     | $x=i+j,\ y=i-j$            |
|      3 | Opposite-parity checkerboard sampling | $x=i+j+1,\ y=i-j$          |
|      4 | Even/even                             | $x=2i,\ y=2j$              |
|      5 | Even/odd                              | $x=2i,\ y=2j+1$            |
|      6 | Odd/even                              | $x=2i+1,\ y=2j$            |
|      7 | Odd/odd                               | $x=2i+1,\ y=2j+1$          |

For a general sample map $t\mapsto Bt+e$, displayed translations are tested by applying $B$ to them. It is sufficient to evaluate the sampled table on the displayed $K\times K$ torus for integer pre-polynomials. All seven methods retain opposite-parity **operand forms** $a,b$; the original-grid parities named in the table are not the parities of $a,b$.

### 4.2 Checkerboard separates branches with different intrinsic periods

Under method 2 the operand forms are $a=-2j-1$, $b=2i$. Method 3 instead has $a=-2j-2$, $b=2i+1$. Thus checkerboard sampling isolates an odd-input pre-function on one displayed axis and an even-input pre-function on the other.

For $P(x)=x^q$, even $q$, and $w=\nu_2(q)$, let $L_q(h)$ be the least additive period of $x^q\bmod2^h$, taking $L_q(h)=1$ for $h\le0$. Its explicit formula is

$$
L_q(h)=\begin{cases}2,&0<h\le\min(q,w+2),\\2^{\max(2,h-w)},&h>\min(q,w+2).\end{cases}
$$

The displayed periods of the separate branches are

$$
E=L_q(k-q),\qquad O=\begin{cases}1,&k\le w+2,\\2^{k-w-1},&k>w+2.\end{cases}
$$

The even branch is $2^q i^q\bmod K$, proving the first formula. For the odd branch, a shift of one in its displayed index changes odd inputs by two, with minimum difference depth $w+2$. Displayed shifts $2^h$, $h\ge1$, change them by $2^{h+1}$, with minimum depth $w+h+1$. This proves the second formula. The shared family in Section 3 retains these same branch periods.

For OR, XOR, ADD, and ABSDIFF the basic checkerboard periods are exactly $(E,O)$ in method 2, and $(O,E)$ in method 3. The slices with even pre-input zero recover the odd branch. The odd pre-input one recovers the even branch injectively: OR and XOR give $1+E_i$, ADD gives the same, and $|1-E_i|$ is injective on even-branch values, which are zero or multiples of $2^q\ge4$.

For MULT and CLMUL, the same result holds once the even branch is nonzero, using multiplication by a fixed nonzero operand. If it is zero, both tables are constant. AND requires its own mask calculation. In the normal range where both branch formulas take their growing forms, $O/E=2^{q-1}$. It is therefore incorrect to reuse the no-pre-operation XOR square-period rule for these checkerboard styles.

### 4.3 A complete small comparison

At $K=64$, the following periods are measured before post-processing. All four parity selections 4–7 have the same axis-period pair in these examples; their actual tables and centers need not coincide.

| Pre-power and basic combiner  | Whole grid | Same-parity checkerboard | Opposite-parity checkerboard | Each of methods 4–7 |
| ----------------------------- | ---------- | ------------------------ | ---------------------------- | ------------------- |
| 2; any of the seven combiners | (32, 32)   | (8, 16)                  | (16, 8)                      | (16, 16)            |
| 4; AND                        | (8, 8)     | (2, 4)                   | (4, 2)                       | (4, 4)              |
| 4; each other combiner        | (16, 16)   | (2, 8)                   | (8, 2)                       | (8, 8)              |
| 6; AND, MULT, CLMUL           | (1, 1)     | (1, 1)                   | (1, 1)                       | (1, 1)              |
| 6; OR, XOR, ADD, ABSDIFF      | (32, 32)   | (1, 16)                  | (16, 1)                      | (16, 16)            |

This makes identity sampling a meaningful option. Checkerboard sampling can expose a constant direction rather than remove a collection of isolated dead cells. A one-variable diagonal texture can still have nontrivial periods on both displayed axes under methods 4–7; its additional oblique translations must be recorded too.

### 4.4 Symmetry must preserve the selected phase

For the full grid, set $X=x+1/2$, $Y=y-1/2$. The operand forms are $a=Y-X$, $b=Y+X$. A square symmetry permutes these forms and changes their signs. If $P(-t)\equiv P(t)\pmod K$, every symmetric basic combiner, tuple, and subsequent post-expression has the full square symmetry about $(-1/2,1/2)$.

Sampling can exchange phases under that symmetry. For example, reflection $x\mapsto-1-x$ switches the two checkerboard cosets. A quarter-turn about the same center sends $(x,y)$ to $(-y,x+1)$, also switching those cosets. Thus functionally even pre-operations do not alone give full square symmetry on each fixed checkerboard phase. The four parity selections likewise require phase tests. Arithmetic identities can supply extra symmetries, but they must be checked at the fixed origin.

Odd pre-powers are lower priority because of the stated aesthetic preference. There is no theorem here that they are all asymmetric or unattractive. The identity-pre XOR family is already an exception to any such blanket symmetry claim, as explained in the earlier research.

### 4.5 Where variation is erased

For even $q$, odd pre-inputs satisfy $x^q\equiv1\pmod{2^{w+2}}$, while even pre-inputs are divisible by $2^q$. OR, XOR, and ADD therefore produce odd basic values with low bits $1\pmod{2^{\min(k,q,w+2)}}$. ABSDIFF is odd but can have either sign of that congruence. AND, MULT, and CLMUL are even; MULT and CLMUL have valuation equal to the even operand's valuation when nonzero.

For pure powers, if $q\ge k$, the even pre-operand is zero everywhere. AND, MULT, and CLMUL then vanish. OR, XOR, ADD, and ABSDIFF coincide with the odd pre-operand. No sampling among the seven rules restores the lost two-operand interaction. This extends the earlier AND/OR/XOR observation to all seven combiners.

After a post-power $p$, a basic value $z$ vanishes modulo $2^m$ exactly when $p\nu_2(z)\ge m$, including zero by the infinite-depth convention. Odd $z$ does not vanish, although different odd values can still merge. For each proposed style, count these cells on its actual sampled torus, and separately test equality of powered values. Increasing the post-modulus can prevent the annihilation, so large powers alone are not a justification for discarding a parity class.

The script records exact zero fractions and period pairs for all seven sampling methods, all seven combiners, $K=16,32,64,128$, and pre-powers 2, 4, 6, 8, 10. These are numerical diagnostics. No claim about perceived attractiveness is inferred from zero fractions alone.

## 5. Finite parameter spaces and uniform shift-class sampling

### 5.1 Pre-functions at a fixed pre-modulus

At a fixed $K=2^k\ge8$, pure positive pre-powers have a complete finite representative range

$$
q=1,2,\ldots,k+2^{k-2}-1.
$$

Keep $q<k$ unchanged; for $q\ge k$, reduce into the tail starting at $k$ with cycle $2^{k-2}$. Even inputs have vanished in the tail and the odd-unit exponent cycle is exact. This is the [existing fixed-modulus theorem](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md), Section 8.2, now with pre-modulus $K$ instead of original domain $C$.

All integer pre-polynomial functions modulo $K$ also have finite coordinates. With $(x)_j=x(x-1)\cdots(x-j+1)$, retain indices with $\nu_2(j!)<k$ and use coefficients

$$
0\le a_j<2^{k-\nu_2(j!)}.
$$

These falling-factorial coordinates represent each function exactly once. Evaluating successively at $x=0,1,\ldots$ proves uniqueness, while divisibility of $(x)_j$ by $j!$ proves the coefficient reductions. Functional evenness and requested basic-combiner periods are subsequent admissibility conditions. Uniformly choosing these coefficients samples pre-functions, not necessarily resulting numerical patterns uniformly.

A fixed-$K$ classification does not classify all pre-powers at their individually selected minimum moduli. For example, the MULT/CLMUL minimum in Section 3 grows with $q$ even if $\nu_2(q)$ stays fixed. One cannot impose one finite pre-power list across changing $K$ without a separate proof.

### 5.2 All post-powers at a fixed final modulus

Fix the selected basic table, sampling, and $M=2^m$. Let $t$ be the smallest valuation among its nonzero even input values. Set $L=\max(1,\lceil m/t\rceil)$, or $L=1$ if there are no such values. Let $T$ be the least common multiple of the multiplicative orders modulo $M$ of its odd input values, taking $T=1$ if there are none.

Then positive post-powers have the complete range $1\le p<L+T$. Below $L$ an even input distinguishes the successive powers by its valuation. At and above $L$ all even inputs vanish and odd inputs repeat with cycle $T$. This applies to the full outputs of ADD, MULT, CLMUL, and ABSDIFF as well as bitwise combiners.

An exact finite sampler enumerates that range and odd multipliers modulo $M$, filters by the target period and optionally minimum-period precision, and stores each anchored shift signature once. Remove unused low bits to compare normalized signatures across moduli. Uniform catalogue indexing is uniform over the distinct classes. Enumerating raw descriptions without deduplication is generally biased.

For order classes, replace the numerical signature by the vector of ranks of the anchored values. Choose one canonical representative per signature and sample those signatures uniformly. Projecting a uniform shift-class catalogue onto order classes is uniform only if every order class has the same number of shift classes.

This is complete at fixed precision. It is not a proof of a finite post-power range when $M$ is selected separately for each unbounded $p$.

### 5.3 Polynomial post-operations at a fixed final modulus

At fixed $K,M$, evaluate the permitted polynomial monomials on the distinct reachable basic inputs or tuples, subtracting the fixed reference value. Their image is a finite additive group. Modular row and column elimination yields independent cyclic generators of orders $2^{e_j}$; independent coefficients $0\le a_j<2^{e_j}$ enumerate anchored shift classes exactly once. The earlier [XOR polynomial implementation](../2026-11-02-xor-polynomial-period/xor_polynomial_period.py) supplies such elimination and retains the polynomial column transformations.

A finite spanning list for unrestricted scalar polynomials follows by dividing by the monic polynomial $\prod_i(z-z_i)$ to reduce to degree below $n$, where $z_1,\ldots,z_n$ are the actual input values. For even-only polynomials, perform that reduction in the feature $z^2$; the same-valuation list is supplied by the earlier XOR report. For several unrestricted polynomial features, their finitely many coordinate values give a separate monic reduction in each variable. These are general bounds; valuation-based Newton lists can be much shorter.

First impose the two requested full-period translations as homogeneous linear constraints, obtaining a subgroup $V$. Let $V_x,V_y$ be its subgroups invariant under the two half-periods. The exact number of valid shift classes is

$$
|V|-|V_x|-|V_y|+|V_x\cap V_y|.
$$

All four sizes are finite-module image or kernel calculations. Uniform cyclic coordinates in $V$, rejecting the two half-period subgroups, give uniform valid shift classes. If valid classes exist and both targets exceed one, acceptance is at least one quarter: each excluded proper subgroup has index at least two, and two distinct index-two subgroups have intersection of index four. Identical subgroups give acceptance at least one half.

If minimum-period precision is also imposed, retain only tables satisfying Section 2.2. This is another Boolean combination of kernels, since “all differences are zero or $M/2$” is equivalent to $2D=0\pmod M$ for that difference map. Exact counting remains possible by subgroup intersections and inclusion–exclusion, but the one-quarter acceptance bound does not apply to this additional filter.

### 5.4 An unbounded-power theorem for odd-valued basic tables

The precision cap can be removed for an important class: **every reachable basic value is odd**. This includes pure even pre-powers, and the shared family of Section 3, with OR, XOR, ADD, and ABSDIFF, under all seven sampling rules. Fix their selected pre-modulus and target periods.

For odd post-powers, every shift depth is independent of the power: $\nu_2(a^p-b^p)=\nu_2(a-b)$ for odd $a,b,p$. Thus either all odd powers are inadmissible or all use one minimum exponent $m_0$. Their tables are covered by the finite odd exponent cycle modulo $2^{m_0}$.

For even post-powers $p=2^v u$, $v\ge1$, $u$ odd, every finite shift depth is $v$ plus the corresponding minimum of

$$
\nu_2(a-b)+\nu_2(a+b)-1.
$$

Consequently either all even powers are inadmissible, or their minimum valid exponent has the form $m=v+e$ for one fixed integer $e$, independent of $u,v$. It can be found by testing $p=2$ and subtracting one from its minimum exponent. The upper full-period constraints shift by $v$ too, so admissibility is independent of $u,v$.

**Finite-tail theorem.** For each fixed odd $u$, the normalized anchored pattern is identical for all

$$
\boxed{v\ge V=\max(1,e-3).}
$$

**Proof.** Anchor at odd basic input $z_0$. Define the integer

$$
T_{v,u}(z)=\frac{z^{2^v u}-z_0^{2^v u}}{2^v}.
$$

The normalized anchored pattern is $T_{v,u}(z)/2^e$ modulo one. Every $T_{v,u}$ is divisible by four. Writing $A=z^{2^v u}$ and $B=z_0^{2^v u}$ gives

$$
T_{v+1,u}=T_{v,u}\frac{A+B}{2}.
$$

Since $A,B\equiv1\pmod{2^{v+2}}$, the factor $(A+B)/2$ is $1\pmod{2^{v+1}}$. The difference $T_{v+1,u}-T_{v,u}$ is therefore divisible by $2^{v+3}$. It vanishes modulo $2^e$ whenever $v\ge e-3$, proving exact stabilization, uniformly over all reachable odd inputs and odd $u$. This proof does not assume a complete value grid. It is a sufficient pointwise bound; the special XOR classification can identify equivalent families earlier by changing representatives.

A complete parameter catalogue now uses the admissible odd-power cycle, plus $1\le v\le V$. For each even row, odd $u$ modulo $2^{\max(e-2,0)}$ covers every raw power table at its modulus: the exponent of the odd-unit group modulo $2^{v+e}$ divides $2^{v+e-2}$. Use $u=1$ if that cycle has size one. Enumerate effective odd multipliers, canonicalize anchored signatures, and deduplicate. Uniform indexing gives uniform shift classes, or uniform order classes after the separate rank quotient. No user-chosen precision cap is required.

This supplies a complete finite classification procedure for those four even-pre combiner families at fixed $K$, even when their value sets do not fill a grid and order classes can merge shift classes. Its catalogue can still be large; a compact closed count for every pre-function and sample phase is not asserted. Basic tables containing zero or even values require another argument and can have infinite shift families, as AND demonstrates below.

As a complete small example, squared pre-operation with target periods 16 selects $K=32$ on the full grid. Allowing every positive post-power and every odd multiplier, always at minimum-period precision, gives:

| Basic combiner | Shift classes | Order classes |
| -------------- | ------------: | ------------: |
| OR             |             8 |             8 |
| XOR            |             8 |             8 |
| ADD            |             8 |             8 |
| ABSDIFF        |             5 |             5 |

These are full unbounded-power counts for these particular tables, not counts under a sampled power cutoff. The equality of the two columns is an outcome of these examples, not an extra assumption of the general odd-valued theorem.

## 6. No-pre-operation XOR: when order and shift classes coincide

### 6.1 A simple sufficient condition

Anchor at the same reachable reference cell. Say a numerical pattern **fills its value grid** if its distinct normalized values are exactly

$$
0,1/Q,2/Q,\ldots,(Q-1)/Q
$$

for some $Q$. Within any collection of patterns that fill their value grids, order equivalence is exactly shift equivalence. The number of groups determines $Q$, and the rank of a group determines its value $j/Q$. Thus an order signature recovers the complete anchored numerical pattern, even when the raw moduli differ.

This condition concerns the set of distinct values, not how often cells attain each value.

### 6.2 Single powers, odd multipliers, and offsets

Use the established XOR baseline: operands reduced modulo $C$, full historical grid or its established checkerboard sampling, $p=2^v u$ with odd $u$, $M=C2^v$, and target $R=C/2$. Every odd raw input $1\le z<C$ is reached. Anchor at $z=1$.

For odd $p$, exponentiation permutes all odd residues modulo $C$. Subtracting one and dividing by two therefore fills the grid with $Q=C/2$. Odd multiplication permutes this same grid.

For even $p$, every $z^p$ is $1\pmod{2^{v+2}}$. There are exactly $C/4$ distinct values modulo $M$. Indeed, the lifting formula gives equality for odd $z,z'$ in the input range exactly when $z'\equiv z$ or $-z\pmod C$. These are pairs of distinct inputs. The resulting image therefore fills the entire congruence class $1\pmod{2^{v+2}}$, whose size is $Q=C/4$. Anchoring again fills its value grid, and odd multipliers preserve that fact.

**Conclusion.** Order classes and shift classes coincide for the complete balanced single-power-and-odd-multiplier space, across both parities and all valuations, including the tail. The old family identifications, compact ranges, counts, and uniform shift-class samplers remain valid for order classes. In particular, order sampling uses the same odd/even weighting $8/9$ versus $1/9$ when both are allowed. It does not use the affine-family weighting $4/5$ versus $1/5$.

| Field dimensions in cells    |     C | Odd order classes | Even order classes |   Total |
| ---------------------------- | ----: | ----------------: | -----------------: | ------: |
| 512 × 256                    | 1,024 |            32,768 |              4,096 |  36,864 |
| 1,024 × 512                  | 2,048 |           131,072 |             16,384 | 147,456 |
| 2,048 × 512 or 2,048 × 1,024 | 4,096 |           524,288 |             65,536 | 589,824 |

These counts assume the same fresh/adapted field-to-domain convention as the [earlier explanation](../2026-10-25-pattern-space/2026-11-01-xor-post-operations-explained.md), Section 16. Preserved references, crops, and stretching follow their stored coordinate domain.

The old master-parameter qualifications also remain: reducing an affine-family power can require compensating its multiplier to preserve an individual class. Equality of sampling distributions is weaker than equality for one stored master draw. Replacing “shift class” by “order class” does not remove that issue.

### 6.3 Valid same-valuation polynomial sums

Fix $v$ and the same $M=C2^v$. The [November 2 space](../2026-11-02-xor-polynomial-period/2026-11-02-xor-polynomial-period.md) consists of

$$
H(z)=b+\sum_{u\text{ positive and odd}}a_u z^{2^v u}.
$$

The earlier period theorem requires $\sum a_u$ odd. Put $w=z^{2^v}$ and $J(w)=\sum a_u w^u$. For odd $w,w'$, each difference quotient $(w^u-w'^u)/(w-w')$ is odd, since it contains an odd number of odd summands. Therefore

$$
\frac{J(w)-J(w')}{w-w'}\equiv\sum_u a_u\equiv1\pmod2.
$$

So $J$ preserves every difference valuation. For $v=0$ its input is the complete odd congruence class modulo $C$; for $v>0$ it is the complete class $1\pmod{2^{v+2}}$ just proved above. Its image has the same size and lies in one congruence class of that size. Consequently every valid same-valuation polynomial fills its value grid, with $Q=C/2$ or $C/4$ respectively.

**Conclusion.** The previous independent polynomial coordinates, period bit, counts, and rejection-free uniform sampler also enumerate order classes without duplication. Their binary controls retain their numerical additive interpretation because they select unique numerical representatives; this does not give a general additive operation on arbitrary order classes.

Each table entry below is the number of independent valid bits $D$, meaning exactly $2^D$ shift classes **and** order classes at that fixed valuation:

|     C | v = 0 | v = 1 | v = 2 | v = 3 | v = 4 |
| ----: | ----: | ----: | ----: | ----: | ----: |
| 1,024 |    18 |    11 |    10 |     9 |     8 |
| 2,048 |    22 |    13 |    12 |    11 |    10 |
| 4,096 |    26 |    16 |    14 |    13 |    12 |

These are conditional counts, not a disjoint sum across valuations. The equivalence also holds when comparing valid members across valuations, since all positive-valuation members fill grids of the same size, but a combined count still requires deduplicating their numerical spaces. Existing theorems did not supply that joint count.

### 6.4 Arbitrary and even-only post-polynomials can behave differently

The preceding proof uses the same-valuation coefficient-parity condition. It does not extend to every arbitrary polynomial that happens to retain the period.

For a small explicit example, take $C=8$, $M=32$, target periods four, and odd inputs $1,3,5,7$. Write $B_1=z-1$, $B_2=(z-1)(z-3)$, $B_3=(z-1)(z-3)(z-5)$. The two anchored polynomials

$$
H_1=2B_1+B_2+B_3,\qquad H_2=4B_1
$$

have respective residue tables

$$
(0,4,16,20),\qquad(0,8,16,24).
$$

Their ordering is identical, but their normalized spacings differ, so they are distinct shift classes in one order class. Both half-input pairs differ by 16, proving that both expressions use their minimum valid modulus 32. The collision is therefore not an artifact of excess precision.

Even-only polynomials can also merge. At $C=8$, $M=1024$, the polynomials $z^4+18z^6$ and $3z^4+22z^6$, anchored at one, give

$$
(0,896,256,384),\qquad(0,896,512,640).
$$

They have the same ascending order of cell groups, different shift signatures, and the same exact periods four. The second half-input difference is 512 in both, so this modulus is minimal. Thus the old arbitrary-polynomial shift counts and coefficient sampler cannot generally be reused as uniform order counts and sampling weights. Section 7 supplies a complete alternative in principle.

## 7. Unbounded post-polynomials: a finite theoretical classification of orders

This section fixes the pre-function, chosen $K$, sampling, and basic input table. It allows arbitrary integer post-polynomials and arbitrarily large $M$. It also covers even-only polynomials of a scalar nonnegative input. The bounds are existence and termination guarantees, not practical estimates of catalogue size.

### 7.1 Interpolation with a power-of-two divisibility allowance

Let the distinct scalar basic inputs be $z_1,\ldots,z_n$. Put

$$
D_i=\prod_{j\ne i}(z_i-z_j),\qquad d=\max_i\nu_2(D_i).
$$

For $n=1$ use $D_1=1$. For any $m>d$, every residue assignment divisible by $2^d$ is realizable by an integer polynomial modulo $2^m$.

**Proof.** Write $D_i=2^{d_i}u_i$ with odd $u_i$, and choose an integer inverse $u_i^{-1}$ modulo $2^m$. The integer polynomial

$$
E_i(z)=2^{d-d_i}u_i^{-1}\prod_{j\ne i}(z-z_j)
$$

is zero at the other nodes and equals $2^d$ at node $i$ modulo $2^m$. A linear combination of the $E_i$ realizes the prescribed multiples. No division by an even integer is performed in the coefficient ring.

For even-only polynomials, apply the same construction to the distinct nodes $z_i^2$ and substitute $z^2$ afterward. Distinctness holds because the basic inputs are nonnegative. Its value of $d$ can be larger, but its attainable unbounded-precision order classes are the same. This statement is about a union over moduli; it does not identify the two spaces at a fixed modulus.

For a tuple of basic inputs, encode its finite distinct tuples injectively by an integer linear form. For example, a mixed-radix encoding with a base larger than every coordinate value works. Apply the scalar construction to that encoding. Its polynomials remain integer polynomials in the original symmetric features.

### 7.2 Without the minimum-precision restriction

If any period-preserving precision is allowed, the attainable order classes are exactly the ordered partitions of the input groups that retain the target periods. Full-period translations impose the identifications in Section 2.3; no post-polynomial can separate those components. Conversely, give the desired ordered blocks successive dyadic labels starting at zero, then apply interpolation at a sufficiently large modulus.

Before period filtering, the number of anchored order signatures on $n$ input groups is

$$
\sum_{s=1}^n (s-1)!\,{n\brace s},
$$

where ${n\brace s}$ counts partitions into $s$ nonempty blocks. The block containing the reference input is first; the other blocks can be ordered in $(s-1)!$ ways. Period filtering depends on the actual cell incidences, not just $n$.

This proves that sufficiently flexible post-polynomials can realize every allowed ordering of the basic equality groups. It is also a reason to retain simpler polynomial subfamilies as aesthetic choices: the unrestricted family is ultimately a very general relabeling mechanism.

### 7.3 Minimum-period precision adds an antipodal condition

For one proposed ordered partition, examine the half-period edges between its output groups. By Section 2.2, a realization at minimum-period precision must permit at least one axis's nontrivial edges to connect values separated by exactly one half of the circle. Edges inside one group contribute zero. Each group can have at most one distinct antipodal partner. If two distinct groups would both have to be antipodal to the same group, the ordered partition is impossible under this policy.

The remaining ordering condition is concrete. Assign labels $0=t_0<t_1<\cdots<t_{s-1}<1$ in the prescribed group order, and require $|t_i-t_j|=1/2$ on each nontrivial edge of the selected axis. Both axes must still have some nontrivial edge. This is a finite feasibility test; one can enumerate whether each label lies below or above one half and solve the resulting strict linear ordering constraints. An equivalent finite grid procedure follows next.

This restriction explains why “all ordered partitions” is too broad for the minimum-period catalogue, even though it is correct when excess precision is allowed.

### 7.4 A proved finite search bound, including canonical minima

**Theorem.** Let $n$ be the number of distinct basic input groups, and let $d$ be the interpolation allowance above, using squared nodes for even-only polynomials. Every attainable order class at minimum-period precision has a representative with

$$
\boxed{m\le d+1+\lceil\log_2(n+1)\rceil.}
$$

Consequently a search through that finite precision range is sufficient to find every such order class and its minimum-modulus representative. There is no conjectural stopping rule based on observing an apparently stable catalogue.

**Proof.** Start with any admissible realization, with $s\le n$ distinct anchored values. At least one half-period map changes values only by zero or one half. Complete the value set under addition by one half. Its distinct fractional positions in the lower half number at most $s+1$, including zero. Replace them, in their original order, by $j/(2L)$, where $L=2^{\lceil\log_2(s+1)\rceil}$ and $j$ begins at zero. Give their upper-half partners the same new value plus one half.

This transformation preserves every equality, every ascending order, and the designated antipodal differences. It therefore preserves the requested full periods and the failure of both half-periods. The transformed table has a dyadic denominator $2^b$ with $b=1+\lceil\log_2(s+1)\rceil$. Interpolation realizes its integer labels scaled by $2^d$ modulo $2^{d+b}$. The designated half-period differences are zero or $2^{d+b-1}$, with some nonzero, so that modulus is minimal for the resulting polynomial. Since $s\le n$, the displayed bound follows.

A complete canonical algorithm now has two equivalent forms. Enumerate ordered partitions, test period and antipodal feasibility, and then search for each one's smallest modulus up to the bound; or enumerate the finite polynomial-function images at each precision through the bound, retain exact-period tables at minimum-period precision, and deduplicate order signatures. The first occurrence gives the minimum modulus. Break remaining ties lexicographically in fixed independent polynomial coordinates. Uniformly index the resulting signatures.

The interpolation degree bound is below $n$ for ordinary scalar polynomials and below $2n$ for even-only polynomials. These are finite guarantees. The ordered-partition count can grow extremely quickly, and neither algorithm is claimed to run interactively on a large arbitrary rug style.

### 7.5 Exactly when the unrestricted polynomial shift space is finite

Under the same fixed-basic-table and minimum-period policy, the full shift-class set is infinite **if and only if** an attainable pattern has at least three distinct output groups.

**Proof.** With only two groups, minimum-period precision forces their normalized values to be zero and one half. There are finitely many ways to partition finitely many input groups into those two groups, so shift and order classification coincide on this set.

If at least three groups occur, choose an axis satisfying the antipodal condition. Its nontrivial edges form disjoint pairs of groups. The anchored zero group and its antipode can fix at most two values. Some other group's value is free to move, together with its antipodal partner if needed, inside a nonempty ordering interval. Infinitely many dyadic movements preserve the ordered partition, the designated antipodal relations, and both exact periods. Interpolation realizes all of them, still at minimum-period precision. Their distinct spacings are distinct shift classes.

This is a complete theoretical finiteness criterion for the unrestricted polynomial families considered here. It is not a finiteness criterion for the much more constrained single-post-power family. The balanced XOR monomial and same-valuation spaces illustrate that distinction.

## 8. Squared-pre AND at its actual minimum pre-modulus

Use full-grid sampling and target $R=32$, corresponding to the historical domain label $C=64$. At every $K<64$ the squared pre-function already has axis periods below 32. At $K=64$, basic AND has exactly periods 32 and raw values

$$
0,16,32.
$$

Thus the corrected basic-combiner pre-modulus rule selects **K = 64**, just as in the earlier infinite example. Its obstruction survives the clarification.

A half-period shift can exchange the zero and thirty-two groups while leaving the sixteen group fixed. For every positive post-power $p$, the minimum final modulus is $M_p=2^{5p+1}$. The normalized anchored values are

$$
0,\quad2^{-(p+1)},\quad1/2.
$$

Odd multipliers give exactly two order classes: the sixteen group lies below or above the thirty-two group. They never merge these groups. Both orders already have representatives at $p=1$, $M=64$, using multipliers one and three. There remain infinitely many shift classes because the spacings vary with $p$.

Allowing arbitrary polynomial post-operations gives exactly four valid order classes. Two preserve all three groups as above. The other two merge the sixteen group with either the zero or the thirty-two group. Merging the zero and thirty-two groups would lose the target period and is forbidden. Explicit representatives of the new two-group orders are

$$
H_1(z)=z(z-16),\qquad H_2(z)=z(z-48),\qquad M=1024.
$$

Their anchored outputs on $(0,16,32)$ are $(0,0,512)$ and $(0,512,512)$. In each, the half-period change is 512, so the modulus is minimal. Even-only representatives also exist: $z^2(z^2-256)$ and $z^2(z^2-1280)$ modulo $2^{19}$ give the same two orders.

The two three-group orders have minimum modulus 64 among all integer post-polynomials. The two merging orders have minimum modulus 1024. To prove the latter lower bound, subtract the constant term of any integer polynomial and observe that $H(32)-2H(16)$ is divisible by 512: the linear term cancels and every higher term has that divisibility. If either $H(16)=0$ or $H(16)=H(32)$ modulo a modulus at most 512, then $H(32)=0$ too, losing the period. The displayed witnesses attain 1024.

For even-only polynomials, the corresponding minimum moduli are $2^{11}$ for the three-group orders and $2^{19}$ for the merging orders. Substitute $s=z^2$. Every anchored $J$ satisfies $J(1024)-4J(256)\equiv0\pmod{2^{18}}$; the same argument gives the merging lower bound, and the displayed even-only witnesses attain it. This is a concrete example where ordinary and even-only polynomials have the same attainable order classes but different canonical minimum moduli.

## 9. Exact verification and implementation implications

Run the standard-library checker from the repository root:

```sh
python3 research/theory/2026-11-03-combiners-and-order-classes/combiners_order_classes.py
```

It regenerates [results.json](results.json). The accompanying run completed **39,928 exact assertions**. The checks compare pre-period formulas with literal sequences, common family minima with literal grids, difference depths with integer powers, predicted minimum post-moduli with independently scanned axis periods, XOR saturation with complete small-space enumeration, interpolation with direct evaluation, and antipodal compression with explicit finite labels. They also compare the complete odd-valued power catalogues with an independent enumeration through post-power 128. A complete polynomial-image search through the proved bounds recovers all four AND order classes and their canonical minimum moduli. The report's general results rest on the proofs; finite checks validate the implementation and examples within their stated ranges.

The numerical catalogue covers all seven basic combiners and sampling rules at $K=16,32,64,128$, pre-powers 2, 4, 6, 8, 10, and post-powers 1–4. It also records the first pre-modulus found for targets 16 and 32 when one is found through 128, with polynomial target feasibility and post-power feasibility at that modulus. An absent entry means “not found through 128,” not a general impossibility claim. Since displayed periods divide $K$, no smaller $K$ below a given target can have been missed for those found minima.

For the generator, the proved workflow is:

1. Define the pre-family, basic feature tuple, coordinate map, sample phase, and target periods. Use a family theorem such as Section 3 where available; otherwise certify the chosen pre-modulus on the basic table.
1. Keep that pre-modulus fixed. Reject post-operations failing the exact final-period test. Use Section 2.3 to rule out an impossible polynomial target before searching coefficients.
1. For balanced XOR monomials or valid same-valuation sums, retain the existing compact coordinates and samplers for either shift or order classes.
1. For other fixed-precision polynomial styles, use independent image coordinates and exact period constraints. Use numerical signatures for shift classes and anchored rank signatures for order classes.
1. For unbounded polynomial precision, use the proved order bound as a complete fallback. Use a more structured subfamily or precomputed catalogue when the general search is too large.
1. Record exact symmetries, zero fractions, and oblique translations for the chosen sample phase. Apply the palette afterward; numerical counts are single-channel counts before color conversion.

Several broad questions remain. This report does not give a complete unbounded-post-power classification for every basic table containing zero or even values, or a scalable uniform order sampler for every unrestricted polynomial style at production sizes. It does not classify the union of all individually minimum-pre-modulus pre-functions, deduplicate every overlap across combiners and pre-families, or optimize visual spread. Those tasks require additional structure beyond the general finite procedures proved here. The shared pre-polynomial family now has common-modulus guarantees for all seven combiners; the odd-valued post-power theorem settles its stated subproblem, and the remaining cases must not be inferred from it.

## Relationship to existing research

- [Research goal and decisions](research-goal.md): the current four-stage contract, sampling scope, priorities, and canonical preference.
- [October 13 XOR theory](../2026-10-13-post-power/2026-10-13-xor-post-power-theory.md): odd-input lifting and balanced XOR period results.
- [October 25 pattern-space theory](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md), Sections 5–10: fixed-precision exponent ranges, difference depths, sampling lattices, pre-power periods, polynomial-function normal forms, and the original infinite AND example.
- [November 1 XOR explanation](../2026-10-25-pattern-space/2026-11-01-xor-post-operations-explained.md): shift-class samplers, practical size conversions, and master-parameter qualifications.
- [November 2 XOR polynomial report](../2026-11-02-xor-polynomial-period/2026-11-02-xor-polynomial-period.md): the same-valuation period character, cyclic coordinates, polynomial counts, and arbitrary-polynomial period tests used in the order comparison.
