# Main board PCB design constraints

- **Status:** Draft v0.1 (2026-10-24). Task E2.1 of the [electronics plan](https://github.com/opendap-project/t1/blob/main/docs/plans/2026-10-electronics-plan.md). Nothing here is laid out or measured yet.
- **Purpose:** every limit the main-board layout must respect, derived from the product requirements, the parts and the fab, in one place. Each constraint has an ID, a minimum, a target and a maximum where they apply, its source, and the mechanism that enforces it.
- **Enforced by:** `DRC` = the T1 product rule set composed on top of the PCBWay fab rule set (E3.4); `NC` = KiCad net class or custom rule generated from the data file (E2.4); `CHK` = a script check on the layout (E4.5); `SIM` = a simulation in `sim/` (E4.4); `REV` = a review item with its checklist line, because no tool can check it.
- **Values:** a value with no source is not used. **UNVERIFIED** marks values taken from a sibling part, an assumption, or a source not yet retrieved; each one names what closes it. Arithmetic is shown as such.

## 0. Summary

1. **The z budget does not fit a double-sided board under the display yet.** The thickness stack ([battery selection](../research/2026-10-battery-selection.md) §2.2) gives 0.3 mm between the display module and the board, while the FH35C faceplate connector alone is 0.9 mm high and BRD-054 allows both sides populated. PCB-Z-03 sets the front-side zones and §9 item 1 lists the options; the choice needs the maintainers (it moves the battery layer).
2. **High-speed layout values wait for Rockchip's RK3566 hardware design guide.** LPDDR4X impedance, length and skew limits are not in any retrieved document. They are marked **UNVERIFIED** with the usual values as placeholders, and retrieving the guide is a blocker before routing (§9 item 2).
3. **The main board is an HDI build.** The 0.4 mm part of the RK3566 ball field needs laser microvias in the pads ([PCBWay capabilities](https://github.com/opendap-project/kicad-lib/blob/main/docs/research/2026-10-pcbway-capabilities.md) §2.1); the build order follows the ball map.
4. **Copper for power is sized for the protection rating, not the typical draw** (BRD-049): the battery path carries the 5 A fuse rating continuously with ≤ 10 °C rise.
5. **Audio rules come from the CS43198 and OPA1622 datasheets** and from the decided topology (ADR 0010, 0012, 0015): split nothing, partition everything.

## 1. Outline and mechanics (inputs from the product)

The case owns its walls, bosses and keep-outs; these values are the board's inputs until the case and the t1 interface files (E4.6) publish them.

| ID | Constraint | Min | Target | Max | Source | Enforced by |
|---|---|---|---|---|---|---|
| PCB-M-01 | Body the board lives in | — | 59.5 × 94.3 × 24 mm | 62.5 × 95 × 25 mm (T1-031) | [t1 ADR 0003](https://github.com/opendap-project/t1/blob/main/docs/adr/0003-tentative-body-size.md), T1-031 | REV |
| PCB-M-02 | Board outline inside the cavity | — | cavity minus 0.5 mm per side | cavity = body − 2 × wall: 56.3 × 91.1 mm with 1.6 mm walls (arithmetic) | Walls 1.6 mm per side: assumption of the battery selection §2.3, **UNVERIFIED** until the case sets them; clearance 0.5 mm per side **UNVERIFIED** (ISO 2768-m ±0.3 mm on the case plus PCBWay outline ±0.1 mm advanced [P2]) | DRC (board edge), REV |
| PCB-M-03 | Board outline tolerance | — | ±0.1 mm | ±0.2 mm | PCBWay advanced / standard [P1, P2] | fab notes |
| PCB-M-04 | Coordinate system | — | origin at the device centre, x across, y along, +z towards the faceplate | — | T1-021 (Draft) | KiCad grid origin, export (E4.9) |
| PCB-M-05 | Edge connectors on the bottom edge, left to right | — | 3.5 mm jack, 4.4 mm jack, USB-C centred, speaker on the right | — | T1-016 | REV |
| PCB-M-06 | Side buttons | — | Action, Vol+, Vol− on the left edge; Main on the right | — | T1-014, T1-015 | REV |
| PCB-M-07 | Battery connector in a notch outside the pocket | — | Micro-Fit 3.0 43650-0400, right angle | — | ADR 0014, BOM line 47; mated envelope **UNVERIFIED** (§7.23) | REV |
| PCB-M-08 | Mounting holes | 4 | 4 (two top, two bottom bosses) | — | Battery selection §2.3 (Ø 4 bosses), **UNVERIFIED** until the case | DRC (keep-out), REV |
| PCB-M-09 | Fiducials | 3 global per populated side | 3 + 2 local at the RK3566 | — | PCBWay assembly practice, **UNVERIFIED** (ask in DFM review) | REV |

## 2. Height zones (z)

Heights are above the board surface. "Front" is +z (towards the display), "back" is −z (towards the battery).

| ID | Zone | Max part height | Source | Enforced by |
|---|---|---|---|---|
| PCB-Z-01 | Back, under the battery pocket footprint | 1.5 mm | Battery selection §2.2 (components under the pocket capped at 1.5 mm; pocket floor 0.4 mm) | CHK (3D height per zone) |
| PCB-Z-02 | Back, bottom band (jacks, USB-C, speaker) and top band (microSD, antenna feed) | Battery layer + 1.9 mm: 14.2 mm at 24 mm thickness (arithmetic: 24 − 11.7 + 1.5 + 0.4) | Battery selection §2.2, §2.3 | CHK |
| PCB-Z-03 | Front, under the display module | 0.3 mm today: **conflict**, see §9 item 1 | Battery selection §2.2 (module-to-board gap 0.3 mm, assumption) | CHK |
| PCB-Z-04 | Front, outside the display footprint (side strips, display 54.46 × 82.94 mm) | Gap + display module thickness: 5.8 mm where the faceplate frame leaves room, **UNVERIFIED** until the faceplate mechanics exist | [faceplate-touch ADR 0001](https://github.com/opendap-project/faceplate-touch/blob/main/docs/adr/0001-focus-lcds-e35gh-display.md) | CHK |
| PCB-Z-05 | Tallest known parts and their zone | G-Switch 4.4 mm jack 6.5 mm (bottom band), USB4105 3.31 mm (bottom band), DM3AT microSD 1.68 mm (top band), XAL4020 inductor 2.1 mm (bands only), DF40 header 1.14 mm, FH35C 0.9 mm | parts-lib sheets | CHK |

## 3. Stackup and build

| ID | Constraint | Min | Target | Max | Source | Enforced by |
|---|---|---|---|---|---|---|
| PCB-S-01 | Board thickness | 1.0 mm | 1.0–1.2 mm | 1.2 mm (z stack) | Battery selection §2.2 (1.2 mm); PCBWay HDI example 8 layers 1.0 ± 0.1 mm [P3] | fab notes, export |
| PCB-S-02 | Build | 1+N+1 | 2+N+2 (stacked or staggered, copper-filled) | any-layer only if the ball map needs it | 0.4 mm field escape needs via-in-pad microvias (PCBWay research §2.1); RK3566 ball map **UNVERIFIED** | stackup, DRC (via types) |
| PCB-S-03 | Layer count | 8 | 8–10 | 10 (1.2 mm limit, PCBWay 10-layer HDI example is 1.3 mm [P3]) | LPDDR4X + RK3566 escape + audio planes; final count from the escape study | stackup |
| PCB-S-04 | Reference planes | — | Every high-speed and every analog-audio layer adjacent to a solid ground plane | — | Standard practice; CS43198 §8 (DS1156F2 p. 121) | REV |
| PCB-S-05 | Dielectric | 50 µm (impedance) | per PCBWay stackup | — | [P2, P12] | stackup (E3.6 asks PCBWay) |
| PCB-S-06 | Material | Tg 170 FR-4 | Tg 170, high-speed class 1–5 G if the USB 3 / PCIe loss budget needs it | — | PCBWay materials [P2, P16]; loss budget E4.5 | stackup |
| PCB-S-07 | Finish | — | ENIG (or ENEPIG) | — | Fine-pitch BGA and QFN flatness; PCBWay [P1] | fab notes |
| PCB-S-08 | Acceptance class | IPC Class 2 | Class 2 for prototypes | Class 3 on request | [P1, P16] | fab notes |

## 4. Geometry beyond the fab rules

The fab rule set (`pcbway-hdi`, E3.1) carries PCBWay's limits. These are the T1's own, tighter values.

| ID | Constraint | Min | Target | Source | Enforced by |
|---|---|---|---|---|---|
| PCB-G-01 | Track and space, general | 0.1 / 0.1 mm | 0.1 / 0.1 mm or more | Margin over PCBWay HDI 0.065 mm [P3] and normal outer 4/5 mil [P1]; finer only in the BGA escape | DRC |
| PCB-G-02 | Track and space inside the RK3566 courtyard | 0.065 / 0.065 mm | 0.075 / 0.075 mm | PCBWay HDI [P3] | DRC (area rule) |
| PCB-G-03 | Laser microvia | 0.10 mm drill | 0.10 mm drill, 0.25 mm land | PCBWay 4 mil laser [P3]; land from the 0.25 mm BGA pad (research §2.1) | DRC |
| PCB-G-04 | Mechanical via (outside the BGA) | 0.20 mm drill, 0.45 mm pad | 0.25 / 0.50 mm | PCBWay advanced normal 0.20 mm [P1, P3] | DRC |
| PCB-G-05 | Copper to board edge | 0.30 mm | 0.50 mm | PCBWay 0.20 mm milled [P1]; margin for the ±0.1 mm outline | DRC |
| PCB-G-06 | Courtyard clearance | 0 (no overlap) | 0.1 mm | IPC-7351 courtyard practice | DRC |
| PCB-G-07 | Thermal relief on plane connections of hand-reworkable parts | — | Relief on connectors and test pads; solid on power parts and exposed pads | Assembly and thermal pads (CS43198 §8.4, OPA1622 pad to V−) | DRC (zone rules) |
| PCB-G-08 | Silkscreen | 0.15 mm line, 0.8 mm text | 0.15 / 0.8 mm | PCBWay [P1] | DRC |

## 5. Signal classes

Impedance tolerance on the board is PCBWay's ±10 % [P1]. A class whose standard allows less has to say so; those windows are **UNVERIFIED** until the standards' texts are in parts-lib or the docs.

| ID | Net class | Signals | Impedance | Length and skew | Source | Enforced by |
|---|---|---|---|---|---|---|
| PCB-I-01 | `USB2_90D` | Main USB-C D± (OTG0), HAT `USB3_D±` | 90 Ω differential | Intra-pair skew ≤ 0.15 mm **UNVERIFIED** | HAT interface v1 §L1; USB 2.0 tolerance **UNVERIFIED** | NC, CHK |
| PCB-I-02 | `USB3_90D` | HAT `USB3_SSTX±`, `USB3_SSRX±` | 90 Ω differential | Intra-pair ≤ 0.1 mm **UNVERIFIED**; AC caps on TX near the source | HAT interface v1 §L1 | NC, CHK |
| PCB-I-03 | `PCIE_85D` | HAT `PCIE_TX±`, `PCIE_RX±`, `PCIE_REFCLK±` | 85 Ω differential (85–100 Ω allowed, **UNVERIFIED**) | Intra-pair ≤ 0.1 mm **UNVERIFIED**; AC caps on TX | HAT interface v1 §L3 | NC, CHK |
| PCB-I-04 | `MIPI_100D` | Faceplate DSI, HAT CSI-2 | 100 Ω differential | Intra-pair ≤ 0.1 mm, lane-to-clock ≤ 1 mm **UNVERIFIED** | HAT interface v1 §L3; faceplate interface | NC, CHK |
| PCB-I-05 | `DDR_DQ`, `DDR_CA`, `DDR_CK` | LPDDR4X | 40 Ω single-ended, 80 Ω differential (CK, DQS) **UNVERIFIED** | Byte-lane and CA matching per the Rockchip guide **UNVERIFIED** | RK3566 hardware design guide, not retrieved (§9 item 2) | NC, CHK |
| PCB-I-06 | `EMMC_SD_50` | eMMC (HS200), microSD (SDR104, BRD-051) | 50 Ω single-ended | CLK to data ≤ 2 mm **UNVERIFIED** | BRD-051; Rockchip guide **UNVERIFIED** | NC, CHK |
| PCB-I-07 | `RF_50` | Module RF pins to U.FL | 50 Ω coplanar with ground | Shortest; π network at the pin | U.FL-R-SMT-1 50 Ω; Murata layout guide **UNVERIFIED** | NC, REV |
| PCB-I-08 | `I2S_DSD` | SoC → CS43198 ASP (SCLK, LRCK, SDIN) | 50 Ω single-ended, series-terminated at the source | Matched within the bus ≤ 5 mm **UNVERIFIED**; slave SCLK ≤ 24.58 MHz | CS43198 Table 3-18; test pads BRD-040 | NC, CHK |
| PCB-I-09 | `MCLK` | 22.5792 / 24.576 MHz oscillators → attenuator → CS43198 XTI | 50 Ω, ground-guarded, no via changes of reference | Shortest; ≥ 3 × trace width from any other signal; away from FILT± | ADR 0010; CS43198 §8 (keep clocks away from FILT±) | NC, REV |

## 6. Power and current

Widths are the IPC-2221 external/internal formula at ΔT = 10 °C (conservative, arithmetic: I = k·ΔT^0.44·A^0.725), as provisional minimums for the net classes; sign-off uses IPC-2152 at layout (E4.5). Currents are the protection rating or the worst continuous case, whichever is higher (BRD-049).

| ID | Path | Design current | Min width, 35 µm outer | Min width, 35 µm inner | Source | Enforced by |
|---|---|---|---|---|---|---|
| PCB-P-01 | Battery: connector → fuse → BQ25798 BAT; P− → sense resistor → GND | 5.0 A (fuse) | 2.8 mm or a pour | 7.2 mm or a pour on two layers | BOM lines 43, 47, 104; ADR 0014 | NC, CHK (copper area per net) |
| PCB-P-02 | VSYS (6.0–8.8 V) trunk | 3.2 A worst continuous | 1.5 mm or a pour | 3.9 mm | Power tree §4.7, BOM §7 item 17 | NC, CHK |
| PCB-P-03 | VBUS → TPS2121 → BQ25798 | 3.0 A (TPS2121 ILM max) | 1.4 mm | 3.6 mm | Power tree line VBUS_CHG | NC |
| PCB-P-04 | HAT_5V and USB-C source (5.1 V) | 1.66 A (eFuse ILIM max) | 0.6 mm | 1.6 mm | Power tree §4.6 | NC |
| PCB-P-05 | HAT_3V3 | 1.0 A (ILIM) | 0.3 mm | 0.8 mm | Power tree §4.6 | NC |
| PCB-P-06 | Amplifier rails ±7 V / ±6 V | 0.3 A per rail (275 mA design case) | 0.15 mm (use ≥ 0.3 mm for impedance) | 0.3 mm | Power tree §4.10.1, ADR 0015 | NC |
| PCB-P-07 | Switching loops (BQ25798, TPS62136, TPS62903 ×2, LMR33630C, TPS65131, RK809, RK860, TPS62840) | — | Input capacitor, switch node and inductor on one side, loop area per each datasheet layout example | — | Each part's datasheet layout section (parts-lib) | REV |
| PCB-P-08 | Switch-node copper | — | Smallest area that carries the current; no other net under it on the adjacent layer except ground | — | Standard practice, datasheets | REV |
| PCB-P-09 | Vias per amp of plane change | — | ≥ 1 via (0.25 mm) per 0.5 A **UNVERIFIED**; for laser microvias per the PCBWay copper fill | — | Rule of thumb, to replace with an IPC-2152 via calculation (E4.5) | CHK |
| PCB-P-10 | Decoupling | — | Smallest capacitor closest to its pin, same side, via-in-pad or ≤ 0.5 mm to the via | — | CS43198 §8; RK3566 guide **UNVERIFIED** | REV |

## 7. Audio partition and grounding

| ID | Constraint | Source | Enforced by |
|---|---|---|---|
| PCB-A-01 | One ground. No split planes; the analog section is partitioned by placement, and return currents of digital and switching circuits never cross it | CS43198: GNDA, GNDCP and GNDD meet in a common ground area under the chip (DS1156F2 Table 1-1, p. 7) | REV |
| PCB-A-02 | DAC exposed pad to ground through a via array to inner ground planes | CS43198 §8.4, p. 121 | REV |
| PCB-A-03 | REFA and REFB routed independently to each headphone connector's ground pin | CS43198 §8, p. 121 | NC (separate nets), REV |
| PCB-A-04 | FILT+ capacitor short to VA, FILT− to −VA; VCP_FILT± capacitors short to GNDCP | CS43198 §8, p. 121 | REV |
| PCB-A-05 | VA and VCP from independent clean supplies; VL and VD may share the logic supply | CS43198 §8, p. 121 | schematic, REV |
| PCB-A-06 | Distance from any switch node or inductor to the DAC analog pins, FILT±, the OPA1622 inputs and the headphone traces | ≥ 5 mm target, **UNVERIFIED** until the power and audio test board (E5.2) | DRC (courtyard area rule) |
| PCB-A-07 | No digital or switching trace on any layer under the analog section's area (DAC analog side, amplifiers, output network, jack traces) | Partition rule; ADR 0012 output stage | DRC (keep-out area) |
| PCB-A-08 | OPA1622 thermal pad to V−, per TI example layout DRC0010J | OPA1622 sheet (SBOS727B pp. 34–35) | REV |
| PCB-A-09 | Paralleled OPA1622 halves: symmetric layout of the two halves and their output resistors per leg | ADR 0012 (current sharing measured 53/47 % in `sim/output-stage`) | REV, SIM |
| PCB-A-10 | Left/right and leg symmetry of the headphone paths: equal length and topology | T1-050 (identical left/right), ADR 0012 | CHK |
| PCB-A-11 | Jack detect lines kept away from the audio paths and ESD-protected at the jack | BRD-052 | REV |
| PCB-A-12 | I2S/DSD test pads on the DAC side, stub ≤ 1 mm, passive (no series parts) | BRD-040, BRD-041 | REV |

## 8. RF, protection, test and assembly

| ID | Constraint | Source | Enforced by |
|---|---|---|---|
| PCB-R-01 | Radio module footprint, ground and keep-out exactly per Murata's Type 2EL hardware design guide, to keep the pre-certification | BRD-025; guide not retrieved (**UNVERIFIED**, LBES5PL2EL-923 sheet) | DRC (keep-out from the footprint), REV |
| PCB-R-02 | U.FL connectors and π networks in the top band; 0402 C0G, DNP by default | BOM lines 56–58 | REV |
| PCB-E-01 | ESD protection at every external connector (USB-C, jacks, HAT DF40, faceplate FH35C, microSD), placed between the connector and everything else, ≤ 3 mm from the connector pins **UNVERIFIED** | BRD-007; BOM ESD lines | CHK (distance), REV |
| PCB-E-02 | USB-C VBUS: TVS2200 at the connector, TPS2121 next | Power tree (VBUS surge note) | REV |
| PCB-E-03 | Each HAT rail behind its eFuse | BRD-026 | schematic |
| PCB-T-01 | UART test pads for BootROM / TPL / SPL | BRD-047 | REV |
| PCB-T-02 | A test pad on every regulated rail and on VSYS, VSYS_LV, VBAT | Bring-up (E8.2) | CHK (one pad per power net) |
| PCB-T-03 | SWD pads for the RP2354A | BRD-015 | REV |
| PCB-T-04 | Assembly variants: every optional part has its variant field, DNP parts keep their footprint | BRD-053, ADR 0013 | CHK (BOM fields) |
| PCB-T-05 | Every part has Manufacturer and MPN fields | `fab-package` check | CHK |
| PCB-T-06 | Shielding-can frames (DNP first) around the SoC/DDR and the radio, with a 0.5 mm frame keep-out **UNVERIFIED** | BOM line 90, §7.7 | DRC (keep-out), REV |

## 9. Open items

1. **Front-side height (PCB-Z-03).** The FH35C (0.9 mm) and every front-side part need more than the 0.3 mm gap. Options: (a) grow the gap to about 1.0 mm and take 0.7 mm from the battery layer (about −6 % of the 10.9 mm pocket thickness, arithmetic); (b) a single-sided board under the display, with front-side parts only in the side strips (PCB-Z-04); (c) a recess in the display support for the FH35C only. Needs the maintainers, with the case.
2. **Rockchip RK3566 hardware design guide** (LPDDR4X, eMMC, SD, USB 3, PCIe, DSI rules; land pattern; decoupling): retrieve before routing. Every PCB-I value marked **UNVERIFIED** is replaced from it.
3. **Murata Type 2EL hardware design guide** (footprint, keep-out, RF pins): before placement (PCB-R-01).
4. **Standards' tolerance windows** (USB 2.0, USB 3.x, PCIe, MIPI D-PHY): add the texts or a secondary source to the docs.
5. **Case inputs**: walls, bosses, clearances (PCB-M-02, PCB-M-08) through the t1 interface files (E4.6).
6. **PCBWay**: HDI stackup, microvia land, shielding frames, fiducial practice (E3.6).
