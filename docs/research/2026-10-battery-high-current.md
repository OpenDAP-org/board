# Battery for the full output budget (ADR 0011 search)

- **Date:** 2026-10-22. All stock and price figures were captured on 2026-10-22.
- **Question:** is there an off-the-shelf, stocked battery that meets the acceptance criteria of [ADR 0011](../adr/0011-battery-path-rated-for-the-full-output-budget.md), so that BRD-050 can be met on battery?
- **Inputs:**
  - [ADR 0011](../adr/0011-battery-path-rated-for-the-full-output-budget.md), [ADR 0007](../adr/0007-off-the-shelf-battery.md), [ADR 0008](../adr/0008-battery-technology-ready-for-lihv.md);
  - [battery selection](2026-10-battery-selection.md) (pocket arithmetic, earlier candidates) and [sourcing alternatives](2026-10-sourcing-alternatives.md) §3;
  - [power tree v0](../specs/power-tree-v0.md) §4.7 (4.8 A budget, path drop) and [BOM v1](../specs/bom-v1.md) lines 43, 47, 104;
  - [T1 requirements](https://github.com/opendap-project/t1/blob/main/docs/requirements/README.md) T1-031 to T1-039, [t1 ADR 0003](https://github.com/opendap-project/t1/blob/main/docs/adr/0003-tentative-body-size.md) and the [battery-life analysis](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-battery-life-analysis.md).
- **Conventions:**
  - **UNVERIFIED** means no primary source was found in this session.
  - "Not stated" means the page or datasheet that was read gives no value.
  - Dimensions are T × W × L in mm. Prices are USD at qty 1 unless the currency is shown.
  - Nothing here edits an ADR or the BOM.

> **How this was gathered, and its limits.**
>
> - **Read directly:** Digi-Key filter and product pages; FindChips (for Mouser, TME and broker stock); TME; the maker shops of Adafruit, SparkFun, Pimoroni, Gens ace (gensace.de, genstattu.com), HobbyKing, Horizon Hobby, BetaFPV and CNHL; the catalogs of Jauch, EEMB, Ultralife, Renata, GlobTek, MikroElektronika, BatterySpace and Molicel; TI and ABLIC protection-IC datasheets; JST catalogs.
> - **Not covered:** web search was not available (session budget used up), so only pages reachable by direct URL were read. Mouser pages timed out. The Digi-Key sweep was cut short by rate limiting (HTTP 429) before the 3.3–4.5 Ah keyword searches ran. LiPol Battery, Tenergy, RS PRO and VARTA pages did not load. GNB/Gaoneng's official shop was not found. Molex and Hirose ratings could not be read. Grepow sells large high-rate cells only by quote.
> - **Not measured:** nothing here was tested on hardware.

---

## 0. Summary

1. **No stocked battery meets ADR 0011 item 1.** No pouch pack from 2,000 to 4,500 mAh found in any shop or distributor that was reached combines a continuous rating of at least 6 A, a protection trip of at least 6 A and a fit inside the pocket.
   - Every protected pack that fits is rated **≤ 2C** (about 1.5–5 A continuous). Its protection circuit (PCM) and leads are sized for that rating.
   - The high-rate (20–40C) 1S hobby cells of this capacity are **97 mm or longer** and have no PCM.
   - The high-rate hobby packs that do fit are below 1,000 mAh.
2. **Cylindrical cells are excluded by thickness.** The smallest cell with ≥ 6 A and ≥ 2,000 mAh is an 18650 (Ø 18.3–18.6 mm). A body of at most 25 mm (T1-031) cannot hold it behind the display in any layout (§3).
3. **The limit is the cell, not the connector.** Latching connectors rated above 6.9 A per contact are stocked: Molex Micro-Fit 3.0 at 8.5 A with AWG 18, JST VH at 7–10 A. A board-side protection that trips above 6 A is possible with stocked parts (TI BQ2970 family with low-RDS(on) FETs). What does not exist in stock is a **≥ 2,000 mAh, ≥ 6 A pouch cell or pack that fits** the pocket.
4. **Recommendation (labeled):** **no pack can be adopted under ADR 0011 today.**
   - Keep the **Adafruit 328** as the interim pack (ADR 0011 item 3). It is still the best stocked fit: in stock, a UN 38.3 report, 9.4 Wh, and the highest stated cell rating of the packs that fit (2C, 5 A).
   - The second source for the same bay stays the **Adafruit 2011**. The **MikroElektronika MIKROE-1120** is an alternative with published PCM and lead data, if the pocket is at least 63.5 mm long.
   - **Every stocked candidate supports about the same on-battery budget as today: about 1.4–1.6 A**, limited by a 2 A class cell or lead.
   - Meeting BRD-050 needs a decision among the three branches already named in ADR 0011's consequences (§7).

---

## 1. Criteria applied

From [ADR 0011](../adr/0011-battery-path-rated-for-the-full-output-budget.md), item 1, and [power tree](../specs/power-tree-v0.md) §4.7:

| # | Criterion | Value |
|---|---|---|
| C1 | Continuous discharge rating | ≥ 6.0 A (4.8 A at 80 %) |
| C2 | Protection | Over-current trip ≥ 6.0 A, plus short-circuit protection |
| C3 | Leads and pack connector | ≥ 6.9 A per pole (4.8 A at 70 %), latching |
| C4 | Capacity | ≥ 2,000 mAh |
| C5 | Fit | Inside the pocket (below) |
| C6 | Certification | UN 38.3 report; IEC 62133-2 for the Commercial edition |
| C7 | Chemistry | 4.2 V or LiHV ([ADR 0008](../adr/0008-battery-technology-ready-for-lihv.md)) |
| C8 | Sourcing | Off the shelf, in authorized stock (ADR 0007, T1-038) |
| — | Implied by §4.7 | The cell must hold about **3.55 V at 4.8 A** for VSYS = 3.3 V (path drop about 0.24 V). That favors low-impedance cells |

**Pockets** (pack maximum T × W × L, including the PCM fold and lead exit). The arithmetic is from the [battery selection](2026-10-battery-selection.md) §2 and the [battery-life analysis](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-battery-life-analysis.md) §11.3.

| Body (W × H × T) | Source | Pack maximum T × W × L |
|---|---|---|
| 62.5 × 93.75 × 25 | ADR 0011 | **11.8 × 53.5 × 63.25** |
| **59.5 × 94.3 × 24** | t1 ADR 0003 (tentative body) | **10.9 × 50.5 × 63.8** |
| 62.5 × 95 × 25 | T1-031 maximum | 11.8 × 53.5 × 64.5 |
| 59.5 × 94.3 × 20 | Ideal thickness (T1-032) | 7.3 × 50.5 × 57.8 |

---

## 2. Pouch packs

### 2.1 Protected packs that fit (or nearly fit), 1.9–3.5 Ah: none meets C1/C2

Stock and prices are at Digi-Key unless the row says otherwise.

| Pack | Capacity / Wh | Max T × W × L | Continuous (peak) discharge | PCM over-current / short circuit | Leads / connector | Certifications seen | Stock / price | Fails |
|---|---|---|---|---|---|---|---|---|
| **Adafruit 328** (cell: Sounddon 785060, spec Q/WAPL785060-1011) | 2,500 mAh / 9.4 Wh (3.75 V) | 7.9 × 50.5 × 60.5 with PCM | 0.5C standard; **2C (5 A) maximum** | Over-current not stated; short circuit yes | JST-PH 2-pin, 26 AWG (BOM v1 line 47) | UN 38.3 report offered; IEC 62133-2 not seen | Digi-Key 1,828 @ $14.95; Adafruit in stock @ $14.95 | C1, C2, C3 |
| **Adafruit 2011** (cell: PKCELL LP803860) | 2,000 mAh / 7.4 Wh | 7.0 × 36 × 60 (listing); the cell sheet says 8 × 38 × 60 nominal | 1C (2 A) | Not stated | JST-PH 2-pin, AWG not stated | UN 38.3 report offered | Digi-Key 4,394 @ $12.50; Adafruit out of stock | C1, C2, C3 |
| **MikroElektronika MIKROE-1120** | 2,000 mAh / 7.4 Wh | 7.0 × 44.2 × **63.5** | 2 A continuous | 2–5 A | UL1007 24 AWG | Not stated | Digi-Key 56 @ $18.00 | C1, C2, C3, C6. 0.25 mm too long for the ADR 0011 pocket; fits the ADR 0003 pocket |
| **US Electronics USE-104060-3K-PCBJST** | 3,000 mAh / 11.1 Wh | 10.0 × 40.5 × 62.0 | 0.5C (1.5 A) | 2–5 A, delay 7.2–11 ms; short-circuit delay 220–380 µs | UL1007 26 AWG, JST-PH | None claimed | Digi-Key marketplace 1,249 @ $14.95 | C1, C2, C3, C6 |
| **Pimoroni BAT0005** (cell: PKCELL LP804257) | 2,000 mAh / 7.4 Wh | 8.3 × 42.5 × 60 | 2 A maximum continuous | 5–8 A (DW01 + 8205) | JST, 100 mm, AWG not stated | Not stated | Pimoroni £9.00; stock not confirmed | C1, C2 (minimum 5 A), C3 |
| **Jauch LP103450JH+PCM+PTC+2 WIRES 70MM** | 1,900 min mAh / 7.0 Wh | 10.8 × 34.5 × 52 (11.0 after cycling, battery selection §3.1) | 1C (about 1.9 A) | 2.0–7.0 A, second protection IC and PTC | Wires, AWG not stated | **UN 38.3; IEC 62133-2 compliant; UL 1642** | Digi-Key 411 @ $17.10 | C1, C2, C4 |
| Gens ace 3500mAh 1S TX (SKU GEA35001STXJR) | 3,500 mAh / about 12.95 Wh | about 9 × 43 × **64** | Not stated (charge 0.2C recommended, 1C maximum) | Not stated | JR plug, AWG not stated | Not stated | gensace.de "available" @ €11.99 | C1–C3 and C6 unknown; 64 mm only fits the 64.5 mm (T1-031 maximum) pocket |
| SparkFun PRT-13855 | 2,000 mAh / 7.4 Wh | 5.6 × 49.2 × **68.8** | Not stated | Over-current protection yes, trip not stated | JST-PH 2-pin | Not stated | SparkFun in stock @ $19.41 | C5 (too long), C1–C3 unknown |

Sources: [Adafruit 328](https://www.adafruit.com/product/328) and its [cell specification](https://cdn-shop.adafruit.com/datasheets/785060-2500mAh_specification_sheet.pdf); [Adafruit 2011](https://www.adafruit.com/product/2011) and its [cell sheet](https://cdn-shop.adafruit.com/datasheets/LiIon2000mAh37V.pdf); [MIKROE-1120 at Digi-Key](https://www.digikey.com/en/products/result?keywords=MIKROE-1120); [USE-104060-3K-PCBJST at Digi-Key](https://www.digikey.com/en/products/result?keywords=USE-104060-3K-PCBJST); [Pimoroni PKCELL LP804257 sheet](https://cdn.shopify.com/s/files/1/0174/1800/files/PKcell_LIPO804257_2000mAh_3.7V.pdf); [Jauch LP103450JH datasheet](https://www.jauch.com/downloadfile/66cedf5839843f10180fc6f4cdf848212/matd_246520_lp103450jhpcm2ic2_wires_70mm.pdf); [Gens ace 3500mAh TX](https://www.gensace.de/products/gens-ace-3500mah-3-7v-tx-1s1p-lipo-battery-pack-with-jr-plug); [SparkFun PRT-13855](https://www.sparkfun.com/lithium-ion-battery-2ah.html).

### 2.2 Packs or cells rated for ≥ 6 A that do not fit

| Item | Capacity | T × W × L | Rating | PCM / leads | Stock / price | Why it fails |
|---|---|---|---|---|---|---|
| Turnigy 2200mAh 1S 40C (SKU 9067000201-0) | 2,200 mAh | 9 × 34 × **97** | 40C | None (bare cell) | HobbyKing $5.49, stock unclear | Length; no PCM |
| Turnigy 2200mAh 1S 20C (SKU 9067000202-0) | 2,200 mAh | 8 × 34 × **97** | 20C | None | HobbyKing $4.94, stock unclear | Length; no PCM |
| Turnigy 5000mAh 1S 20C | 5,000 mAh | 10 × 42 × **128** | 20C | None | HobbyKing $10.34 | Length |
| Gens ace 6900mAh 1S2P 3.8 V TX | 6,900 mAh | **18** × 50 × 69 | Not stated | Not stated | gensace.de €29.99 | Thickness, length |
| Gens ace / Trinity 1S "shorty" hard cases (8,000–8,600 mAh, 130–140C, 3.8 V LiHV) | 8,000–8,600 mAh | Not stated (hard-case shorty) | 130–140C | No PCM; 5 mm bullets | genstattu.com 349 @ $45.99 (8000 mAh) | Hard-case format, far too large |
| Jauch LP675365JU+PCM+2 WIRES 70MM | 2,800 min mAh | 7.5 × **54** × **68** | "2 A (wire limited)"; PCM 4.2–9.0 A | Wire limited | Digi-Key 693 @ $17.93 | Width, length, 2 A |
| BatterySpace 3.7 V 4000 mAh "7A rate" (2 × 605060) | 4,000 mAh | **15** × 54 × 66 | 7 A; PCB 8 A | 20 AWG | Seller marks it prototype, not UN 38.3 tested | Thickness, certification |
| BatterySpace PL5467100 | 4,250 mAh | 5.7 × **67** × **100** | 8 A (PCB-limited) | 18 AWG | Seller: not UN 38.3 tested | Size, certification |
| GlobTek BL2200F6034501S2PZAL (2 × 603450) | 2,000 min mAh | **13** × 35 × 53 | 1C; over-current 4.0–6.5 A | 2 × 24 AWG | Digi-Key 189 @ $17.26 | Thickness, C1 |
| EEMB High Power series (5–20C cells) | ≤ 1,700 mAh in the size class (LP803560HA); 3,000–3,400 mAh only as 555590 / 605590 | 605590 class is 90 mm long | 5–20C (series level) | No PCM listed | Quote only ([EEMB](https://www.eemb.com/products-58)) | C4 or length; not stocked |
| Grepow high-rate cells | — | — | 15–50C (vendor claim) | Bare or custom | Quote only; Digi-Key marketplace lists Grepow only up to 1,050 mAh | C8 |

Sources: [HobbyKing Turnigy 2200mAh 1S 40C](https://hobbyking.com/turnigy-2200mah-1s-40c-lipoly-single-cell-1.html), [Turnigy 2200mAh 1S 20C](https://hobbyking.com/turnigy-2200mah-1s-20c-lipoly-single-cell-1.html), [Turnigy 5000mAh 1S 20C](https://hobbyking.com/turnigy-5000mah-1s-20c-lipoly-single-cell.html), [gensace.de](https://www.gensace.de/), [genstattu.com](https://www.genstattu.com/), [Jauch LP675365JU at Digi-Key](https://www.digikey.com/en/products/result?keywords=LP675365JU), [GlobTek at Digi-Key](https://www.digikey.com/en/products/result?keywords=BL2200F6034501S2PZAL), [Grepow at Digi-Key](https://www.digikey.com/en/products/filter/batteries-rechargeable-secondary/91?keywords=grepow).

### 2.3 Shops searched with nothing in range

- **Gens ace / Tattu:** their 1S range is 200–950 mAh (45–95C), then 3,500 mAh (the TX pack above), then 6,900 mAh and up.
- **HobbyKing (Turnigy):** the high-C 1S packs that fit are ≤ 950 mAh. The 2,000 mAh pack that fits (SKU 9067000191-0, 10 × 34 × 49 mm, JST-PH, $6.46) is rated 1C.
- **Horizon Hobby:** Spektrum Li-ion transmitter packs (2,200–10,500 mAh) give no discharge rating, for example SPMB2200LITX1S at $19.99. The only high-C 1S packs are the Trinity shorties.
- **BetaFPV:** ≤ 550 mAh. **CNHL:** no 1S between 1,500 and 5,000 mAh.
- **Ultralife UBP:** UBP001 (1.75 Ah, PCM 1.8–3.0 A) is the largest soft pack. **Renata ICP606168PRT:** 2,800 mAh, 6.7 × 62 × 71, too large.
- **DFRobot, Seeed:** no LiPo from 2 to 4.5 Ah was found.

**Reading:** stocked 1S pouch packs from 2 to 4.5 Ah are built as energy packs (≤ 2C) with a PCM and leads to match. High-rate cells of that capacity are sold only in long RC formats, or bare and by quote.

---

## 3. Cylindrical cells: excluded by thickness

| Cell | Ø × L (mm) | Capacity | Continuous discharge | Stock / price | Source |
|---|---|---|---|---|---|
| Jauch LI INR18650JD-30P | 18.3 × 65.0 | 3.0 Ah | 20 A | Digi-Key 1,253 @ $11.20 | [Digi-Key](https://www.digikey.com/en/products/result?keywords=INR18650JD-30P) |
| Jauch LI-INR21700JD-40P | 21.7 × 70.9 | 4.0 Ah | 20 A | Digi-Key 1,154 @ $13.91 | [Digi-Key](https://www.digikey.com/en/products/result?keywords=INR21700JD-40P) |
| Samsung INR21700-50S | 21.3 × 70.6 | 5.0 Ah | 25 A (TME listing) | TME 556 @ $5.96 | [FindChips](https://www.findchips.com/search/INR21700-50S) |
| Murata US18650VTC6 | 18.35 × 65.2 | 3.0 Ah | Continuous not stated (TME: 30 A maximum) | TME 900–1,254 (FindChips); TME's own page shows 0, MOQ 50 | [FindChips](https://www.findchips.com/search/US18650VTC6) |
| Molicel INR-18650-P28A / INR-21700-P45B / P50B | 18.6 × 65.2 (P28A) | 2.8 / 4.5 / 5.0 Ah | 35 / 45 / 60 A | No authorized stock found | [Molicel P28A](https://www.molicel.com/product/inr-18650-p28a/) |
| Largest 14500 at Digi-Key (Jauch LI14500J1S1P+PCM) | 14.5 class | 850 mAh | — | Digi-Key 1,151 @ $11.82 | Fails C4 |

**Fit:**

- **Behind the board:** the battery layer is T − 11.7 mm, so 12.3 mm at 24 mm and 13.3 mm at 25 mm ([battery selection](2026-10-battery-selection.md) §2.2). An 18650 needs at least about 18.9 mm (Ø 18.6 + 0.3 mm foam), which means a body of about 30.6 mm, beyond the 25 mm of T1-031.
- **Beside the board:** the cell still lies behind the 54.46 × 82.94 mm display. The depth there at 25 mm is 25 − 1.5 (back cover) − 0.9 (lens) − 5.5 (display) − 0.3 (gap) = **16.8 mm**, still under Ø 18.3 mm.
- **Holders** add height: Keystone 1042 stands 14.86 mm above the board (Digi-Key 4,882 @ $5.99); MPD BH-18650-PC stands 21.31 mm (Digi-Key 9,774 @ $3.35).
- **No high-drain 14500, 18350 or 10440 cell ≥ 2,000 mAh exists** (the 14500 format tops out well under 1 Ah).

Cylindrical cells would need a body above T1-031, so the board-mounted holder and on-board protection variant asked for in the brief is not viable.

---

## 4. Parts around the pack (stocked; usable once a cell exists)

These parts do **not** limit the search. They are recorded so that the board and case changes in §6 are concrete.

### 4.1 Connectors rated ≥ 6.9 A per contact, latching

| Series | Rating per contact | Wire | Height | Stocked MPNs (2026-10-22) | Note |
|---|---|---|---|---|---|
| **Molex Micro-Fit 3.0** (3.00 mm) | **8.5 A** with crimp 43030-0038 (AWG 18); 5 A with 43030-0001 (AWG 20–24) | AWG 18 for 8.5 A | Right-angle header insulator 4.37 mm; mated height not stated | Header 43650-0200 (Digi-Key 47,122 @ $1.07); housing 43645-0200 (Digi-Key, $0.39); crimp 43030-0038 (Digi-Key 514,504 @ $0.082) | 4.8 A is **56 %** of 8.5 A. Low enough to sit in a band outside the pocket |
| JST VH (3.96 mm) | 10 A with AWG 16 (standard header); 7 A with AWG 18 (shrouded header) | AWG 22–16 | Top entry 16.5 mm; side-entry height not stated | B2P-VH (TME 18,922), B2PS-VH, VHR-2N, SVH-21T-P1.1 | Top entry too tall; 7 A at AWG 18 is 69 %, at the 70 % limit |
| JST PH, XH, XA, EH, GH, ACH | ≤ 3 A | — | — | — | Fail C3 |
| JST LBT A-type | 8 A power contact at AWG 20 | AWG 24–20 | — | — | Friction lock only: fails "latching" |
| Molex Nano-Fit / Pico-Lock / Micro-Lock Plus, Hirose DF63 | **Not stated** (maker pages unreachable) | — | — | DF63-2S-3.96C housing: Digi-Key 20,797 @ $0.30 | **UNVERIFIED** |

Sources: [Micro-Fit 43650-0200 at Digi-Key](https://www.digikey.com/en/products/result?keywords=43650-0200), [43030-0038 at Digi-Key](https://www.digikey.com/en/products/result?keywords=43030-0038), [JST VH catalog](https://www.jst-mfg.com/product/detail_e.php?series=228).

### 4.2 Board-side protection (if the pack PCM rule were ever met on the board instead)

- **TI BQ2970 family** (WSON-6):
  - Over-current is sensed as the voltage across the two external FETs. The over-current discharge threshold (VOCD) is set at the factory between 90 and 200 mV (±15 mV), with delays of 8, 16, 20 or 48 ms. Short circuit is 0.3–0.6 V at 250 µs.
  - TI's design example targets **7 A**: 100 mV ÷ 14.3 mΩ, with 2 × CSD16406Q3 at 7.5 mΩ each.
  - Stock: BQ29700DSER Mouser 13,276 @ $0.254; CSD16406Q3 Mouser 19,640 from $0.514.
  - The trip falls as the FETs heat up, so a higher-VOCD variant (BQ29702, 160 mV) leaves more room above 6 A. That is an inference, not a datasheet statement.
- **ABLIC S-82K1B:** sense-resistor based, over-current level 1 at 3–100 mV. Mouser S-82K1BAN-I6T1U 64 @ $1.07.
- **Board fuse:** BOM v1 line 104 already plans **Littelfuse 0451007.MRL** (7 A, LCSC 8,458). 0451008.MRL (8 A, Mouser 8,620 @ $1.02) and 0451010.MRL (10 A, Mouser 28,841) share the footprint.

ADR 0011 requires the protection **in the pack**, and the battery must stay user-replaceable. A board-side protector therefore adds a second layer; it does not replace the pack PCM. It does not help any of the candidates in §2.1, whose limit is the cell's rating.

---

## 5. Ranking

**Ranking order (from the brief):**

1. safety margin (BRD-049), as the current the pack supports at the 80 % / 70 % rules;
2. fit;
3. autonomy;
4. availability;
5. price.

**Supported battery budget:** the minimum of 80 % of the cell rating, 70 % of the lead or connector rating, and the PCM minimum trip. JST-PH figures follow BOM v1 line 47: 2 A with AWG 24, about 1.6 A estimated for 26 AWG.

**Autonomy:** typical scenario 1 (screen off, 3.5 mm SE, 0.66 W) and the pessimistic draw (1.5 W) from the [battery-life analysis](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-battery-life-analysis.md) §0.1, with 90 % of label energy usable. Formula: h = 0.9 × Wh / P. The T1-039 thresholds are 6 h red, 8 h warning and 12 h ideal.

| Rank | Pack | Meets ADR 0011? | Supported battery current (est.) | Fits ADR 0003 pocket (10.9 × 50.5 × 63.8)? | Fits ADR 0011 pocket (11.8 × 53.5 × 63.25)? | Autonomy typical / pessimistic | Availability | Price |
|---|---|---|---|---|---|---|---|---|
| 1 | **Adafruit 328** | No | about **1.6 A** (26 AWG lead into the JST-PH contact; cell 5 A max → 4.0 A at 80 %) | Yes | Yes | **12.8 h** / 5.6 h | Digi-Key 1,828; Adafruit in stock; UN 38.3 report | $14.95 |
| 2 | **MikroElektronika MIKROE-1120** | No | about **1.4 A** (JST-PH 2 A at AWG 24 × 70 %; cell 2 A × 80 % = 1.6 A; PCM minimum 2 A) | Yes (L 63.5) | No (+0.25 mm L) | 10.1 h / 4.4 h | Digi-Key 56 (thin) | $18.00 |
| 3 | Adafruit 2011 | No | about **1.6 A** (cell 2 A at 80 %; lead 26 AWG assumed, **UNVERIFIED**) | Yes | Yes | 10.1 h / 4.4 h | Digi-Key 4,394; Adafruit out of stock | $12.50 |
| 4 | Pimoroni BAT0005 | No | about **1.6 A** (cell 2 A at 80 %; lead AWG not stated) | Yes | Yes | 10.1 h / 4.4 h | Stock not confirmed | £9.00 |
| 5 | USE-104060-3K-PCBJST | No | about **1.2 A** (cell 1.5 A at 80 %) | Yes | Yes | **15.1 h** / 6.7 h | Digi-Key marketplace 1,249; no certificate claim | $14.95 |
| 6 | Jauch LP103450JH | No (also C4) | about **1.5 A** (cell 1.9 A at 80 %) | Yes, at the edge (10.8 delivered against 10.9) | Yes | 9.6 h / 4.2 h | Digi-Key 411; full certificate set | $17.10 |
| — | Gens ace 3500mAh TX | Unknown (no rating published) | Not stated | No (L 64 > 63.8 by 0.2) | No | 17.7 h / 7.8 h | gensace.de available | €11.99 |

**Reading:**

- All stocked fitting packs land at **1.2–1.6 A** on battery: the same order as the v1.1 interim budget. None reaches the 4.8 A budget.
- The Adafruit 328 keeps the best combination of supported current, fit, availability and certificate evidence. It is also the only fitting pack with a published 2C cell maximum.
- The USE-104060-3K gives the most autonomy, but the lowest current and no certificates.
- No candidate reaches 6 h at the pessimistic draw except the USE-104060-3K and the Gens ace TX pack, neither of which is qualified. This is the T1-039 measurement gate already noted in t1 ADR 0003, and it is independent of ADR 0011.

---

## 6. What the board and case would need for a compliant pack (when one exists)

These follow from §1 and §4. They are the same for a stocked pack found later or a quoted one.

1. **Connector:** replace BOM line 47 (JST S2B-PH-SM4-TB) with a **Molex Micro-Fit 3.0 right-angle header** (43650-0200, or the 3-pin version for an NTC pack) and require **AWG 18 leads** on the pack. It sits in a band outside the pocket. Its footprint is larger than JST-PH, about 3.0 mm pitch with retention pegs (drawing to be checked).
2. **Fuse:** BOM line 104 moves to 0451007.MRL (7 A), already planned.
3. **Gauge sense:** BOM line 43 moves to 5 mΩ, ≥ 0.5 W, already noted in BOM v1 (the MAX17055 range is **UNVERIFIED**).
4. **Copper and BATFET:** already sized for 4.8 A (ADR 0011 item 2). No change.
5. **Case:** AWG 18 leads have a larger outer diameter and bend radius than 26 AWG. The 2.5 mm lead-exit allowance of the battery selection §2.3 is **UNVERIFIED** for AWG 18 and probably needs about 4–5 mm (estimate: bend radius about 5 × OD), which costs pack length. A high-rate cell of the same volume holds less energy than an energy cell (**UNVERIFIED** by how much for any specific 105060-class part). The pocket does not change otherwise.
6. **Interim pack (unchanged):** JST-PH footprint, 2.5 A fuse, 1.6 A software budget (ADR 0011 item 3). Two footprints (JST-PH and Micro-Fit) can coexist only if the board edge allows. That is an open layout question.

---

## 7. Paths left for the maintainers (from ADR 0011 consequences)

No pack meets ADR 0011, so its consequence clause applies. The options, with what this search adds:

| Option | What it means | Facts from this search |
|---|---|---|
| A. Lower on-battery output budget | Size the on-battery budget to the stocked pack | Every stocked fitting pack supports about 1.2–1.6 A. The Adafruit 328's 1.6 A interim figure is already the best available |
| B. Quoted pack (against T1-038) | A 105060-class high-rate cell, PCM tripping at ≥ 6 A, AWG 18 leads, Micro-Fit 3.0, with UN 38.3 and IEC 62133-2 reports | Grepow and EEMB make 5–50C cells (vendor claims), but only by quote. EEMB lists no 2–3.5 Ah high-power cell in this size class. Needs a T1-038 exception, which only the maintainers can grant |
| C. Different charger and cell format | For example a 2S pack, which halves the current for the same power, with a buck-boost charger | Not researched here. No stocked 2S protected pack was checked (**UNVERIFIED**). It changes the power tree and the charger choice |

The search should be repeated with web search available. Mouser, Farnell, RS, Arrow, LiPol Battery, Tenergy and VARTA could not be read in this session, and the Digi-Key sweep above 3 Ah was incomplete. Those are the gaps that could still turn up a stocked pack.

---

## 8. Sources

- ADRs and specs in this repository, linked in the header.
- Distributor pages: [Digi-Key rechargeable batteries](https://www.digikey.com/en/products/filter/batteries-rechargeable-secondary/91), [FindChips](https://www.findchips.com/), [TME](https://www.tme.eu/).
- Maker and shop pages: [Adafruit](https://www.adafruit.com/), [SparkFun](https://www.sparkfun.com/), [Pimoroni](https://shop.pimoroni.com/), [Gens ace EU](https://www.gensace.de/), [Gens ace / Tattu US](https://www.genstattu.com/), [HobbyKing](https://hobbyking.com/), [Horizon Hobby](https://www.horizonhobby.com/), [EEMB high-power LiPo](https://www.eemb.com/products-58), [Jauch](https://www.jauch.com/), [Molicel](https://www.molicel.com/).
- Protection: TI BQ2970 datasheet and design example ([ti.com BQ2970](https://www.ti.com/product/BQ2970)); ABLIC S-82K1B datasheet ([ablic.com](https://www.ablic.com/)).
- Connectors: [JST VH](https://www.jst-mfg.com/product/detail_e.php?series=228), Molex Micro-Fit 3.0 ratings from the Digi-Key product pages of 43650-0200 and 43030-0038.
