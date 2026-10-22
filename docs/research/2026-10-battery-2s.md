# Two-cell (2S) battery architecture (ADR 0011, branch C)

- **Date:** 2026-10-22. All stock and price figures were captured on 2026-10-22.
- **Question:** can a two-cell series (2S) pack, with a 2S charger and the power tree changes it implies, meet the full output budget of [ADR 0011](../adr/0011-battery-path-rated-for-the-full-output-budget.md) (BRD-050) within the product rules, and how does it compare with keeping 1S at the lower budget (branch A)?
- **Inputs:**
  - [ADR 0007](../adr/0007-off-the-shelf-battery.md), [ADR 0008](../adr/0008-battery-technology-ready-for-lihv.md), [ADR 0011](../adr/0011-battery-path-rated-for-the-full-output-budget.md), [ADR 0012](../adr/0012-headphone-output-stage.md);
  - [battery for the full output budget](2026-10-battery-high-current.md) (why no 1S pack works) and [battery selection](2026-10-battery-selection.md);
  - [power tree v0](../specs/power-tree-v0.md) §2, §3, §4.6, §4.7, §4.10 and [BOM v1](../specs/bom-v1.md);
  - [T1 requirements](../../../t1/docs/requirements/README.md) T1-031 to T1-039, [t1 ADR 0003](../../../t1/docs/adr/0003-tentative-body-size.md) and the [battery-life analysis](../../../t1/docs/research/2026-10-battery-life-analysis.md);
  - part sheets in `libs/parts/` (input ratings of every part fed from VSYS).
- **Conventions:**
  - **UNVERIFIED** means no primary source was read in this session.
  - **Est.** marks an engineering estimate, to be replaced by simulation or measurement (T1-026).
  - Dimensions are T × W × L in mm. Prices are USD at qty 1 unless stated.
  - Nothing here edits an ADR or the BOM.

> **How this was gathered, and its limits.**
>
> - **Read directly:** TI datasheets BQ25798 (SLUSDV2C, June 2026, sha256 `163e4568…f1e222`), BQ28Z610-R1 (SLUSE07B, sha256 `d7506515…1c4da0`) and BQ29209 (SLUSA52C, sha256 `009f7245…c2d1ce`); TI product pages for BQ25798, BQ28Z610-R1, TPS62903 and TPS62136; mainline Linux sources (`drivers/mfd/bq257xx.c`, `drivers/power/supply/bq257xx_charger.c`, `bq27xxx_battery_i2c.c`, `sbs-battery.c`, `max1720x_battery.c`) and the commit history of `bq257xx.c`; Debian kernel configuration (`debian/config/config` and `debian/config/arm64/config`, branch `debian/latest`); Digi-Key keyword listings; FindChips; product pages of Adafruit, SparkFun, DFRobot and Gens ace / Tattu (genstattu.com).
> - **Not covered:** web search was unavailable (session budget used up), so only pages reachable by direct URL were read. Mouser and Farnell listing pages timed out (Mouser stock below comes through FindChips). The MikroElektronika and Seeed catalogs, BatterySpace and Tenergy did not render or returned 404. EEMB and Jauch list 2S packs only through quotes or pages that were not reached. Pimoroni was not re-checked. The BQ25792 datasheet download failed; the BQ40Z50 and MAX17320 datasheets were not read.
> - **Not measured:** nothing here was simulated or tested.

---

## 0. Summary

1. **No stocked 2S pack meets the criteria.** No off-the-shelf 2S Li-ion or LiPo pack was found that is in authorized stock, fits the 10.9 × 50.5 × 63.8 mm pocket, has a protection circuit (PCM) and a published continuous rating of at least 3.0 A (§2).
   - The stocked 2S packs that were found are either **hobby packs** (18–21 mm thick, no PCM, no safety report published) or **2S 18650 packs** (20 mm thick, excluded for the same reason as 1S cylindricals).
   - The two flat 2S LiPo packs at Digi-Key (GlobTek, 14–15 mm thick) have **zero stock** and are too thick.
   - A flat 2S pack made of two 5 mm cells stacked would fit the pocket. None was found in a catalog with stock; makers list it only by quote (T1-038).
2. **The electronics side of 2S is viable with stocked parts** (§3, §4):
   - **Charger:** TI **BQ25798** (1–4S buck-boost, 3.6–24 V input, 5 A charge, 6 A continuous battery discharge, NVDC power path; Mouser 9,488). Its mainline driver is **not** in place: mainline `bq257xx` binds only the BQ25703A and the **BQ25792**, and Debian leaves `MFD_BQ257XX` off. The BQ25792, which mainline supports, has thin authorized stock (Mouser 34).
   - **Protection, balancing and gauge (board side, if the pack has none):** TI **BQ28Z610-R1** (1–2S gauge with integrated protection, high-side N-FET drive and internal cell balancing; Mouser 5,765; mainline `bq27xxx_battery` binds `ti,bq28z610`), plus a **BQ29209** secondary overvoltage protector with balancing (Mouser 7,884). The MAX17055 is a 1-cell gauge and is dropped.
   - **Power tree:** everything fed from VSYS today is rated ≤ 5.5 V (RK809, RK860, TPS62826, TPS65131, TPS61169, LP5521, MAX98357A, TLV62569, TPS22919). A 2S tree needs a **pre-regulator** from VSYS (6.0–8.8 V) to a fixed ≈ 3.8 V rail that feeds the existing 1S tree unchanged. The 5 V HAT/USB-C source becomes a **buck** from VSYS instead of the TPS61089 boost.
3. **Effect on autonomy (est.):** the pre-regulator adds a conversion stage to the playback load. At the same pack energy, the core session drops by about **8–12 %** (§5).
4. **Effect on the battery path:** the full output budget drops from 4.8 A at 3.3 V to about **2.4 A at 6.6 V** (§4.1). Every element of the battery chain then runs far inside its rating, and the pack needs a continuous rating of only **≥ 3.0 A**. A pack of two standard energy cells of about 1.5 Ah each could carry that at about 2C (est.); no high-rate cell is needed.
5. **Verdict:** **2S is not viable within the product rules today.** The blocker is the same as for 1S: **no off-the-shelf, stocked, protected pack** that fits. It also carries a software gap: the BQ25798 has no mainline entry, and the mainline-supported BQ25792 is not well stocked. Branch A (1S, Adafruit 328, 1.6 A budget) stays the only branch that complies with T1-038 and T1-029 today. 2S becomes the strongest option **if** the maintainers grant a T1-038 exception for a quoted pack (branch B), because a quoted 2S pack can be built from ordinary energy cells, while a quoted 1S pack needs a high-rate cell (§7).

---

## 1. Criteria applied

Derived from ADR 0011 item 1 for the same power, and from the brief:

| # | Criterion | 1S (ADR 0011) | 2S (this study) |
|---|---|---|---|
| C1 | Continuous discharge rating | ≥ 6.0 A | **≥ 3.0 A** (2.4 A at 80 %, §4.1) |
| C2 | Protection | Pack PCM, over-current trip ≥ 6.0 A, short circuit | Pack PCM with 2S over-/under-voltage per cell, over-current trip ≥ 3.0 A, short circuit; **or** a maker-documented recommendation for board-side protection |
| C3 | Leads and pack connector | ≥ 6.9 A per pole, latching | **≥ 3.4 A per pole** (2.4 A at 70 %), latching |
| C4 | Energy | ≥ 2,000 mAh at 1S (≈ 7.4 Wh) | **≥ 7.4 Wh** (T1-012 reads "≥ 2,000 mAh"; for 2S the equivalent is ≥ 1,000 mAh at 7.4 V. The maintainers have not stated how T1-012 applies to 2S: **open question**) |
| C5 | Fit | Pocket below | Same pocket |
| C6 | Certification | UN 38.3; IEC 62133-2 for the Commercial edition | Same |
| C7 | Chemistry | 4.2 V or LiHV (ADR 0008) | Same, per cell |
| C8 | Sourcing | Off the shelf, authorized stock (T1-038, T1-029) | Same |

**Pocket:** **10.9 × 50.5 × 63.8 mm** for the tentative 59.5 × 94.3 × 24 mm body (t1 ADR 0003), from the pocket arithmetic in the [battery-life analysis](../../../t1/docs/research/2026-10-battery-life-analysis.md) §11.3 (t_max already includes 10 % swelling). ADR 0011 states 11.8 × 53.5 × 63.25 mm for the 62.5 × 93.75 × 25 mm body. A flat 2S pack fits the 10.9 mm pocket only as **two cells stacked**, each ≤ about 5.2 mm thick including the wrap (est.); two cells side by side need about 2 × 34 mm of width, more than 50.5 mm.

---

## 2. Packs

### 2.1 2S packs found

Stock and prices are at Digi-Key unless the row says otherwise.

| Pack | Capacity / energy | T × W × L | Continuous rating | PCM | Leads / connector | Safety documents seen | Stock / price | Fails |
|---|---|---|---|---|---|---|---|---|
| SparkFun **PRT-11855** | 1,000 mAh / 7.4 Wh | **18** × 35 × 70 | 25C (vendor claim) | **None** ("care needed to avoid short circuits") | Deans discharge plug, JST-XH balance plug | MSDS only | Digi-Key 38 @ $17.04; SparkFun in stock @ $16.95 | C2, C5, C6 |
| Tattu 2500mAh 2S1P (SKU TAA25002SGDC, goggle pack) | 2,500 mAh / 18.5 Wh | **18.6** × 38.1 × **73.7** | Not stated | Not stated | 14 AWG, DC 5.5 mm plug, JST-XH 3-pin balance | ISO 9001 / 14001 (factory), no UN 38.3 or IEC 62133 seen | genstattu.com "20–100" @ $19.59 | C1 unknown, C2, C5, C6 |
| Gens ace G-Tech 2300mAh 2S 35C (GEA232S35E2GT) | 2,300 mAh / 17.0 Wh | **21** × 31 × **101** | 35C (vendor claim) | Not stated | 18 AWG, IEC2 plug | Same as above | genstattu.com "over 100" @ $23.99 | C2, C5, C6 |
| GlobTek BL1800P0639602S1PPLB | 1,800 mAh / 13.3 Wh | **14** × 43.5 × 60 | Not stated | Not read | Leads with connector | Not read | Digi-Key **0** @ $16.09 | C5, C8 |
| GlobTek BL1200F7034452S1PQAN | 1,200 mAh / 8.9 Wh | **15** × 35 × 46 | Not stated | Not read | Leads | Not read | Digi-Key **0** @ $21.99 | C5, C8 |
| Jauch LI18650JP2S1P+PCM+2 WIRES 70MM | 3,250 mAh / 23.4 Wh (7.2 V) | **20** × 38 × 69 | Not read | PCM | Wires | Not read | Digi-Key 1,439 @ $25.68 | C5 (cylindrical, see [high-current study](2026-10-battery-high-current.md) §3) |
| Jauch LI18650JLS HB 2S1P+PCM+PTC | 3,350 mAh / 24.1 Wh (7.2 V) | **20** × 38 × 69 | Not read | PCM + PTC | Wires | Not read | Digi-Key 312 @ $18.21 | C5 |
| DFRobot FIT0137 (7.4 V 2,500 mAh) | — | — | — | — | — | — | **Discontinued** | C8 |

Sources: [Digi-Key, keyword "7.4 V"](https://www.digikey.com/en/products/filter/batteries-rechargeable-secondary/91?keywords=7.4%20V), [keyword "2S1P"](https://www.digikey.com/en/products/filter/batteries-rechargeable-secondary/91?keywords=2S1P), [keyword "7.2V lithium"](https://www.digikey.com/en/products/filter/batteries-rechargeable-secondary/91?keywords=7.2V%20lithium); [SparkFun PRT-11855](https://www.sparkfun.com/products/11855); [Tattu 2500mAh 2S](https://www.genstattu.com/tattu-2500mah-2s1p-fatshark-goggles-lipo-battery-pack-with-dc3-5mm-plug.html); [Gens ace 2300mAh 2S](https://www.genstattu.com/gens-ace-g-tech-2300mah-2s-35c-7-4v-lipo-battery-pack-with-iec2-plug/); [DFRobot search](https://www.dfrobot.com/search-lipo.html).

**Reading:**

- Hobby 2S packs are built thick (two cells of 8–10 mm stacked, or long RC sticks). None has a PCM or a published UN 38.3 or IEC 62133 report, as the brief expected. They are recorded for comparison only.
- No authorized distributor or maker shop that was reached lists a **flat** 2S LiPo pack (two cells of about 5 mm) with stock. Adafruit lists only 1S packs; DFRobot's 2S packs are discontinued; EEMB and Jauch offer 2S assemblies on request (**UNVERIFIED** part numbers, quote only).
- The Digi-Key keyword sweep is partial: the site's keyword search returns only listings whose title contains the keyword, so a 2S pack described only by its cell code may have been missed. Mouser and Farnell were not read (§0 limits).

### 2.2 Two stocked 1S packs in series: rejected

The only stocked way found to put about 9 Wh of 2S into the pocket is two protected 1S packs in series, stacked. For example, two **Adafruit 258** (1,200 mAh, 5 × 34 × 62 mm, PCM with short-circuit protection, JST-PH lead rated 2 A, UN 38.3 report available, in stock @ $9.95; [product page](https://www.adafruit.com/product/258)) give 8.9 Wh in 10 × 34 × 62 mm. It is rejected under BRD-049:

- Each PCM is a 1S protector. Neither sees the other cell, and nothing balances the pair. Adafruit publishes no guidance on series use.
- The current is still capped by the JST-PH lead (2 A, so 1.4 A at 70 %), about 9 W at 6.6 V: below the 3.0 A of C1.
- Two leads and two connectors per pack double the user-replaceable interfaces.

---

## 3. Charger, protection, balancing and gauge

### 3.1 Charger

| Part | Key figures (source) | Mainline Linux | Debian | Authorized stock (FindChips) | Verdict |
|---|---|---|---|---|---|
| **TI BQ25798RQMR** | 1–4S buck-boost; VBUS 3.6–24 V (30 V absolute maximum); IVBUS ≤ 3.3 A; charge ≤ 5 A; **IBAT discharge 6 A RMS continuous, 10 A for ≤ 1 s**; BATFET 11 mΩ; IBAT_OCP 9.3 A min; 2S defaults VSYSMIN 7.0 V, VREG 8.4 V, VREG range at 2S 5.0–9.99 V (10 mV steps, so 2S LiHV at 8.7–8.9 V is in range); IQ_BAT 17 µA (BATFET on, no VBUS); 750 kHz / 1.5 MHz; OTG 2.8–22 V up to 3.32 A; MPPT and backup mode; QFN-29 4 × 4 mm; **no cell balancing** (SLUSDV2C §1, §6.3, §6.5, Table 7-2) | **No.** `bq257xx` matches only `ti,bq25703a` and `ti,bq25792`. The MFD probe reads no part-ID register, so a BQ25798 would bind as a BQ25792, but that is not a supported configuration (**UNVERIFIED** register compatibility) | `MFD_BQ257XX` not set ([component selection](2026-10-component-selection.md) §2.1) | Mouser **9,488** @ $2.96–5.27 | Hardware fits; needs an upstream ID entry, DKMS until Debian enables it |
| TI BQ25792RQMR | Same family without MPPT and backup mode (**UNVERIFIED**: datasheet download failed; earlier figures in [component selection](2026-10-component-selection.md) §2.1) | **Yes**: commit `9adbe53e` "mfd: bq257xx: Add BQ25792 support" (Alexey Charkov, 2026-06-17), placed in v7.2 by the component selection | Off | Mouser **34** @ $4.16–7.36 (Maritex and Win Source list more, not authorized distributors per this study) | Fails availability (T1-028, T1-029) |
| TI BQ25895 (current) | **1S only** | Yes (`bq25890_charger`) | `CHARGER_BQ25890=m` (arm64) | Mouser 3,608 | Not usable at 2S |

- The BQ25798 cannot run OTG while it charges, like the BQ25895 (power tree §1 finding 9). The separate HAT/USB-C source stays (§4).
- At 2S the full budget draws about 2.4 A (§4.1), **40 %** of the 6 A continuous discharge rating.

Sources: [BQ25798 datasheet](https://www.ti.com/lit/ds/symlink/bq25798.pdf), [BQ25798 product page](https://www.ti.com/product/BQ25798), [bq257xx MFD](https://github.com/torvalds/linux/blob/master/drivers/mfd/bq257xx.c), [bq257xx charger](https://github.com/torvalds/linux/blob/master/drivers/power/supply/bq257xx_charger.c), [FindChips BQ25798RQMR](https://www.findchips.com/search/BQ25798RQMR), [FindChips BQ25792RQMR](https://www.findchips.com/search/BQ25792RQMR).

### 3.2 Protection and balancing (needed on the board only if the pack has none)

| Part | Function (source) | Key figures | Stock | Note |
|---|---|---|---|---|
| **TI BQ28Z610-R1** (DRZR) | 1–2S Impedance Track gauge **and** primary protection, high-side N-FET drive, internal cell balancing, SHA-1 (SLUSE07B §1, §3) | VCC 2.2–26 V; OCD threshold 8.3–50 mV (RSNS = 0) or 16.6–100 mV (RSNS = 1); SCD1/SCD2 22.2–100 mV (RSNS = 0); balance FET ≤ 200 Ω; 250 µA normal, 100 µA sleep, 0.5–2 µA shutdown (§7) | Mouser **5,765** @ $2.42–4.56 ([FindChips](https://www.findchips.com/search/BQ28Z610)) | With a 5 mΩ sense, OCD is settable from about 1.7 A to 10 A, so a 3.0–4.0 A trip is in range. Internal balancing at ≤ 200 Ω gives about 20 mA at 4 V per cell (est.) |
| **TI BQ29209** (DRBR) | 2S **secondary** overvoltage protection with automatic cell balancing (SLUSA52C §1) | OVP 4.30 or 4.35 V fixed (variant), ±25 mV at 0–60 °C; balancing up to 15 mA internal; ICC < 3 µA | Mouser **7,884** @ $0.50–1.07 ([FindChips](https://www.findchips.com/search/BQ29209DRBR)) | Drives a fuse or FET through OUT. A 4.30 V threshold is below LiHV charge voltages, so a LiHV pack would need a different secondary protector (**UNVERIFIED** variant table) |
| TI BQ77905, BQ7718 (named in the brief) | Not read in this session | — | — | BQ77905 is a 3–5S part by its family naming (**UNVERIFIED**); not needed for 2S |

**What protection the board needs.** ADR 0011 requires the PCM **in the pack**, because the pack is user-replaceable. With a protected 2S pack, the board keeps a fuse (§4.4) and adds nothing else. With an unprotected pack (every hobby pack in §2.1), the board would need the BQ28Z610-R1 with two N-FETs, a sense resistor and the BQ29209, and the pack would need a balance lead to the board. That moves pack-level safety onto the board. It is technically possible with stocked parts; whether it satisfies ADR 0011 is a maintainers' call.

### 3.3 Fuel gauge

| Option | Cells | Linux | Debian (arm64) | Stock | Verdict |
|---|---|---|---|---|---|
| ADI MAX17055 (current) | **1S** (part sheet) | `max17042_battery` | Off (DKMS today) | — | Not usable at 2S |
| **TI BQ28Z610-R1** | 1–2S | `bq27xxx_battery_i2c` binds `ti,bq28z610` | `BATTERY_BQ27XXX=m`; the generic config sets `BATTERY_BQ27XXX_I2C` "not set" and the arm64 file does not override it, so the I2C front end may be off (**UNVERIFIED**) | Mouser 5,765 | **Preferred:** gauge, protection and balancing in one 4 × 2.5 mm part |
| TI BQ40Z50-R2 | 1–4S gauge with protection and balancing (**UNVERIFIED**, datasheet not read) | `sbs-battery` (generic `sbs,sbs-battery`; the driver names only BQ20Z65/75) | `BATTERY_SBS=m` | Mouser 8,465 @ $2.48–4.58 ([FindChips](https://www.findchips.com/search/BQ40Z50RSMR-R2)) | Debian-enabled path; larger part and more complex configuration |
| ADI MAX17320 | 2–4S (**UNVERIFIED**) | **None**: `max1720x_battery` binds only `maxim,max17201` | — | Not checked | Rejected: no driver |

Sources: [bq27xxx_battery_i2c.c](https://github.com/torvalds/linux/blob/master/drivers/power/supply/bq27xxx_battery_i2c.c), [sbs-battery.c](https://github.com/torvalds/linux/blob/master/drivers/power/supply/sbs-battery.c), [max1720x_battery.c](https://github.com/torvalds/linux/blob/master/drivers/power/supply/max1720x_battery.c), [Debian config](https://salsa.debian.org/kernel-team/linux/-/blob/debian/latest/debian/config/config), [Debian arm64 config](https://salsa.debian.org/kernel-team/linux/-/blob/debian/latest/debian/config/arm64/config), [BQ28Z610-R1 product page](https://www.ti.com/product/BQ28Z610-R1).

---

## 4. Power tree impact

### 4.1 Battery current for the full output budget at 2S

Same loads as power tree §4.7, at the 2S equivalent of the 3.3 V shed point: **VSYS = 6.6 V** (3.3 V per cell), below which OpenDAP OS sheds HAT and USB-C load.

| Load | Output | Converter, efficiency | From VSYS |
|---|---|---|---|
| HAT_5V + USB-C source | 5.1 V × 1.6 A = 8.16 W | Buck from VSYS, 0.93 (est.) | 8.77 W |
| HAT_3V3 | 3.3 V × 1.0 A = 3.3 W | Buck from VSYS, 0.90 (est.) | 3.67 W |
| System, screen on with CPU load | 3.0 W (est., as §4.7) | Pre-regulator, 0.92 (est.) | 3.26 W |
| **Total** | | | **15.7 W → 2.38 A at 6.6 V** |

- 1S figure for the same budget: 15.9 W → 4.8 A at 3.3 V (power tree §4.7). The 2S current is **about half**.
- Path drop at 2.4 A with about 40 mΩ in the path (BATFET 11 mΩ, fuse, sense, shunt, connector; est.): about 0.1 V, against about 0.24 V at 4.8 A for 1S.
- Path dissipation: about 0.23 W, against about 1.15 W for 1S at 4.8 A and 50 mΩ (est.).

### 4.2 What changes, part by part

Every part below is fed from VSYS in the current tree. Input ratings are from the part sheets in `libs/parts/`.

| Part (BOM line) | Input rating | At 2S (VSYS 6.0–8.8 V, OVP up to ≈ 9.9 V) | Change |
|---|---|---|---|
| RK809-5 VCC1–4 (2) | 2.7–5.5 V | Exceeded | Move to the **3.8 V pre-regulated rail** |
| RK860-0 (3) | T1 range 3.5–4.4 V (device rating **UNVERIFIED**) | Exceeded | Pre-regulated rail (3.8 V is inside 3.5–4.4 V) |
| TPS62826 vcc3v3_sys (6) | 2.4–5.5 V | Exceeded | Pre-regulated rail |
| TPS65131 ±6 V (22) | 2.7–5.5 V | Exceeded | Pre-regulated rail. A fixed 3.8 V input removes the 3.0–3.5 V low-battery corner where ADR 0012 puts the inverter at 72–79 % of its current limit (improvement, **est.**; the margin needs the simulation ADR 0012 already asks for) |
| TPS61169 backlight (51) | 2.7–5.5 V | Exceeded | Pre-regulated rail |
| LP5521 (105), MAX98357A (32) | 2.7–5.5 V, 2.5–5.5 V | Exceeded | Pre-regulated rail |
| TPS22919 DAC_VP (50) | 1.6–5.5 V | Exceeded | Pre-regulated rail (CS43198 VP 3.0–5.25 V) |
| TPS62840 AUDIO_2V2 (27) | 1.8–6.5 V | Exceeded above 6.5 V | Pre-regulated rail |
| TPS7A2031 MCLK_3V1 (29) | 1.6–6.0 V | Exceeded | Pre-regulated rail (≥ 3.4 V needed: 3.8 V gives 0.7 V headroom) |
| TLV62569 HAT_3V3 (38) | 2.5–5.5 V | Exceeded | **Replace** with a buck from VSYS: TPS62902 (2 A, 3–17 V, same family as below; stock **UNVERIFIED**) or TPS62903 |
| TPS61089 5.1 V boost (91, 92) | Boost, needs VIN < VOUT | Cannot work | **Replace** with a buck from VSYS: **TPS62903** (3–17 V, 3 A, 0.4–5.5 V out, 4 µA Iq, 1.5 × 2 mm; Mouser 2,589 @ $0.99–2.02). Dropout at 1.6 A ≈ 1.6 × (62 + 30 mΩ DCR) ≈ 0.15 V (est.), so 5.1 V holds down to about 5.3 V |
| BQ25895 charger (39, 40) | 1S | — | **Replace** with the BQ25798 (§3.1) and its inductor (TI recommends 1 µH at 1.5 MHz per its curves; part selection open) |
| MAX17055 gauge (42, 43) | 1S | — | **Replace** with the BQ28Z610-R1 (§3.3) |
| TPS259470 eFuses (44) | 2.7–23 V | Fed from the new bucks | No change |
| TPS2121 mux (45), FUSB302B (41), TVS2200 (64) | Input side | Unchanged (VBUS 5–12 V into the BQ25798, 3.6–24 V) | No change |
| INA236 VSYS shunt (54) | Bus up to 48 V (**UNVERIFIED** here) | Fine | No change |
| Battery fuse (104) | — | 2.4 A design | 4 A NANO2 in the same footprint (0451004.MRL, stock **UNVERIFIED**): 60 % |
| Battery connector (47) | JST-PH 2 A | 2.4 A > rating | Molex Micro-Fit 3.0 with crimp 43030-0001 (5 A, AWG 20–24; [high-current study](2026-10-battery-high-current.md) §4.1): 48 %. A 2S pack needs at least P+, P− and, with board-side protection, the mid-cell tap and NTC: a 4-pin header (43650-0400, stock **UNVERIFIED**). A Micro-Fit plug also prevents plugging a 1S JST-PH pack into a 2S board |

**New part: the pre-regulator (VSYS → 3.8 V "VSYS_LV").** The rail feeds the whole current 1S tree. Its load is the system plus the headphone stage: up to about 3 W system and 1.4–1.6 A from VSYS at full-scale balanced output (ADR 0012), about **1.6 A continuous and 2 A peak at 3.8 V (est.)**.

- **TPS62136** (3–17 V, 4 A, 0.8–12 V out, 18 µA Iq, 100 % duty, 3 × 2 mm; Mouser 2,196 @ $1.16–2.32; Arrow 1,536): 2 A peak is **50 %** of 4 A.
- TPS62903 (3 A, 4 µA Iq) has the lower quiescent current but sits at 67 % at the 2 A peak; acceptable under the 80 % rule, with less room.
- The rail voltage is a design choice: 3.8 V keeps every existing part inside the range it was chosen for. A higher value (up to about 5.0 V) would help the TPS65131 and the speaker amplifier but costs headroom loss in the MCLK LDO and DAC_VP (est.); left open.

Sources: [TPS62903](https://www.ti.com/product/TPS62903), [FindChips TPS62903RPJR](https://www.findchips.com/search/TPS62903RPJR), [TPS62136](https://www.ti.com/product/TPS62136), [FindChips TPS62136RGXR](https://www.findchips.com/search/TPS62136RGXR).

### 4.3 Quiescent current (battery only, BATFET on, playback rails off)

| Item | 1S tree | 2S tree |
|---|---|---|
| Charger | BQ25895 32 µA at ≈ 3.7 V ≈ 0.12 mW | BQ25798 17 µA at 7.4 V ≈ 0.13 mW |
| Gauge / protection | MAX17055 (**UNVERIFIED** figure) | BQ28Z610-R1 100 µA sleep at 7.4 V ≈ 0.74 mW; BQ29209 < 3 µA |
| Pre-regulator | — | TPS62136 18 µA (TPS62903 4 µA) at 7.4 V ≈ 0.13 mW (0.03 mW) |

The 2S tree adds below 1 mW of standby draw (est.). The gauge's sleep current dominates and depends on its configuration (SLUSE07B note 1).

### 4.4 BRD-049 margins of the new parts

| Item | Rating (source) | Design load | Use | Verdict |
|---|---|---|---|---|
| BQ25798 battery discharge | 6 A continuous, 10 A ≤ 1 s, OCP 9.3 A min (SLUSDV2C §6.3, §6.5) | 2.4 A | **40 %** | OK |
| BQ25798 input | IVBUS 3.3 A (§6.3) | IINLIM ≤ 2.6 A to keep 80 % (est.; today 2.0 A) | ≤ 80 % | OK |
| BQ25798 SW output | ISW 5 A (§6.3) | Charge plus system on adapter, ≤ 4 A by IINLIM (est.) | ≤ 80 % | To set in the design |
| Pre-regulator TPS62136 | 4 A; VIN 17 V | 1.6 A / 2 A peak (est.); VSYS ≤ 9.9 V | 40–50 %; 58 % of VIN | OK |
| 5.1 V buck TPS62903 | 3 A; VIN 17 V | 1.6 A design; 1.66 A eFuse ceiling | 55 % | OK. With both eFuses at their 1.66 A ceilings (software fault), the buck's own current limit bounds the fault, as the TPS61089 limit does today (limit value **UNVERIFIED**) |
| HAT_3V3 buck TPS62902 | 2 A | 1.0 A; 1.15 A ceiling | 58 % | OK (same as the TLV62569 today) |
| Battery fuse 4 A | 4 A | 2.4 A | 60 % | OK (≤ 75 %) |
| Battery connector Micro-Fit 3.0, AWG 20–24 crimp | 5 A per contact | 2.4 A | 48 % | OK (≤ 70 %) |
| Pack cell rating | ≥ 3.0 A (C1) | 2.4 A | ≤ 80 % | Pack not found (§2) |
| BQ28Z610-R1 protection FETs (if fitted) | Per FET choice | 2.4 A | — | Pick FETs for ≤ 80 % and an OCD trip of 3.0–4.0 A |

---

## 5. Autonomy

Model: the [battery-life analysis](../../../t1/docs/research/2026-10-battery-life-analysis.md) §6.1, scenario 1 (screen off, 3.5 mm SE), battery-side draw **0.39 / 0.66 / 1.49 W** (best / typical / worst), 90 % of label energy usable. In the 2S tree the same loads sit behind the pre-regulator. Its efficiency at 0.1–0.4 A from 6.6–8.4 V to 3.8 V is taken as **0.88–0.92** (est.; datasheet curves not read). The 2S draw is therefore 1.09–1.14 × the 1S draw: typical **0.72–0.75 W**.

| Pack (label energy) | 1S tree, typical | 2S tree, typical (est.) | 2S, worst (est.) |
|---|---|---|---|
| 9.4 Wh (Adafruit 328 class) | 12.8 h | 11.3–11.7 h | 5.0–5.2 h |
| 8.9 Wh (two Adafruit 258 stacked, §2.2, rejected) | — | 10.7–11.1 h | 4.7–4.9 h |
| ≈ 12 Wh (105060-class volume; for 2S, two ≈ 5 mm cells stacked, quote only) | 16.3 h | 14.4–15.0 h | 6.4–6.7 h |

- These rows predate ADR 0012, which lowers the core session by about 11 % on any pack (12.8 → 11.4 h). The two effects multiply: a 9.4 Wh 2S pack lands at about **10.1–10.4 h** typical (est.), still above the 8 h warning of T1-039.
- A 2S pack has two PCMs' worth of tabs and wrap in the same pocket, which costs some energy against one 10 mm cell (**UNVERIFIED** amount; no flat 2S datasheet was read).
- The worst case stays below the 6 h red line for packs under about 12 Wh, as it does at 1S. The measurement gate of t1 ADR 0003 is unchanged.

---

## 6. Size, case and thermal

- **Pocket:** unchanged for a flat stacked 2S pack (§1). Hobby 2S packs (18–21 mm) and 2S 18650 packs (20 mm) do not fit any body within T1-031.
- **Lead exit:** a 2S pack with a balance lead or a 4-pin Micro-Fit plug needs more room at the lead end than the 2.5 mm allowance of the battery selection §2.3 (**UNVERIFIED** how much; the Micro-Fit band sits outside the pocket, as in the [high-current study](2026-10-battery-high-current.md) §6).
- **Board area (est.):** the BQ25798 has the same 4 × 4 mm footprint as the BQ25895. The TPS61089 and its 4 × 4 mm inductor go; the pre-regulator, the 5.1 V buck and their inductors come in; the MAX17055 becomes a BQ28Z610-R1 (4 × 2.5 mm), with two FETs and a BQ29209 only for board-side protection. Net about **+20–40 mm²** (est.).
- **Thermal (est.):**
  - Battery path at the full budget: about 0.23 W instead of about 1.15 W (§4.1).
  - The pre-regulator dissipates about 0.06 W at playback (0.7 W × 8 %) and about 0.5 W at the 6 W peak system load.
  - The 5.1 V buck at 8.16 W out and 0.93 dissipates about 0.6 W, against about 1.1 W for the TPS61089 boost at 0.88.
  - Charging: about 12.6 W into the pack at 1.5 A × 8.4 V would come close to the current 15 W input cap once the system load is added. The charge current follows the pack (0.5C of a 1.5 Ah 2S pack is 0.75 A, about 6.3 W), similar to the 1S charge power today.
- **Safety:** 8.4–8.9 V stays far below any SELV limit. UN 38.3 and IEC 62133-2 apply to 2S packs as to 1S. A 2S pack needs per-cell protection and balancing; that is the pack maker's job when the PCM is in the pack, and the board's job otherwise (§3.2). A different, keyed connector keeps 1S and 2S packs from being swapped by mistake.

---

## 7. Verdict and comparison with branch A

| | **Branch A: 1S at the lower budget** | **Branch C: 2S** |
|---|---|---|
| Pack | Adafruit 328, stocked, UN 38.3 report ([ADR 0011](../adr/0011-battery-path-rated-for-the-full-output-budget.md) item 3) | **None stocked that fits with a PCM** (§2); quote only |
| On-battery output | About 0.4 A at 5.1 V for HAT_5V and the USB-C source together; full headphone output only under an OS ceiling (ADR 0012) | Full budget (1.5 A at 5.1 V + 1.0 A at 3.3 V) at about 2.4 A from the pack |
| Charger | BQ25895, mainline, Debian `=m`, stocked | BQ25798: stocked, **not in mainline** (BQ25792 is, but has thin stock); DKMS either way (`MFD_BQ257XX` off) |
| Gauge | MAX17055 (DKMS) | BQ28Z610-R1 (`bq27xxx`; Debian I2C front end **UNVERIFIED**) or BQ40Z50 (`sbs-battery`, Debian `=m`) |
| Power tree | As BOM v1.2 | + pre-regulator, boost → buck, 1S parts swapped (§4.2) |
| Autonomy, core session (typ., est.) | 12.8 h (11.4 h with ADR 0012) | About 9–12 % less at the same pack energy |
| BRD-049 | Met with the 1.6 A software budget and the 2.5 A fuse | Met with wide margins on paper (§4.4), once a pack exists |
| Product rules | Complies (T1-038, T1-029) | **Fails T1-038 / T1-029 at the pack**; software path needs upstream work (T1-011) |

**Conclusion:**

1. **2S is not viable within the product rules today.** Charger, protection, balancing, gauge and converters exist in authorized stock, but the pack does not: no off-the-shelf, stocked, protected 2S pack fits the pocket. The charger that fits the stock rule (BQ25798) also lacks a mainline driver entry.
2. **Branch A stays the compliant choice** until a pack appears: Adafruit 328, 1.6 A budget, about 0.4 A at 5.1 V for HAT and USB-C on battery.
3. **If the maintainers grant a T1-038 exception for the pack (branch B), 2S is the stronger form of it** (est.): a 2S pack of two ordinary ≈ 1.5 Ah, ≈ 5 mm energy cells at about 2C carries the full budget, while a 1S pack needs a ≥ 6 A high-rate cell that no maker lists in this size. It would come with a PCM and balancing in the pack, a Micro-Fit lead and UN 38.3 / IEC 62133-2 reports, and the board would take the BQ25798, the BQ28Z610-R1 (gauge only, or full protection), a 4 A fuse, the TPS62136 pre-regulator and the TPS62903 5.1 V buck.
4. **Before any 2S decision:** confirm BQ25798 register compatibility with the mainline BQ25792 support and send the ID entry upstream; confirm Debian's `BATTERY_BQ27XXX_I2C` on arm64; read the BQ40Z50 and BQ25792 datasheets; repeat the pack search on Mouser, Farnell and RS with web search available.

---

## 8. Sources

- Repository documents linked in the header.
- Datasheets: [TI BQ25798 (SLUSDV2C)](https://www.ti.com/lit/ds/symlink/bq25798.pdf), [TI BQ28Z610-R1 (SLUSE07B)](https://www.ti.com/lit/ds/symlink/bq28z610-r1.pdf), [TI BQ29209 (SLUSA52C)](https://www.ti.com/lit/ds/symlink/bq29209.pdf).
- Product pages: [BQ25798](https://www.ti.com/product/BQ25798), [BQ28Z610-R1](https://www.ti.com/product/BQ28Z610-R1), [TPS62903](https://www.ti.com/product/TPS62903), [TPS62136](https://www.ti.com/product/TPS62136).
- Linux: [drivers/mfd/bq257xx.c](https://github.com/torvalds/linux/blob/master/drivers/mfd/bq257xx.c) and its [commit history](https://github.com/torvalds/linux/commits/master/drivers/mfd/bq257xx.c), [bq257xx_charger.c](https://github.com/torvalds/linux/blob/master/drivers/power/supply/bq257xx_charger.c), [bq27xxx_battery_i2c.c](https://github.com/torvalds/linux/blob/master/drivers/power/supply/bq27xxx_battery_i2c.c), [sbs-battery.c](https://github.com/torvalds/linux/blob/master/drivers/power/supply/sbs-battery.c), [max1720x_battery.c](https://github.com/torvalds/linux/blob/master/drivers/power/supply/max1720x_battery.c); Debian [config](https://salsa.debian.org/kernel-team/linux/-/blob/debian/latest/debian/config/config) and [arm64 config](https://salsa.debian.org/kernel-team/linux/-/blob/debian/latest/debian/config/arm64/config).
- Stock: [FindChips](https://www.findchips.com/) (BQ25798RQMR, BQ25792RQMR, BQ28Z610, BQ29209DRBR, BQ40Z50RSMR-R2, TPS62903RPJR, TPS62136RGXR); [Digi-Key rechargeable batteries](https://www.digikey.com/en/products/filter/batteries-rechargeable-secondary/91).
- Packs: [Adafruit battery category](https://www.adafruit.com/category/574), [Adafruit 258](https://www.adafruit.com/product/258), [SparkFun PRT-11855](https://www.sparkfun.com/products/11855), [Gens ace / Tattu](https://www.genstattu.com/), [DFRobot](https://www.dfrobot.com/search-lipo.html), [EEMB LiPo packs](https://www.eemb.com/products-59).
