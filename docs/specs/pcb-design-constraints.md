# Main board PCB design constraints

- **Status:** Draft v0.5 (2026-10-24; v0.2 applies ADR 0016, v0.3 Rockchip's layout rules, v0.4 Murata's 2EL notes and the interface standards, v0.5 the design-for-compliance constraints and RFC 0010 levels). Task E2.1 of the [electronics plan](https://github.com/opendap-project/t1/blob/main/docs/plans/2026-10-electronics-plan.md). Nothing here is laid out or measured yet.
- **Purpose:** every limit the main-board layout must respect, derived from the product requirements, the parts and the fab, in one place. Each constraint has an ID, a minimum, a target and a maximum where they apply, its source, and the mechanism that enforces it.
- **Enforced by:** `DRC` = the T1 product rules ([`hardware/rules/`](../../hardware/rules/)), composed on top of the PCBWay HDI fab rule set (E3.4); a rule whose value is still **UNVERIFIED** is a DRC warning, the others are errors; `NC` = net class in [`hardware/rules/netclasses.toml`](../../hardware/rules/netclasses.toml) (E2.4); `CHK` = a script check on the layout (E4.5); `SIM` = a simulation in `sim/` (E4.4); `REV` = a review item with its checklist line, because no tool can check it.
- **Levels:** `[Qn]` after an ID is the RFC 0010 quality level at which the constraint becomes mandatory; an ID without it is Q1 until it is next reviewed.
- **Values:** a value with no source is not used. **UNVERIFIED** marks values taken from a sibling part, an assumption, or a source not yet retrieved; each one names what closes it. Arithmetic is shown as such.

## 0. Summary

1. **Front side under the display: parts up to 1.0 mm; the body grows to 25 mm** ([ADR 0016](../adr/0016-front-side-height-under-the-display.md)). The thickness stack gave 0.3 mm between the display and the board, while about 2,100–3,700 mm² of parts must sit under the display. The extra 1.0 mm comes from body thickness (T1-031 maximum), not from the battery, whose energy is the limit of T1-039. No thickness margin is left within 25 mm.
2. **High-speed values come from Rockchip's documents** ([RK3566 layout rules](../research/2026-10-rk3566-layout-rules.md): RK3566 Hardware Design Guide V1.1.0 and the RK3568 High Speed PCB Design Guide V1.0.0, which covers the same interface blocks). LPDDR4X is 50 Ω single-ended and 100 Ω differential; the PCIe reference clock is 100 Ω, a class of its own. Where Rockchip is looser than a standard or than the T1's need, the T1 keeps the tighter value and says why.
3. **The main board is an HDI build, without via-in-pad as a requirement.** The RK3566 has 343 core balls at 0.65 mm and a two-row ring of 222 balls at 0.4 mm. Laser microvias as dog-bones in the 0.825–0.875 mm channel between the ring and the core escape every inner-ring ball (arithmetic on the package drawing, [RK3566 layout rules](../research/2026-10-rk3566-layout-rules.md) §3); through vias do not fit there. Rockchip itself uses 4–6 layers, so the T1's 8–10 layers rest on its own density, double-sided z budget and audio partition, to be confirmed by an escape study.
4. **Copper for power is sized for the protection rating, not the typical draw** (BRD-049): the battery path carries the 5 A fuse rating continuously with ≤ 10 °C rise.
5. **Audio rules come from the CS43198 and OPA1622 datasheets** and from the decided topology (ADR 0010, 0012, 0015): split nothing, partition everything.

## 1. Outline and mechanics (inputs from the product)

The case owns its walls, bosses and keep-outs; these values are the board's inputs until the case and the t1 interface files (E4.6) publish them.

| ID | Constraint | Min | Target | Max | Source | Enforced by |
|---|---|---|---|---|---|---|
| PCB-M-01 | Body the board lives in | — | 59.5 × 94.3 × 25.0 mm | 62.5 × 95 × 25 mm (T1-031) | [t1 ADR 0003](https://github.com/opendap-project/t1/blob/main/docs/adr/0003-tentative-body-size.md), [ADR 0016](../adr/0016-front-side-height-under-the-display.md), T1-031 | REV |
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
| PCB-Z-01 | Back, under the battery pocket footprint (RK3566, LPDDR4X, eMMC here) | 1.5 mm, shield can and thermal pad included | Battery selection §2.2; ADR 0016 | CHK (3D height per zone) |
| PCB-Z-02 | Back, bottom band (jacks, USB-C, speaker) and top band (microSD, antenna feed) | 14.2 mm (arithmetic: battery layer 12.3 + 1.5 + 0.4) | Battery selection §2.2, §2.3; ADR 0016 (fixed stack 12.7 mm at 25 mm) | CHK |
| PCB-Z-03 | Front, under the display module | 1.0 mm (FH35C 0.9 ± 0.1 mm included); no shield cans; display-to-board gap 1.3 mm | ADR 0016 | CHK |
| PCB-Z-04 | Front, outside the display footprint | 6.8 mm where the faceplate frame leaves room, **UNVERIFIED** until the faceplate mechanics exist | ADR 0016 | CHK |
| PCB-Z-05 | Tallest known parts and their zone | G-Switch 4.4 mm jack 6.5 mm (bottom band), USB4105 3.31 mm (bottom band), DM3AT microSD 1.68 mm (top band), XAL4020 inductor 2.1 mm (bands only), DF40 header 1.14 mm, FH35C 0.9 mm | parts-lib sheets | CHK |

## 3. Stackup and build

| ID | Constraint | Min | Target | Max | Source | Enforced by |
|---|---|---|---|---|---|---|
| PCB-S-01 | Board thickness | 1.0 mm | 1.0–1.2 mm | 1.2 mm (z stack) | Battery selection §2.2 (1.2 mm); PCBWay HDI example 8 layers 1.0 ± 0.1 mm [P3] | fab notes, export |
| PCB-S-02 | Build | 1+N+1 | 1+N+1 or 2+N+2 (copper-filled microvias), via-in-pad only where the escape study needs it | any-layer only if the escape study needs it | [RK3566 layout rules](../research/2026-10-rk3566-layout-rules.md) §3: microvias needed for the 0.4 mm ring, not necessarily in the pad | stackup, DRC (via types) |
| PCB-S-03 | Layer count | 8 | 8–10 | 10 (1.2 mm limit, PCBWay 10-layer HDI example is 1.3 mm [P3]) | T1 density, double-sided z budget, audio planes; Rockchip's templates use 4–6 ([RK3566 layout rules](../research/2026-10-rk3566-layout-rules.md) §2); escape study (E4) | stackup |
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
| PCB-I-01 | `USB2_90D` | Main USB-C D± (OTG0), HAT `USB3_D±` | 90 Ω ±10 % differential | Intra-pair skew ≤ 0.15 mm (T1; Rockchip allows 0.51 mm); ≤ 152 mm; ≤ 4 vias; 2.2 Ω series at the SoC | HSPCB p. 13; HDG p. 59 ([RK3566 layout rules](../research/2026-10-rk3566-layout-rules.md)) | NC, CHK |
| PCB-I-02 | `USB3_90D` | HAT `USB3_SSTX±`, `USB3_SSRX±` | 90 Ω ±10 % differential | Intra-pair ≤ 0.30 mm; ≤ 152 mm; ≤ 2 vias; spacing ≥ 4 × W; 100 nF 0201 AC caps on SSTX | HSPCB p. 13; HDG p. 59 | NC, CHK |
| PCB-I-03 | `PCIE_85D`, `PCIE_REFCLK_100D` | HAT `PCIE_TX±`, `PCIE_RX±`; `PCIE_REFCLK±` | 85 Ω ±10 % data; 100 Ω ±10 % reference clock | Intra-pair ≤ 0.30 mm; ≤ 152 mm; ≤ 2 vias; spacing ≥ 4 × W (≥ 5 × W to other signals recommended); 100 nF 0201 AC caps on TX | HSPCB p. 15; HDG p. 89 | NC, CHK |
| PCB-I-04 | `MIPI_100D` | Faceplate DSI, HAT CSI-2 | 100 Ω ±10 % differential | Intra-pair ≤ 0.1 mm (T1; Rockchip 0.30 mm); data to clock ≤ 0.91 mm; ≤ 152 mm; ≤ 4 vias; spacing ≥ 3 × W | HSPCB pp. 18–19 | NC, CHK |
| PCB-I-05 | `DDR_DQ`, `DDR_CA`, `DDR_CK` | LPDDR4X | 50 Ω ±10 % single-ended, 100 Ω ±10 % differential (CK, DQS) | DQ/DM to DQS within a byte ≤ 15.2 mm; CA to CK ≤ 12.7 mm; DQS and CK pair halves ≤ 0.30 mm; DQS to CK ≤ 30.5 mm; spacing ≥ 2 × W (≥ 3 × W around DQS and CK); no DQ or CA swapping; a layout that departs from Rockchip's template is simulated | HSPCB pp. 44–45, Table 34 | NC, CHK, SIM |
| PCB-I-06 | `EMMC_SD_50` | eMMC (HS200), microSD (SDR104, BRD-051), SDIO to the radio | 50 Ω ±10 % single-ended | Data and CMD to CLK ≤ 2 mm (T1; Rockchip 3.05 mm); ≤ 102 mm; ≤ 4 vias; 22 Ω series on CLK; SD ESD < 1 pF | HSPCB pp. 19–20; HDG pp. 26, 52, 54 | NC, CHK |
| PCB-I-07 | `RF_50` | Module RF pins to U.FL | 50 Ω coplanar with ground | Shortest; π network at the pin | U.FL-R-SMT-1 50 Ω; Murata layout guide **UNVERIFIED** | NC, REV |
| PCB-I-08 | `I2S_DSD` | SoC → CS43198 ASP (SCLK, LRCK, SDIN) | 50 Ω single-ended, series-terminated at the source | Matched within the bus ≤ 5 mm **UNVERIFIED**; slave SCLK ≤ 24.58 MHz | CS43198 Table 3-18; test pads BRD-040 | NC, CHK |
| PCB-I-09 | `MCLK` | 22.5792 / 24.576 MHz oscillators → attenuator → CS43198 XTI | 50 Ω, ground-guarded, no via changes of reference | Shortest; ≥ 3 × trace width from any other signal; away from FILT± | ADR 0010; CS43198 §8 (keep clocks away from FILT±) | NC, REV |

## 6. Power and current

Widths are the IPC-2221 external/internal formula at ΔT = 10 °C (conservative, arithmetic: I = k·ΔT^0.44·A^0.725), as provisional minimums for the net classes; sign-off uses IPC-2152 at layout (E4.5). Currents are the protection rating or the worst continuous case, whichever is higher (BRD-049).

Outer layers are taken at 35 µm finished (18 µm base plus plating, **UNVERIFIED** until the PCBWay stackup) and inner layers at 18 µm, the HDI base copper [P3].

| ID | Path | Design current | Min width, outer (35 µm) | Min width, inner (18 µm) | Source | Enforced by |
|---|---|---|---|---|---|---|
| PCB-P-01 | Battery: connector → fuse → BQ25798 BAT; P− → sense resistor → GND | 5.0 A (fuse) | 2.8 mm or a pour | 14.0 mm, so a pour on two or more layers | BOM lines 43, 47, 104; ADR 0014 | DRC (`PWR_BAT`), CHK (copper area per net) |
| PCB-P-02 | VSYS (6.0–8.8 V) trunk | 3.2 A worst continuous | 1.5 mm or a pour | 7.6 mm or a pour | Power tree §4.7, BOM §7 item 17 | DRC (`PWR_VSYS`), CHK |
| PCB-P-03 | VBUS → TPS2121 → BQ25798 | 3.0 A (TPS2121 ILM max) | 1.4 mm | 6.9 mm or a pour | Power tree line VBUS_CHG | DRC (`PWR_VBUS`) |
| PCB-P-04 | HAT_5V and USB-C source (5.1 V) | 1.66 A (eFuse ILIM max) | 0.6 mm | 3.1 mm | Power tree §4.6 | DRC (`PWR_5V1`) |
| PCB-P-05 | HAT_3V3 | 1.0 A (ILIM) | 0.3 mm | 1.5 mm | Power tree §4.6 | DRC (`PWR_HAT3V3`) |
| PCB-P-06 | Amplifier rails ±7 V / ±6 V | 0.3 A per rail (275 mA design case) | 0.3 mm (the current needs 0.06 mm; the width keeps the rail impedance low) | 0.3 mm | Power tree §4.10.1, ADR 0015 | DRC (`PWR_AMP`) |
| PCB-P-07 | Switching loops (BQ25798, TPS62136, TPS62903 ×2, LMR33630C, TPS65131, RK809, RK860, TPS62840) | — | Input capacitor, switch node and inductor on one side, loop area per each datasheet layout example | — | Each part's datasheet layout section (parts-lib) | REV |
| PCB-P-08 | Switch-node copper | — | Smallest area that carries the current; no other net under it on the adjacent layer except ground | — | Standard practice, datasheets | REV |
| PCB-P-09 | Vias per amp of plane change | — | ≥ 1 via (0.25 mm) per 0.5 A **UNVERIFIED**; for laser microvias per the PCBWay copper fill | — | Rule of thumb, to replace with an IPC-2152 via calculation (E4.5) | CHK |
| PCB-P-10 | Decoupling | — | Smallest capacitor closest to its pin with the shortest via path; for the RK3566 and LPDDR4X, Rockchip's placement under the package on the opposite side (with ADR 0016 the SoC is on the back, so its decoupling goes on the front, under the ball field, within PCB-Z-03); values per supply from the HDG | — | CS43198 §8; HDG ([RK3566 layout rules](../research/2026-10-rk3566-layout-rules.md) §4) | REV |

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
| PCB-R-01 | Radio module land, ground and keep-out per Murata's Type 2EL hardware application note E2B-09-1413 Rev. 9.0 and footprint drawing; the datasheet (supply ranges, sequencing, keep-out under the module) is still **UNVERIFIED** (Murata's link refused) | BRD-025; LBES5PL2EL-923 sheet | DRC (keep-out from the footprint), REV |
| PCB-R-02 | Two antenna paths: ANT0 (pin 15) for Wi-Fi and ANT1 (pin 23) for Bluetooth / 802.15.4, each with a U.FL and matching positions where Murata places them, in 0603 as in Murata's design, in the top band | E2B-09-1413 §3.5.1; BOM lines 56–58 | REV |
| PCB-R-03 [Q1] | RF trace: a copy of Murata's U.FL layout. 50 Ω microstrip over a solid ground 230–240 µm below it (inner-plane cut-outs in the HDI stack, never over a change of dielectric or ground), width within ±0.25 mm of Murata's, 7–25 mm long; ≥ 0.8 mm copper keep-out under the U.FL | E2B-09-1413 §3.5.1 p. 15; CER-0248 §2.1.6.2 pp. 31–33 | DRC (keep-out area), REV |
| PCB-R-04 [Q2] | Antennas from the FCC, ISED and Japan lists of the module's certification, with the listed cable length, or a permissive change agreed before layout freeze | CER-0248 Tables 20, 36, 56; [design for compliance](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-design-for-compliance.md) | REV |
| PCB-R-05 [Q2] | Antenna feeds and radiators at the board edges or in the top band, away from the body-facing surface and from HAT metal; the distance is fixed by the SAR pre-assessment | [design for compliance](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-design-for-compliance.md) §2.3 | REV |
| PCB-EMC-01 [Q1] | Common-mode filter positions (0 Ω fitted by default) on the USB-C USB 2 pair, the faceplate DSI and the HAT high-speed entry, placed per each class's signal-integrity rules | [design for compliance](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-design-for-compliance.md) §2.1; BRD-053 | REV |
| PCB-EMC-02 [Q1] | Ferrite positions on HAT_5V, HAT_3V3 and the faceplate supplies at their connectors | [design for compliance](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-design-for-compliance.md) §2.1 | REV |
| PCB-EMC-03 [Q1] | Shield-can frame footprints (DNP first) around the switching converters near the radio and around the headphone stage, besides PCB-T-06 | [design for compliance](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-design-for-compliance.md) §2.1 | REV |
| PCB-E-01 | ESD protection at every external connector (USB-C, jacks, HAT DF40, faceplate FH35C, microSD), placed between the connector and everything else, ≤ 3 mm from the connector pins **UNVERIFIED** | BRD-007; BOM ESD lines | CHK (distance), REV |
| PCB-E-02 | USB-C VBUS: TVS2200 at the connector, TPS2121 next | Power tree (VBUS surge note) | REV |
| PCB-E-03 | Each HAT rail behind its eFuse | BRD-026 | schematic |
| PCB-E-04 [Q1] | Each connector shell and each ESD diode return reaches the ground plane through at least two vias at the pad; no ESD return shares a path with an audio ground return | [design for compliance](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-design-for-compliance.md) §2.10 | REV |
| PCB-P-11 [Q3] | HAT_5V, HAT_3V3 and the USB-C source output each have a second, independent limiter (fuse or PTC) so the available power after 3 s stays ≤ 15 W with the eFuse shorted (IEC 62368-1 PS1) | [design for compliance](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-design-for-compliance.md) §2.4 | schematic, V4-12 |
| PCB-A-13 [Q1] | Amplifier enables and the DAC reset default to off at power-up and reset (hardware pull), so no output is driven before the OS sets a level (T1-049, T1-072) | [design for compliance](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-design-for-compliance.md) §2.6 | schematic, REV |
| PCB-S-09 [Q3] | Laminate and solder mask flammability V-0, with recognition evidence from the fab | IEC 62368-1 clause 6; [design for compliance](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-design-for-compliance.md) | fab notes |
| PCB-T-07 [Q2] | Every BOM line carries its RoHS and REACH status and a supplier declaration reference (T1-082) | [design for compliance](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-design-for-compliance.md) §2.7 | CHK (BOM fields) |
| PCB-T-01 | UART test pads for BootROM / TPL / SPL | BRD-047 | REV |
| PCB-T-02 | A test pad on every regulated rail and on VSYS, VSYS_LV, VBAT | Bring-up (E8.2) | CHK (one pad per power net) |
| PCB-T-03 | SWD pads for the RP2354A | BRD-015 | REV |
| PCB-T-04 | Assembly variants: every optional part has its variant field, DNP parts keep their footprint | BRD-053, ADR 0013 | CHK (BOM fields) |
| PCB-T-05 | Every part has Manufacturer and MPN fields | `fab-package` check | CHK |
| PCB-T-06 | Shielding-can frames (DNP first) around the SoC/DDR and the radio, with a 0.5 mm frame keep-out **UNVERIFIED** | BOM line 90, §7.7 | DRC (keep-out), REV |

## 9. Open items

1. **Front-side height (PCB-Z-03):** decided by [ADR 0016](../adr/0016-front-side-height-under-the-display.md). Still open from its study: package heights of the RK3566, LPDDR4X and eMMC; the back bands at 104–123 % of their area with today's tall parts (4020 inductors, haptic motor, microSD socket); the microSD socket fits neither the top band nor the zone under the battery. Both go to placement (E7.1).
2. **Rockchip documents** retrieved (E1.11 part 1). Still missing: the RK3566 edition of the high-speed guide, RK3566 DDR templates, package pin lengths, a land pattern (Rockchip publishes none: the footprint is drawn from the package drawing and checked by a second reading) and IBIS models. LPDDR4X needs 1.10 V (VDD2) besides 0.60 V (VDDQ) at the SoC: check against the power tree.
3. **Murata Type 2EL:** application note, footprint and certification note retrieved ([interface standards](../research/2026-10-interface-standards-layout.md)); the datasheet is still missing. Findings for the power tree and the product: the module needs a 1.8 V power rail (AVDD18, 323–390 mA typical in Bluetooth/802.15.4 transmit, peaks above 1 A on the carrier datasheet) besides 3.3 V; the US and Canada modular approvals cover mobile use at ≥ 20 cm only, so the handheld T1 needs SAR and a permissive change through Murata; the Molex 146187 antenna is on Japan's list only (with a ≥ 50 mm cable). Plan tasks E1.12, E1.13.
4. **Standards** ([interface standards](../research/2026-10-interface-standards-layout.md)): USB 2.0 and USB 3.2 texts retrieved (USB 2.0 allows ±15 %, the board keeps PCBWay's ±10 %; USB 3 AC caps 75–265 nF); PCIe and MIPI from vendor guides only (member-only specs); the eMMC 5.1 text and SD SDR104 timing are still missing.
5. **Case inputs**: walls, bosses, clearances (PCB-M-02, PCB-M-08) through the t1 interface files (E4.6).
6. **PCBWay**: HDI stackup, microvia land, shielding frames, fiducial practice (E3.6).
