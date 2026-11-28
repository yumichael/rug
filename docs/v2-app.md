# Rug studio v2

## Writing convention

**Bolded terms** are domain-specific terminology. "Quoted terms" are exact UI element names that show up for the user to see.

## Initial prompt

I want a completely revamped version of the rug app now, with incompatible saved settings compared to the original app, now under `legacy/`. I will spec out what the app should do differently by walking you through a user's experience as they use the app. Let's focus on the app being used on a web browser with a fair amount of screen space, e.g. maximized window on a computer, for now.

One thing I want to emphasize throughout the app is that the user should be able to freely experiment with settings and get back to patterns they liked without worrying too much about saving in between. I'll leave some of the finer details of the UI and behavior up to the implementer.

### Saved rugs

First, they will be able to choose a rug out of two lists, one for built-in rugs (which cannot be deleted), and one for user-saved rugs. Even before the first-time user chooses a rug, the default first built-in rug will be chosen.

Each entry in either list is called a **rug slot**. There is a **saved rug** associated with each slot, and a **rug draft** on top of it if the user has made unsaved changes. The **current rug** is the working rug in the currently selected slot. All the rug slots, including their drafts, will together be called the **rug workspace**.

The rug previews will have a togglable (naturally small because they exist in a preview list) viewing area to display the rugs in, with an option to zoom in to the rug. They show the drafts if there are any. The list highlights (I'm envisioning more of a box highlight rather than a background color highlight) the currently selected slot, and notes which slots have unsaved changes. Switching between rug slots preserves the unsaved changes made on top of each saved rug.

The built-in rugs are always shown in the order provided by the app. The user can reorder the rug slots in the user-saved list, e.g. with drag handles that work with both mouse and touch. Reordering doesn't change which slot is selected. User-saved rugs can also be renamed and deleted.

There is a "Save rug" button and a "Save as new rug" button to save the current rug and style settings; overall UI options of the app are not saved as part of a rug. "Save rug" is disabled when the currently selected slot is one of the built-in ones. "Save as new rug" creates a prompt to enter a name for the saved rug and selects the newly created slot in the user-saved list, leaving the old slot and its draft as they were. There is also a "Revert changes" action to discard the draft of a slot and go back to its saved rug.

### Customization

Now for the rug customization workbench. There is one section for global rug settings, then collapsible separate sections for further customizing each component of the rug.

#### Global rug settings

Under the global rug settings (not titled as a whole), there are the "Rug construction" and "Rug color style" sections.

##### Rug construction

Rug construction has the following options:

1. "Field shape". Same settings as supported in the legacy app, except now they're portrait orientation.
2. "Field dimensions". This is the same setting as used in the legacy app. The units will be in cells, not pixels. We will no longer have "Cell size": cell size will be locked at 2× and not informed to the user.
3. "Main border": a checkbox enabling the main border in the rug and its options in the UI to show up.
4. "Main border size". Same as legacy app, but this sticks across changing field dimensions as a ratio of the field dimensions when possible.
5. "Inner guard": a checkbox enabling the inner guard in the rug and its options in the UI to show up.
6. "Inner guard size". The whole inner guard's size. This is selectable this time, subject to logical size constraints to make the rug area fillable. Sticks as ratio of the main border size.
7. "Inner guard construction": "Single", "Double", or "Triple".
   - A **guard** consists of one or more **guard bands**. From the field going outwards there is the inner guard, the main border, then the outer guard (whichever of those are enabled).
   - Guard constructions explained:
     - "Single" is just one guard band, like the guard for the legacy app.
     - "Double" is two guard bands of the same size, both 1/2 of the total guard size, called the inner band and the outer band.
     - "Triple" is three guard bands, one being 1/2 of the total guard size and the other two being 1/4 each. In order from inside to outside, they are called the inner band, the middle band, and the outer band.
   - For "Triple" there is a "Wider band" option with the options "Inner", "Middle", and "Outer", defaulting to "Middle".
   - There is also a "Mirror inner guard bands" option for "Triple". This makes it so that the outer band of the inner guard automatically takes on the pattern and color styles (including the actual pattern) of its inner band. The widths of the bands are still determined by the guard construction.
8. "Outer guard": a checkbox enabling the outer guard in the rug and its options in the UI to show up.
9. "Mirror inner guard". This is under the outer guard settings and mirrors the entire inner guard to the outside of the main border, including its size, construction, patterns and color styles. The inner and outer bands (and which one is wider) are flipped when mirrored. Hidden if "Outer guard" is unchecked.
10. If "Mirror inner guard" is not checked, "Outer guard size" becomes available as a dimension selector. Again sticks as ratio of the main border size.
11. If "Mirror inner guard" is not checked, "Outer guard construction" becomes available.
    - This has the exact same options as "Inner guard construction", including its own "Wider band" and "Mirror outer guard bands" options.

The guards can still be enabled when the main border is disabled, with their sizes based on the retained main border size setting. Only allow guard sizes that can be subdivided into whole cells as dictated by the construction (e.g. multiples of four for "Triple"). I want the intended size ratios to be remembered, so rounding of the dimensions when resizing the field doesn't cause the ratios to drift as the user changes the field size back and forth.

When the user disables a component, changes a guard's construction, or enables mirroring, retain the settings of the components that are no longer independently visible so that they can be brought back when the user switches back. Give newly available bands sensible default settings if they haven't been configured before.

##### Rug color style

This section allows the user to set a global **color style** for every component of the rug, overridable individually.

Just use the same settings as the legacy app's color settings. However, only keep RGB, HSV, HSL, OKLCH, and lose the "original" and "independent channels" tags. Also remove "Square RGB" (it's covered by gamma; extend the lower end of the gamma range to 0.1) and all of the hue offsets.

There is also a "Copy color style from…" button. This opens up a UI to copy a color style from a component of any rug in the workspace, including the current rug. The rug color style counts as a source of color style as well.

#### Component settings

Each of "Field", "Main border", and the various guard bands gets its own section if it's enabled. I'm envisioning that the bands for a subdivided guard are grouped under "Inner guard" or "Outer guard" so that they can simply be titled "Inner band", "Middle band" or "Outer band" in their respective groups. For a single-band guard the guard itself is the component. If a component is set to mirror another component, it still gets its own section, but with a placeholder explaining that it's locked and which component it's mirroring, like in the legacy app.

Each independently configurable component has a "Pattern style" section and a "Color style" section. These section UIs are shared between the components.

##### Pattern style

The user sets the **pattern style**, every changed setting of which immediately reflects in the shown rug pattern. Behind each component's pattern style there is a random 128-bit **pattern seed** that remains unchanged unless the user rerolls the pattern. This seed allows the user to switch style families while maintaining a fixed pattern view for each different style family. The seed is never exposed to the user.

I'll call the actual mathematical channel mappings drawn from the seed (including any overrides to those mappings) the **pattern realization**. Some of the pattern style settings determine which realization is drawn from the seed, while others simply determine how that pattern is used spatially. When the former settings change and then change back, the same realization should be drawn again.

Let's walk through the option selections.

1. "Pattern family".
   - Options are:
     - "Checkerboard XOR (even)". Sample from no-pre-operation XOR using the uniform sampler over the union of the non-zero 2-valuation families. Each sampled polynomial has no constant term, an odd coefficient sum, and all its nonzero terms have exponents of the same positive 2-valuation (which can vary from one sampled polynomial to another).
     - "Checkerboard XOR (odd)". Same as previous but with the 2-valuation of the exponents fixed at zero, i.e. odd-power polynomials only.
     - "Checkerboard even pre-powers". Use the uniform raw equalities with IID levels samplers on OR XOR ADD ABSDIFF with even pre-powers and pre-twists.
     - "Odd-odd even pre-powers". Use the uniform raw equalities with IID levels samplers on AND OR XOR ADD ABSDIFF MUL (instead of MULT) CLMUL with even pre-powers and pre-twists.
   - Regenerates the pattern from the seed or loads the saved pattern-style-specific advanced-customized pattern if switched.
   - It would be nice to have some short explanations of the visual characteristics of the families, maybe with a little example preview of each.
2. "Combiners". Only shows up for the even pre-powers families.
   - Normal options are "OR" "XOR" "ADD" "ABSDIFF" for the checkerboard one and "AND" "OR" "XOR" "ADD" "ABSDIFF" "MUL" "CLMUL" for the odd-odd one.
   - Make this list a multi-select list instead of a single-select list, and add a "Select all" checkbox that deselects all when pressed again. A selection with no combiners isn't a valid pattern style.
   - Each different multi-selection draws differently using the random seed, as each channel is allowed to draw from the entire multi-selected set of combiners independently. Sample uniformly over the deduplicated union of raw equality partitions for the selected combiners, as in the pooled combiner research.
   - Regenerates the pattern from the seed or loads the saved pattern-style-specific advanced-customized pattern if the multi-selection is changed.
3. "Pattern orientation". Only shows up for the checkerboard families.
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
   - Stretch levels go up by powers of two until the stretch is high enough that it becomes constant in the component.
   - This setting sticks as-is even when component dimensions from rug construction change. When changing orientation, preserve the user-selected stretch multiplier relative to the orientation's native stretch, so that switching back restores the original stretch.
5. "Vertical stretch". Same as horizontal stretch but vertical.
6. "Tile size". A **pattern tile** is a fundamental repeating region of the pattern. Depending on the sampling and orientation it can be rectangular or diamond-shaped. Its **tile size** is the size of the smallest axis-aligned rectangle containing the tile (the least horizontal and vertical periods), in cells before stretching.
   - Expose the **tile shape** to the user, e.g. with a little rectangle or diamond symbol next to the tile size. This is informative, not independently selectable. The sampling algorithms give each channel the selected least axis periods.
   - Support power-of-two tile sizes all the way from 1 × 1 cells up to 16384 × 16384 cells (2^14 per axis). Do additional mathematical research as needed to make all the sampling methods work for the small domains, including sizes below 8 × 8. A 1 × 1 tile is just a spatially constant random channel. Where the existing construction cannot attain a requested small tile size, come up with a mathematically natural extension of that sampler, retaining the intended symmetry, exact axis periods and sampling distribution where possible.
   - When the component dimensions from the rug construction are changed, this changes accordingly by the same ratio while preserving the constant stretch. Remember the intended ratio so that changing the dimensions back and forth doesn't cause the tile size to drift.
   - Display not only the original cell dimensions but also the stretched cell dimensions and the relative dimensions as ratios of the component size. The label on the options and in particular the selected option may therefore change even if the pattern stays the same across another setting's change.
   - Regenerates the pattern from the seed or loads the saved pattern-style-specific advanced-customized pattern if switched.
7. "Lock tile size". Checkbox that locks the base cell dimensions of the pattern tile even when other settings are changed.
8. "Symmetry center". No matter the pattern, the pattern phase will be aligned so that it retains exact rectangular symmetry through the exact center of the rug. There are four possible symmetry centers for a rectangular tile.
   - The options are:
     - "Corner". This is the center that's nearest to (0, 0) of the original, pre-sampling coordinates for a rectangular tile.
     - "Tile center". The center of the tile.
     - "Horizontal edge center". The horizontal edge's center as determined after grid sampling.
     - "Vertical edge center". Same as above but vertical edge.
   - For diamond tiles there are only two distinct choices, "Corner" and "Tile center", with the canonical diamond placed consistently relative to the original sampling coordinates. For "Checkerboard XOR (even)" only expose these two choices regardless of the tile shape, as the patterns in this family tend to have approximately square symmetry. For degenerate small tiles there may be even fewer meaningful choices.
   - Again, the pattern is always centered. Therefore we will not have the spatial phase options.

Try to keep the settings valid in the first place, but if the pattern style is invalid due to out of range values or an empty combiner selection, show a placeholder error notice for the affected component without unnecessarily hiding the rest of the rug.

Then there is a "New pattern" button. This will generate a random seed and then create the pattern associated with that seed in the pattern style. There is also a "Copy pattern from…" button to copy a pattern from another component of any rug in the workspace (see copying below).

There is a further collapsible "Advanced pattern settings" section.

1. "Channel phase". For each randomly sampled channel, let the user adjust the circular phase of the values in the channel using a number in [0, 1).
2. "Channel assignment". Use a UI that lets the user specify which randomly generated channel goes to which color channel. Since there are only six permutations, this could be as simple as a dropdown. The channel phases follow the sampled channels when their assignments are changed.

The advanced customization options remain in place if the pattern style is changed without needing to regenerate the pattern from the seed. When the pattern style is changed requiring regenerating the pattern from the seed, the advanced customization options are remembered for when the pattern style comes back to the one used to set them. However, the advanced customization options (including any remembered pattern overrides) are reset when generating a new seed for that component. Copying or restoring a pattern brings along the corresponding overrides instead.

##### Color style

This has the same UI as the rug color style selection, but with a "Use rug color style" checkbox. If the component has never had its own color style, unchecking it initializes its own style to the current rug color style. Remember the component's own style when the checkbox is checked again, so that the user can switch back and forth.

##### Resetting and reverting settings

I want the user to be able to reset or revert individual sections without having to revert the whole rug. I'm envisioning a little action menu in the section headers for "Rug construction", "Rug color style", and each independently configurable component's "Pattern style" and "Color style".

- "Reset pattern style" restores the default pattern style settings for that component, keeping its seed and its remembered pattern overrides and advanced settings.
- "Revert pattern style" restores the component's pattern style as it was in the saved rug, including the seed, actual pattern and remembered overrides.
- "Reset color style" restores the default color settings for the currently selected color space, keeping the color space selection. For a component, this resets its own color style without changing whether it uses the rug color style.
- "Revert color style" restores the color style as it was in the saved rug, including whether the component uses the rug color style.
- "Reset rug construction" and "Revert rug construction" similarly restore the default and saved rug construction settings, respectively.

There is also a "Reset advanced pattern settings" action in the "Advanced pattern settings" section. This resets the channel phases to zero and the channel assignment to the default for the current pattern realization. It doesn't change the underlying mathematical mappings or the remembered advanced settings for other realizations.

If there's no corresponding component in the saved rug, don't offer a revert action for its settings. All of these reset and revert actions are undoable through edit history, so there's no need for confirmation dialogs.

##### Copying patterns and color styles

The copying UI should let the user pick a rug and one of its components (it would be nice to be able to do the latter by clicking on the component in a preview of the rug). For a rug with unsaved changes, default to the draft but include a toggle to copy from the saved rug instead.

"Copy pattern from…" copies the pattern seed and all of the pattern style settings, including the mathematical realization and any remembered overrides, but not the color style. Preserve the absolute tile size and stretch even if the destination component is a different size, enabling "Lock tile size" in the destination.

"Copy color style from…" copies the source's effective color style, making it an independent color style if copying to a component. When copying from a component that mirrors another component or inherits the rug color style, copy the effective settings. These are copies, so subsequent changes to the source don't change what was copied.

### New rug

There is a "New rug" button always visible at the bottom. This button generates new seeds for each component from a master seed, letting each component be redrawn with a pattern derived from the seed, but preserving the non-seed-derived pattern style settings and color styles. It makes the seed changes on top of the current rug slot as unsaved changes.

I want to be able to lock individual component patterns (e.g. with a little lock icon in their section headers) so that if I particularly like the field and inner guard, I can keep pressing "New rug" to experiment with the other components. The lock only affects generation through "New rug"; the user can still use "New pattern" for a locked component. Mirrored components follow the component they're mirroring.

### Rug view

The legacy app's rug view is just about good as it is. Instead of "Rotate rug", we'll have "View orientation" with options "Portrait" and "Landscape"; we default to portrait. View orientation is disabled when the rug is a square.

### History

There are two types of histories.

#### Generation histories

One is the histories that track the previously generated patterns and rugs along with their settings at the time of generation. There are two places for these histories.

##### Rug generation history

"Rug generation history" brings up a view similar to the saved rugs view but it has the rugs as they were right after the "New rug" button was clicked, across any slot in the workspace. Selecting one of these past rugs will put the rug and style selections exactly as they were at that point, on top of the current rug slot. These past rugs are labelled by the count of the number of times the user has pressed "New rug", prefixed by "R", a symbol marking that it's the new rug.

##### Pattern generation history

"Pattern generation history" acts similarly as the rug generation history does, except it tracks the patterns actually generated for a component when either the "New rug" button or the "New pattern" button was pressed. These UI elements go under each component's customization section. Let the user choose whether to restore just the pattern (default) or also the color style as it was at the time the pattern was generated. These past patterns are labelled by a generation counter separately for each component, prefixed by an abbreviation of the component name to distinguish them from each other and the global rug generation history. Make sure the abbreviations for the various guard bands don't conflict with each other.

#### Edit history

This saves a stack of editing actions. For each rug editing action there is one affected rug slot; store its rug and style settings before and after the action, along with the relevant overall app UI state. Switching rug slots or changing the rug view does not itself create a return point, but the app UI state is remembered at the return points. Like the browser, upon going back in history, the user can return forward still, but if they perform a new editing action, the forward part of the stack gets lost.

Going back or forward for a rug editing action selects the affected rug slot and restores its draft and the remembered UI state. The other rug slots' drafts are unaffected. Returning to a previous point does not undo rug saving; it restores the working settings on top of whatever is currently saved in that slot.

Deleting, renaming and reordering user-saved rug slots are also editing actions that can be undone and redone. In particular, undoing a deletion should restore the entire slot, with the same identity, name, saved rug, draft and position in the list, so we can still undo the editing actions that came before the deletion. Importing additional rugs is also an undoable action, preferably as a single action even when importing several rugs.

"Save rug" and "Save as new rug" are not themselves undoable. Restoring something from a generation history, resetting settings or reverting changes is a rug editing action. Undoing a generation does not remove it from the generation history. Group continuous slider changes and the like into a single editing action rather than putting every intermediate value into the stack.

### Persistence

#### Autosave

The generation histories and the entire workspace state are autosaved in browser storage, as are the app's UI preferences and (within reasonable storage limits) the edit history. I'd favor IndexedDB for this given the amount of data the app might end up keeping. Avoid storing full-sized rendered images in the histories and put some sensible limits on the storage used by the histories. Let the user know if autosaving fails.

#### Exporting

##### Workspace state export

There are "Export workspace", "Import workspace", and "Import rugs" actions for saving to and loading from the user's filesystem. Possibly combine the two import actions into a common file picker and let the user choose whether to add the rugs or replace the workspace. I want this to work conveniently on both the computer and the phone.

The workspace save file will have the `.rugs` extension. Save the user-saved rug slots in order, including their saved rug and any unsaved draft changes, and remember which slot is selected. The built-in rugs are handled specially as described below. The same format can be used for a file containing just one rug or several rugs, and the import rugs action should allow the user to choose multiple files if possible. The edit history and overall UI preferences are local to the app, and the generation histories can be kept local as well.

The app has a current list of built-in rugs, each with a permanent identifier. Keep an archive of the definitions of all past built-in rugs as well; a built-in identifier always refers to the same rug definition (give a revised built-in rug a new identifier if its definition changes). In the save file only the permanent identifier is needed for a built-in rug with no draft, and for one with a draft also save the draft on top of it. User-saved rugs have their saved configurations included in the file.

"Import workspace" overwrites the workspace state and starts a new edit history. A confirmation dialog pops up before overwriting unless the workspace is in a completely untouched fresh state with no unsaved changes (but possibly with view changes).

When loading a workspace, the built-in list always contains the app's current built-in rugs in the order provided by the app. Restore any drafts from the file for the built-ins that are still current. If there are built-in identifiers from the file that are no longer in the current built-in list, bring those rugs into the user-saved list using their archived definitions, keeping any drafts on top of them. This way the user still has access to the old built-in rugs as well as the newest ones.

"Import rugs" lets the user add rugs from a save file to the user-saved list without touching the existing slots. For a built-in from the file that is still a built-in of the app, only bring it into the user-saved list if it has a draft change. For a retired built-in, bring it into the user-saved list using its archived definition even if there are no draft changes. Preserve the relative order of the rugs being added.

When importing rugs, if the name and saved rug of an incoming slot are identical to those of an existing slot, and the incoming slot has no draft change, skip that slot regardless of whether the existing slot has a draft change. If the incoming slot does have a draft change, add it as a separate user-saved slot with the draft and append a name deduplication suffix to the name (e.g. the first available suffix starting with " (2)"). Use the suffix for other name conflicts as well. Importing rugs never overwrites a slot or its draft.

##### PNG export

There is an "Export PNG" button to save the entire current rug as a PNG file, keeping the current portrait or landscape view orientation, at the usual 2× cell size. The size of the PNG isn't affected by preview zoom, the screen size, or the device pixel ratio.

### UI layout

#### Landscape layout

On a computer or a phone with enough screen space, we can keep the UI layout much the same as in the legacy app. The global rug settings and component settings can stay on the left pane. The saved rugs and edit history can go on top. The biggest change is that I want the rug generation history and new rug button to go below the rug view.

#### Portrait layout

We can convert the landscape layout to a portrait layout in the same spirit as how the legacy app does it. There are two key behaviors I want in addition. When the user scrolls down to show the rug view, as the user scrolls further down to reveal the customization settings, the rug view should shrink a little to make room, but push everything above it out of view so the rug view remains at the top. The smaller rug view should always remain at the top so that the user gets instant feedback whenever they change the settings. The second behavior I want is that the rug generation history and new rug button should always show up at the very bottom. This way the simplest ways the user can interact with the app are always kept visible: the rug view and the new rug button.

Choose between the two layouts based on the available width and height of the window (a landscape phone might not actually have enough height for the landscape layout). Make the pinned preview expandable/collapsible by the user, and make sure the bottom controls fit within the phone's safe area. On the computer, it would be nice to have keyboard shortcuts for "New rug", undo, redo and "Save rug".

### State format

I give the implementer freedom in choosing the very nitty-gritty details of the save-file format. There are just some requirements I have.

Give the rug slots stable identifiers independent of their names and positions in the lists. Use a deterministic, versioned RNG for the sampling, and generate fresh 128-bit seeds using the browser's random number generator. Derive component seeds from the master seed using stable component identifiers, and use independent random streams for the channels. Treat the multi-selected combiners as a set when deriving the draw. Store component seeds individually as they can be rerolled independently.

I want saved rugs to continue to give the same patterns when the app gets updated. Account for changes to the save-file schema, sampling algorithms, and rendering/color conversion independently as needed to preserve the saved realizations and their appearance.

The file format should be able to support pattern mappings that are not generated with a seed. To see how this works, consider converting one of the legacy app's save settings into a single-rug workspace in the new app. Each of that rug's component patterns will not be drawn from the new random generation algorithm. That's ok. We will configure a random master seed and generate random component seeds. But then for the compatible pattern style settings in each component, we will calculate the equivalent specifications for that pattern in the new app's language (e.g. converting polynomials to the IID levels) and add that as a saved override in that seed-draw view, in the same way the advanced customization does. Treat these explicit mappings as first-class pattern realizations, even when they can't be obtained by sampling from the chosen seed.

For the larger tile sizes, avoid materializing the entire tile if possible. Ideally use implicit representations and evaluate the parts of the tile that are actually needed for the rug, including generating the IID equality-class values lazily where applicable. Make sure expensive sampling and rendering work doesn't block the UI. Do the mathematical and computational work needed to determine how best to implement the samplers at the supported sizes.
