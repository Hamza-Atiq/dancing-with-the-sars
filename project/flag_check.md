# What are the other 268 flags? — check against optical images

**Status: rules written and committed on 15 Nov 2026 before any optical image for this check was downloaded.** Results go in a section below, without changing anything above it.

## Question

The frozen rule raised 270 flags in 22 pairs over the Langtang window; 2 are on the Langtang slope, 268 are unchecked (`docs/data/flags.json`, `project/results.md` section 5). Are they snow, ice, or something that could be ground movement?

## Data

NASA HLS (Harmonized Landsat Sentinel-2, 30 m), products HLSS30 and HLSL30, quality layer `Fmask` only. Fmask bits used: 1 cloud, 2 next to cloud, 3 cloud shadow, 4 snow/ice. The cirrus bit (0) is not used (unreliable over snow).

## Rules (fixed now)

1. **Flag box:** the flag's bounding box from `flags.json`, widened by 60 m on each side.
2. **Image for a radar date:** for each start and end date of a pair, the HLS scene within ±5 days whose flag box has the most clear pixels (clear = not cloud, not next to cloud, not shadow). A date counts only if at least 70% of the box is clear.
3. **Snow fraction s:** share of clear pixels with the snow/ice bit.
4. **Class of each flag** (first that applies):
   - **No image:** neither date has a usable scene.
   - **One date:** only one date usable (s reported, no class).
   - **Snow change:** |s(end) − s(start)| ≥ 0.3.
   - **Snow both:** s ≥ 0.5 on both dates.
   - **Snow-free both:** s < 0.2 on both dates.
   - **Mixed:** anything else.
5. **Lasting ice/snow:** s ≥ 0.5 in the clearest scene of 1 Oct – 15 Dec 2025 (end of the melt season). Used as a rough stand-in for glacier ice and permanent snow. It misses debris-covered glacier, which looks like rock.
6. **Look by eye:** 20 flags drawn at random (Python `random.Random(2026).sample`) from the 268, each shown on true-colour HLS before (autumn 2025) and after (autumn 2026). Each is put into one of: clean glacier or snowfield, debris-covered glacier, moraine or bare rock slope, vegetated slope, valley floor or river, other. The eye check comes after the automatic classes are written, and does not change them.
7. **Reading:** "snow change" flags are most likely surface effects. "Snow-free both" flags are the shortlist that could be ground movement (or atmosphere); they are not called movement.

## Limits known in advance

Snow can fall and melt between two optical images; 12-day radar pairs and ±5-day image windows do not line up exactly; monsoon cloud (June–September) will leave many flags with no image; Fmask confuses some bright rock and cloud with snow.

Script: `scripts/flag_check.py`.
