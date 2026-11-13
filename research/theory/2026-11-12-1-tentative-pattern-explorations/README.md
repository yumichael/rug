# Tentative pattern explorations

Tentative research collected from the November 10–12, 2026 chat: XOR pseudo-square symmetry, modulus selection, complete order-class sampling, and sampled even-pre-power families. This folder preserves an exploratory direction for possible future use. It does not select a generator design. Statements with proofs, bounded exact checks, and unresolved design or implementation questions are distinguished below.

## Scope and terminology

The displayed side is $N = 2^r$. Requested repetition means least horizontal and vertical periods $N$; extra oblique translations are separate information. XOR without pre-operations uses operand modulus $K = 2N$. Even-pre families write $q = 2^w u$ with $u$ odd and use a sampling-dependent $K$. The post-modulus is $M = 2^m$. These three quantities have different roles.

Pseudo-square symmetry here is the numerical condition $H(2N-z) \equiv H(z)\pmod M$ on odd XOR inputs. It gives square symmetry of the two mixed Cartesian parity components. Their centers are staggered when interlaced into the current vertical opposite-checkerboard display. The term does not assert a literal quarter-turn symmetry of the entire pixel array or characterize aesthetic resemblance.

A shift class identifies normalized numerical tables differing by a common circular color offset. An order class identifies their anchored rank tables. Equality geometry retains only the partition into equal-valued cell groups. Spatial translations, rotations, and reflections are not quotiented by these class definitions.

Minimum-period precision chooses the smallest $M$ attaining the requested axis periods for a fixed formula and $K$. A globally smallest modulus among all formulas representing one order class is an additional canonicalization problem. A value-preserving modulus instead retains a specified equality partition, sometimes with a further requirement to keep nonzero outputs nonzero.

## Reports and result inventory

| Report                                                        | Main results                                                                                                                                                                                                                           | Status                                                                                     |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| [XOR symmetry](xor-symmetry.md)                               | Necessary-and-sufficient reflection test; exact admissible-modulus interval; complete G(z(2N−z)) representation; even-polynomial guarantee when M_min ≤ 2N²; counterexample beyond that regime; derivative shortcut; spatial centering | Derived here with proofs and exact checks                                                  |
| [Fixed-modulus sampling](fixed-modulus-sampling.md)           | Independent centered-square Newton coordinates; exact coefficient ranges; linear period/minimum constraints; complete rejection-free M = 4N recipe; higher-precision shift/order collisions                                            | Derived here with proofs and bounded enumeration                                           |
| [Uniform orders across all minimum moduli](uniform-orders.md) | Complete matching-and-circular-order characterization; integer counting recurrence; direct uniform order sampler; polynomial realizations at minimum-period precision                                                                  | New combinatorial extension and research prototype, with proof and small exhaustive checks |
| [Precision policy](precision-policy.md)                       | Distinction-preserving M is an upper bound on minimum-period precision; all three selectors agree for the tail post family; concrete overshoots; fixed-precision XOR gallery corrections and counts                                    | Derived consequences and dated workbench observations                                      |
| [Pre-power families](pre-power-families.md)                   | OR tail equality geometry; adaptive cutoffs; zero occupancy; odd/odd group frequencies and exact valuation tail; derivative-controlled rank formula; later-tail counterexample; four-combiner collapse                                 | Derived refinements of existing valuation lemmas, with proofs and bounded exact checks     |

The new conclusions use background from the [November 2 polynomial-period report](../2026-11-02-xor-polynomial-period/2026-11-02-xor-polynomial-period.md), its [November 3 count comparison](../2026-11-02-xor-polynomial-period/2026-11-03-xor-polynomial-examples.md), and the [November 4 combiner and order-class report](../2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md). In particular, the isometry of the shared pre-twist, balanced monomial and same-valuation period results, interpolation allowance, and the general infinite-shift criterion are existing results. The reports identify where those are specialized or extended.

## Important boundaries

- Ordinary even post-polynomials can fail the complement symmetry at their actual minimum-period modulus. The complete centered-square representation and the low-precision corollary have different hypotheses.
- Shift/order equivalence holds for the older grid-filling families and for the lowest-modulus fixed-M construction here. For the unrestricted pseudo-square family, order classes are finite but shift classes are infinite at N ≥ 8.
- The earlier no-increase/2× comparison fixes an exponent valuation. It is not a count of all mixed-valuation pseudo-square patterns or of the union over all minimum moduli.
- The derivative simplification in the odd/odd OR tail applies to the named catalogue post family. A larger derivative valuation can delay it; a zero first derivative changes the leading term.
- OR tail equality geometry survives injective post-processing. Minimum-period precision alone permits mergers. Separate sampled panels can also use different pre-moduli, so literal interlacing requires fixed arithmetic and colors.
- The exact uniform order sampler targets rank classes. It does not give a uniform measure on perceived visual variety. Its representative construction is minimum-period for its own formula; globally smallest-modulus representatives remain a separate task.

## Reproducible evidence

Use the existing optional research environment from [development setup](../../../README.md#optional-python-research-tools). From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 research/interactive/.venv/bin/python research/theory/2026-11-12-1-tentative-pattern-explorations/verify.py
```

Add `--benchmark` to time $N = 1024$ order sampling on the current machine. The command writes [results.json](results.json) in this folder, or a path supplied with `--output`. It does not require a Jupyter kernel or modify app settings or Git state. NumPy and ruglab are used for the native cross-checks; the combinatorial sampler itself uses only the standard library.

The saved rerun covers 2,400 XOR symmetry examples, the 360-draw precision comparison, finite Newton-coordinate enumeration, pre-power partitions and derivative formulas, independent order enumeration through side 16, and 100 native polynomial realizations through side 32. The proof statements are not inferred solely from those checks. Coverage counts, source hashes, and optional machine timings are recorded in the JSON.

| File                                             | Purpose                                                                                               |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| [verify.py](verify.py)                           | Run the recorded check groups and regenerate results                                                  |
| [xor_checks.py](xor_checks.py)                   | Exact reflection depths, centered representatives, and native minimum-period counterexample           |
| [family_checks.py](family_checks.py)             | Precision policies, fixed-M coordinates, pre-power families, and combiner comparisons                 |
| [tail_modulus_checks.py](tail_modulus_checks.py) | Compare all three selectors in the erased-even-branch tail and check an outside-family counterexample |
| [count_orders.py](count_orders.py)               | Integer order counts and an independent small ordered-partition enumeration                           |
| [sampler.py](sampler.py)                         | Uniform order-class prototype; constructor takes p = N/4                                              |
| [realize.py](realize.py)                         | Integer polynomial interpolation and native cell/period verification                                  |

For example, from this folder:

```python
from random import Random
from sampler import Sampler

N = 1024
sampler = Sampler(N // 4)
rank, structure = sampler.draw(Random(0))
```

The rank tuple indexes the $N/2$ reduced scalar input classes, not the $N\times N$ rendered grid. The paired-node convention and complete uniformity argument are in [the sampler report](uniform-orders.md). The [post-square comparison image](xor-even-power-example.png) preserves the notebook example at two precisions.

## Continuation

The [numbered head-and-tail investigation](../2026-11-12-2-checkerboard-head-tail/README.md) extends this work to arbitrary post-polynomials and shared-family twists over general dyadic domains, with exact modulus criteria and uniform component-order samplers.

## Open directions

Independent mathematical review of the new completeness and combinatorial arguments would be useful before promoting this work into generator design. A production implementation would need API and persistence decisions, large-domain performance checks, and a representative-precision policy. Efficient globally canonical minimum-modulus realization for a sampled order class is unresolved here. Aesthetic selection among this much larger space is also a separate investigation.
