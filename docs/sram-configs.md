# Dual SRAM Configuration Analysis

Comparison of tile sizes for two dual-memory SRAM configurations on IHP SG13G2.

## Macro Dimensions

| Macro                           | Width (um) | Height (um) | Area (um²) |
| ------------------------------- | ---------- | ----------- | ---------- |
| RM_IHPSG13_1P_512x32_c2_bm_bist | 416.64     | 191.34      | 79,739     |
| RM_IHPSG13_1P_512x16_c2_bm_bist | 236.80     | 191.34      | 45,310     |
| RM_IHPSG13_1P_512x8_c3_bm_bist  | 236.80     | 110.38      | 26,138     |
| RM_IHPSG13_1P_512x64_c2_bm_bist | 784.48     | 191.34      | 150,102    |

### IHP Tile Size Formula

```
width  = N × 217.44 − 15.36  (um)
height = M × 198.45 − 83.16  (um)
```

| Tile | Die Width (um) | Die Height (um) | Die Area (um²) |
| ---- | -------------- | --------------- | -------------- |
| 4x2  | 854.40         | 313.74          | 268,055        |
| 4x4  | 854.40         | 710.64          | 607,019        |
| 5x4  | 1,071.84       | 710.64          | 761,537        |
| 6x4  | 1,289.28       | 710.64          | 916,110        |
| 8x2  | 1,724.16       | 313.74          | 540,907        |
| 8x4  | 1,724.16       | 710.64          | 1,224,682      |

### Critical: SRAM Macro Orientation

IHP SRAM macros **require R90 orientation** for the PDN to work correctly.
The macros have power pins on Metal4; in R90, these align properly with
the vertical TopMetal1 PDN stripes. N orientation causes PSM-0069 ("check
connectivity failed on VPWR") — all standard cells lose power grid connection.

Exception: the 512×64 macro works in N orientation on wide tiles (8x2, 4x4).

R90 dimensions (width × height swap):

| Macro  | R90 Width (um) | R90 Height (um) |
| ------ | -------------- | --------------- |
| 512x32 | 191.34         | 416.64          |
| 512x16 | 191.34         | 236.80          |
| 512x8  | 110.38         | 236.80          |
| 512x64 | 191.34         | 784.48          |

---

## Configuration A: 2×512×56 (6 macros)

Each memory = 512×32 + 512×16 + 512×8 = 56 bits/word.
Two memories = 6 macro instances total.
Total macro area: 2 × (79,739 + 45,310 + 26,138) = **302,374 um²**
Total SRAM capacity: 2 × 512 × 56 bits = **57,344 bits (7,168 bytes)**

### CI Results

| Branch       | Tile    | Die Area (um²) | Macro % | Logic Area (um²) | GDS      | GL Test  | Harden Time |
| ------------ | ------- | -------------- | ------- | ---------------- | -------- | -------- | ----------- |
| `6macro-4x4` | **4x4** | 607,019        | 49.8%   | 304,645          | **FAIL** | —        | 6m          |
| `6macro-5x4` | **5x4** | 761,537        | 39.7%   | 459,163          | **PASS** | **PASS** | 45m         |
| `main`       | **6x4** | 916,110        | 33.0%   | 613,736          | **PASS** | **PASS** | 57m         |
| (old)        | 8x2     | 540,907        | 55.9%   | —                | FAIL     | —        | —           |

Note: 8x2 fails because R90 macros are too tall (416.64 > 313.74 height).

### 5x4 Layout (smallest confirmed working) — 1,071.84 × 710.64 um

All diagrams use consistent scale: 1 char ≈ 20um, 1 line ≈ 45um.

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│                                                     │
│                                                     │
│                                  [logic]            │
│                                                     │
│ ┌────────┐┌────────┐ ┌────────┐┌─────┐             │
│ │ sram0  ││ sram1  │ │ sram1  ││sram1│             │
│ │  _32   ││  _32   │ │  _16   ││ _8  │             │
│ │191×417 ││191×417 │ │191×237 ││110× │             │
│ │  R90   ││  R90   │ │  R90   ││237  │             │
│ │        ││        │ └────────┘└─────┘             │
│ │        ││        │ ┌────────┐┌─────┐             │
│ │        ││        │ │ sram0  ││sram0│             │
│ │        ││        │ │  _16   ││ _8  │             │
│ │        ││        │ │191×237 ││110× │             │
│ │        ││        │ │  R90   ││237  │             │
│ └────────┘└────────┘ └────────┘└─────┘             │
└─────────────────────────────────────────────────────┘
 1,071.84 × 710.64 um  (5x4 tiles)
```

Two 32-bit macros side by side (left), 16-bit and 8-bit macros in 2×2 grid (right).
All R90 orientation. ~44um gaps between macros (> PDN_VPITCH 38.87).

### 4x4 Layout (FAILED) — 854.40 × 710.64 um

Same arrangement compressed to 854.40 width. Right margin only 19um,
which is too tight for PDN stripe routing (PDN-0179). **5x4 is the minimum.**

---

## Configuration B: 2×512×64 (2 macros)

Each memory = single 512×64 macro = 64 bits/word.
Two memories = 2 macro instances total.
Total macro area: 2 × 150,102 = **300,204 um²**
Total SRAM capacity: 2 × 512 × 64 bits = **65,536 bits (8,192 bytes)**

### CI Results

| Branch            | Tile    | Die Area (um²) | Macro % | Logic Area (um²) | GDS      | GL Test  | Harden Time |
| ----------------- | ------- | -------------- | ------- | ---------------- | -------- | -------- | ----------- |
| `dual-512x64-4x4` | **4x4** | 607,019        | 49.4%   | 306,815          | **PASS** | **PASS** | 64m         |
| `dual-512x64`     | **8x2** | 540,907        | 55.5%   | 240,703          | **PASS** | **PASS** | 62m         |
| `dual-512x64-6x4` | **6x4** | 916,110        | 32.8%   | 615,906          | pending  | —        | —           |
| `dual-512x64-8x4` | **8x4** | 1,224,682      | 24.5%   | 924,478          | pending  | —        | —           |

Note: R90 doesn't fit in 4x4 (784.48 > 710.64 height). N orientation works for 512×64.

### 4x4 Layout (smallest working) — 854.40 × 710.64 um

```
┌───────────────────────────────────────────┐
│                                           │
│                                           │
│                                           │
│              [logic area]                 │
│                                           │
│                                           │
│ ┌───────────────────────────────────────┐ │
│ │     sram1  784×191  N                 │ │
│ │                                       │ │
│ └───────────────────────────────────────┘ │
│                                           │
│ ┌───────────────────────────────────────┐ │
│ │     sram0  784×191  N                 │ │
│ │                                       │ │
│ └───────────────────────────────────────┘ │
│                                           │
└───────────────────────────────────────────┘
 854.40 × 710.64 um  (4x4 tiles)
```

Two macros stacked vertically. N orientation. ~49um inter-macro gap.
Macros fill ~92% of die width. ~240um above for standard cell logic.

### 6x4 Layout — 1,289.28 × 710.64 um

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│                                                                │
│                                                                │
│                          [logic area]                          │
│                                                                │
│                                                                │
│ ┌───────────────────────────────────────┐                      │
│ │     sram1  784×191  N                 │     [logic]          │
│ │                                       │                      │
│ └───────────────────────────────────────┘                      │
│                                                                │
│ ┌───────────────────────────────────────┐                      │
│ │     sram0  784×191  N                 │     [logic]          │
│ │                                       │                      │
│ └───────────────────────────────────────┘                      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
 1,289.28 × 710.64 um  (6x4 tiles)
```

Stacked vertically. Macros fill ~61% of die width, ~465um unused to the right.
Logic area: 615,906 um² (67.2% of die). Spacious but wasteful.

### 8x2 Layout — 1,724.16 × 313.74 um

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                      │
│                                    [logic area]                                      │
│ ┌───────────────────────────────────────┐  ┌───────────────────────────────────────┐ │
│ │     sram0  784×191  N                 │  │     sram1  784×191  N                 │ │
│ │                                       │  │                                       │ │
│ └───────────────────────────────────────┘  └───────────────────────────────────────┘ │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
 1,724.16 × 313.74 um  (8x2 tiles)
```

Side by side, N orientation. Macros fill ~91% of die width, ~61% of die height.
Logic area: 240,703 um² (44.5% of die). Tight but functional.

### 8x4 Layout — 1,724.16 × 710.64 um

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                      │
│                                                                                      │
│                                                                                      │
│                                                                                      │
│                                                                                      │
│                                    [logic area]                                      │
│                                                                                      │
│                                                                                      │
│                                                                                      │
│                                                                                      │
│                                                                                      │
│ ┌───────────────────────────────────────┐  ┌───────────────────────────────────────┐ │
│ │     sram0  784×191  N                 │  │     sram1  784×191  N                 │ │
│ │                                       │  │                                       │ │
│ └───────────────────────────────────────┘  └───────────────────────────────────────┘ │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
 1,724.16 × 710.64 um  (8x4 tiles)
```

Side by side, N orientation. Same width as 8x2 but 4-row height.
Logic area: 924,478 um² (75.5% of die). Maximum space but largest tile.

---

## Comparison Summary

| Metric                | Config A (6 macros)          | Config B (2 macros)      |
| --------------------- | ---------------------------- | ------------------------ |
| Total SRAM bits       | 57,344 (7,168 B)             | 65,536 (8,192 B)         |
| Total macro area      | 302,374 um²                  | 300,204 um²              |
| Minimum working tile  | **5x4** (761,537 um²)        | **4x4** (607,019 um²)    |
| Smallest digital tile | N/A (R90 too tall for 2-row) | 8x2 (540,907 um²)        |
| Wasted SRAM bits      | 8 per word (56 of 64 used)   | 0                        |
| Macro count           | 6                            | 2                        |
| Orientation required  | R90                          | N (or R90 on tall tiles) |
| Routing complexity    | High (6 macros)              | Low (2 macros)           |
| Controller complexity | Higher (3 bit-mask decoders) | Lower (single bit-mask)  |

### Space Utilization

| Config       | Tile    | Die Area | Macro Area | Macro %   | Available for Logic |
| ------------ | ------- | -------- | ---------- | --------- | ------------------- |
| B (2 macros) | **4x4** | 607,019  | 300,204    | **49.4%** | 306,815 um²         |
| B (2 macros) | 8x2     | 540,907  | 300,204    | 55.5%     | 240,703 um²         |
| B (2 macros) | 6x4     | 916,110  | 300,204    | 32.8%     | 615,906 um²         |
| B (2 macros) | 8x4     | 1,224,682 | 300,204   | 24.5%     | 924,478 um²         |
| A (6 macros) | **5x4** | 761,537  | 302,374    | **39.7%** | 459,163 um²         |
| A (6 macros) | 6x4     | 916,110  | 302,374    | 33.0%     | 613,736 um²         |

### Recommendations

1. **Config B on 4x4 is the best option overall:**
   - More SRAM (8 KB vs 7 KB)
   - Smallest tile that works (4x4 = 607,019 um²)
   - Simplest routing (2 macros, N orientation)
   - 50.6% of die available for logic

2. **Config B on 8x2** if digital tiles are preferred:
   - Same SRAM, same 2 macros
   - Long thin tile may be more available in shuttles
   - 44.5% available for logic

3. **Config A on 5x4** only if 56-bit words are specifically needed:
   - Requires R90 orientation for all macros
   - 6 macros = complex routing and PDN
   - 60.3% of die available for logic (larger tile)
   - Higher risk of build failures

### Tiles That Don't Work

| Tile | Config A | Config B | Reason                                                                     |
| ---- | -------- | -------- | -------------------------------------------------------------------------- |
| 4x2  | No       | No       | Macros exceed die area                                                     |
| 6x2  | No       | No       | Macros too wide for 2-row die height                                       |
| 8x2  | No       | **Yes**  | R90 macros too tall for A; N works for B                                   |
| 3x4  | No       | No       | 636.96 too narrow for any macro                                            |
| 4x4  | **No**   | **Yes**  | PDN-0179 for A (right margin 19um too tight); B works (stacked vertically) |

## CI Build Status

| Branch            | Config       | Tile | Orientation | GDS      | GL Test  | Harden Time | Notes                                   |
| ----------------- | ------------ | ---- | ----------- | -------- | -------- | ----------- | --------------------------------------- |
| `dual-512x64-4x4` | B (2 macros) | 4x4  | N           | **PASS** | **PASS** | 64m         | Smallest working tile                   |
| `dual-512x64`     | B (2 macros) | 8x2  | N           | **PASS** | **PASS** | 62m         | Digital tile option                     |
| `dual-512x64-6x4` | B (2 macros) | 6x4  | N           | pending  | —        | —           | Spacious option                         |
| `dual-512x64-8x4` | B (2 macros) | 8x4  | N           | pending  | —        | —           | Maximum space                           |
| `6macro-5x4`      | A (6 macros) | 5x4  | R90         | **PASS** | **PASS** | 45m         | Smallest for 6-macro                    |
| `main`            | A (6 macros) | 6x4  | R90         | **PASS** | **PASS** | 57m         | Comfortable fit                         |
| `6macro-4x4`      | A (6 macros) | 4x4  | R90         | **FAIL** | —        | 6m          | PDN-0179: right margin too tight (19um) |

Precheck DRC failures are upstream IHP PDK issues (same as ttihp-sram-test).
