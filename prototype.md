# Rug generator prototype

Build a single-page HTML app in the `rug` folder that generates and exports rug images. Each image has a patterned central **field** surrounded by three rectangular rings: **inner guard**, **main border**, and **outer guard**, in that order. A **cell** is one output pixel, colored by an integer function of its coordinates. Preserve the existing diagonal, modular-arithmetic aesthetic while adding controls for field dimensions, pattern styles, borders, and coloring.

This specification is self-contained. Its reference is `generate_carpet_specs` in `symbols/maps1.ipynb`, together with the rendering functions in `symbols/maps.py`. The notebook supplies the field pattern and coloring; the border layout and rectangular field are new. Choices labeled “proposed” below resolve details the request leaves open.

## Field and border geometry

Let the field's shorter side be `S = 2^k`. Offer square and landscape rectangular fields, with dimensions `S × S` and `2S × S`. The dimension selector must show both integer dimensions and powers, for example `512 × 256 cells (2^9 × 2^8)`. Include choices through `k = 12`, giving a largest field of `8192 × 4096` cells. Proposed lower bound: `k = 3`, so the smallest field is `8 × 8`.

Let `W × H` be the field dimensions, `B` the main-border width, and `G` each guard's width. Require `G = B / 2` exactly and `B ≤ S / 2`. Interpret “field width” in the border limit as the shorter side, so the thickness constraint stays the same for both aspect ratios. All widths are integer cell counts. The total border thickness on each side is `G + B + G = 2B`, making the complete image `(W + 4B) × (H + 4B)`.

Proposed main-border choices are powers of two from `4` through `S / 2`. This makes both guards at least two cells wide and makes square pattern periods divide the relevant strip lengths. A two-cell main border is geometrically valid but gives one-cell guards, whose one-cell repeat would be a solid color; include it only if that result is useful.

Use nested, axis-aligned rectangular rings with square corners. The following cell classification fixes ring boundaries and prevents overlaps; `x, y` are coordinates in the complete output image:

```python
# Field begins at (2*B, 2*B); d is its outward Chebyshev distance.
u, v = x - 2*B, y - 2*B
d = max(-u, u - (W - 1), -v, v - (H - 1), 0)
region = ("field" if d == 0 else
          "inner_guard" if d <= G else
          "main_border" if d <= G + B else
          "outer_guard")
```

Proposed corner treatment: evaluate each ring's pattern over its entire enclosing rectangle and mask out its interior. Use that rectangle's top-left cell as the pattern origin. This produces corners from the same mathematical pattern as the straight portions, without separate corner ornaments or conflicting strip overlaps. A border's rotation is one rotation of this coordinate system; automatically turning motifs to follow each edge would be a separate design choice.

## Pattern calculation

The existing generator uses unmodified integer coordinates, combines them with bitwise XOR, applies a diagonal coordinate transform, raises the result to a positive integer **post-power**, and then applies channel-specific multiplication, addition, and modulus. “No pre-power” means the coordinates go directly into XOR; it is equivalent to pre-power `1`.

A crucial size distinction: the notebook's `n` is the side of the source coordinate grid. Both diagonal transforms return a square of side `n / 2`. Thus a `256 × 256` field reproducing the existing square calculation uses source size `N = 512`, not `256`.

The following mathematical reference replaces construction of the source array with direct evaluation. Here `i` is the output row and `j` the output column; all `%` operations return nonnegative residues. `centered` selects the notebook's `diag1m` instead of `diag1`. `pre` and `combine` select the pattern family.

```python
def combined_cell(i, j, N, centered, pre, combine):
    shift = N // 4 if centered else 0
    i, j = i + shift, j + shift
    u = (N // 2 - 1 + i - j) % N
    v = (-N // 2 + i + j) % N
    a, b = u**pre, v**pre
    return a ^ b if combine == "xor" else a | b

# p is the post-power; a_c, b_c are per-channel parameters.
z = combined_cell(i, j, N, centered, pre, combine)
r_c = (a_c * pow(z, p, M) + b_c) % M
```

The `-1` in the first coordinate is part of the original pattern and must be retained. The code uses mathematical integers: implement modular exponentiation rather than constructing enormous powers. Reduce pre-powers modulo the power-of-two channel modulus before bitwise combination when needed; only those low bits affect the output.

For the field, expose XOR with either **odd** or **even** positive post-powers, plus rotations `0°`, `90°`, `180°`, and `270°`. Retain both diagonal variants, with a selector or reproducible random choice. A rotation changes the sampled pattern coordinates while preserving the selected field dimensions.

Proposed rectangular extension: set `L = max(W, H)` and `N = 2L`, then take the central `W × H` window of the mathematical `L × L` diagonal image. Rotate that square coordinate domain before cropping. This retains the square implementation when `W = H` and gives the rectangle one coherent wider pattern. Extending a shorter-side square instead would naturally repeat it along the long side; that is another possible interpretation, but is not the proposed default.

The original random generator chooses an even post-power by drawing `q` uniformly from integers `1 ≤ q < N² / 32` and setting `p = 2q`. To add odd powers, a proposed matching sampler uses `p = 2q - 1`. Define `lowbit(p) = p & -p`, the largest power of two dividing `p`, and use `M = N * lowbit(p)` for the field. Larger post-power magnitude is not itself a reliable control for repeat frequency; its divisibility by powers of two matters.

## Border styles and natural repetition

Give the main border and each guard independent pattern settings. Each supports these families:

| Family | Coordinate pre-power | Combiner | Post-power |
| --- | --- | --- | --- |
| XOR | 1 | XOR | Odd or even |
| Squared OR | 2 | OR | Odd or even |
| Fourth-power OR | 4 | OR | Odd or even |

Each ring also supports all four rotations. Provide **Lock guard styles**, making the outer guard use the inner guard's complete pattern and color settings. Their placement origins remain local to their respective enclosing rectangles. Unlocking permits independent edits; the width relationship always remains fixed.

Each ring should contain a square motif whose side is its thickness: `T = B` for the main border and `T = G` for either guard. Prefer direct evaluation of a periodic integer function across the ring over copying a rendered square. This preserves the cell-based construction even if a cached tile is later used as an optimization.

A sufficient parameter rule for a period of `T` cells in both directions is:

```python
# T >= 2 is a power of two; N is a power-of-two multiple of 2*T.
M = 2 * T * lowbit(p)
# Use the same combined_cell and channel equation throughout the ring.
# With fixed parameters, for every cell:
color(i + T, j) == color(i, j)
color(i, j + T) == color(i, j)
```

This rule works for XOR without a pre-power and for OR with pre-power `2` or `4`. For XOR, shifting by `T` flips the same bit in both transformed coordinates modulo `2T`, which cancels in their XOR. For the two OR families, shifting a coordinate by `T` leaves its pre-powered value unchanged modulo `2T`. The subsequent power with exponent `p` preserves the required residue modulo `2T * lowbit(p)`. This guarantees a repeat period; individual parameter choices can have a smaller fundamental period or produce a weak motif.

To obtain repetition through post-power selection at a fixed power-of-two modulus `M`, choose an even exponent satisfying `lowbit(p) = M / (2T)`, when that ratio is an integer power of two at least `2`. For example, with `N = 512` and fixed `M = 1024`, a post-power with `lowbit(p) = 16` gives a guaranteed `32`-cell period while the source diagonal square is `256` cells wide.

Odd powers have `lowbit(p) = 1`. On odd XOR values they permute the residues at a fixed power-of-two modulus, so selecting a larger odd exponent cannot force a shorter period. Support odd border styles by reducing the modulus to `2T`, as in the general rule above. The practical interpretation of the request is therefore: prioritize natural mathematical repetition, choosing post-power divisibility when possible and adjusting the modulus when necessary.

Proposed ring source size: choose a power-of-two `N` at least twice the longer enclosing-rectangle dimension. Evaluate the whole ring with continuous local coordinates rather than resetting them at motif boundaries. The diagonal variants can coincide after the shorter-period reduction; if distinct phases are desired, add an explicit motif phase rather than assuming `diag1` and `diag1m` will always differ.

## Coloring

Migrate the active coloring behavior of `generate_carpet_specs`, with HSV as the initial mode. The existing generator supports RGB, HSV, and HSL, plus a single scalar channel sampled through a named colormap. Within each region, all channels share the pattern family, diagonal variant, post-power, and modulus. Each channel independently draws an odd multiplier `a_c` in `[1, M)` and an offset `b_c` in `[0, M)`.

Normalize the modular channel residue as follows:

```python
t = r_c / M
channel = t if channel_name == "H" else 0.5 + 0.5 * sin(2*pi*t)
```

Hue uses the linear mapping; RGB components, saturation, value, and HSL lightness use the sine mapping. Convert HSV or HSL triples to RGB after mapping. The original sine mapping nudges its result toward zero by one floating-point step, keeping the maximum below `1`; preserve that endpoint treatment where pixel parity matters. For PNG output, clamp channels and use a documented conversion to eight-bit values that cannot wrap `1.0` to zero.

The active generator varies all channels and uses odd multipliers. Its disabled branches for fixed channels and multipliers with additional factors of two are not needed for the initial migration. Notebook comments also suggest squaring mapped RGB values, but the active `generate_carpet_specs` does not do that; offer it only as an additional contrast option.

The scalar-colormap path optionally quantizes the mapped value to `d ≥ 2` equally spaced levels: `floor(t * nextafter(d, 0)) / (d - 1)`. The small downward adjustment preserves the original handling of exact bucket boundaries; require a positive level count of at least two. If included, provide explicit palette data in the HTML app instead of depending on Python's Matplotlib registry. A small curated palette set is sufficient for the prototype.

An optional alternative is [Inigo Quilez's procedural cosine palette](https://iquilezles.org/articles/palettes/), also implemented in [glsl-cos-palette](https://github.com/Erkaman/glsl-cos-palette). It colors one normalized scalar with four RGB vectors:

```glsl
vec3 palette(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
    return a + b * cos(6.283185307179586 * (c * t + d));
}
```

Here `a` sets the midpoint, `b` the amplitude, `c` the frequency, and `d` the phase of each color channel. Use a few named presets and clamp the result to `[0, 1]`. A shared palette across field and border can help the rug read as one composition, while independent region palettes allow stronger guard contrast. These palette additions are optional; the migrated coloring is the baseline.

## App behavior and implementation

Deliver a self-contained `index.html` with the controls and preview on one page. Generate in the browser. Provide field aspect ratio and size, main-border width, region style controls, guard locking, a seed, a Generate or Randomize action, and full-resolution PNG export. Show field and total output dimensions separately. Let users inspect a crisp, scaled preview without changing the underlying cell count.

Use a deterministic browser PRNG and save the resolved settings alongside the seed, preferably with JSON import/export. The same settings must reproduce the same image. Matching Python's NumPy random stream is a separate compatibility feature; the prototype needs to preserve the rendering equations and distributions, not produce identical parameter choices for a given Python seed. Keep control edits from silently rerandomizing unrelated region styles.

At maximum rectangular size and border width, the image is `16384 × 12288` pixels, approximately 768 MiB for one RGBA buffer alone. Render progressively or in a worker, avoid allocating the unused source grid and full-size intermediate channel arrays, and handle export allocation failures visibly. A reduced preview must sample the same cell function rather than substitute lower-resolution pattern parameters.

Use exact integer arithmetic for pattern calculation. JavaScript's ordinary bitwise operators truncate to 32 bits, and products in modular exponentiation can exceed the exact range of `Number`. BigInt is a clear correctness reference; an optimized implementation must produce the same residues. In particular, do not use floating-point `Math.pow` for modular powers. Cache periodic border work and use lookup tables where useful, while keeping the mathematical evaluator as the reference.

## Completion checks

Verify that a square field agrees with the reference coordinate and color equations for both diagonal variants; exercise odd and even XOR powers, both OR families, and all rotations. Confirm the exact field sizes, guard ratio, border limit, and ring boundary pixels. Check border period identities in both coordinate directions, including beyond the first square and across the source-grid wrap, and inspect the corners visually. Confirm guard locking, deterministic regeneration, and PNG dimensions. Compare optimized arithmetic against the integer reference and keep the page responsive during large renders.

The proposed choices to review before implementation are the lower size bound, power-of-two border widths, the centered rectangular crop, continuous ring corner treatment, and the scope of guard locking. They make the prototype implementable while leaving the requested pattern families, cell geometry, and coloring intact.
