# Modulus selectors and shared pre-twists

**Catalogue and Distinct outputs agree for every positive single post-power in this study.** Minimum period agrees with them for checkerboard-opposite OR and XOR, all four checkerboard tail combiners, and odd-odd AND and OR. In the other cases the distinction-preserving modulus can recover many color groups. A shared pre-twist can change the shape of those groups. On odd-odd sampling at fixed pre-power it preserves the complete color histogram.

The [direct-sampling extension](direct-sampling.md) gives algebraic coordinates for the conditional unit cases and resolves several unions across pre-powers and twists.

This extends the [first pass](report.md) to the workbench's three selectors and to the full shared family $f(z)=z+2z(z-1)Q(z)$ with $Q\in\mathbb{Z}[z]$. The pre-modulus and sample maps are the same as in the first pass. The result concerns $N=2^r\ge16$, positive even pre-power $q=2^wu$, positive post-power $p=2^vj$, and an odd multiplier. Choose the modulus for the powered values and apply an independent circular color offset afterward. The [earlier checkerboard tail result](../2026-11-12-1-tentative-pattern-explorations/precision-policy.md#4-all-three-selectors-agree-in-the-opposite-checkerboard-tail) already covers that tail, including shared twists.

## What each selector preserves

The workbench's **Minimum period** keeps the least horizontal and vertical periods at $N$. **Distinct outputs** chooses the least dyadic modulus that preserves the partition of the actual Catalogue output. **Catalogue** for a single post-power chooses the least dyadic modulus that preserves all distinct integer powers and keeps every nonzero power separate from zero. Since Catalogue preserves the integer partition, Distinct outputs also preserves that partition in this setting.

Odd multiplication preserves divisibility of every powered difference and preserves zero. For all checkerboard cases and odd-odd AND, OR, MULT, and CLMUL, the raw values are odd, so a distinction-preserving modulus already keeps them away from zero. Odd-odd ADD has every raw value exactly divisible by two and its least distinction-preserving modulus exceeds $2^p$. Odd-odd XOR and ABSDIFF already contain zero. These observations prove equality of Catalogue and Distinct outputs for the full scope.

The equality partition at the common preservation modulus is exactly the raw combiner partition for each fixed twist, independently of post-power. The integer map $z\mapsto z^p$ is injective on the nonnegative raw values. At Minimum period a smaller modulus can merge raw groups. More distinct colors can either improve or worsen spacing around the circle.

## Checkerboard-opposite selectors

Here $K=N2^w$. Use the [previous head and tail cutoff](../2026-11-12-2-checkerboard-head-tail/theory.md#1-one-half-period-graph-controls-both-axes). Every recipe in the tail has $q\ge r+w$ and the even operand vanishes.

| Case                     | Minimum period | Distinct outputs and Catalogue |
| ------------------------ | -------------: | -----------------------------: |
| Tail, all four combiners |         $K2^v$ |                         $K2^v$ |
| Head OR or XOR           |         $K2^v$ |                         $K2^v$ |
| Head ADD                 |         $K2^v$ |                        $2K2^v$ |
| Head ABSDIFF, odd $p$    |            $4$ |                            $K$ |
| Head ABSDIFF, even $p$   |         $K2^v$ |                        $2K2^v$ |

These formulas hold for every admissible twist. The twist is a 2-adic isometry, preserves valuations, and permutes the odd operand coset $1+2^{w+2}\mathbb{Z}$ modulo $K$. It preserves the existing half-period witnesses. Write $O$ and $E$ for the odd and even pre-operands. The values for OR, XOR, ADD and the signed difference $O-E$ are all $1$ modulo four. Differences between powered values then gain exactly $v$ bits of divisibility, by lifting the exponent. For even $p$ the signed and absolute differences have the same powers, and two distinct signed differences cannot be negatives of one another since both are $1$ modulo four. For odd $p$ the valuation of a difference between any two odd absolute differences is preserved. The head sign-comparison witness at modulus 4 is [already proved](../2026-11-12-2-checkerboard-head-tail/theory.md#6-lower-bounds-on-the-modulus-and-the-absdiff-exception).

To prove the preservation widths for OR, XOR, and odd-post ABSDIFF, their raw values lie in $[0,K)$, and the $E=0$ row includes two odd operands differing by $K/2$. For ADD and signed difference, the complete integer ranges of the respective tables have width less than $2K$. In the head there is a nonzero even operand $e$ divisible by $2^{w+2}$. For $q\ge4$ choose any nonzero even operand. For $q=2$, input four yields valuation four, preserved by the twist, and $K\ge32$. Both 1 and $K-e+1$ lie in the odd coset. Then $1+0$ and $(K-e+1)+e$ differ by $K$ in ADD. In the signed difference use $(K-e+1)-0$ and $1-e$. This proves the extra preservation bit in both cases. Taken with the first-pass half-period argument, it also shows that every head ADD and even-post ABSDIFF recipe merges some raw groups at Minimum period.

## Odd-odd selectors

Set $K=2N2^w$, $S=2^{w+2}$ and $T=N/2=2^t$, so $K=ST$. With odd-odd sampling the operand code $A$ in $1+SA$ runs over all of $[0,T)$, twice along each axis. Each allowed twist replaces the code by an invertible permutation, leaving the set of integer raw values and their frequencies unchanged. The permutation commutes with the top-bit toggle by the isometry property, so the half-period difference set is also preserved. All three moduli in the table therefore apply with or without twists. For fixed $q,p$ and multiplier, each selector's complete color histogram is unchanged by twisting.

| Case                                  | Minimum period | Distinct outputs and Catalogue |
| ------------------------------------- | -------------: | -----------------------------: |
| AND, OR                               |         $K2^v$ |                         $K2^v$ |
| ADD                                   |   $K2^{p-1+v}$ |                     $K2^{p+v}$ |
| MULT, $S\ge2T$                        |         $K2^v$ |                    $K^2 2^v/4$ |
| CLMUL, $S\ge T$                       |         $K2^v$ |                    $K^2 2^v/2$ |
| MULT and CLMUL below their thresholds |         $K2^v$ |                      $2^{d+v}$ |
| XOR                                   |     $S^p T2^v$ |                      $S^p 2^b$ |
| ABSDIFF, even $p$                     |     $S^p T2^v$ |                      $S^p 2^b$ |
| ABSDIFF, odd $p$                      |         $4S^p$ |                      $S^p 2^b$ |

Here $d$ is the least bit width that distinguishes the distinct **raw integer** product values, computed once from the full untwisted product table at the selected $K$. For the last three rows, $b=p(t-1)+1$ for $p\ne2$, and $b=2t$ for $p=2$. The Minimum period column is from the [first-pass proofs](report.md#odd-odd). Distinct outputs merges none of the integer groups.

**ADD.** The complete raw table is $2+SB$ for $B=0,\ldots,2T-2$. Its deepest raw difference has valuation $\log_2 K$, from codes separated by $T$. After factoring out two, the remaining values are units in $1+(S/2)\mathbb{Z}$. Powering adds $p-1+v$ to the valuation of the original raw difference. This gives one extra bit over Minimum period.

**MULT and CLMUL.** All raw values are $1$ modulo $S$, so differences gain $v$ bits after powering. The unpowered distinction depth $d$ is a finite test on the raw values and can be found by binary search on the low-bit projections. For MULT and $S\ge2T$, the raw code is $A+B+SAB$, with the sum in $[0,S)$. A deepest difference must come from pairs with the same sum. At fixed sum, the difference of products has the same valuation as $(A-C)(A-D)$, for the compared pairs $(A,B)$ and $(C,D)$. Both factors have magnitude less than $T$. Both cannot have valuation $t-1$: that would force $C=D$ at distance $T/2$ from $A$ and force $B=2C-A$ out of range. The deepest valuation is $2t-3$, attained with $(A,B)=(T/2,T/4)$ and $(C,D)=(0,3T/4)$. Restoring the $S^2$ scale gives the stated width.

For CLMUL and $S\ge T$, the two parts of the shifted code occupy disjoint bit ranges. Compare pairs with the same XOR of their operands. Over the binary polynomial ring, the XOR of their carryless products factors as the carryless product of $A\mathbin{\mathrm{XOR}}C$ and $A\mathbin{\mathrm{XOR}}D$. Its deepest possible first nonzero bit is $2t-2$, realized by $(T/2,T/2)$ and $(0,0)$. Restoring $S^2$ gives the stated width. In both separated product regimes the two parts determine the unordered operand pair by their sum and product in the corresponding ring. Thus Distinct outputs retains $T(T+1)/2$ colors, versus $T$ at Minimum period. The product cases below the thresholds use the exact finite $d$ test.

**XOR and ABSDIFF.** Both raw sets are $S$ times the complete interval $[0,T)$. Remove the factor $S^p$ and consider the deepest difference between powers on this interval. The pair $0,T/2$ gives depth $p(t-1)$, which also bounds all pairs of unlike input valuations. For a same-valuation pair of depth $h\le t-2$, divide out $2^h$ first. For odd $p$ the two odd parts contribute at most $t-h-1$ bits, which gives depth at most $p(t-1)$ after restoring $2^{ph}$. For even $p$ the contribution is at most $t-h+v$, using lifting on the sum and difference of the odd parts. The bound $p(t-1)$ then holds for $p\ge4$, since $p\ge v+2$ and $t-1-h\ge1$. For $p=2$ the upper bound is $2t-1$, reached by the pair $2^{t-2},3\cdot2^{t-2}$. Add one to the maximum depth to get the minimum distinguishing width $b$.

## What twists add

At fixed side and pre-power, use the earlier [complete checkerboard twist coordinates](../2026-11-12-2-checkerboard-head-tail/theory.md#5-finite-twist-coordinates-at-every-domain). For odd-odd, write $Q$ in powers of $z-1$. On the whole odd pre-coset, a coefficient of $(z-1)^i$ contributes $2z(z-1)^{i+1}$. This vanishes modulo $K=2^k$ once $1+(w+2)(i+1)\ge k$. Apply the same dyadic diagonalization to the remaining finite columns on the odd coset. This gives independent coordinates and enumerates every distinct restriction of the arbitrary-degree twist.

Some twist freedoms can be absorbed by varying the odd part of the pre-power. On a complete odd code range of size $T=2^t$, write the operand as $1+2^s A$ with $s=w+2$. When $s\ge t-1$, the normalized twist is $(1+2Q(1))A\pmod T$. Raising the operand to an odd exponent $u$ also acts linearly on the code: the quadratic term vanishes or becomes linear because $A^2\equiv A\pmod 2$. Higher terms vanish. Evaluating at $A=1$ shows these linear maps cover every odd multiplier, by lifting. Thus a twist can be absorbed into an odd pre-power part throughout that range, for every combiner and selector. This covers odd-odd $w\ge r-4$ and the checkerboard tail $w\ge r-5$, where $T=N/4$ and each odd part has an erased-branch representative.

Below those thresholds, extra operand maps can produce extra spatial classes. At side 64, odd-odd valuation one gives 16 operand sequences from varying the odd pre-power part and 32 after adding all twists. With post-power one, preservation-precision equality classes double from 16 to 32 for six combiners. XOR stays at eight. At Minimum period, the same expansion doubles AND, OR, ABSDIFF, and MULT, and leaves ADD, CLMUL, and XOR unchanged. The [results](selector-results.json) give each count.

At a fixed checkerboard pre-power, the selector itself determines much of the twist variety that is visible. At side 64 with pre-power two, the 128 admissible twist actions give 128 ADD equality partitions at the preservation modulus and four at Minimum period. For head ABSDIFF with pre-power two, odd posts at Minimum period expose 128 sign partitions, while even posts expose only four. Both parities recover 128 partitions at the preservation modulus. A smaller palette can therefore carry substantial spatial variety. A larger palette can preserve distinctions that twists change before reduction.

## Order sampling and visual comparisons

For the unit-coset cases, the finite post-power method in the first pass also works at the preservation modulus for each fixed pre-power and twist. Use the normalized output bit width selected by the preservation formula in the same squaring recurrence. Factor out $2^p$ first for odd-odd ADD, and use signed differences for even checkerboard ABSDIFF. Odd checkerboard head ABSDIFF uses the odd-unit exponent cycle at its fixed modulus $K$. Enumerating those representative powers and all effective odd multipliers, then deduplicating within the selected policy, gives exact conditional order or shift samplers at modest sizes. Because the order encodes the equality classes, the two selectors can produce disjoint order spaces when preservation keeps more colors.

At side 16 and pre-power two, allowing all twists gives checkerboard ADD 8 orders at Minimum period and 128 at preservation precision, with zero shared orders. Odd-odd MULT goes from 4 to 65,536 with zero shared. These counts include every positive post-power. Odd-odd XOR and ABSDIFF at preservation precision have a width growing with $p$ even after removing $S^p$. Their order counts in the results are for post-powers one through four. The proof of finite all-power order sampling at Minimum period does not supply a bound for this policy. The preservation-precision shift spaces are infinite since the normalized difference of the 0 and 1 basic groups for multiplier one is $2^{-b}$. Similarly, in high-valuation odd-odd MULT and CLMUL, the preservation-precision shift space across pre-valuations is infinite even at post-power one. Along an axis through the origin an operand with fixed nonzero stabilized code $A$ gives difference $SA$, while the modulus is proportional to $S^2$.

The [paired atlas](selectors-and-twists.png) holds post-power and multiplier fixed within each row. For side-64 checkerboard ADD with pre-power two, the preservation modulus increases the identity recipe from 32 to 52 colors, but its largest circular gap increases from 3.1% to 14.1%. With $Q=1$ the same preservation modulus gives 58 colors and a largest gap of 4.7%. For odd-odd MULT and CLMUL in their separated product regimes, the preservation modulus increases the color count from 32 to 528. In the illustrated recipes their largest gaps shrink. The results record the largest cell group along with the circular gaps, so equal spacing of distinct levels can be compared with how often each color occurs.

## Reproduction

[precision.py](precision.py) computes the three moduli and full twist representatives. [verify_precision.py](verify_precision.py) checks the workbench's three actual selector paths, sweeps all twist actions at the stated fixed pre-powers, checks high-degree signed odd-odd twists against the finite image, and regenerates [selector-results.json](selector-results.json) and the atlas. The all-twist modulus sweeps use the six post-powers listed in the results. The formulas apply beyond those sweeps. The larger-preservation order catalogues are conditional on the fixed pre-powers used in the pilot. A scalable sampler across all pre-valuations at preservation precision remains open.

Run from the repository root.

```sh
MPLCONFIGDIR=/private/tmp/rug-research-mpl PYTHONPATH=research/interactive PYTHONDONTWRITEBYTECODE=1 research/interactive/.venv/bin/python research/theory/2026-11-19-monomial-first-pass/verify_precision.py
```
