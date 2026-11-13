# Research request

Source: [personal notes](../../../notes/yumichael/2026-10-00%20rug.md), latest substantive research section read on November 12, 2026. The trailing TODO list is separate. Inline plural notation is normalized for Markdown rendering.

Consider my observations from the last cell of the explore research notebook.

I want to scope my patterns of interest to just 1 collection: checkerboard-opposite sampling on OR, XOR, ADD, or ABSDIFF. Of these, there is a tail on the pre-twist pre-power depending on the domain size such that at the tail pre-power and greater, the four combiners almost have the same $M$ for each of the $M$-selection methods and have the same pattern. I want to know how to qualify the "almost" in the previous sentence and otherwise uniformly sample order classes and shift classes from this tail.

For the most visually appealing field size for checkerboard, 64x64, the tail starts at pre-power 10. The head, consisting of pre-powers 2, 4, 6, and 8, have these traits that I observed, but do not have proofs for:

- Pre-power 2 is always unique looking; pre-powers 6 and 8 many times look alike, and sometimes also alike with pre-power 4, though interestingly enough pre-power 4 the other half of the time looks more approaching the tail than pre-powers 6 or 8.
- The three $M$-selection methods often do not change the sampled $M$ for OR and XOR. For ADD and ABSDIFF, the catalogue $M$-selection and "Distinct outputs" also agree almost all the time, but "Minimum period" gives distinct, equally interesting patterns for ADD, whereas it seems to always be unavailable for ABSDIFF. I suspect a larger range of moduli between the ones available and possibly also outside could also give equally interesting patterns. FYI, My ideal pattern family is consistently spaced out across the $M$ range.

I also want to be able to uniformly sample order classes and shift classes from the head. But I want the eventual rug app user to be able to choose visually consistent families within the head collection to sample from. Splitting into all the combiners and pre-powers and moduli in the head might be too much. Investigate natural coarser groups in the head to sample from.

## Subsequent scope clarifications

The user requested general integer polynomials rather than only the gallery catalogue, and head results across a general reasonable range of domains rather than only 64×64. The reports therefore state results for every dyadic side at least eight, retain the shared difference-preserving pre-twist family, and run domain checks from 8 through 4096. The 64×64 complete-union example is a specialization.
