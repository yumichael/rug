# Research goal: symmetric rug patterns with controlled repetition

## Status and purpose

This research brief records the discussion of November 3–4, 2026, including the expanded four-stage model. It records the intended investigation, the obstacles identified in applying the initial prompt, and the working resolutions. It supplies no new classification, experiments, or sampler implementation.

The investigation's results are in [the November 4 report](2026-11-04-combiners-and-order-classes.md), with [a plain-language explanation](explained.md). This document states the research contract; the report identifies which questions have been resolved and which remain open.

The overarching goal is to expand the rug generator's aesthetic possibilities while maintaining control of the repetition domain and the choice of useful sampling. Seek reproducible numerical pattern families with clear period guarantees and practical parameter choices. The motivating baseline is the existing pre-power-one XOR work, explained in the [post-operation companion](../2026-10-25-pattern-space/2026-11-01-xor-post-operations-explained.md).

Investigate shared pre-operations and symmetric combinations. The initial combiners are AND, OR, XOR, ADD, MULT, CLMUL, and ABSDIFF. Powers are one starting pre-operation family; a central goal is to obtain results for entire families such as polynomials with a consistent pre-modulus, rather than only one exponent at a time. Stage-three combinations may also use several intermediate combined values and further operations on them.

Prioritize families with useful centered reflection and rotation symmetries. Even pre-powers and functionally even pre-polynomials provide established starting points. Give AND, OR, XOR, ADD, MULT, CLMUL, and ABSDIFF equal research priority. Deprioritize only odd pre-powers, giving them a limited diagnostic treatment because the user has found their examples less visually appealing. Treat that as a product preference to explain and investigate, rather than an established universal theorem about aesthetics or symmetry. This preference does not exclude other shared pre-functions that meet the desired symmetry conditions.

The intended deliverable is a theoretical foundation for generator controls: which constructions are useful and feasible, how their sampling and modulus choices determine exact repetition, which numerical distinctions should remain available, and how to choose canonical representatives without accidentally biasing their selection.

## 1. Comparing patterns

A shift class identifies normalized numerical patterns differing by a common circular phase. Its **anchored representative** subtracts the value at a fixed reference cell modulo one so that the cell becomes zero. If the reference is specified through an input value or tuple, it must be reachable in the sampled pattern.

A cell value group is the set of cells assigned the same anchored numerical value. An **order class** groups patterns with the same cell value groups and the same ascending order of those groups in the interval from zero inclusive to one exclusive. An order class may contain many distinct numerical shift classes with different spacing between values.

Study both classifications. Where the full attainable shift-class set is finite, seek its classification, counts, and uniform sampler without imposing an additional precision cutoff. Study order classes in those finite cases as well as in cases with infinite shift-class families. If the shift-class set is infinite, retain bounded shift-class sampling as an optional numerical refinement and pursue order classes as the finite classification target.

For families whose parameters grow without bound, investigate each eventual stable ordering and seek its simplest attainable realization. Different parameter paths can have different eventual orderings; their behavior and realizability remain research questions.

Assess ordering after applying each candidate odd multiplier, since multipliers can change the ordering. Keep the origin, orientation, reference cell, and sample indexing fixed when comparing patterns.

The distinctions between exact tables, affine families, and equality partitions in [October 25, Section 2](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md) provide context for this comparison. Classification by order is the subsequent design choice from the discussion and remains to be investigated.

## 2. Four-stage arithmetic model

Let $C=2^c$ describe the original grid and its coordinate-domain convention. Introduce a pre-modulus $K=2^k$ and a post-modulus $M=2^m$. They are distinct from the grid size and are chosen to preserve the requested repetition domain. The coordinate wrapping, sampling, origin, and displayed indexing must be specified for each construction.

### Stage 1: Shared pre-operation

Apply the same integer-valued univariate function $P$ to both original coordinate operands. Allow useful families beyond powers, with integer polynomials as a priority. Give conditions defining which members of each family are eligible to preserve the requested period and symmetry.

### Stage 2: Pre-modulus

Reduce both pre-operation results modulo a selected power of two:

$$
A=P(a)\bmod K,\qquad B=P(b)\bmod K.
$$

Choose the minimum suitable $K$ by testing the sampled output of the immediate basic combiner $Z_K=G(A,B)$, before further post-operations. Its smallest axis periods must be at least the requested axis periods, so that this stage does not shrink the repetition domain. The reduced operand pair alone is insufficient to determine this minimum. For several basic combiners, test the tuple of their intermediate outputs. State the target axis periods and sampling coordinates used for this test. The final output must attain those periods exactly; requiring exact periods at the basic-combiner stage as well is a stricter optional style constraint, since intermediate periods can jump past a requested size.

### Stage 3: Symmetric combination, including further operations

Produce an integer result $S(A,B)$ with exchange symmetry:

$$
S(A,B)=S(B,A).
$$

This stage includes both the combiner and what earlier reports called post-operations. It may use one or several intermediate values and operations on them. An important starting family is $S(A,B)=\alpha G(A,B)^p+\beta$; a broader one is a joint integer polynomial in several symmetric intermediate values. Require the overall expression to be symmetric and state its arithmetic and bit-width conventions explicitly.

Start with AND, OR, XOR, ADD, MULT, CLMUL, and ABSDIFF as basic combinations. ADD and MULT are integer arithmetic within the expression, with final reduction by $M$ at stage 4. Any intermediate modular reduction must be part of the specified expression or justified as an equivalent evaluation method. Do not silently insert a reduction modulo $C$ inside this stage.

Exchange symmetry does not alone imply centered axial or quarter-turn symmetry. Investigate the additional conditions on the pre-function, coordinate forms, combination, and sample phase that give the desired spatial symmetries. The even-function result in [October 25, Section 7.3](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md) is an existing sufficient starting point under its coordinate and lattice assumptions.

### Stage 4: Post-modulus

Reduce the result modulo a selected power of two:

$$
F=S(A,B)\bmod M.
$$

Seek the minimum suitable $M$ for the exact requested displayed period. Polynomial combinations use this common modulus for the whole expression. Distinguish arbitrary polynomial expressions from sums whose exponents are constrained to one valuation; [November 2, Section 1](../2026-11-02-xor-polynomial-period/2026-11-02-xor-polynomial-period.md) establishes that these are different spaces even for the XOR baseline.

### Minimum moduli and family-level guarantees

First determine the minimum pre-modulus from the immediate basic-combiner output. At that chosen $K$, characterize the post-operations and post-moduli that retain the exact target period. If a later post-operation cannot retain it, record that operation as inadmissible at the chosen $K$; increasing $K$ defines a separately specified policy or style. The pre-modulus selection does not depend on which later post-power or post-polynomial is drawn.

A central deliverable is a family-level result: one consistent pre-modulus, with explicit admissibility conditions, for a useful set of pre-functions such as polynomials. Distinguish a member's individual minimum from the least common sufficient modulus for the eligible family. Determine whether such a finite shared modulus exists for the claimed parameter ranges. A theorem for unrestricted coefficients cannot silently exclude period-collapsing members or impose an undisclosed precision bound.

Selection of a shared pre-modulus belongs to the style definition. The preference for minimum post-modulus representatives of order classes is then conditional on that chosen pre-modulus. If candidate representatives are also compared across different pre-moduli, the priority between minimizing $K$ and minimizing $M$ must be stated; a pair need not minimize both coordinates simultaneously.

### Carryless multiplication and absolute difference

CLMUL is carryless multiplication: interpret the binary digits of each nonnegative integer as polynomial coefficients over the two-element field, multiply those polynomials, and encode the resulting coefficients as binary digits again. Coefficient addition is XOR, so no carries propagate between bit positions. This is the polynomial-ring definition given in the [RISC-V specification, Zbc extension](https://docs.riscv.org/reference/isa/v20260120/unpriv/b-st-ext.html).

Use the full carryless product in stage 3. Its reference implementation is:

```python
def clmul(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result
```

The operands are nonnegative because stage 2 reduces them modulo $K$. For example, the binary representation of 3 corresponds to $t+1$. Multiplying it by itself over the two-element field gives $t^2+1$, so $\mathrm{CLMUL}(3,3)=5$, whereas ordinary multiplication gives 9.

Retain the entire product until the declared post-modulus stage. A low-word truncation or reduction by an irreducible binary polynomial would be a separate operation and is not included in this definition. Hardware instructions can expose different portions of the product: for example, RISC-V `clmul` returns the lower half and `clmulh` the upper half. The mathematical operation here denotes their full underlying product rather than a particular register-sized portion. The definition, example, and code above fully specify the operation without another local project.

ABSDIFF is the ordinary nonnegative absolute difference $|A-B|$. It is not the shortest circular distance between two residues.

The fixed pre-modulus model in [October 25, Section 1.1](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md) and [index.html](../../../index.html) remains a reference case. Reassess its results under the newly selected $K$ and complete stage-three expression rather than assuming every conclusion transfers.

## 3. Sampling scope and inactive cells

Restrict the initial study to the seven sampling rules in the proposed prompt. They are the chosen initial search family, rather than an assertion that only seven sampling rules exist.

Checkerboard sampling selects cells whose original grid coordinates have the same parity or opposite parity, then reindexes the selected cells on a square grid. The even/even, even/odd, odd/even, and odd/odd selections retain the specified coordinate parities directly.

| Method | Absolute selection relative to the original grid |
| -----: | ------------------------------------------------ |
|      1 | Whole grid                                       |
|      2 | Same-parity checkerboard sampling                |
|      3 | Opposite-parity checkerboard sampling            |
|      4 | Even/even                                        |
|      5 | Even/odd                                         |
|      6 | Odd/even                                         |
|      7 | Odd/odd                                          |

The parity pair refers to the first and second original grid coordinates in that order. Fix the original grid's origin and orientation. Give each method an exact selection and displayed-index mapping; specify the orientation of the 45-degree reindexing used for checkerboard sampling. Measure repetition in those displayed indices before stretching. Identify phases that give identical patterns, phases that only move or reorient a pattern, and phases that give distinct outputs.

Study the locations and proportions of cells whose numerical distinctions are lost at the pre-operation, pre-modulus, symmetric-combination, or post-modulus stage. Separate forced constant regions from parameter-dependent collapse and from similarities introduced only by a palette or quantization. A large post-power is not sufficient evidence of collapse when the arithmetic precision grows with it. The relevant inputs, operation families, and both modulus policies must be included.

For each method, describe which inactive regions are retained or removed and what visible bias the retained pattern is likely to exhibit. Keep proved numerical statements distinct from aesthetic interpretation. If none of the seven methods works adequately, record that limitation and whether further subsampling would be worth a later extension.

Existing foundations are [October 25, Sections 5.1, 7.4–7.7, and 8.4](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md): reachable-input exponent behavior, sampling phases and symmetries, and AND's power-induced annihilation.

## 4. Exact period and symmetry requirements

Keep the original domain $C$, pre-modulus $K$, post-modulus $M$, and requested smallest displayed axis periods separate. Preserving the original repetition domain means preserving the explicitly requested target in the stated sampling coordinates. The XOR baseline has period $C/2$ under its particular balanced rule; that formula is a reference result, not the definition of the target for the expanded pipeline.

For each specified construction, determine feasible target periods, feasible pairs $(K,M)$, and the admissibility conditions on its operation families. Find the relevant minimum moduli where they exist, and identify impossible requests. Do not assume that larger moduli always retain the target, that separate minima coexist, or that a later stage can recover distinctions already erased earlier.

Use smallest horizontal and vertical periods as the main generator contract. Record additional translations and a smaller oblique fundamental domain separately. The difference-depth theorem in [October 25, Section 6.1](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md) gives valid post-modulus intervals for a fixed integer construction, and Section 6.5 distinguishes the full translation lattice. Apply that theorem only after fixing the pre-modulus and all other arithmetic conventions. If an operation itself depends on the candidate post-modulus, account for that dependence explicitly.

Shared functionally even pre-operations supply strong centered symmetry guarantees under the earlier coordinate assumptions, but a sampling phase can exchange with another phase under a symmetry instead of preserving itself. Verify centered symmetries after selecting the sampling rule and phase. The relevant existing results are [October 25, Sections 7.2–7.4](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md).

The user's observations about odd pre-powers motivate their lower priority. They do not justify assuming those cases have no useful symmetry. Where inexpensive existing identities explain an observation or supply a counterexample to a blanket claim, record them without turning this secondary check into the main project.

## 5. Why the original uniform-sampling request needed revision

The first prompt sought uniform shift-class sampling after choosing the smallest period-preserving modulus for every post-operation. That space can still be infinite.

The concrete obstruction is the existing pre-power-two AND example at coordinate domain $C=64$ and fixed pre-modulus $K=64$, with the construction specified in [October 25, Section 8.5](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md). The combined inputs are exactly $0,16,32$. For every positive post-power $p$, the smallest post-modulus retaining axis period 32 is

$$
M_p=2^{5p+1}.
$$

The normalized outputs of its three fixed cell groups are

$$
0,\qquad\frac1{2^{p+1}},\qquad\frac12.
$$

The effective value denominator increases with $p$. These are infinitely many distinct shift classes, and even distinct affine classes. Choosing the smallest valid post-modulus for each power does not remove the infinity. Section 10.4 of the same report gives polynomial counterexamples, including an even-only family, so a degree bound alone is also insufficient in general. These are obstructions in their stated fixed-pre-modulus constructions; whether a particular obstruction remains after choosing a new minimum pre-modulus is a question for the expanded investigation.

For infinite shift-class families, keep those numerical distinctions available as an explicitly bounded option while investigating canonical selection among order classes. Where no such infinity arises, retain uniform sampling over the full finite shift-class set alongside the order-class target. Uniformity over shift classes and uniformity over one canonical representative per order class are different distributions and must be named separately.

For a fixed finite sampled domain there are finitely many possible ordered partitions of the cells. This explains why classification by order can eliminate precision-only infinity conceptually. It does not supply an efficient classifier, a realizability test, or a sufficient finite search cutoff. Establishing those results is part of the future research.

## 6. Spread preference and canonical selection

The user initially favored the smallest post-power in the AND example because it separated the output values better. The preferred spread score is the **minimum circular separation between distinct anchored output values**, considering all odd multipliers. For sorted distinct values $0=t_0<t_1<\cdots<t_{s-1}<1$, this is the minimum of adjacent gaps and the wraparound gap.

That score is an unweighted measure of distinct-value separation. Cell-group occupancy and the eventual color mapping are separate considerations. Ordering by itself does not determine the score, and an odd multiplier can change both the score and the ordering.

The discussion identified that a representative with the smallest parameter need not maximize separation within its order class. The polynomial family in [October 25, Section 10.4](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md) provided an example whose anchored values preserve their ordering while approaching more even spacing at higher precision. That report proves its infinitude; it does not prove a spread-optimization theorem. There is also no existing general theorem that the minimum post-power maximizes separation in every monomial family.

The user's accepted simplification is to avoid requiring that optimization. Seek a simple attainable representative of each order class instead. **At a chosen style-level pre-modulus, the working canonical policy is minimum post-modulus**, with minimum post-power as a tie-breaker for the monomial family. A further deterministic tie-breaker between remaining multiplier arrangements must be specified before defining a reproducible sampler. This is a practical low-precision preference, not a theorem of maximal visual separation. Cross-pre-modulus canonicalization requires the priority decision described in Section 2.

Minimum post-power and minimum post-modulus coincide in the particular AND family above, but not generally. Under the XOR rule $M=C2^{\nu_2(p)}$, powers 2 and 6 have the same modulus while power 4 has a larger one. Arbitrary stage-three expressions also have no single distinguished post-power to minimize. A precision-based preference extends more naturally across those families, but the two modulus choices must be kept distinct.

For the three-group AND example, anchoring the zero-input group gives two orderings after considering all odd multipliers. Both already have representatives at $p=1$, $M=64$:

| Anchored ordering                           | Multiplier | Values assigned to the original zero, sixteen, and thirty-two groups |
| ------------------------------------------- | ---------: | -------------------------------------------------------------------- |
| Zero group, sixteen group, thirty-two group |          1 | 0, 1/4, 1/2                                                          |
| Zero group, thirty-two group, sixteen group |          3 | 0, 3/4, 1/2                                                          |

This illustrates the intended canonical preference: infinitely many distinct shift classes are represented by two order classes at the smallest precision. It does not establish that minimum-modulus representatives can be found by the same rule in every construction.

## 7. Uniform selection and grouping pre-powers

The future investigation should state the sampling target for every result:

1. Distinct shift classes, retaining their numerical spacing: use the full attainable set when finite, or an explicitly bounded arithmetic policy when the full set is infinite.
1. Distinct order classes, each represented using the canonical precision preference.

For finite shift-class sets, determine how many shift classes belong to each order class. Check whether projecting a uniform shift-class sampler yields uniform order-class sampling; if the class sizes differ, derive the weights or independent coordinates needed for the latter target.

For the second target, establish which order classes are attainable and how to find their canonical representatives under the declared pre- and post-modulus policy. Investigate whether useful closed formulas, finite bounds, or constructive coordinates make uniform sampling possible. A finite observed catalogue is evidence at its stated bounds, not proof that a larger pre- or post-modulus introduces no new order types.

When combining pre-operation families, distinguish equality of functions modulo the chosen pre-modulus, equality of sampled combined tables, equality of attainable shift-class sets, and equality of sets of attainable order classes. Canonicalize functions rather than coefficient descriptions. Seek broad parameter conditions admitting a common period-preserving pre-modulus and useful symmetry, especially for polynomial families. A reduction preserving the pre-function is safe downstream, but later operations can create additional identifications.

Existing finite pre-power representatives and the roles of exponent size and valuation are given in [October 25, Sections 8.1–8.3](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md). Sections 9.1–9.3 provide polynomial-function normal forms and symmetry/permutation subfamilies at a fixed arithmetic modulus. Those results are foundations for family-level analysis; they do not determine the new minimum pre-modulus automatically.

Do not weight an overlap multiple times merely because it has several pre-power or combiner descriptions. Derive counts and sampling weights for new disjoint classes, or specify a deliberate style-conditioned distribution instead. The corresponding general sampling contract is discussed in Section 12 of the same report.

### No-pre-operation XOR baseline under order classes

Revisit the existing no-pre-operation XOR results using order-class equivalence alongside shift-class equivalence. Cover both a single post-power with odd post-multiplier and post-addition, and the polynomial post-operation spaces studied in the [November 2 report](../2026-11-02-xor-polynomial-period/2026-11-02-xor-polynomial-period.md), including the fixed-valuation spaces and their stated common-modulus constraints. Keep the existing coordinate, checkerboard sampling, modulus, and exact-period assumptions explicit when making the comparison.

Determine which existing conclusions carry over: the distinctions between odd and even powers, valuation and tail identifications, canonical parameter ranges, class counts at the user's usual field sizes, uniform samplers, and projection from master parameters to smaller domains. Identify which distinct shift classes merge into one order class and whether the existing representatives already give minimum-modulus order-class representatives. Separate conclusions about period and symmetry from conclusions about classification and sampling; a theorem about the former does not itself establish the latter.

For polynomial spaces, determine what information from the existing additive coordinates remains useful after passing to order classes. Do not assume that an order-class quotient inherits the additive structure, independent coordinates, or counts of the shift-class space. Report retained results, changed counts or sampling weights, and unresolved questions with references to the original statements. This is an additional research task, not a claim that the existing shift-class results already settle order-class equivalence.

## 8. Intended research outputs and unresolved work

The future report should provide, for each prioritized family of four-stage constructions and the seven chosen sampling methods:

1. A complete arithmetic, coordinate, anchor, and phase definition, using the full carryless product and absolute difference specified in Section 2.
1. Family admissibility conditions and a consistent pre-modulus where one exists, distinguishing the common family requirement from individual minima.
1. Reachable operand pairs and intermediate values, erased distinctions at each stage, retained inactive cells, and centered symmetries.
1. Feasible exact displayed periods, feasible pre/post-modulus pairs, and justified minimum choices, including impossibility results.
1. Finiteness results and canonical coordinates or samplers for the declared shift-class policy.
1. Attainable order classes and a justified low-precision selection method where available.
1. Safe grouping of pre-operation families and overlaps between styles, with counts that match the declared equivalence.
1. A comparison of the existing no-pre-operation XOR results under shift-class and order-class equivalence, including counts, canonical representatives, and uniform sampling where established.
1. Clearly separated proofs, exact finite checks, visual evidence, and remaining open questions.

Favor results that avoid enumerating enormous tables at the user's usual field sizes. The [November 2 XOR polynomial report](../2026-11-02-xor-polynomial-period/2026-11-02-xor-polynomial-period.md) is a useful model: it gives coefficient-level period criteria and independent coordinates where possible, and explicitly identifies broader cases requiring finite matrix calculations. Its XOR-specific criteria must be proved anew before applying them to other combiners or pre-powers.

The research tasks include minimum pre-moduli and family-wide feasibility, order-class classifiers and search bounds, reproducible tie-breakers, and a joint distribution across styles. Assess their resolution against the accompanying report. The pre-modulus policy fixes the basic-combiner minimum before post-operations are chosen; a larger shared family-level modulus must be declared as part of its style.

## Existing research to consult

- [October 11 post-power investigation](../2026-10-11-post-power/2026-10-11-post-power-range.md): coordinate-domain versus generation-size distinctions, exponent reduction, and phase refinements.
- [October 13 XOR theory](../2026-10-13-post-power/2026-10-13-xor-post-power-theory.md): the pre-power-one baseline, exact periods, and balanced modulus assumptions.
- [October 25 pattern-space theory](../2026-10-25-pattern-space/2026-10-25-pattern-space-theory.md): the general framework, pre-power and sampling results, infinite-family obstructions, and bounded polynomial procedures cited above.
- [November 1 XOR explanation](../2026-10-25-pattern-space/2026-11-01-xor-post-operations-explained.md): numerical examples and the distinctions between affine families, shift classes, and exact outputs.
- [November 2 XOR polynomial report](../2026-11-02-xor-polynomial-period/2026-11-02-xor-polynomial-period.md) and [November 3 examples](../2026-11-02-xor-polynomial-period/2026-11-03-xor-polynomial-examples.md): constructive exact-period results, count comparisons, and precision-dependent new components.
- [RISC-V bit-manipulation specification, Zbc extension](https://docs.riscv.org/reference/isa/v20260120/unpriv/b-st-ext.html): authoritative definition of carryless multiplication and the distinction between the full product and the portions returned by individual instructions. Section 2 includes the complete definition and a reference implementation.
