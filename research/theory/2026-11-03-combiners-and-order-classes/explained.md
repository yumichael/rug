# What this research means for the rug generator

The [main report](2026-11-04-combiners-and-order-classes.md) contains the proofs, precise assumptions, and limitations. This companion explains the main results in terms of generator choices.

## Choose the two moduli at different points

First choose a pre-operation, basic combiner, sampling rule, and desired repetition size. Increase the pre-modulus until the **basic combined pattern** has enough repetition room on both displayed axes. Freeze that modulus. Only then choose the post-operation and find its smallest final modulus that retains the exact requested repetition.

For example, squared-pre-operation rugs with a requested period of 32 select pre-modulus 64 on the full grid for all seven combiners. But their final moduli differ. With post-power one, XOR uses 64, MULT and carryless multiplication use 256, and ABSDIFF uses only four. AND uses 64 for post-power one but needs 2,048 for post-power two.

So there is no replacement for the XOR modulus formula that can simply be applied unchanged to every combiner. There is, however, one exact method for finding the answer: test the differences caused by a full-period shift and a half-period shift. The report turns that into a complete interval of allowed moduli.

Sometimes a basic combiner skips a requested size. Fourth-pre-power AND has axis periods eight at pre-moduli 32 through 256, then 128 at pre-modulus 512. For a target of 16, 512 is the first pre-modulus that does not shrink the domain. A later post-operation must still produce exactly 16; the pre-modulus test alone does not guarantee success.

## You can expose families of pre-polynomials

There is a useful way to vary the pre-operation without repeatedly solving its minimum pre-modulus. Start with an even power $q$, and replace $x^q$ by

$$
x^q+2x^q(x^q-1)Q(x^q),
$$

where $Q$ can be any integer polynomial. Choosing $Q=0$ gives the original power; choosing $q=2$ and $Q=1$ gives $2x^4-x^2$.

These changes preserve the divisibility of every difference between pre-values. That gives a common minimum pre-modulus for the entire family, on the full historical grid, for six combiners. For OR, XOR, ADD, and ABSDIFF, use the requested period times $2^{\nu_2(q)}$. MULT and carryless multiplication use that too unless a larger modulus is needed to keep the even operand from becoming zero.

For a period of 512, every squared-family member uses pre-modulus 1,024 for those six combiners. The fourth-power family uses 2,048. This is a genuinely broader family than selecting another exponent, with a proved modulus guarantee.

AND is different because an operand acts as a bit mask. For pure even pre-powers, the report gives an exact rule: find the first bit position high enough to retain the requested period that can occur in both operands. Fourth-pre-power AND can use bit four, then none of bits five through seven, then bit eight and higher. That gap explains its jumps in repetition size.

For the broader pre-polynomial family, individual AND minima can be smaller because the mask overlap can change. However, the pure-power minimum is proved sufficient for every family member, and it is the smallest modulus with that family-wide guarantee. So all seven combiners can use a consistent pre-modulus for this family.

Arbitrary unrestricted pre-polynomials also cannot all share one modulus: multiplying a pre-polynomial by a sufficiently large power of two makes it zero at any fixed modulus.

## Sampling can change the kind of pattern

The full grid remains an important choice. Checkerboard sampling is particularly well matched to the existing no-pre-operation XOR construction, but its behavior changes with even pre-powers.

For squared pre-operation at pre-modulus 64, the full grid has basic periods 32 by 32. Same-parity checkerboard sampling gives eight by sixteen; opposite-parity checkerboard sampling gives sixteen by eight. Each of the four original-grid parity selections gives sixteen by sixteen in this example.

The reason is that checkerboard sampling separates the odd-input pre-function onto one axis and the even-input pre-function onto the other. Those functions have different periods. At sufficiently large pre-powers, the even-input function vanishes entirely. Checkerboard sampling then exposes a constant direction for some combiners, rather than filtering out isolated dead cells.

The report specifies all seven maps and their phases. A symmetry of the full pattern can exchange two sample phases, so the symmetry must be checked on the actual selected phase.

## Order classes do not reduce the established XOR counts

For the balanced no-pre-operation XOR single-power family, the distinct anchored values fill a complete, equally spaced grid. If there are 64 distinct values, they are exactly $0,1/64,\ldots,63/64$. Knowing the ascending order of the cell groups already tells you every numerical value.

Therefore two such patterns cannot have the same ordering but different numerical spacings. **Order classes and shift classes coincide.** The old counts, multiplier choices, tail identifications, and uniform samplers carry over unchanged.

The same argument extends to the valid same-valuation polynomial sums from the previous research. Their full-period coefficient condition forces them to fill the same complete value grid. The earlier independent binary controls therefore also select order classes uniformly without duplication.

This does not extend to every arbitrary or even-only post-polynomial. The main report gives explicit pairs with identical orderings and different spacings, even when each is evaluated at its own minimum valid modulus. Their old numerical samplers would need new weights to sample order classes uniformly.

## Four other combiner families also have a finite power tail

With even pre-powers, OR, XOR, ADD, and ABSDIFF produce odd basic values in the chosen coordinates. For any fixed table made entirely of odd values, increasing the post-power's valuation eventually stops introducing new normalized patterns, even though its final modulus keeps increasing. The report proves where that tail starts from the table's half-period difference depths.

This gives a complete finite procedure for all positive post-powers and odd multipliers in these four cases, with no arbitrary precision cap. You can catalogue shift classes or order classes and sample either uniformly. The procedure applies to all seven sampling rules, after their separate pre-modulus and period checks. It does not assume that order and shift classes coincide outside the special XOR cases.

## Polynomial order classes have a finite stopping rule

Fix the selected pre-modulus and basic table. There are only finitely many distinct basic values, each labeling a fixed group of cells. A post-operation can merge those groups and reorder them; it cannot split one basic group into different outputs.

With unrestricted integer polynomials and sufficiently large final moduli, every ordering and merging consistent with the desired period can be realized. Even-only polynomials have the same eventual ordering possibilities for a nonnegative basic input, though they may need larger moduli.

Requiring the final modulus to be minimal adds a constraint: at least one half-period shift must change each output either by zero or by exactly half a circle. The report proves how to test this constraint and gives a finite precision bound large enough to find every attainable order class. Searching through that bound finds the smallest-modulus representative of each class too.

This settles the theoretical stopping problem for these unrestricted polynomial families. It does not make the general catalogue small. The complete procedure can be far too expensive for an interactive generator, so compact subfamilies and offline catalogues remain useful.

## The infinite AND example remains useful

The squared-pre AND example still selects minimum pre-modulus 64 for target period 32. Its three basic value groups are 0, 16, and 32.

Single post-powers and odd multipliers give two order classes: the sixteen group falls either below or above the thirty-two group after anchoring the zero group. Both have representatives at post-power one and final modulus 64. The infinitely many numerical spacings are still infinitely many shift classes.

Arbitrary post-polynomials add two valid order classes by merging the sixteen group with either of the other groups. Merging zero with thirty-two would destroy the requested period. The minimum representative moduli are:

| Output grouping                        | Arbitrary integer post-polynomial | Even-only post-polynomial |
| -------------------------------------- | --------------------------------: | ------------------------: |
| Three distinct groups, either ordering |                                64 |                     2,048 |
| Sixteen merged with zero               |                             1,024 |                   524,288 |
| Sixteen merged with thirty-two         |                             1,024 |                   524,288 |

So ordinary and even-only polynomials eventually reach the same four order classes, but can have very different simplest numerical realizations.

## What is ready to use and what needs more work

The existing balanced XOR controls can support either equivalence unchanged. The shared pre-polynomial family supplies a concrete expansion with common pre-moduli. The difference-depth test and the polynomial feasibility test apply to all seven combiners and sampling rules. At fixed precision, finite polynomial coordinates give uniform shift-class sampling.

The general unbounded polynomial order catalogue now has a proved finite search bound. The odd-valued theorem also gives a finite unbounded-post-power procedure for the four stated even-pre combiner families. A complete unbounded single-power classification for the remaining zero/even-valued basic tables and a compact sampler for every possible style remain unresolved. Those limits are stated explicitly in the report; the application itself has not been modified.
