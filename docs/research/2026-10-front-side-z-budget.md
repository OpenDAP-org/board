# Front-side height of the main board under the display (2026-10)

- **Date:** 2026-10-24
- **Task:** E2.5 of the [electronics plan](https://github.com/opendap-project/t1/blob/main/docs/plans/2026-10-electronics-plan.md): constraint PCB-Z-03 and §9 item 1 of the [PCB design constraints](../specs/pcb-design-constraints.md). Decided in [ADR 0016](../adr/0016-front-side-height-under-the-display.md).
- **Question:** the thickness stack of the [battery selection](2026-10-battery-selection.md) §2.2 leaves 0.3 mm between the display module and the board, while the faceplate connector is 0.9 mm high and BRD-054 allows both sides populated. How much board area does BOM v1.7 need per side, and which way of making room under the display serves the product rules best?
- **Inputs:**
  - [BOM v1.7](../specs/bom-v1.md) (lines 1–128 and §5 passives) and the [parts-lib](https://github.com/opendap-project/parts-lib) sheets for package sizes and heights;
  - [t1 ADR 0003](https://github.com/opendap-project/t1/blob/main/docs/adr/0003-tentative-body-size.md) (59.5 × 94.3 × 24 mm body), [ADR 0014](../adr/0014-two-cell-battery.md) (2S pack sized to the 10.9 × 50.5 × 63.8 mm pocket);
  - [faceplate-touch ADR 0001](https://github.com/opendap-project/faceplate-touch/blob/main/docs/adr/0001-focus-lcds-e35gh-display.md) and the [E35GH sheet](https://github.com/opendap-project/parts-lib/blob/main/Focus-LCDs/E35GH-I-MW800-CB.md): module 54.46 × 82.94 × 5.50 mm, operating temperature −20 to +70 °C, tails exit the bottom edge and bend behind the module;
  - [FH35C-51S sheet](https://github.com/opendap-project/parts-lib/blob/main/Hirose/FH35C-51S-0.3SHW.md): 16.9 × 3.2 mm, 0.9 ± 0.1 mm high, actuator opens to 1.8 mm;
  - [battery-life analysis](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-battery-life-analysis.md) §6.1, §11.3 and the [2S study](2026-10-battery-2s.md) §5;
  - T1 requirements T1-009, T1-031, T1-032, T1-035, T1-037, T1-039; board requirements BRD-049, BRD-054.
- **Conventions:** **UNVERIFIED** marks a value without a primary source read in this session; **est.** marks an engineering estimate. Areas are in mm², heights are above the board surface. Nothing here was laid out, simulated or measured.

## 0. Summary

1. **The board needs both sides, and needs them under the display.** BOM v1.7 adds up to about **4,810 mm² of courtyard** (§2). With a placement and routing factor of **1.7** (1.5–1.9) derived from the Radxa ZERO 3W (§3), it needs about **7,800 mm²** (7,000–8,600) of board. The board offers about **4,880 mm² per side** (55.3 × 90.1 mm, less the bosses), and the display shadows **91 %** of the front (54.46 × 82.94 mm on 55.3 × 90.1 mm).
2. **Option (b), single-sided under the display, does not fit:** about 5,350 mm² usable against 7,000–8,600 mm² needed, short by **1,650–3,250 mm²** (§4.2). Option (c), a recess for the FH35C only, solves the connector but not the area, so it fails for the same reason. Option (d), folding the faceplate flex to the back, also leaves the area problem.
3. **About 2,100–3,700 mm² of parts must sit on the front, under the display** (§4.1). All of them can be parts of **1.0 mm or less** (passives up to 0603, QFN/DFN/SON packages, the FH35C), so a 1.0 mm front zone carries them at 48–86 % use. A 0.8 mm zone would fit only with no slack; a 1.5 mm zone (SoC and shields on the front) costs 0.5 mm more and puts the SoC's heat against the LCD.
4. **Decision (ADR 0016):** front zone **1.0 mm**, display-to-board gap **1.3 mm** (1.0 + 0.3 clearance), taken **from body thickness, not from the battery**: the tentative body goes from 24.0 to **25.0 mm** (T1-031 maximum). The battery pocket and the ADR 0014 pack stay as they are.
5. **Why not from the battery:** each millimetre taken from the battery layer costs about **8.3 %** of pack energy (§5). 1.0 mm would move the pessimistic core session from about 5.7–6.0 h to about **5.2–5.5 h** (est., with the ADR 0012 correction), further below the 6 h red line of T1-039, a must. Body thinness (T1-032) is a should, and T1-031 allows 25 mm when needed.
6. **Thermal:** the RK3566, LPDDR4X and eMMC go on the **back** (they are taller than 1.0 mm). Their heat goes through the board planes and the pocket floor, not into the LCD. The pocket floor should be a metal plate tied to the frame, and the pack's temperature becomes a documented charging and load limit (§6).
7. **The back bands are at 104–123 % of their area** with today's tall parts (§4.3). That is independent of this decision and goes to placement (E4): lower-profile inductors, the haptic actuator and the microSD socket are the candidates.

## 1. Geometry used

| Item | Value | Source |
|---|---|---|
| Body | 59.5 × 94.3 × 24 mm (tentative) | t1 ADR 0003 |
| Cavity | 56.3 × 91.1 mm (1.6 mm walls, **UNVERIFIED**) | PCB-M-02 |
| Board outline | 55.3 × 90.1 mm = 4,983 mm² per side (0.5 mm clearance per side, **UNVERIFIED**) | PCB-M-02 |
| Bosses | 4 × Ø 4 mm, ≈ 25 mm² each per side with keep-out (est.) | PCB-M-08 |
| Usable per side | ≈ 4,880 mm² (arithmetic) | — |
| Display footprint on the front | 54.46 × 82.94 = 4,517 mm² (91 % of the board) | E35GH sheet |
| Front outside the display | ≈ 466 mm²: two strips of about 0.4 mm along the sides and about 3.6 mm at each end if the module is centred (arithmetic; its y position is **UNVERIFIED** until the faceplate mechanics) | arithmetic |
| Back under the battery pocket (≤ 1.5 mm) | ≈ 51.3 × 67.1 mm = 3,442 mm² | Battery selection §2.3, battery-life analysis §11.3 |
| Back bands (tall parts) | bottom 17 × 55.3 = 940, top 7 × 55.3 = 387, side strips 2 × 2.0 × 67.1 = 268; total ≈ 1,595 mm² | Battery selection §2.3 |

The front strips along the sides, which §9 item 1 (b) of the constraints counted on, are only about 0.4 mm wide: the display is nearly as wide as the board.

## 2. Courtyard area from BOM v1.7

Method: courtyard = (body length + 0.5) × (body width + 0.5) mm, i.e. body + 0.25 mm per side (the brief; IPC-7351 nominal density is of this order). Each part is put in a height class from its sheet:

- **F:** maximum height ≤ 1.0 mm, can sit under the display in a 1.0 mm zone;
- **B:** 1.0 < h ≤ 1.5 mm, back under the battery (PCB-Z-01) or a band;
- **T:** h > 1.5 mm, bands only (PCB-Z-02, PCB-Z-05);
- **E:** edge and external parts with a fixed place (jacks, USB-C, speaker, buttons, battery connector, U.FL).

Parts on the faceplate (display, touch controller, ALS, faceplate microphone, status LEDs, FH12 connectors, panel translators) and parts on the HAT device-side piece (pogo pins, DF40 receptacles) are not on the main board and are excluded.

| Class | Main contributors (courtyard, mm²) | Total (mm²) |
|---|---|---|
| **B** (≤ 1.5) | RK3566 238 (15.5 × 14.4 mm; height **UNVERIFIED**, taken as ≤ 1.2 mm); LPDDR4X 163 (200-ball FBGA, 10 × 15 mm from the sibling K4UBE3D4AA listing, height ≤ 1.0 mm assumed: **UNVERIFIED**, so treated as B); eMMC 162 (153-ball FBGA 11.5 × 13 mm, JEDEC size: **UNVERIFIED**); Murata 2EL 76 (7.7 × 8.8 × 1.3 mm, distributor listing, **UNVERIFIED**); TSSOP translators 95; SOT-23/SC70/SOT-23-THIN parts (TPS22919 ×7, INA236 ×4, TPS7A20 ×3, others) ≈ 190; DFE252012F ×7 53; 0805 bulk capacitors ×45 (est.) 197; others | **1,255** |
| **F** (≤ 1.0) ICs | TPD4E05U06 ×25 113; OPA1622 ×6 74; CS43198 ×2 61; RK809-5 56; RP2354A 56; LT3045/LT3094 ×4 49; PN7160 42; SLB9673 30 (size **UNVERIFIED**); LP5521 25; BQ25798, TPS65131, TCA6416A 20 each; mute-shunt footprints (DNP) 27; others | **870** |
| **F** passives and pads | 0201 ×150 132; 0402 ×420 630; 0603 ×100 273; shunts 33; test pads ×59 (Ø 1.0 mm, BOM 86–89) 133. Counts from BOM §5 (≈ 400 C, 259 R, 11 FB) plus ≈ 30 for the v1.7 additions; the size split is an estimate | **1,201** |
| FH35C-51S | 17.4 × 3.7 mm courtyard plus a 2 mm FPC approach | **99** |
| **T** (> 1.5) | microSD DM3AT 236 (13.85 × 15.95 × 1.68 mm); XGL/XAL4020 ×5 101 (2.1 mm); LRA 110 (Ø 10 × 4.0 mm); DF40 headers 118 (1.14 mm, mated stack 1.5 mm plus the FPC); WE-LHMI 23 (1.8 mm); NANO2 fuse 21 (2.69 mm); GRM32ER 1210 11 (2.5 mm, thickness code **UNVERIFIED**) | **620** |
| **E** (edge) | 4.4 mm jack 185; speaker shadow 178 (15 × 11 mm); Micro-Fit 137 (12.5 × 10 mm, **UNVERIFIED**: no drawing read); 3.5 mm jack 98 (14.5 × 6 mm, **UNVERIFIED**); USB-C 74; buttons 68; U.FL ×2 22 | **761** |
| **Total** | | **≈ 4,810** |

## 3. Placement and routing factor

The factor turns courtyard area into board area: it covers fan-out, via fields, spacing for rework and inspection, switching-loop and partition rules, and the area that routing makes unusable.

The Radxa ZERO 3W is the closest published design: RK3566, LPDDR4, eMMC, an RK817 PMIC, an RK860 vdd_cpu buck and a Wi-Fi 6 module on **65 × 30 mm, both sides** ([CNX Software](https://www.cnx-software.com/2023/10/30/radxa-zero-3w-sbc-features-rockchip-rk3566-soc-up-to-8gb-ram-in-raspberry-pi-zero-2-w-form-factor/)). Its passive count (214 C, 117 R, 16 L, 6 ferrite beads) was read from its v1.12 schematic for the BOM (§5). Its courtyard sum, with the same method:

| ZERO 3W item | Courtyard (mm², est.) |
|---|---|
| RK3566, LPDDR4, eMMC (same packages as the T1) | 238 + 163 + 162 |
| RK817 (QFN68 7 × 7, as the RK809), RK860 | 56 + 12 |
| Wi-Fi module (Radxa D8, size **UNVERIFIED**, 10 × 10 assumed) | 110 |
| 2 × USB-C, micro HDMI, microSD, CSI FPC connector (sizes **UNVERIFIED**, class figures) | 148 + 94 + 150 + 73 |
| Crystals, 16 inductors (2520) | 18 + 120 |
| 337 passives (40 % 0201, 60 % 0402, est.) | 422 |
| Buttons, ESD, LDOs, LED (est.) | 90 |
| **Sum** | **≈ 1,860** |

Board area: 2 × 1,950 = 3,900 mm². Less the 40-pin header field, which blocks both sides (2 × 50.8 × 5.08 ≈ 516 mm²), and four mounting holes (≈ 226 mm² over both sides): ≈ 3,160 mm². **Factor ≈ 3,160 / 1,860 ≈ 1.7.** With the uncertainty of the class figures, **1.5–1.9** is used as the range. Two cross-checks:

- The battery selection §2.2 sized the core (SoC, LPDDR4X, eMMC, PMIC, audio) at about 55 × 35 mm ≈ 1,925 mm² per side; the courtyard of those parts here is about 1,100 mm² (est.), so its implied factor is also about 1.7.
- Edge connectors need little routing around them, so the E class takes **1.2** (est.).

The ZERO 3W layer count and its own density are not published (**UNVERIFIED**); the factor is a planning value until placement (E4) replaces it.

**Need:** 761 × 1.2 + (4,810 − 761) × 1.7 ≈ **7,800 mm²** (7,000 at 1.5; 8,600 at 1.9). The board has ≈ 9,760 mm² over both sides: **72–88 % use**, comparable to a dense handheld board. No single side is enough.

## 4. Options

### 4.1 Where the parts go if both sides are used

Fill the back first with what can only go there (E and T in the bands, B under the battery), then put F parts on the back until it is full, and the rest on the front:

| Factor | Back: E + T + B | Back left for F | F total | **F on the front** | Front use (≈ 4,340 mm² usable, below) |
|---|---|---|---|---|---|
| 1.5 | 3,726 | 1,154 | 3,255 | **≈ 2,100** | 48 % |
| 1.7 | 4,101 | 779 | 3,689 | **≈ 2,910** | 67 % |
| 1.9 | 4,476 | 404 | 4,123 | **≈ 3,720** | 86 % |

Front usable area: 4,880 mm², less a **faceplate connection area** of about 10 × 54 mm at the display's bottom edge (≈ 540 mm², size **UNVERIFIED**), where the display tails bend behind the module (E35GH sheet) and the faceplate flex arrives. In that area the board carries only the FH35C and its ESD parts.

Every F part is ≤ 1.0 mm, so **a 1.0 mm front zone is enough for all of them**. At 0.8 mm, the parts between 0.8 and 1.0 mm (OPA1622, every VQFN-HR regulator, BQ25798, TPS65131, RP2354A, PN7160, the FH35C, SOT523 FETs, oscillators: about 420 mm² of courtyard) move back to the back, which leaves the back with ≈ 60 mm² of slack at factor 1.7 and none at 1.9. A desk estimate with this much uncertainty needs more slack than that.

### 4.2 Option comparison

| Option | Front zone | Gap | Area | z cost | Verdict |
|---|---|---|---|---|---|
| **(a1) Grow the gap, 1.0 mm zone, from body thickness** | 1.0 mm | 1.3 mm | Fits: front at 48–86 % | Body 24.0 → **25.0 mm**; battery unchanged | **Chosen** |
| (a2) Same zone, from the battery layer | 1.0 mm | 1.3 mm | Fits | Pocket 10.9 → 10.0 mm thick, **−8.3 %** energy | Rejected: autonomy (§5) |
| (a3) 1.5 mm zone (SoC, LPDDR4X, eMMC, shield cans on the front) | 1.5 mm | 1.8 mm | Fits, more freedom | 1.5 mm: 25.5 mm body exceeds T1-031, so ≥ 0.5 mm must come from the battery (−4.2 %) | Rejected: energy, and the SoC's heat against the LCD (§6) |
| (a4) 0.8 mm zone, FH35C by recess or fold | 0.8 mm | 1.1 mm | Fits only with no slack (§4.1) | Body 24.8 mm | Rejected: no slack for a desk estimate; saves 0.2 mm |
| (b) Single-sided under the display, front parts only outside it | 0 | 0.3 mm | Back ≈ 4,880 + front outside ≈ 466 = **≈ 5,350 mm²** against 7,000–8,600: short **1,650–3,250 mm²** | None | **Does not fit** |
| (c) Recess in the display support for the FH35C only | 0 (FH35C locally) | 0.3 mm | Same as (b) | None | **Does not fit**: it solves the connector, not the area |
| (d) Phone practice: faceplate flex folds around the board edge to an FH35C on the back | 0 | 0.3 mm | Same as (b), plus ≈ 18 × 1 mm of board edge lost to the fold | None | **Does not fit** on its own; it would also put the faceplate connector under the battery or in a full band (§4.3) |

A larger board does not rescue (b): the largest body of T1-031 (62.5 × 95 mm) gives a board of about 58.3 × 90.8 mm, 5,294 mm² per side, still short. A second stacked board costs more z than the gap does.

### 4.3 Band capacity (independent of this decision)

The bands hold the E and T classes: 761 × 1.2 + 620 × (1.2–1.7) ≈ **1,660–1,970 mm²** against ≈ 1,595 mm², **104–123 %**. The front decision cannot relieve it, because T parts fit neither under the battery nor under a 1.0 mm front zone. Placement (E4) has to close it, with these candidates:

- the five 4020 inductors (2.1 mm) and the WE-LHMI (1.8 mm): a ≤ 1.5 mm part with the same current rating would let a converter sit under the battery. That is a BOM change with an efficiency check, since the TPS62136 pre-regulator is in the playback path (T1-009);
- the haptic LRA (Ø 10 × 4 mm): in the case or the front end strips (PCB-Z-04);
- the microSD socket DM3AT: 15.95 mm deep, it does not fit the 7 mm top band, and at 1.68 mm it exceeds PCB-Z-01 (1.5 mm) where it overlaps the pocket. It needs a local relief of the pocket floor or another place. This is a finding for the constraints and the case; nothing here decides it.

## 5. Autonomy

Model: 2S pack of about 12 Wh (105060-class volume, two ≈ 5 mm cells stacked; quote only), scenario 1 (screen off, 3.5 mm SE), 90 % usable ([2S study](2026-10-battery-2s.md) §5): typical **14.4–15.0 h**, worst **6.4–6.7 h**. [ADR 0012](../adr/0012-headphone-output-stage.md) lowers the core session by about 11 %; applied to both ends: typical **12.8–13.4 h**, pessimistic **5.7–6.0 h** (est.), below the 6 h red line (T1-039), as the T1 requirements note.

Pack energy scales with the cell thickness that fits: t_max = (battery layer − 0.3 mm foam) / 1.1 (swelling), with a 12.3 mm battery layer at 24 mm (battery-life analysis §11.3). One millimetre less battery layer is 0.91 mm less cell, **≈ 8.3 % of the energy** (arithmetic; discrete cell thickness codes make the real step coarser).

| Where the z comes from | t_max | Energy | Typical core session (est.) | Pessimistic (est.) | Body |
|---|---|---|---|---|---|
| **Body (chosen)** | 10.9 mm | 100 % | 12.8–13.4 h | 5.7–6.0 h | 25.0 mm |
| Battery, 0.5 mm (half and half) | 10.45 mm | 95.9 % | 12.3–12.9 h | 5.5–5.8 h | 24.5 mm |
| Battery, 1.0 mm (a2) | 10.0 mm | 91.7 % | 11.7–12.3 h | 5.2–5.5 h | 24.0 mm |
| Battery, 1.5 mm (a3 within 24 mm) | 9.55 mm | 87.6 % | 11.2–11.7 h | 5.0–5.3 h | 24.0 mm |

The pessimistic estimate is already below the red line. Taking energy away would deepen a breach of a must (T1-009, T1-039) to keep part of a should (T1-032). T1-035 (battery as large as fits) and the 105060-class pocket of ADR 0014 are kept.

## 6. Thermal (qualitative; no simulation)

- **SoC on the back, facing the battery.** The RK3566, LPDDR4X and eMMC are B parts and sit on the back under the pocket. Heat leaves through the board planes (the main spreader in either case), through a thermal pad to the pocket floor, and from the floor to the frame. The floor should therefore be a metal plate, thermally tied to the case frame (0.4 mm in the stack; material is the case's call). With 1.2 mm of SoC and a shield can within 1.5 mm, a thermal pad has about 0.1–0.2 mm (**UNVERIFIED** until the can and pad are chosen).
- **What it implies for the battery.** In the core session the SoC and memory draw about 0.32 W (48 % of 0.66 W, battery-life analysis §0.4), which warms a 12 Wh pack by little. Sustained high loads (UI, transcoding, HAT compute) warm the pack. Li-ion charging is temperature-limited, so the pack temperature becomes a load and charge limit: the BQ25798 TS window on the pack NTC and the gauge temperature already stop charging in hardware (BRD-049), and Blackbird OS should reduce SoC load before that, as a documented, visible limit (T1-045).
- **Why not the display side.** The E35GH is rated to +70 °C and carries its own 0.9 W backlight. A SoC against its back would add a local hot spot to the LCD and to the touch surface the user holds. On the front, only low-power parts face the display. The air gap of 0.3 mm in front of them is a poor heat path, which suits that.
- **Audio.** The analog stage (DACs, OPA1622, LDOs) is F class and can sit on either side. Its shield can (BOM line 90) fits only on the back (≤ 1.5 mm), so a shielded audio stage goes on the back.

## 7. Signal integrity and assembly

- **Decoupling.** With the SoC on the back, its 0201 decoupling capacitors go on the front directly under the ball field, through via-in-pad microvias: the shortest loop the HDI build allows (PCB-P-10).
- **LPDDR4X and eMMC** stay on the SoC's side (back), so their buses route without layer changes at the package.
- **DSI** runs from the SoC (back) to the FH35C (front) through one via transition. At one lane (E35GH) that is a small cost; the via stays in the `MIPI_100D` class with a ground via next to it.
- **Shield cans** only on the back, within 1.5 mm. The front zone admits none (PCB-Z-03).
- **Double-sided reflow.** The front holds only light parts (passives, QFN/DFN/SON, the FH35C), so it is reflowed first and rides upside down through the second reflow of the BGA side. The BGAs see one reflow. The Micro-Fit is through-hole: pin-in-paste or selective solder, and its tails on the front must stay outside the display footprint or within 1.0 mm (**UNVERIFIED** tail length).
- **Test access.** Flat test pads go on the front (PCB-T-01 to PCB-T-03, BRD-040): reachable with the faceplate off, before final assembly, from a single-sided fixture. The pads under the display must stay outside the faceplate connection area.
- **Service.** The FH35C opens to 1.8 mm. That needs the faceplate off, which is the faceplate's own removal path (t1 faceplate interface). Plugging the faceplate flex before the module is laid down needs a service loop in the flex (faceplate-touch, E1.9).

## 8. Resulting height zones

| ID | Zone | Max part height | Change |
|---|---|---|---|
| PCB-Z-01 | Back, under the battery pocket | **1.5 mm** (shield can and thermal pad included) | Unchanged |
| PCB-Z-02 | Back, bands | Battery layer + 1.9 mm = **14.2 mm** at 25.0 mm (arithmetic: 25.0 − 12.7 + 1.5 + 0.4) | Value unchanged; the fixed stack is 12.7 mm instead of 11.7 |
| PCB-Z-03 | Front, under the display | **1.0 mm** for any part (FH35C 0.9 ± 0.1 included); display-to-board gap **1.3 mm** (1.0 + 0.3 for insulation, tolerance and module deflection under touch, **UNVERIFIED**); no shield cans; a faceplate connection area of ≈ 10 × 54 mm at the display's bottom edge holds only the FH35C and its ESD (size **UNVERIFIED**) | Was 0.3 mm (conflict) |
| PCB-Z-04 | Front, outside the display footprint | Gap + module = **6.8 mm** where the faceplate frame leaves room (**UNVERIFIED** until the faceplate mechanics) | Was 5.8 mm |

Thickness stack (front to back): lens and OCA 0.9, display module 5.5, **gap 1.3**, board 1.2, back components 1.5, pocket floor 0.4, battery layer 12.3, back cover 1.5, HAT case features 0.4: **25.0 mm**.

## 9. What remains open

- **No z margin left.** 25.0 mm is the T1-031 maximum. Any later growth (the 1.1 mm IP65 lens adds 0.4 mm, battery selection §2.2) would come from the battery. Two recoveries return z to the body first: a 1.0 mm board (8-layer HDI, PCBWay example 1.0 ± 0.1 mm; PCB-S-01) gives 0.2 mm, and the faceplate's option of using the module's own touch lens (display selection §7, option 1) gives up to 0.9 mm.
- **Heights not from a primary source:** RK3566 FCCSP565L, LPDDR4X and eMMC packages (no datasheet in parts-lib), Murata 2EL size, Micro-Fit footprint and tail length, 3.5 mm jack size, GRM32ER thickness code. RK3566 above 1.5 mm with a can would break PCB-Z-01; the Rockchip hardware design guide (constraints §9 item 2) closes it.
- **Clearance of 0.3 mm** in front of the parts: display back material, module deflection under touch pressure and board bow between bosses are **UNVERIFIED**. A measurement on the display sample replaces it.
- **Faceplate side:** the display tails, the faceplate flex and its FH12 connectors (2 mm high) must sit in the faceplate connection area or outside the display footprint; behind the module the gap leaves no room for them. Goes to E1.9 and the t1 interface files (E4.6).
- **Band capacity** at 104–123 % (§4.3) and the microSD height and depth: placement items (E4).
- **Routing factor 1.5–1.9:** replaced by the real figure after first placement.
