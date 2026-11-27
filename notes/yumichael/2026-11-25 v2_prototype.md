# Rug studio v2 prototype

## Initial prompt

I want a completely revamped version of the rug app now, with incompatible saved settings compared to the original app, now under `legacy/`. I will spec out what the app should do differently by walking you through a user's experience as the use the app. Let's focus on the app being used on a web browser with a fair amount of screen space, e.g. maximized window on a computer, for now.

### Saved rugs

First, they will be able to choose a saved rug out of a list of saved rugs, some of which are built-in and cannot be deleted, some of which were added by the user and can be deleted. Even before the first-time user chooses a saved rug, the default first built-in saved rug be chosen. The saved rugs preview will have a (naturally small because it exists in a preview list) viewing area to display the rug in, with an option to zoom in to the rug. The saved rug list highlights (I'm envisioning more of a box highlight rather than a background color highlight) the currently loaded saved rug. On working with a saved rug to customize it, the currently loaded saved rug will note that there are unsaved changes. There is a "Save rug" button and a "Save new rug" button to save the current workspace's rug and pattern sampling settings to the saved rug list; overall UI options of the app is not saved. "Save rug" is disabled when the currently loaded saved rug was originally one of the built-in ones. "Save new rug" creates a prompt to enter a name for the saved rug.

### Customization

Now for the rug customization workbench. There is one section for global rug settings, then collapsible separate sections for further customizing each component of the rug.

#### Global rug settings

Under the global rug settings (not titled as a whole), there are the "Rug construction" and "Rug color style" sections.

##### Rug construction

Rug construction has the following options:

1. "Field shape". Same settings as supported in the legacy app, except now they're portrait orientation.
2. "Field dimensions". This is the same setting as used in the legacy app. The units will be in cells, not pixels. We will no longer have "Cell size": cell size will be locked at 2x and not informed to the user.
3. "Main border": a checkbox enabling the main border in the rug and its options in the UI to show up.
4. "Main border size". Same as legacy app, but this sticks across changing field dimensions as a ratio of the field dimensions when possible.
5. "Inner guard": a checkbox enabling the inner guard in the rug and its options in the UI to show up.
6. "Inner guard size". The whole inner guard's size. This is selectable this time, subject to logical size constraint to make the rug area fillable. Sticks as ratio of the main border size.
7. "Inner guard style": "Single", "Double", or "Children".
   - Guard styles explained:
     - "Single" is just one guard between the field and the border for the inner guard, like how it is for the legacy app.
     - "Double" is two guards of the same size, both 1/2 of the total inner guard size, called the **inner inner guard** and the **outer inner guard**.
     - "Children" is three guards, the middle one being 1/2 of the total inner guard size and the other two being 1/4. In order from inside to outside, they are called the **inner inner child guard**, the **inner parent guard**, and the **outer inner child guard**.
   - If the guard style is "Children", there is an additional option to "Mirror inner child guards". This makes it so that the outer inner child guard automatically takes on the style of the inner inner child guard styles.
8. "Outer guard": a checkbox enabling the outer guard in the rug and its options in the UI to show up.
9. "Make outer guard mirror inner guard". Same as the "Lock guard styles" in the legacy app. Hidden if "Outer guard" is unchecked. The inner and outer children are flipped when mirrored.
10. If "Lock guard styles" is not checked, "Outer guard size" becomes available as a dimension selector. Again sticks as ratio of the main border size.
11. If "Lock guard styles" is not checked, "Outer guard style" becomes available.
    - This is is the exact same options as with "Inner guard style". All the names in UI and in our documentation or code change accordingly, replacing "inner" with "outer" where appropriate.

##### Rug color style

This section allows the user to set a global color style for every component of the rug, overridable individually.

Just use the same settings as the legacy app's color settings. However, only keep RGB, HSV, HSL, OKLCH, and lose the "original" and "independent channels" tags. Also remove "Square RGB" (TODO: that's already covered by gamma, right?) and all of the hue offsets.

#### Component settings

Each of "Field", "Border", and the various guard pieces exclusively including only the most granular ones produced by the guard styles currently selected gets its own section with its name as title (in sentence case) if it's not disabled. Each section has a "Pattern style" section and a "Color style" section. These section UIs are shared between the components.

##### Pattern style

The user sets the pattern style, every changed setting of which immediately reflects in the shown rug pattern. Behind each component's pattern style there is a random 128-bit seed (TODO: is 128 bits a good size?) that remains unchanged unless the user rerolls the pattern. This seed allows the user to switch style families while maintaining a fixed pattern view for each different style family. The seed is not exposed to the user.

Let's walk through the option selections.

1. "Pattern family".
   - Options are:
     - "Checkerboard XOR even". Sample from no-pre-operation XOR using the uniform sampler that samples over odd-coefficient-sum polynomials without constant term, over each of the non-zero 2-valuation polynomials.
     - "Checkerboard XOR odd". Same as previous but over odd-power polynomials only.
     - "Checkerboard even pre-powers". Use the uniform raw equalities with IID levels samplers on OR XOR ADD ABSDIFF with even pre-powers and pre-twists.
     - "Odd-odd even pre-powers". Use the uniform raw equalities with IID levels samplers on AND OR XOR ADD ABSDIFF MUL (instead of MULT) CLMUL with even pre-powers an pre-twists.
   - Regenerates the pattern from the seed or load the saved pattern-style-specific advanced-customized pattern if switched.
2. "Pattern family details". Only shows up for the even pre-powers families.
   - Normal options are "OR" "XOR" "ADD" "ABSDIFF" for the checkerboard one and "AND" "OR" "XOR" "ADD" "ABSDIFF" "MUL" "CLMUL" for the odd-odd one.
   - Make this list a multi-select list instead of a single-select list, and add a "Select all" checkbox that deselects all when pressed again.
   - Each different multi-selection draws differently using the random seed, as each channel is allowed to draw from the entire multi-selected set of combiners independently.
   - Regenerates the pattern from the seed or load the saved pattern-style-specific advanced-customized pattern if the multi-selection is changed.
3. "Orientation". Only shows up for the checkerboard families.
   - Options are:
     - "Horizontally doubled".
       - If XOR, use checkerboard-opposite sampling with the orientation so that the doubling stretches horizontally (in the default portrait view).
       - If even pre-powers, use doubled-checkerboard-opposite sampling with the doubling stretching horizontally.
     - "Vertically doubled". Same as previous but stretches vertically instead.
     - "Diagonal".
       - If XOR, use even-odd or odd-even sampling.
       - If even pre-powers, use checkerboard-opposite sampling.
4. "Horizontal stretch". Determines the pixel-perfect stretch level of the pattern.
   - Default and minimum level reads as either "1×" or "2×" where the latter option is for the horizontally doubled orientation.
   - Zoom levels go up by powers of two until zoom is high enough that it becomes constant in the component.
   - This setting sticks as-is even when component dimensions from rug construction change.
5. "Vertical stretch". Same as horizontal stretch but vertical.
6. "Repetition unit size". Determines the axis-aligned repetition domain size.
   - Options stretch from whatever minimum dimensions are supported for the samplers all the way up to 65536 × 65536 cells.
   - When the component dimensions from the rug construction are changed, this changes accordingly by the same ratio while preserving the constant zoom.
   - Display not only the original cell dimensions but also the stretched cell dimensions and the relative dimensions as ratios of the component size. The label on the options and in particular the selected option may therefore change even if the pattern stays the same across another setting's change.
   - Regenerates the pattern from the seed or load the saved pattern-style-specific advanced-customized pattern if switched.
7. "Lock repetition unit size". Checkbox that locks the base cell size of the repetition unit even when other settings are changed.
8. "Symmetry center". No matter the pattern, the pattern phase will be aligned so that it retains exact rectangular symmetry through the exact center of the rug. There are however four choices for the center of symmetry of the pattern taken as a tesselation of the plane that can be placed in the center of the rug.
   - The options are:
     - "Corner". This is the center that's nearest to (0, 0) of the original, pre-sampling coordinates.
     - "Face center". This is the center that's nearest to the center of the domain span.
     - "Horizontal edge center". The horizontal edge's center as determined after grid sampling.
     - "Vertical edge center". Same as above but vertical edge.
   - Again, the pattern is always centered. Therefore we will not have the phase options.

Then there is a "Generate random pattern" button. This will generate a random seed and then create the pattern associated with that seed in the pattern style.

The rug gets a placeholder error notice if the pattern style is invalid due to out of range values.

There is a further collapsible "Advanced customization" section.

1. "Circular value phase". For each randomly sampled channel, let the user adjust the circular phase of the values in the chanel using a number in [0, 1).
2. "Color channel order". Use a UI that lets the user specify which randomly generated channel goes to which color channel. Maybe a drag and drop?

The advanced customization options remain in place if the pattern style is changed without needing regenerating the pattern from the seed. When the pattern style is changed requiring regenerating the pattern from the seed, the advanced customization options are remembered for when the pattern style comes back to the one used to set the advanced customization options. However, the advanced customization options are reset upon pressing "Generate random pattern" or any other operation that loads a new seed.

##### Color style

This has the same UI as the rug color style selection.
