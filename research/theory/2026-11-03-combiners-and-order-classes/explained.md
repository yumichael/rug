# What this research means for the rug generator

The [main report](2026-11-04-combiners-and-order-classes.md) contains the proofs, precise assumptions, and limitations. This companion explains the main results in terms of generator choices.

## Choose the two moduli at different points

First choose a pre-operation, basic combiner, sampling rule, and desired repetition size. Increase the pre-modulus until the **basic combined pattern** has enough repetition room on both displayed axes. Freeze that modulus. Only then choose the post-operation and find its smallest final modulus that retains the exact requested repetition.

With squared pre-operation and a requested period of 32, all seven combiners choose pre-modulus 64 on the whole operand grid and on the opposite-parity checkerboard. The final moduli can still differ. For squared AND with post-power two, the whole grid needs $M=128$ and the opposite-parity checkerboard needs $M=2{,}048$. A full-period shift and a half-period shift determine the allowed moduli on the chosen sample.

The opposite-parity checkerboard can skip requested sizes. With fourth-power pre-operation, AND has axis periods eight at pre-moduli 32 through 256 and 128 at pre-modulus 512. At that first candidate modulus for a target of 16, the polynomial feasibility test rules out a post-operation that gives periods 16. On the whole operand grid the same combiner already has basic period 16 at $K=64$.

## You can expose families of pre-polynomials

There is a useful way to vary the pre-operation without repeatedly solving its minimum pre-modulus. Start with an even power $q$, and replace $x^q$ by

$$
x^q+2x^q(x^q-1)Q(x^q),
$$

where $Q$ can be any integer polynomial. Choosing $Q=0$ gives the original power; choosing $q=2$ and $Q=1$ gives $2x^4-x^2$.

These changes preserve the divisibility of every difference between pre-values. On the whole operand grid all seven combiners attain the requested basic period at the same minimum, $K=R\,2^{\nu_2(q)}$. A fixed second operand can detect every change in the first pre-value. For AND, choose the input that has a set bit where the two pre-values differ.

On the opposite-parity checkerboard the fixed operand must have the opposite parity. MULT and CLMUL need enough precision to keep some even pre-values nonzero. AND needs a bit that occurs in both parity branches, which explains the skipped sizes. The main report gives these minimum-modulus rules separately.

## Sampling can change the kind of pattern

Both checkerboards select from the original operand grid and rotate their selected cells into displayed axes. The same-parity checkerboard keeps even/even and odd/odd pairs. The opposite-parity checkerboard keeps even/odd and odd/even pairs. The four Cartesian selections isolate one parity pair each.

At pre-modulus 64 with squared pre-operation, XOR has basic axis periods 32 on the whole grid and on the opposite-parity checkerboard, and 16 on the same-parity checkerboard. In the Cartesian selections, the even branch has period eight and the odd branch period 16, measured in displayed cells. The even/even, even/odd, odd/even, and odd/odd period pairs are $(8,8)$, $(8,16)$, $(16,8)$, and $(16,16)$.

A sufficiently large even pre-power makes every even operand zero. At pre-modulus 64 and pre-power six, AND is zero everywhere on the opposite-parity checkerboard, the same-parity checkerboard’s AND is zero on half the cells, and odd/odd AND has no zeros. Post-powering can erase further distinctions, so the report applies period and occupancy tests to each selected table.

## Order classes do not reduce the established XOR counts

For the balanced single-power XOR family on the opposite-parity checkerboard and its additional display-grid sampling, the distinct anchored values fill a complete, equally spaced grid. If there are 64 distinct values, they are exactly $0,1/64,\ldots,63/64$. Knowing the ascending order of the cell groups already tells you every numerical value.

Therefore two such patterns cannot have the same ordering but different numerical spacings. **Order classes and shift classes coincide.** The old counts, multiplier choices, tail identifications, and uniform samplers carry over unchanged.

The same argument extends to the valid same-valuation polynomial sums from the previous research. Their full-period coefficient condition forces them to fill the same complete value grid. The earlier independent binary controls therefore also select order classes uniformly without duplication.

This does not extend to every arbitrary or even-only post-polynomial. The main report gives explicit pairs with identical orderings and different spacings, even when each is evaluated at its own minimum valid modulus. Their old numerical samplers would need new weights to sample order classes uniformly.

## Four other combiner families also have a finite power tail

With even pre-powers, OR, XOR, ADD, and ABSDIFF produce only odd basic values on the opposite-parity checkerboard and on the two mixed-parity Cartesian selections. For any fixed table made entirely of odd values, increasing the post-power's valuation eventually stops introducing new normalized patterns, even though its final modulus keeps increasing. The report proves where that tail starts from the table's half-period difference depths.

This gives a complete finite procedure for all positive post-powers and odd multipliers in these four cases, with no arbitrary precision cap. You can catalogue shift classes or order classes and sample either uniformly. The procedure applies wherever the complete basic table consists of odd values. It does not assume that order and shift classes coincide outside the special XOR cases.

## Polynomial order classes have a finite stopping rule

Fix the selected pre-modulus and basic table. There are only finitely many distinct basic values, each labeling a fixed group of cells. A post-operation can merge those groups and reorder them; it cannot split one basic group into different outputs.

With unrestricted integer polynomials and sufficiently large final moduli, every ordering and merging consistent with the desired period can be realized. Even-only polynomials have the same eventual ordering possibilities for a nonnegative basic input, though they may need larger moduli.

Requiring the final modulus to be minimal adds a constraint: at least one half-period shift must change each output either by zero or by exactly half a circle. The report proves how to test this constraint and gives a finite precision bound large enough to find every attainable order class. Searching through that bound finds the smallest-modulus representative of each class too.

This settles the theoretical stopping problem for these unrestricted polynomial families. It does not make the general catalogue small. The complete procedure can be far too expensive for an interactive generator, so compact subfamilies and offline catalogues remain useful.

## The infinite AND example remains useful

On the opposite-parity checkerboard, the squared-pre AND example selects minimum pre-modulus 64 for target period 32. Its three basic value groups are 0, 16, and 32.

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
