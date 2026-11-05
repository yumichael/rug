# Symmetric rug patterns with controlled repetition: research brief

Read [the research goal and decisions](research-goal.md) for the proposed investigation of shared pre-operation families, period-preserving pre- and post-moduli, symmetric combinations, sampling, and both shift classes and order classes. Study full shift-class sets where finite and canonical representatives of order classes in both finite and infinite shift-class cases. The initial combiners are AND, OR, XOR, ADD, MULT, CLMUL, and ABSDIFF.

The scope also includes checking which existing no-pre-operation XOR results carry over from shift classes to order classes, for both single-power affine post-operations and the studied polynomial spaces.

The brief defines all added operations within this repository. CLMUL uses the standard full carryless product, with its definition, example, and reference implementation included in the document.

This folder records the goal, existing evidence, decisions from the discussion, and remaining research questions. The proposed investigation has not started. Its four-stage model applies the same pre-operation to both coordinates, reduces the results by a selected minimum power-of-two pre-modulus, applies a symmetric combination that may use several intermediate results, and reduces the final result by a selected minimum power-of-two post-modulus. The original grid size and the two arithmetic moduli are distinct parameters. A main goal is to characterize useful families, including pre-polynomials, that can share one pre-modulus.
