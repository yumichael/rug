# Precision policy and the gallery observations

This note distinguishes mathematical modulus policies and records the bounded gallery comparisons obtained in the chat. The workbench snapshot now exposes `catalogue`, `distinct_outputs`, and `minimum_period` selections. The original observations were made before those choices were separated in the UI. All numerical comparisons below name their policy explicitly; they do not prescribe future generator behavior.

## 1. Value preservation versus minimum-period precision

Fix $K$, the sampling, the pre-function, and the integer post-polynomial. Let $U(t)$ be the resulting integer output on a complete periodic torus. A distinction-preserving modulus keeps distinct integer $U$ values distinct after reduction. The original OR study additionally adjoined zero when choosing its modulus, keeping every nonzero output separate from zero. Its catalogue polynomials are strictly increasing on nonnegative combined inputs, so preserving their outputs also preserves all combined-input groups.

A minimum-period modulus only requires the requested least horizontal and vertical periods. It permits groups to merge and permits nonzero integer outputs to become zero when those changes leave the target periods intact.

**Upper-bound result.** A distinction-preserving modulus is an upper bound on the minimum modulus attaining the target, whenever the target is attainable for the fixed construction. Above that modulus, the equality partition has already stabilized to the integer $U$ partition. If the target occurs there or at a larger modulus, it already occurs at that modulus; if it occurs only after mergers, it occurs at a smaller modulus. This statement assumes the supplied table is a complete torus or complete reachable value set, rather than a crop.

Consequently a value-preserving catalogue can overestimate the precision needed for repetition. It inherits the integer output's symmetries and periods. A pattern with insufficient integer period cannot acquire a larger period through reduction.

## 2. Concrete OR differences

Use $N = 8$, pre-power two, no twist, and post-cube $H(z) = z^3$:

| Sampling              | Catalogue M | Minimum-period M | Least periods at the minimum |
| --------------------- | ----------: | ---------------: | ---------------------------- |
| Full                  |         128 |               16 | (8,8)                        |
| Checkerboard-same     |         128 |               16 | (8,8)                        |
| Checkerboard-opposite |          16 |               16 | (8,8)                        |

In the full field, combined inputs zero and four give cubes zero and 64. They merge modulo 16 while the target periods survive. There are six groups before reduction and five at the minimum.

For opposite-checkerboard sampling with the same pre-operation, choose $H(z) = 3z+z^4$. The catalogue chooses $M = 256$, while the minimum-period modulus is 16. At 16 all four combined groups remain distinct, but $H(5) = 640$ becomes zero. Thus zero preservation alone can impose extra precision, separately from preserving distinctions between reachable values.

The current odd/odd study family and its ten post-polynomials have matching catalogue and minimum-period moduli, as proved in [the pre-power report](pre-power-families.md). The same holds inside its opposite-checkerboard erased-even-branch tail. The overshoot examples do not invalidate those tail results.

## 3. XOR gallery precision

The single-power and valid same-valuation sum strata use balanced minimum-period moduli for the reference opposite checkerboard. The broader even-only and unrestricted strata select a precision and test the target period there. That acceptance test does not establish that the selected modulus is minimum.

At $N = 1024$, seed zero, and 24 draws per stratum, exact checks give:

| Stratum    | Precision parameter v in M = 2N·2^v | Excess-precision draws | Rank changes on reduction |
| ---------- | ----------------------------------: | ---------------------: | ------------------------: |
| Even only  |                                   1 |                      0 |                         0 |
| Even only  |                                   2 |                     16 |                        16 |
| Even only  |                                   4 |                     23 |                        23 |
| Any powers |                                   0 |                      0 |                         0 |
| Any powers |                                   1 |                     19 |                        19 |
| Any powers |                                   2 |                     21 |                        21 |
| Any powers |                                   4 |                     24 |                        24 |

The other eight strata each have zero excess-precision draws. Overall 103 of the 360 draws change their anchored rank arrays when reduced to their minimum-period modulus.

The even-only strata initially have 24,8,1 complement-symmetric draws at $v = 1,2,4$. Every one of the 39 failures gains that symmetry after reduction, leaving all 72 even-only draws symmetric. This is explained by the general bound $M_{\min}\le 2N^2$ in [the XOR symmetry report](xor-symmetry.md), not only by the finite observations.

These counts concern the reference opposite-checkerboard XOR sampling. A polynomial drawn for that reference may have different minimum periods or insufficient precision under another sampler or combiner; those constructions require their own period test. The [results](results.json) record the precise counts and source hashes used in the rerun.

## 4. All three selectors agree in the opposite-checkerboard tail

**Theorem for the current post family.** Fix $N = 2^r \ge 8$, an even pre-power $q = 2^w u$ in the erased-even-branch tail $q \ge r+w$, any integer pre-twist $Q$ in the shared family, and any of OR, XOR, ADD, or ABSDIFF. Use the opposite checkerboard, $K = N\cdot 2^w$, and a post $H$ from [the ten-polynomial catalogue family](pre-power-families.md#6-the-catalogue-post-family). Then

$$
\boxed{M_{\mathrm{catalogue}}=M_{\mathrm{distinct\ outputs}}=M_{\mathrm{minimum\ period}}=K\,2^d,\qquad d=\nu_2(H'(1)).}
$$

This is selector agreement for each fixed recipe. The common $M$ can change with $q$ through $K$ and with $H$ through $d$; equal tail geometry does not mean a constant numerical modulus across different recipes.

**Proof.** The even branch is zero, so all four combiners return the odd pre-value. These values fill precisely

$$
\{1+Sa:0\le a<T\},\qquad S=2^{w+2},\quad T=N/4,\quad K=ST.
$$

The post family has $d \le 1$, so its difference quotient on this class has valuation exactly $d$. At $M_0 = K\cdot 2^d$ it preserves all $T$ groups, and its outputs form the complete congruence class $H(1)$ modulo $S\cdot 2^d$. At $M_0/2$ that class has at most $T/2$ available residues, forcing mergers. Therefore the smallest distinction-preserving modulus is $M_0$. Since $1 \le H(1) \le 4 < S$, none of the residues is zero at $M_0$; the catalogue's additional zero-preservation condition imposes no extra bit. Catalogue and Distinct outputs both select $M_0$.

A spatial half-period changes the surviving odd pre-value by $K/2$ modulo $K$. Its post-difference has valuation $\log_2 K-1+d$, so the half-period survives at $M_0/2$ and fails at $M_0$, while the $N$-period already holds. Hence Minimum period also selects $M_0$. The pre-twist preserves the complete class and the difference valuations, so the proof is uniform over $Q$.

**Every positive single post-power also agrees.** For $H(z) = z^p$ with any integer $p \ge 1$, the lifting formula on inputs $a,b = 1$ modulo $S$ gives

$$
\nu_2(a^p-b^p)=\nu_2(a-b)+\nu_2(p).
$$

The outputs are odd, so zero preservation is automatic. The same distinctness and period argument yields all three moduli equal to $K\cdot 2^{\nu_2(p)}$, without restricting the valuation of $p$ to zero or one.

**Boundary of the statement.** Arbitrary post-polynomials can merge groups at minimum-period precision even in this tail. At $N = 128$, $q = 10$, no twist, and $H(z) = z^2+6z$, the three choices are:

| Selector         |    M | Distinct output groups |
| ---------------- | ---: | ---------------------: |
| Catalogue        | 4096 |                     32 |
| Distinct outputs | 4096 |                     32 |
| Minimum period   | 2048 |                     16 |

Here $K = 256$ and the tail inputs are $z = 1+8a$ with $0 \le a < 32$. The post becomes $7+64a(a+1)$. Reducing to $M = 2048$ merges groups while retaining both least axis periods 128; at $M = 1024$ the requested periods are lost. This positive-coefficient quadratic has $H'(1) = 8$, beyond the ten-post family's $d \le 1$ condition.

For AND, MULT, and CLMUL at this same $K$, the erased branch makes the basic field constant, so Minimum period reports an unattainable target rather than a matching modulus. Other samplings require their own analysis. OR on odd/odd sampling has the selector agreement proved in the pre-power report without needing to be in its valuation tail.

The [new selector checks](tail_modulus_checks.py) compare all three actual implementation paths on 800 recipes spanning all 16 twists, all ten posts, and five tail powers at $N = 128$; 60 recipes spanning five sides and all four surviving combiners; and 24 pure-post-power recipes, including post-powers 32 and 64. They compare the numerical fields as well as $M$ and independently verify the quadratic counterexample's periods. The general scope comes from the proofs, rather than extrapolation from those bounded sweeps.
