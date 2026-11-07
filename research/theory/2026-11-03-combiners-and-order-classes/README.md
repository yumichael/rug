# Symmetric rug patterns with controlled repetition

Read [the research goal and decisions](research-goal.md) for the scope: shared pre-operation families, period-preserving pre- and post-moduli, symmetric combinations, sampling, and both shift classes and order classes. It includes full shift-class sets where finite and canonical representatives of order classes in both finite and infinite shift-class cases. The initial combiners are AND, OR, XOR, ADD, MULT, CLMUL, and ABSDIFF.

Start with [the explanation](explained.md) for the generator implications, then read [the November 4 research report](2026-11-04-combiners-and-order-classes.md) for proofs, exact examples, and the limits of the results. The report covers both shift and order classes, including their equivalence for balanced XOR monomials and valid same-valuation polynomial sums, common pre-moduli for an even pre-polynomial family, all seven sampling rules, finite odd-valued post-power catalogues, and a finite order-class search bound for unrestricted post-polynomials.

The brief defines all added operations within this repository. CLMUL uses the standard full carryless product, with its definition, example, and reference implementation included in the document.

The four-stage model applies the same pre-operation to both coordinates, reduces the results by a selected power-of-two pre-modulus, applies a symmetric combination that may use several intermediate results, and reduces the final result by a selected minimum power-of-two post-modulus. The pre-modulus is minimized by testing the immediate basic-combiner output for sufficient repetition room; later post-operations must attain the requested period exactly. The original grid size and the two arithmetic moduli are distinct parameters.

Run [the standard-library verification script](combiners_order_classes.py) to regenerate [the exact results](results.json). General proofs, bounded finite evidence, and unresolved classification or performance questions are distinguished in the report. The generator application is unchanged.
