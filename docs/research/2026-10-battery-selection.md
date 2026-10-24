# Battery selection for the T1 (2026-10)

- **Date:** 2026-10-22, revision 2. It applies the maintainers' answers to the three decisions of revision 1 (§1.1).
- **Updated 2026-10-24: superseded by [ADR 0014](../adr/0014-two-cell-battery.md)** (through ADR 0007 and ADR 0011). The T1 runs on a quoted 2S pack with a BQ25798 charger and a BQ28Z610-R1 gauge; the Adafruit 328 and the BQ25895 / MAX17055 pairing named here are no longer T1 parts. Kept as history.
- **Scope:** the main-body battery of the OpenDAP T1 (not the powerbank HAT).
- **Inputs:**
  - [T1 requirements](https://github.com/opendap-project/t1/blob/main/docs/requirements/README.md): T1-009, T1-012, T1-017, T1-027 to T1-029, T1-031 to T1-033;
  - [BOM v0](../specs/bom-v0.md), line 21;
  - [component selection](2026-10-component-selection.md) §3 and [sourcing alternatives](2026-10-sourcing-alternatives.md) §3;
  - certification and compliance §2.2–2.3;
  - [touch display selection](https://github.com/opendap-project/faceplate-touch/blob/main/docs/research/2026-10-display-selection.md): the Focus E35GH module is 54.46 × 82.94 × 5.50 mm.
- **Maintainers' rules applied, in order:**
  1. a standard **commercial** cell or pack, not custom, with **≥ 2,000 mAh** (T1-012);
  2. **availability first, validated against real stock** (T1-028, T1-029);
  3. **certified**: IEC 62133-2 and UN 38.3 reports available;
  4. **user-replaceable**: connector, no solder, no glue (EU 2023/1542 Art. 11, from 18 Feb 2027), and compatible with a sealed IP65 commercial edition;
  5. the **newest compatible generation** (LiHV 4.35/4.4/4.45 V, silicon anode) when it is available (T1-027);
  6. among candidates that pass rules 1–5, **the most energy (Wh) that fits the derived envelope wins**;
  7. two sources in the same size class, ideally.
- **Conventions:**
  - **UNVERIFIED** means no primary source was found in this session.
  - **(vendor claim)** means the only source is the maker's or the seller's own text.
  - Dimensions are thickness × width × length (T × W × L), in mm. "Max" means the maker's maximum dimension, not the nominal size code.
  - Prices are USD. Stock is a 2026-10-22 snapshot.

> **How this was gathered, and its limits.**
>
> - **Read directly:**
>   - Digi-Key category and product pages: category "Batteries Rechargeable (Secondary)", keyword "lithium polymer", capacity keywords and individual product pages;
>   - Adafruit product pages and the Adafruit-hosted cell specification;
>   - the Jauch LP103450JH datasheet;
>   - Jauch's standard LiPo programme and EEMB's catalogue, on the makers' sites.
> - **Not covered:**
>   - Mouser and Farnell pages timed out.
>   - The session's web-search budget was already used up, so Arrow, LiPol Battery, PKCELL, Varta, Renata and Ansmann were not searched.
>   - LCSC figures come from the sourcing report of the same day (no LiPo ≥ 2,000 mAh listed).
>   - Those rows are **UNVERIFIED**.
> - **Not measured:** nothing here has been measured on hardware or in CAD. The keep-outs in §2 are planning assumptions. Replace them with the real layout as soon as the board and case outlines exist.

---

## 0. Summary

1. **Target body: 62.5 × 93.75 × 25 mm** (W × H × T). The maintainers allows up to 25 mm and up to 62.5 × 95 mm, and prefers a height:width ratio as close to 1.50 as possible.
2. **Battery space (pack envelope)**, after every keep-out and margin:
   - **25 mm body:** **11.8 × 53.5 × 63.25 mm**, with the HAT device-side piece stacked over the bottom-edge port band (§2.3). That gives a geometric maximum of **≈ 15.6–17.6 Wh (≈ 4,200–4,750 mAh)**.
   - **20 mm body:** **7.2 × 53.5 × 57.25 mm**. The HAT piece cannot stack there and needs its own top band. Geometric maximum **≈ 8.6–9.7 Wh (≈ 2,300–2,600 mAh)**.
3. **Ratio conflict:** 93.75 / 62.5 = **1.50**, which is **below the 1.52 lower bound of T1-033** (a *must*). The requirement needs the maintainers' update to 1.50–1.59 before this body is adopted. The 62.5 × 95 mm body (1.52) is the compliant fallback. It adds 1.25 mm to the pack length (§2.6).
4. **Largest stocked options (25 mm body):**
   - **US Electronics USE-104060-3K-PCBJST**: 3,000 mAh, 11.1 Wh, Digi-Key 1,249. Its datasheet makes **no IEC 62133-2 or UN 38.3 claim**.
   - **Adafruit 328**: 2,500 mAh, 9.4 Wh, Digi-Key 1,834. It has a **UN 38.3 report**, but no IEC 62133-2 report was seen.
   - No stocked pack with **both** reports and ≥ 2,000 mAh fits. Jauch publishes both, but its only fitting part is 1,900 mAh.
5. **Best commercial size to quote: 105060** (cell 10 × 50 × 60, ≈ 3,000–3,500 mAh at 4.2 V, ≈ 11–13 Wh; LiHV about +10 %). It fits with 0.75 mm to spare in length. A thicker **115060** (≈ 3,500–3,800 mAh) also fits in thickness, but the size code is less common (**UNVERIFIED**).
6. **The 20 mm body still has no stocked pack ≥ 2,000 mAh that fits.**
   - The thinnest stocked candidate is Adafruit 2011 (7.0 mm), which is too long: 60 mm against 57.25 mm.
   - The best quoted size is **705050** (≈ 2,000–2,300 mAh; LiHV ≈ 2,300–2,500).
7. **The current BOM pick, Jauch LP705176JS+PCM, still fits no envelope.** At 78 mm long it exceeds every pocket length. BOM line 21 should be replaced (§9).

**Recommendation (labeled):** design the 25 mm body around a **105060-class pocket**.

- **Prototypes and the DIY kit:** **Adafruit 328** (primary, UN 38.3 report).
- **Stocked second source:** **USE-104060-3K-PCBJST** (3,000 mAh). Use it for prototypes only until its UN 38.3 and IEC 62133-2 reports exist.
- **Commercial edition:** a **certified 105060 pack** quoted from two of Jauch, EEMB and Grepow.

---

## 1. What the battery has to satisfy

### 1.1 Maintainers' decisions (revision 2)

| # | Question in revision 1 | Maintainers' answer | Effect here |
|---|---|---|---|
| 1 | Body thickness | Up to 25 mm is allowed. The body may grow to the maximum when needed, with a tendency toward the minimum | 25 mm is the design case. 20 mm is still shown for comparison |
| 2 | Position of the HAT device-side piece | Wherever it fits best. The HAT standard is defined after everything else, so the position is not fixed | It is placed to free the largest battery bay (§2.3) |
| 3 | Body footprint | Up to 62.5 × 95 mm, with a height:width ratio as close to exactly 1.50 as possible, e.g. 62.5 × 93.75 mm | Design body: **62.5 × 93.75 mm**. That conflicts with T1-033 (§0, item 3) |

### 1.2 Rules for the pack

| Rule | Source | Consequence for the pack |
|---|---|---|
| Standard commercial cell, ≥ 2,000 mAh | T1-012 | A catalogue size code with a published datasheet. No custom outline. 2,000 mAh is the floor, not the target |
| Battery life is a top priority | T1-009 | Rank by **Wh** (mAh × nominal V), not by mAh. A 3.85 V LiHV cell carries 4 % more energy per mAh than a 3.7 V one |
| Availability first, validated | T1-028, T1-029 | Stock at Digi-Key, Mouser, Farnell, Arrow or LCSC, or at the maker with a public catalogue and datasheet. Quote-only parts are **UNVERIFIED** until they are quoted |
| Newest compatible generation | T1-027 | LiHV (4.35/4.4/4.45 V) or silicon anode, **if** stocked and certified. The charger and gauge must support the voltage (§6) |
| IEC 62133-2 + UN 38.3 | compliance §2.2 | Both reports for the exact pack MPN. UN 38.3 is mandatory for any shipment, including DIY kits |
| User-replaceable from 18 Feb 2027 | EU 2023/1542 Art. 11, compliance §2.3 | Connector, not soldered tabs. No glue that needs heat or solvents. Commercially available tools. A spare part for ≥ 5 years. Don't rely on the IP65 derogation |
| Sealed commercial edition | T1-017 | Battery behind a gasketed, screw-retained back cover. The pocket needs its own retention (foam and a bracket), because the cover must not press on the pouch |
| Two sources | owner | Same size code and connector pinout, so one pocket and one harness serve both |

---

## 2. Envelope derivation

### 2.1 Bodies

| ID | Body (W × H × T, mm) | H:W | Role |
|---|---|---|---|
| **D25** | **62.5 × 93.75 × 25** | **1.50** | **Design case** (maintainers' preference; needs a T1-033 update) |
| D20 | 62.5 × 93.75 × 20 | 1.50 | Same footprint at the ideal thickness, for comparison |
| F25 | 62.5 × 95 × 25 | 1.52 | Fallback that complies with T1-033 as written today |

The Focus E35GH display (54.46 × 82.94 mm) fits all three bodies.

### 2.2 Stack in z (thickness)

**Assumed layout:** the battery sits in a pocket **behind the main board**, under the back cover. The board sits behind the display.

A side-by-side layout (battery beside the board, at full depth) was rejected. The RK3566, LPDDR4X, eMMC, PMIC and audio parts need roughly 55 × 35 mm of board, which would leave a pocket shorter than about 45 mm.

| Layer (front to back) | Thickness (mm) | Basis |
|---|---|---|
| Cover lens + OCA | 0.9 | 0.7 mm lens + 0.2 mm OCA (display report §7). A 1.1 mm IP65 lens adds 0.4 |
| Display module (Focus E35GH) | 5.5 | Datasheet |
| Module-to-board gap and support | 0.3 | Assumption |
| Main board PCB | 1.2 | Within the 1.0–1.6 mm range given |
| Components under the battery footprint | 1.5 | Parts under the pocket are capped at 1.5 mm. Taller parts (shields, inductors, connectors up to ~2.5 mm) go into the bands of §2.3 |
| Pocket floor / mid-frame | 0.4 | Stainless or PC sheet. It protects the pouch from component edges |
| **Battery layer** | **T − 11.7** | 8.3 mm at 20 mm; 13.3 mm at 25 mm |
| Back cover | 1.5 | Within the 1.5–2 mm range given |
| HAT case interface features over the pocket | 0.4 | Keying or recess depth (HAT Case Standard, not yet defined) |
| **Fixed total (without the battery layer)** | **11.7** | |

**Inside the battery layer:**

| Allowance | Value | Basis |
|---|---|---|
| Compression foam (also carries the pull-tab ribbon) | 0.3 mm | Typical PU foam at about 50 % compression. Assumption |
| **Swelling headroom** | **+10 % of the delivered thickness** | Jauch's LP103450JH datasheet gives a maximum thickness of **10.0 mm at delivery and 11.0 mm after cycling**, which is +10 % ([datasheet](https://www.jauch.com/downloadfile/66cedf5839843f10180fc6f4cdf848212/matd_246520_lp103450jhpcm2ic2_wires_70mm.pdf)). The 5–10 % range quoted as typical is taken at its upper end |
| Delivered thickness tolerance | Use the maker's **max** thickness | Datasheets give max values (Jauch, Sounddon). Size codes are nominal |

**Maximum delivered cell thickness:** t ≤ (battery layer − 0.3) / 1.10.

| Body thickness | Battery layer | Maximum delivered thickness t |
|---|---|---|
| 20 mm | 8.3 mm | **7.2 mm** |
| 25 mm | 13.3 mm | **11.8 mm** |

### 2.3 Keep-outs in x/y (inside the battery layer)

**Walls:** 1.6 mm per side, within the 1.5–2 mm range given. The inner cavity is the body minus 3.2 mm in each direction: **59.3 × 90.55 mm** for D20/D25 and 59.3 × 91.8 mm for F25.

| Keep-out | Where | Size assumed | Basis / status |
|---|---|---|---|
| **Bottom-edge band** | Full width, bottom | **17.0 mm** from the inner wall | 3.5 mm jack (Same Sky SJ2-35954D) and 4.4 mm jack (Pentaconn) at about 14.5 mm deep inside the wall. USB-C (~7.4 mm). Speaker (Same Sky CMS-151125, 15 × 11 mm) with its back volume. Body microphone and two bottom screw bosses (Ø 4). 1.0 mm clearance, 0.8 mm pocket rib and 0.7 mm tolerance. Jack depths are **UNVERIFIED** (the Pentaconn drawing is not public) |
| **HAT device-side piece** | Placed for the largest bay: see the placement study below | ~41 × 4 mm pogo array, ~48–52 × 8 mm with housing and 2 screws, ~4.5 mm tall, plus its flat-cable connector | Its position is free (maintainers' decision 2). The dimensions are **UNVERIFIED** (HAT Case Standard requirements: 4 × 32 grid at 1.27 mm proposed) |
| **Top band** | Full width, top | **7.0 mm** without the HAT piece; **13.0 mm** with it | Wi-Fi/BT antenna feed and its keep-out (no battery or metal within ~3–5 mm, **UNVERIFIED** until Murata's 2EL layout guide is applied). microSD (Hirose DM3AT) at a top corner. Two top screw bosses and a 0.8 mm rib |
| **Side margins** | Left and right | **2.5 mm each** | Left: Action, Vol+ and Vol− plungers and guides. Right: Main/Power. The tact switches sit on the board layer, but plungers, guides and the mid-side screw bosses of the gasketed IP65 back cover (Ø 3.5, half in the wall) reach into the battery layer |
| Faceplate FPC connector(s) | Front side of the board | 0 in the battery layer | Hirose FH35C sits between board and display |
| Microphones | Bands | 0 extra | One on the faceplate. The body microphone is in the bottom band |
| Main board tall parts | Bands | 0 extra | Parts above 1.5 mm must sit outside the pocket footprint |

**Placement study for the HAT device-side piece:**

| Option | Where the piece goes | Feasible at 20 mm? | Feasible at 25 mm? | Pack W × L at D20/D25 (mm) | Pack area (cm²) |
|---|---|---|---|---|---|
| **Stacked over the bottom band** | Over the jacks, in z | **No**. Jack ~7 mm + piece ~4.5 mm + 0.5 mm = 12 mm, against an 8.3 mm layer | **Yes**: 12 mm ≤ 13.3 mm | 53.5 × 63.25 | **33.8** (best at 25 mm) |
| In the top band | Top band grows from 7.0 to 13.0 mm | Yes | Yes | 53.5 × 57.25 | **30.6** (best at 20 mm) |
| Along the right side, vertical | Right margin grows from 2.5 to ~9.0 mm | Yes | Yes | 47.0 × 63.25 | 29.7, and it rules out 50 mm-wide size codes |
| Over the battery, in z | On the back cover above the pocket | No: it costs ~4.5 mm of battery thickness | Possible, but t falls from 11.8 to ~7.7 mm | 53.5 × 63.25 | Same area, −35 % thickness: worst |

**Result:**

- **25 mm body:** stack the HAT piece over the bottom-edge band. Its pogo array then sits near the bottom edge of the back.
- **20 mm body:** put it in the top band.
- Both choices go to `hat-standard` as inputs, not as fixed decisions.

**Pocket and pack allowances:**

| Allowance | Value | Basis |
|---|---|---|
| Pocket-to-pack clearance | 0.4 mm per side | Tolerance stack: ISO 2768-m is ±0.3 mm for 30–120 mm, plus molding. Also leaves room to lift the pack out |
| PCM fold at the tab end | 2.5 mm of length | Jauch LP705176JS grows from 76.0 mm (cell) to 78.0 mm (with PCM). Sounddon 785060 grows from 60.0 to 60.5 mm with its PCM folded flat. 2.5 mm covers bare cells that get a PCM board added |
| Lead exit, bend radius and connector seating | 2.5 mm of length | AWG24–26 lead with a bend radius ≥ ~5 × OD. The mating connector sits on the board in a notch outside the pocket |
| Retention for replaceability | Inside the foam allowance | Compression foam + a screwed bracket or the cover rib. **No glue.** A stretch-release pull tab (0.1 mm) is optional; whether it is acceptable under Art. 11 is **UNVERIFIED** (legal check) |

### 2.4 Envelope arithmetic

```text
cavity     = body − 2 × 1.6 (walls)
pocket W   = cavity W − 2 × 2.5 (side margins)
pocket L   = cavity L − 17.0 (bottom band) − top band (7.0, or 13.0 with the HAT piece)
pack W max = pocket W − 2 × 0.4
pack L max = pocket L − 2 × 0.4 − 2.5 (lead/connector)
cell L max = pack L max − 2.5 (PCM fold), for bare cells
t max      = (battery layer − 0.3 foam) / 1.10 (swelling)
```

### 2.5 Resulting envelopes

| ID | Body (W × H × T) | HAT piece | Max pack T × W × L (mm) | Max cell L (bare) | Pack volume (cm³) | Geometric energy at 390–440 Wh/L | ≈ mAh at 3.7 V |
|---|---|---|---|---|---|---|---|
| **D25** | **62.5 × 93.75 × 25** | Over the bottom band | **11.8 × 53.5 × 63.25** | 60.75 | 39.9 | **15.6–17.6 Wh** | **4,210–4,750** |
| D25, alternative | 62.5 × 93.75 × 25 | Top band | 11.8 × 53.5 × 57.25 | 54.75 | 36.1 | 14.1–15.9 Wh | 3,810–4,300 |
| **D20** | **62.5 × 93.75 × 20** | Top band | **7.2 × 53.5 × 57.25** | 54.75 | 22.1 | **8.6–9.7 Wh** | **2,320–2,620** |
| F25 | 62.5 × 95 × 25 | Over the bottom band | 11.8 × 53.5 × 64.5 | 62.0 | 40.7 | 15.9–17.9 Wh | 4,290–4,840 |

- The 390–440 Wh/L range is the volumetric density of the stocked 4.2 V packs measured in §3, at their max dimensions. LiHV adds about 10–12 %.
- These are **upper bounds**: no catalogue size code fills a pocket exactly.
- The pack is limited to 53.5 mm in width. Catalogue size codes come in 50 mm and 55–60 mm widths, so a **50 mm-wide** code is the practical choice. The extra 3.5 mm is not used, which is why §5's realistic figures fall below the geometric bound.

### 2.6 Sensitivity (D25)

| Change | Effect on the pocket | ≈ Energy effect |
|---|---|---|
| Body 62.5 × 95 (F25, T1-033-compliant) instead of 93.75 | +1.25 mm L | +2 % geometric. No change for a 105060 pack, which fits both |
| Jacks 2 mm shorter (if the Pentaconn drawing allows) | +2 mm L | +3 % |
| Lens 1.1 instead of 0.7 mm | −0.36 mm t | −3 % |
| Swelling headroom 5 % instead of 10 % | +0.6 mm t | +5 % |
| HAT piece in the top band instead of over the ports | −6 mm L | −10 %, and a 105060 pack no longer fits |

---

## 3. Candidates found

### 3.1 Stocked commercial packs (≥ 1,900 mAh), validated 2026-10-22

| # | Maker / MPN | Chemistry, V nominal / charge | Capacity | Wh | Max T × W × L (mm) | Weight | Wh/L, Wh/kg | Max charge / discharge | Cycle life | PCM / NTC / connector | Certifications (evidence) | Stock, price, MOQ (2026-10-22) | Lifecycle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Adafruit 328** (cell: Hunan Sounddon **785060**, spec Q/WAPL785060-1011) | LiPo, 3.75 / 4.2 V | 2,500 mAh | 9.4 | Cell 7.8 × 50 × 60; **pack 7.9 × 50.5 × 60.5** with PCM ([spec](https://cdn-shop.adafruit.com/datasheets/785060-2500mAh_specification_sheet.pdf)). Digi-Key lists 8.0 × 50 × 65 | 46 g (spec); 52 g (Digi-Key) | 388 / 204 | 1C (2.5 A) / 0.5C standard. Adafruit advises ≤ 1.2 A charge | ≥ 400 cycles (maker's own end criterion) | PCM yes (OV/OD/short) / **no NTC** / **JST-PH 2-pin** | UN 38.3 report, drop test and MSDS offered by Adafruit ([product page](https://www.adafruit.com/product/328)). **IEC 62133-2: not seen** | [Digi-Key 1,834 @ $14.95, MOQ 1, 4-week lead](https://www.digikey.com/en/products/detail/adafruit-industries-llc/328/5054542); Adafruit in stock, $13.46 @ 10, $11.96 @ 100 | Active. The cell spec is a 2010 edition, so OEM longevity is **UNVERIFIED** |
| 2 | **Adafruit 2011** | LiPo, 3.7 / 4.2 V | 2,000 mAh ±2 % | 7.4 | 7.0 × 36 × 60 (Adafruit; max vs nominal not stated) | 34 g | 489* / 218 | 0.2C standard (0.5 A). Max **UNVERIFIED** | **UNVERIFIED** | PCM yes / **no NTC** / **JST-PH 2-pin** | UN 38.3 report and MSDS offered ([product page](https://www.adafruit.com/product/2011)). **IEC 62133-2: not seen** | Digi-Key 4,395 @ $12.50 ([category listing](https://www.digikey.com/en/products/filter/batteries-rechargeable-secondary/91?keywords=lithium%20polymer)); Adafruit **out of stock**, $10.00 @ 100 | Active |
| 3 | **US Electronics USE-104060-3K-PCBJST** (cell: Shenzhen Hysincere) | LiPo, 3.7 / 4.2 V (PCM cut-off 4.28 V) | 3,000 mAh | 11.1 | 10.0 × 40.5 × 62.0 | **UNVERIFIED** | 442 / — | 0.6 A standard charge and discharge (Digi-Key) | **UNVERIFIED** | PCM / **no NTC** / JST-PH | **No IEC 62133 or UN 38.3 claim** in its datasheet (sourcing report §3) | [Digi-Key marketplace 1,249 @ $14.95; $13.65 @ 100](https://www.digikey.com/en/products/result?keywords=USE-104060-3K-PCBJST) (ships from the seller) | Active |
| 4 | **Jauch LP103450JH+PCM+PTC+2 WIRES 70MM** | LiPo, 3.7 / 4.2 V | **1,900 min** / 1,920 typ. mAh | 7.03 | **10.0 (11.0 after cycling) × 34.5 × 52.0**, PCM included | ~35 g | 392 / 201 | 1C / 1C | 300 cycles to 80 % | PCM + second IC + PTC / no NTC / 70 mm wires | **UN 38.3 yes; IEC 62133-2:2017 compliant; UL 1642 yes** ([datasheet](https://www.jauch.com/downloadfile/66cedf5839843f10180fc6f4cdf848212/matd_246520_lp103450jhpcm2ic2_wires_70mm.pdf)) | Digi-Key 411 @ $17.10; $10.73 @ 480; 28-week lead | Active. **Fails T1-012 (< 2,000 mAh)** |
| 5 | Jauch LP705176JS+PCM+2 WIRES 70MM (current BOM line 21) | LiPo, 3.7 / 4.2 V | 3,000 min / 3,150 typ. | 11.1 | 7.8 × 51.8 × 78.0 with PCM | — | 352 / — | — | — | PCM / no NTC / wires | IEC 62133-2 and UN 38.3 for this MPN **UNVERIFIED** | Digi-Key 199 @ $21.59 (sourcing report); 28-week lead | Active. **Fits no envelope** |
| 6 | Jauch LP735977JH+PCM+2 WIRES 70MM | LiPo, 3.7 / 4.2 V | 4,800 mAh | 17.8 | 7.8 × 59.5 × 78.5 | — | 487 / — | — | — | PCM / no NTC / wires | Jauch datasheet format (UN 38.3, IEC 62133-2) likely; **UNVERIFIED** for this MPN | Digi-Key 762 @ $26.84 | Active. **Too wide and too long** |
| 7 | Jauch LP906090JH+PCM+2 WIRES 70MM | LiPo, 3.7 / 4.2 V | 6,000 mAh | 22.2 | 9.9 × 60.5 × 92.0 | — | — | — | — | PCM / wires | **UNVERIFIED** | Digi-Key 2,621 @ $30.08 | Active. **Too big** |
| 8 | MikroElektronika MIKROE-4474 | LiPo, 3.7 V | 3,000 mAh | 11.1 | 8.1 × 57 × 63 | — | 382 / — | — | — | — | **UNVERIFIED** | Digi-Key 281 @ $26.00 | Active. **57 mm is too wide** |
| 9 | GlobTek BL2200F9031781S1PCKT / BL3000F9031781S1PCxx | LiPo, 3.7 V | 2,200 / 3,000 mAh | 8.1 / 11.1 | 8.8 × 31 × 78 | — | — | — | — | PCM | **UNVERIFIED** | Digi-Key 271 @ $16.52 (2,200); 3,000 mAh: 15–68 units or special order | Active. **78 mm is too long** |
| 10 | SparkFun PRT-13855 | LiPo, 3.7 V | 2,000 mAh | 7.4 | 5.6 × 49.2 × 68.8 | — | — | — | — | PCM / JST-PH | MSDS only (sourcing report) | [SparkFun $19.41](https://www.sparkfun.com/products/13855) | Active. **68.8 mm is too long** |

\* Adafruit gives 2011's size as a plain "60 × 36 × 7 mm", probably nominal, so its 489 Wh/L is optimistic.

### 3.2 Maker-catalogue cells (not in distributor stock this session)

| Maker / model | Capacity | Size (T × W × L, mm) | Certifications | Availability | Fit |
|---|---|---|---|---|---|
| EEMB LP103454 | 2,000 mAh, 3.7 V, 7.4 Wh | 10.3 × 34.5 × 56.0, bare cell with solder tabs, 40 g | UL 1642 / UN 38.3 / IEC 62133 (vendor claim, [product page](https://www.eemb.com/product-136)) | No Digi-Key listing. MOQ, price and lead time **UNVERIFIED** (quote via <sales@eemb.com>) | D25 and F25 once a PCM is added (pack ≈ 58.5 mm) |
| EEMB LP104765 / LP605590 / LP103395 | 3,300 / 3,400 / 3,700 mAh | 10×47×65 / 6×55×90 / 10×33×95 | As above (vendor claim) | **UNVERIFIED** | All too long |
| Jauch LP675365JU+PCM | 2,800 mAh | 6.9 × **54.0** × 68.0 | Jauch datasheets state UN 38.3 / IEC 62133-2 per part (**UNVERIFIED** for this MPN) | Digi-Key 693 @ $17.93 (sourcing report) | Too wide and too long for every envelope |
| Jauch LP685077JU | 3,500 mAh | 7.0 × 51.0 × 78.0 | as above | Out of stock; 120 due 2027-03-22 (sourcing report) | Too long |
| Jauch LP854165J | 2,500 mAh | 8.5 × 41.5 × 64.5 (cell) | **UNVERIFIED** | Quote only | Too long for D25 and F25 once the PCM is added (≈ 67 mm) |
| Grepow LiHV (3.85 V / 4.4–4.45 V) | — | — | Grepow states 4.35/4.4/4.45/4.48 V options and "+15 %" energy ([LiHV page](https://www.grepow.com/lihv-battery.html), vendor claim) | Digi-Key marketplace carries Grepow 3.85 V cells only up to **1,050 mAh** (0 stock); larger LiHV cells are quote-only | Any size code, once quoted |
| Generic size codes 705050, 105050, 105060, 115060 (EEMB, Grepow, LiPol, PKCELL) | ≈ 2,000–2,300 / 2,800–3,100 / 3,000–3,500 / 3,500–3,800 mAh (estimates at 390–440 Wh/L) | as coded | **UNVERIFIED** | **UNVERIFIED** (not searchable this session) | 705050 → D20 and D25. 105050, 105060 and 115060 → D25 and F25 |

**Not suitable:**

- **Cylindrical 18650/21700 cells** (Samsung SDI, LG, Panasonic, Murata; Adafruit 1781, 354): Ø 18.4 mm exceeds the 13.3 mm battery layer even at 25 mm.
- **Silicon-anode pouches** (Amprius, Enovix and similar): no small-format stocked part was found. **UNVERIFIED** whether any is sold through distributors.
- **LCSC:** no LiPo ≥ 2,000 mAh (largest: KAMCY 803450, 1,500 mAh; sourcing report).

---

## 4. Fit matrix

✓ fits, ✗ does not fit, with the limiting dimension. Packs are checked against the "max pack" envelope of §2.5 (with the best HAT placement for each thickness). Bare cells get the PCM allowance added.

| Candidate (max pack T × W × L) | D20 (7.2 × 53.5 × 57.25) | D25 (11.8 × 53.5 × 63.25) | F25 (11.8 × 53.5 × 64.5) |
|---|---|---|---|
| Adafruit 328 (7.9 × 50.5 × 60.5) | ✗ t 7.9 > 7.2, L | **✓** (L margin 2.75, W 3.0) | ✓ |
| Adafruit 2011 (7.0 × 36 × 60) | ✗ L 60 > 57.25 | ✓ | ✓ |
| USE-104060-3K (10.0 × 40.5 × 62.0) | ✗ t | **✓** (L margin 1.25) | ✓ |
| Jauch LP103450JH (11.0 cycled × 34.5 × 52.0) | ✗ t | ✓ | ✓ |
| EEMB LP103454 + PCM (≈ 10.3 × 34.5 × 58.5) | ✗ t | ✓ | ✓ |
| Jauch LP705176JS+PCM (7.8 × 51.8 × 78.0) | ✗ t, L | ✗ L 78 > 63.25 | ✗ L |
| Jauch LP675365JU+PCM (6.9 × 54.0 × 68.0) | ✗ W, L | ✗ W 54 > 53.5, L | ✗ W, L |
| MIKROE-4474 (8.1 × 57 × 63) | ✗ | ✗ W 57 > 53.5 | ✗ W |
| SparkFun PRT-13855 (5.6 × 49.2 × 68.8) | ✗ L | ✗ L 68.8 > 63.25 | ✗ L |
| 705050 class (≈ 7.0 × 50.5 × 52.5) | **✓** | ✓ | ✓ |
| 105050 class (≈ 10.3 × 50.5 × 52.5) | ✗ t | ✓ | ✓ |
| **105060 class (≈ 10.3 × 50.5 × 62.5)** | ✗ | **✓** (L margin 0.75) | ✓ (2.0) |
| 115060 class (≈ 11.3 × 50.5 × 62.5) | ✗ | ✓ (t margin 0.5) | ✓ |

---

## 5. Ranking by energy

Candidates are ranked by Wh **among those that pass the other rules**:

- "Pass" means commercial, ≥ 2,000 mAh, validated stock and connectorised.
- "Gap" names the rule a candidate still misses.

### 5.1 Design body, 62.5 × 93.75 × 25 mm (D25)

| Rank | Option | Wh | Status |
|---|---|---|---|
| — | Geometric ceiling | 15.6–17.6 | — |
| 1 | **115060-class pack, LiHV, quoted** | ≈ 14.5–15.5 (**UNVERIFIED**) | Gap: stock, certificates, and a less common size code. **Largest option overall** |
| 2 | **105060-class pack, quoted** (4.2 V ≈ 3,000–3,500 mAh; LiHV ≈ 3,300–3,800 mAh) | ≈ 11.1–13.0 at 4.2 V, ≈ 12.7–14.6 LiHV (**UNVERIFIED**) | Gap: stock, certificates. **Best commercial size to quote**: a common size code with several makers |
| 3 | **USE-104060-3K-PCBJST** | **11.1** | Stocked (Digi-Key marketplace 1,249). **Fails rule 3**: no IEC 62133-2 or UN 38.3 claim. **Largest stocked** |
| 4 | **Adafruit 328** | **9.4** | Stocked (Digi-Key 1,834). UN 38.3 report available. **IEC 62133-2 not seen**, no NTC. **Largest stocked with any certificate evidence** |
| 5 | Adafruit 2011 | 7.4 | Stocked (Digi-Key 4,395; Adafruit out of stock). Same certificate status as Adafruit 328 |
| 6 | EEMB LP103454 + PCM | 7.4 | Gap: stock **UNVERIFIED**. UL 1642 / UN 38.3 / IEC 62133 (vendor claim) |
| — | Jauch LP103450JH | 7.0 | Full certificate evidence (UN 38.3, IEC 62133-2:2017, UL 1642), but 1,900 mAh (< T1-012) |

### 5.2 Same footprint at 20 mm (D20)

| Rank | Option | Wh | Status |
|---|---|---|---|
| — | Geometric ceiling | 8.6–9.7 | — |
| 1 | **705050-class LiHV (4.4 V), quoted** | ≈ 8.5–9.5 (**UNVERIFIED**) | Gap: stock, certificates. **Largest option at 20 mm** |
| 2 | 705050-class 4.2 V, quoted | ≈ 7.4–8.5 (**UNVERIFIED**) | Gap: stock, certificates |
| — | Any stocked pack ≥ 2,000 mAh | — | **None fits.** Adafruit 2011 misses by 2.75 mm in length, and Adafruit 328 by 0.7 mm in thickness |

**At 20 mm, T1-029 (validated stock) cannot be met today, and the margin over the 2,000 mAh floor is small.** Maintainers' decision 1 already allows 25 mm, so D25 is the design case.

### 5.3 Estimated runtime trend

The T1's real power draw is not known yet. The two loads below are **placeholder assumptions** for comparison only:

- 0.6 W for screen-off wired playback;
- 1.5 W for screen-on use.

Usable energy is taken as 90 % of the label Wh. Runtime scales linearly with Wh.

| Option | Wh | Screen-off at 0.6 W (h) | Screen-on at 1.5 W (h) |
|---|---|---|---|
| Adafruit 2011 | 7.4 | 11.1 | 4.4 |
| 705050-class LiHV (D20 best, UNVERIFIED) | ≈ 9.0 | ≈ 13.5 | ≈ 5.4 |
| Adafruit 328 | 9.4 | 14.1 | 5.6 |
| USE-104060-3K | 11.1 | 16.7 | 6.7 |
| 105060-class 4.2 V (UNVERIFIED) | ≈ 12.0 | ≈ 18.0 | ≈ 7.2 |
| 105060-class LiHV (UNVERIFIED) | ≈ 13.5 | ≈ 20.2 | ≈ 8.1 |
| D25 geometric ceiling | ≈ 15.6–17.6 | ≈ 23–26 | ≈ 9.4–10.6 |

**The trend:** moving from 20 mm to 25 mm thickness gives about **+80 %** geometric energy. LiHV adds another 10–12 % in the same pocket.

---

## 6. Newest generation: LiHV and silicon anode

| Item | Status | Evidence |
|---|---|---|
| BQ25895 charge voltage | **Compatible**: 3.840–4.608 V in 16 mV steps covers 4.35, 4.40 and 4.45 V | TI BQ25895 datasheet (REG06 VREG). Driver `bq25890_charger.c` sets it from the `ti,charge-voltage` / battery `constant-charge-voltage-max-microvolt` property |
| MAX17055 gauge | **Compatible** with HV cells via the ModelGauge m5 model's charge-voltage setting (`VChg`). Exact 4.45 V support is **UNVERIFIED** | ADI MAX17055 datasheet (ModelCfg) |
| PCM | Must be the LiHV variant (over-voltage detection about 4.475–4.55 V) | Pack-level item for the quote |
| LiHV pouches ≥ 2,000 mAh in stock | **None found.** Grepow's Digi-Key marketplace listing tops out at 1,050 mAh (3.85 V, 0 stock) | §3.2 |
| Silicon-anode pouches in stock | **None found / UNVERIFIED** | §3.2 |

**Conclusion:** design the charger, gauge and device tree so the charge voltage is a per-pack parameter (4.20 / 4.35 / 4.40 V). Ship 4.2 V packs now. Ask every quoted maker for the same size code in LiHV with its own IEC 62133-2 report. Never charge a 4.2 V pack at a LiHV voltage: the pack ID or a variant in the device tree must make the voltage impossible to confuse.

---

## 7. Integration requirements for whichever pack is chosen

1. **Connector:** JST-PH 2.0 mm on the stocked packs. For the commercial edition, order a **3-wire variant with a 10 kΩ NTC** (B ≈ 3,435 K) on a latching connector (JST PH 3-pin, or Molex Pico-Lock).
   - Jauch already sells this construction on a smaller pack: [LP503030JU+PCM+2IC+NTC+MOL. 78172-3](https://www.digikey.com/en/products/result?keywords=jauch%20lipo%20battery), Digi-Key 1,170 @ $9.60.
2. **Board-side NTC** pressed against the pocket floor and wired to the BQ25895 TS pin. That keeps the stocked packs (no NTC) safe for prototypes and the DIY kit (as in the sourcing report).
3. **Pocket:**
   - rigid floor (0.4 mm), 0.4 mm clearance per side;
   - compression foam on the cover side;
   - a screwed retaining bracket or rib, and no adhesive;
   - a finger notch or ribbon for removal;
   - lead routed through a notch to the board connector, with ≥ 2.5 mm free length.
4. **Swelling:** the 10 % headroom is part of the envelope. The back cover gasket must not rely on the pouch for compression.
5. **EU Art. 11:** the pack must be a spare part for ≥ 5 years, removable with a standard screwdriver and without heat or solvents. Its label needs a QR code from 18 Feb 2027 (compliance §2.3).
6. **UN 38.3:** the test summary is needed for every MPN shipped, including the DIY kit (PI 965/966).

---

## 8. Open points for the maintainers

1. **T1-033 ratio band.** The preferred body (62.5 × 93.75 mm, ratio 1.50) is below the 1.52 lower bound of T1-033, which is a *must*. Either update T1-033 to about 1.50–1.59, or use 62.5 × 95 mm (1.52).
   - The battery choice is the same for both: a 105060 pack fits each.
   - **Recommendation:** update T1-033 through the requirements process if 1.50 is the intent.
2. **HAT device-side piece near the bottom edge, stacked over the port band.** This is the input to pass to `hat-standard` for the 25 mm body (§2.3). If the standard later needs the piece elsewhere, the pocket loses about 6 mm of length, and a 105060 pack no longer fits (105050 does).
3. **Quotes.** Ask two of Jauch, EEMB and Grepow for a 105060 pack (and a 115060 option), in 4.2 V and LiHV, with certificates. A 105060 order needs no new decision.

---

## 9. Recommendation

### Recommendation (design target): a 105060-class pocket in a 62.5 × 93.75 × 25 mm body

- **Pack envelope:** 11.8 × 53.5 × 63.25 mm.
- **HAT device-side piece:** stacked over the bottom-edge port band.
- **Why:** 105060 is the largest common catalogue size code that fits. Every stocked candidate in §5.1 also fits the same pocket, so prototypes, the DIY kit and the commercial pack share one bay and one harness.

### Recommendation (commercial edition): a certified 105060 pack, quoted from two makers in the same size code and pinout

- **Makers:** Jauch, EEMB, Grepow.
- **Specification for the quote:**
  - 1S LiPo, ≥ 3,000 mAh;
  - max 10.3 × 50.5 × 62.5 mm including the PCM;
  - 4.2 V, with a LiHV 4.35/4.4 V variant if it is separately certified;
  - PCM, 10 kΩ NTC (B ≈ 3,435 K) and a latching 3-pin connector (JST PH 3-pin or Molex Pico-Lock);
  - IEC 62133-2 CB report and UN 38.3 summary for the exact pack MPN;
  - a spare-part commitment of ≥ 5 years.
- **Status:** **UNVERIFIED** until quoted. Adopt it only after quotes, samples and certificates (T1-029).
- **Stretch option:** a 115060 pack, about +10 % energy, if a maker offers it as a catalogue size.

**Recommendation (prototypes and DIY kit, available now):**

- **Primary: Adafruit 328** (2,500 mAh, 9.4 Wh). Stocked, UN 38.3 report available. Request its IEC 62133-2 report.
- **Second source: USE-104060-3K-PCBJST** (3,000 mAh, 11.1 Wh). The largest stocked pack that fits, with the same JST-PH connector. Use it for prototypes only until US Electronics supplies UN 38.3 and IEC 62133-2 reports.
- **Fallback: Adafruit 2011** (2,000 mAh), which has the same documentation as the Adafruit 328.
- **NTC:** none of these packs has one, so use a board-side NTC on the pocket floor, wired to the BQ25895 TS pin.

**Proposed replacement for BOM v0 line 21** (not applied: this report edits nothing else):

| # | Function | Part | Status | Driver path | Second source / note |
|---|---|---|---|---|---|
| 21 | Battery | 1S LiPo pack, **105060 size class** (max 10.3 × 50.5 × 62.5 mm with PCM), ≥ 3,000 mAh, 4.2 V (LiHV variant if certified), PCM + 10 kΩ NTC + latching 3-pin connector, IEC 62133-2 + UN 38.3. To quote from two of Jauch / EEMB / Grepow. Prototypes and DIY kit: **Adafruit 328** (2,500 mAh) | Proposed | none (BQ25895 charge voltage and MAX17055 model per pack) | USE-104060-3K-PCBJST (3,000 mAh, no certificates yet), Adafruit 2011. Board-side NTC for packs without one. Pocket 11.8 × 53.5 × 63.25 mm in a 62.5 × 93.75 × 25 mm body ([battery selection](../research/2026-10-battery-selection.md)) |

**Largest option for each thickness:**

| Thickness (62.5 × 93.75 mm body) | Largest option that fits (any availability) | Largest stocked | Largest stocked with certificate evidence |
|---|---|---|---|
| 20 mm | 705050-class LiHV, ≈ 8.5–9.5 Wh (**UNVERIFIED**) | **None** ≥ 2,000 mAh | **None** |
| 25 mm | 115060-class LiHV, ≈ 14.5–15.5 Wh (**UNVERIFIED**); 105060 is the practical target at ≈ 11–14.6 Wh | USE-104060-3K, 11.1 Wh | Adafruit 328, 9.4 Wh (UN 38.3 only) |

---

## 10. Risks

1. **Certificates.** No stocked fitting pack has a published IEC 62133-2 report. Only UN 38.3 summaries are offered (Adafruit). USE-104060 has neither. Without IEC 62133-2, the commercial edition cannot pass IEC 62368-1 Annex M or Japan's PSE route.
   - *Mitigation:* request the reports now. Make the certified 105060 quote the commercial path.
2. **T1-033 conflict.** The 1.50 ratio is outside today's 1.52–1.59 band.
   - *Mitigation:* update the requirement, or use 62.5 × 95 mm. Either way the battery stays the same.
3. **Tight length for 105060.** It has 0.75 mm of spare length in D25 (2.0 mm in F25).
   - *Mitigation:* confirm the makers' max length including the PCM. Confirm the jack depths and the lead-exit allowance in CAD.
4. **Keep-outs are assumptions.**
   - The Pentaconn jack depth, the HAT device-side piece size and height, the antenna keep-out and the side-button mechanics are all **UNVERIFIED**.
   - Each ±2 mm changes pack energy by about 3–4 %.
   - *Mitigation:* rerun §2.4 when the board outline and HAT Case Standard exist.
5. **The HAT placement depends on another repository.** If the HAT piece cannot sit over the port band, the pocket loses about 6 mm of length: a 105060 pack no longer fits, and a 105050 pack (≈ −17 %) is the fallback.
6. **Thin, aging supply for the prototype packs.**
   - Adafruit does not name the OEM, and the Sounddon spec dates from 2010.
   - Adafruit 2011 is out of stock at Adafruit.
   - USE-104060 is a marketplace listing.
   - Digi-Key stock covers prototypes and early kits, not mass production.
7. **No pack has an NTC.** The board-side NTC senses the pocket floor, not the cell core.
   - *Mitigation:* a pack-internal NTC in the commercial order; firmware temperature limits through the gauge.
8. **Swelling and IP65.** A swollen pouch inside a sealed cover can load the gasket and the display.
   - *Mitigation:* 10 % headroom (already budgeted), no cover pressure on the pack, gauge-based end-of-life warning.
9. **LiHV mix-up.** Mixing 4.2 V and LiHV packs in one pocket is a safety hazard.
   - *Mitigation:* different connector keying or pack ID per chemistry, with the charge voltage tied to it.
10. **Session coverage.**
    - Mouser, Farnell and Arrow were not reachable. Grepow, EEMB, LiPol, PKCELL, Varta, Renata and Ansmann stock is **UNVERIFIED**.
    - A wider sweep could find a stocked 105060-class pack.
    - *Mitigation:* repeat §3 with distributor access and maker quotes before the board freeze.

---

## Sources

- Requirements and internal reports:
  - [T1 requirements](https://github.com/opendap-project/t1/blob/main/docs/requirements/README.md);
  - [BOM v0](../specs/bom-v0.md);
  - [component selection](2026-10-component-selection.md);
  - [sourcing alternatives](2026-10-sourcing-alternatives.md);
  - certification and compliance;
  - [touch display selection](https://github.com/opendap-project/faceplate-touch/blob/main/docs/research/2026-10-display-selection.md);
  - [HAT Case Standard requirements](https://github.com/opendap-project/hat-standard/blob/main/docs/requirements/README.md).
- Digi-Key (2026-10-22):
  - [rechargeable batteries, "lithium polymer"](https://www.digikey.com/en/products/filter/batteries-rechargeable-secondary/91?keywords=lithium%20polymer);
  - ["lithium polymer 3Ah"](https://www.digikey.com/en/products/filter/batteries-rechargeable-secondary/91?keywords=lithium%20polymer%203Ah);
  - ["lithium polymer 3.85V"](https://www.digikey.com/en/products/filter/batteries-rechargeable-secondary/91?keywords=lithium%20polymer%203.85V);
  - [Adafruit 328](https://www.digikey.com/en/products/detail/adafruit-industries-llc/328/5054542);
  - [USE-104060-3K-PCBJST](https://www.digikey.com/en/products/result?keywords=USE-104060-3K-PCBJST);
  - [LP103450JH search](https://www.digikey.com/en/products/result?keywords=LP103450).
- Makers:
  - [Adafruit 328](https://www.adafruit.com/product/328), [Adafruit 2011](https://www.adafruit.com/product/2011), [Adafruit LiPo category](https://www.adafruit.com/category/574);
  - [Sounddon 785060 specification (Adafruit CDN)](https://cdn-shop.adafruit.com/datasheets/785060-2500mAh_specification_sheet.pdf);
  - [Jauch LP103450JH datasheet](https://www.jauch.com/downloadfile/66cedf5839843f10180fc6f4cdf848212/matd_246520_lp103450jhpcm2ic2_wires_70mm.pdf), [Jauch LiPo standard programme](https://www.jauch.com/en-INT/products/battery_technology/getPrm/batteries/Lithium%20Polymer%20Batteries/);
  - [EEMB standard LiPo](https://www.eemb.com/products-55), [EEMB LP103454](https://www.eemb.com/product-136);
  - [Grepow LiHV](https://www.grepow.com/lihv-battery.html).
- Regulation: [Commission guidelines C/2025/214 on Art. 11 removability](https://eur-lex.europa.eu/eli/C/2025/214/oj/eng).
