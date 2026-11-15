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

## Results (run once, 15 Nov 2026; `data/flagcheck/flag_check_table.txt`, `data/flagcheck/flag_check.json`)

All 205 HLS scenes used come from one tile (T45RUM). 268 flags are not on Langtang.

| Class | Flags | On lasting ice/snow | Not on lasting ice/snow | No autumn image |
|---|---:|---:|---:|---:|
| Snow change | 5 | 4 | 1 | 0 |
| Snow on both dates | 23 | 17 | 2 | 4 |
| Mixed | 5 | 1 | 4 | 0 |
| **Snow-free on both dates** | **32** | 1 | 31 | 0 |
| One date only | 93 | 55 | 33 | 5 |
| No image | 110 | 66 | 20 | 24 |

- **Only 65 of 268 flags (24%) could be classed** with a clear image on both dates. Cloud is the main reason: most monsoon flags (June–September) have no usable image, and steep shaded slopes are often marked as shadow.
- **Of the 65:** 28 are snow-covered or had a snow change (43%); 32 were snow-free on both dates (49%); 5 mixed.
- **Lasting ice/snow:** 144 of the 268 flags lie where the autumn 2025 image shows snow or ice (the stand-in for glacier and permanent snow); 112 do not; 12 have no clear autumn image.
- **The 32 snow-free flags** are the shortlist that could be ground movement or air effects. 15 of them are in one pair, 6–18 Oct 2026 (the first clear pair after the monsoon), 5 in 27 May – 8 Jun. They are not checked further here and are not called movement.
- The two Langtang flags (14–26 Jul) have no usable image: monsoon cloud. The method could not have checked them either.

**Eye check of 20 random flags** (true colour, HLS Sentinel-2 8 Oct 2025, 33% cloud, and 23 Oct 2026, clear; mostly judged on the 2026 image; chips in `data/flagcheck/chips/`, one judge, Claude):

| What the flag sits on | Flags |
|---|---:|
| Clean glacier or snowfield | 11 |
| Bare rock or moraine slope (mostly steep and in shade) | 6 |
| Vegetated slope | 1 (no 2026 image there) |
| Valley floor or river | 1 — the Langtang valley floor reshaped by the 26 Aug debris flow (flag in 12–24 Sep) |
| Unclear (possibly debris-covered glacier) | 1 |

None of the 20 sits on a visible fresh landslide scar. One sits on ground that really did change (debris-flow deposits after the collapse), which is a true surface change but not a warning of anything.

**Reading.** Most flags that can be checked are on snow, ice or steep shaded high faces, where phase is disturbed by snow and melt; this supports the earlier guess that many flags are seasonal. About a quarter of all flags could be checked at all, so the share of real movement among the 268 is still unknown; the 32 snow-free flags are where to look next. Limits as stated above; in addition, the eye check uses 30 m images and a single judge.
