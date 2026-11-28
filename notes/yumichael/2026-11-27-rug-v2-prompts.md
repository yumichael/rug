# Rug v2 prompts

Read the v2 app spec and review it, see if I'm missing anything or if it can be improved. I'm also open to rethinking any of the quoted or bolded terminology I came up with.

---

Oh yes: for some of the pattern families, the tile is diamond oriented instead of rectangle. That fact should be exposed to the user. The size of the tile should still be the smallest containing rectangle though.

---

Wait, the symmetry centers must have different names if the tile shape is diamond.

---

~~For edit history, I also forgot to mention, group changes in the exact same UI component. I.e. if I keep adjusting saturation, no matter how many times I adjust it, it only counts as one edit.~~

---

I'm not a big fan of "guard arrangement". I think I would prefer **guard construction**. Do you think that works?

I want an option to change which of the triple style guard bands is the bigger of the three.

Make XOR (even) have only two symmetry centers, because it approximately has square symmetry instead of rectangle symmetry.

Copying patterns and color styles edge cases, some clarifications:

- Copy from a saved rug with unsaved changes: include a toggle button to copy from saved rug instead of current draft.
- Copy a pattern into a differently sized component: yes, preserve, especially noting to use the lock tile size option.

History decision clarifications:

- Deleting a rug with edit-history entries: let's actually put the deletion in the stack so the user can recover deleted rugs as well through undo.

When the user imports rugs from a workspace and the workspace being imported from has a rug slot whose name and saved rug is identical to one already in the current workspace, what should be done depends on whether the workspace being imported from has a draft change at that slot. If there is no draft change in the workspace being imported from, skip importing that slot, even if in the working workspace there is a draft change in that matching slot. If there is a draft on top of that slot in the workspace being imported from, import it, automatically append a name deduplication suffix to the name.

We can change the max tile size to 2^14 to be more conservative.

For PNG export, just always export at the usual 2× cell size.

Request the sampling algorithms to do some work to make all pattern sampling methods work even for overly small cell dimensions, like below 8 × 8 all the way down to 1 × 1.

What do you think?

---

There needs to be an outer and an inner version of "Mirror flanking bands".

---

Forgot to say, let's support reordering rug slots.

---

Wait, if we can reorder built-in rugs, will we save the built-in rug settings in the save files, even if they don't have drafts on them?

---

I think I would prefer to separate the built-ins list from the user-saved list. That way loading an old workspace still lets the user look at the newest built-in rugs. The built-in rugs will only be specified by their permanent identifier in saved files if there is no draft on top of them, taking up less space. The app remembers all past built-in rugs, so loading or importing rugs from an old workspace will populate the saved rugs with the old built-ins, now as user-saved rugs.

---

Great. I like everything you proposed, with my requests on top. Can you make a pull request to edit the spec for the v2 app to include all the things we covered in this chat? I moved the doc to under `docs/`. Try to keep the writing style similar to what's already in the doc (I wrote it by hand). While I say it's a spec, it's not meant to be an airtight behavioral contract; it leaves some choices up to the implementer.

---

Actually, I don't want the built-in rugs to be reorderable.

---

~~About "Give newly available bands sensible default settings if they haven't been configured before." Actually, since all user created rugs branch off of some built-in rug save, this just means that the impl~~

---

"Each of "Field", "Main border", and the various guard bands gets its own section if it's enabled and independently configurable." Let's actually have a placeholder section explaining that the component is locked if it's set as mirroring another component and therefore not independently configurable, just like in the legacy app.

---

"It would also be nice to have ways to reset individual pattern and color settings without having to revert the whole rug." Make this a requirement. Let's discuss how this will work before you edit the PR.

---

I think there should be only two choices for each section. The behaviors in the current PR works perfectly as it is. The only thing I think needs changing is the naming. Can you change the naming so that the expanded scope of the reverts is clear?

---

I don't like how for copying patterns and color styles one has to do it twice if they want to copy both pattern and color style. Suggestions?

---

You have "rug color style", both unquoted and quoted and capitalized. It is confusing to understand what the unquoted "rug color style" is exactly referring to.

---

"it would be nice to be able to do the latter by clicking on the component in a preview of the rug": I just want to note that I want the user to be able to copy from guard components that are not included in the active guard construction. The user might want to do this for example when copying the middle band from the same rug slot's single guard.

---

"Possibly combine the two import actions into a common file picker": Yes, I want them combined.

---

"For a retired built-in, bring it into the user-saved list using its archived definition even if there are no draft changes." only if it either has a draft or it doesn't already appear as an identically defined saved rug among the user-saved list. In other words just treat it as a user-saved rug.

---

"a landscape phone might not actually have enough height for the landscape layout" How is this possible? Doesn't the landscape view demand less vertical space than the portrait view to look good?

---

"Use a deterministic, versioned RNG for the sampling, and generate fresh 128-bit seeds using the browser's random number generator." I don't want to be confused here: you're saying the random value derivations from the seed should be code we write ourselves, and versioned, but the seed picking can come from the browser?

---

**Changes checklist (for me to go through manually only).**

1. Concept of a draft. DONE
2. Missing saved-rug operations. DONE
3. Global color style inheritance. DONE
4. Locking component patterns when using "New rug". DONE
5. Let the user see the source rug and select its individual components visually. DONE
6. Restore pattern only instead of necessitating restoring color style as well. DONE
7. I would not mandate `localStorage` as the underlying persistence mechanism. DONE
8. Provide convenient resets for individual pattern and color settings. DONE
9. Extend supported cell dimensions down to 1 × 1. DONE
