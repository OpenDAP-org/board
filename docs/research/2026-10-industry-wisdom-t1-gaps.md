# Industry wisdom: gaps in the T1 main-board documents

- **Date:** 2026-10-24
- **Status:** Desk research, asked by the maintainers on 2026-10-24. Nothing here is a decision and nothing here edits the [PCB design constraints](../specs/pcb-design-constraints.md), the [electronics plan](https://github.com/opendap-project/t1/blob/main/docs/plans/2026-10-electronics-plan.md) or `hardware/rules/`: their owners apply what they accept. Each gap carries a proposed constraint ID or plan task, a value where a source gives one, and the lowest [RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md) quality level at which it would be mandatory.
- **Inputs:** the [industry wisdom benchmark](https://github.com/opendap-project/toolkit-hardware/blob/main/docs/research/2026-10-industry-wisdom-benchmark.md) (practice IDs `IW-…`, mechanisms and sources) checked against PCB design constraints v0.4, the electronics plan, the [electronics integration and verification spec](https://github.com/opendap-project/t1/blob/main/docs/specs/electronics-integration-verification.md) v0.1, BOM v1.7 and ADRs 0010, 0012, 0014, 0015 and 0016. Reviews run from the shared [design review checklist](https://github.com/opendap-project/toolkit-hardware/blob/main/docs/specs/design-review-checklist.md) (`DRV-…`).
- **Values:** a value with no source is **UNVERIFIED** and names what closes it. Arithmetic is shown as such.

## 0. Summary

1. **Most of the gaps are about return currents the documents do not map.** The constraints state the principle (one ground, PCB-A-01; reference planes, PCB-S-04) but have no rule for stitching vias at layer changes, voids under fast-pair pads, where the six OPA1622's rail currents return, the shared single-ended return, the USB-to-computer ground loop, or where ESD current from the bottom-edge connectors goes. Gaps G-01 to G-13 and G-24.
2. **One constraint contradicts a source:** PCB-I-09 asks for a "ground-guarded" MCLK; Hubing names guard traces a myth for microstrip [IW-SR-05]. Proposed rewording in G-06.
3. **Audio coexistence with the converters needs a board frequency plan and a light-load decision** (G-14, G-15): the LMR33630C has no forced-PWM mode, so its idle bursts are either measured harmless or handled.
4. **Battery safety needs three checks the ADRs do not make:** pins mating in any order at the Micro-Fit (G-19), insertion ringing on ceramic capacitors (G-17), fuse breaking capacity against the pack's short-circuit current (G-18). All Q0.
5. **Bring-up needs provisions that only cost area now:** rail isolation links, reset and boot test points, spare GPIO, scope ground points, revision in copper (G-26 to G-29). All Q1.
6. **Thermal:** a sealed 59.5 × 94.3 × 25 mm body sheds about 0.19 W/K by natural convection and radiation (est.), so 3 W sustained means about 16 K mean surface rise. A device-level sustained power budget is missing (G-33).

## 1. Proposed constraints

Status column: what the T1 documents do today (*Missing*, *Partial*, *Contradicts*), as defined in the benchmark §1.

### 1.1 Stack-up and return paths (constraints §3, §5)

| Gap | Proposed ID | Level | Proposed constraint | Value | Source | Enforced by | Status |
|---|---|---|---|---|---|---|---|
| G-01 | PCB-S-09 | Q1 | A ground stitching via at every signal via that changes reference layer between ground planes, symmetric for pairs | ≤ 0.76 mm centre to centre (Rockchip, general), ≤ 0.64 mm for `DDR_*`; never beyond 5.08 mm (TI's maximum) | IW-SR-03: Rockchip HSPCB pp. 8, 23 ([RK3566 layout rules](2026-10-rk3566-layout-rules.md) §1); TI SPRACP4A §2.4 (200 mil) | CHK (E4.5) | Missing |
| G-02 | PCB-S-10 | Q1 | A layer change that swaps the reference between ground and a power plane gets a stitching capacitor; classes PCB-I-01 to I-06 and I-09 never reference a power plane | 100 nF per 3–4 signal vias | IW-SR-04: Rockchip HSPCB p. 26; TI SPRACP4A §2.4 | CHK, REV | Missing |
| G-03 | PCB-S-11 | Q1 | Every signal layer adjacent to a ground plane (PCB-S-04 extended to all signal layers); the SoC core and LPDDR4X supply planes paired with an adjacent ground at the thinnest HDI dielectric, on the side nearer the front decoupling (ADR 0016) | Dielectric per the PCBWay stack-up (PCB-S-05) | IW-SR-01 (Hartley, Ott), IW-SR-06 (Archambeault: ≤ 10 mil plane pairs), IW-PI-01 | stack-up, REV (DRV-302) | Partial |
| G-04 | PCB-S-12 | Q2 | Ground planes stitched by a via grid, with an edge fence | Edge pitch ≤ 2.5 mm, **UNVERIFIED** (arithmetic: λ/10 at 6 GHz in FR-4, εr ≈ 4); interior grid **UNVERIFIED**; to replace with a source or the first near-field scan | IW-SR-07 (Ott, Ritchey, chapters **UNVERIFIED**) | CHK | Missing |
| G-05 | PCB-I-10 | Q1 | Reference plane voided under SMD pads on classes PCB-I-01 to I-04 (AC capacitors, ESD parts, connector pads), at least two layers deep; equal via count on both members of a pair and across matched lanes | 100 % of the pad, two layers (TI); Rockchip's void figures per HSPCB pp. 8–11 | IW-HS-02, IW-HS-04: TI SPRACP4A §2.12–2.13; Rockchip HSPCB | DRC (keep-out on pads), CHK | Missing |
| G-06 | PCB-I-09 (rewording) | Q1 | `MCLK`: stripline between two ground planes, spacing ≥ 3 × W to other nets, no reference change. A guard trace only if via-stitched along its length, and never counted as the protection | — | IW-SR-05: Hubing, LearnEMC (guard traces "can actually make coupling between microstrip traces worse") | NC, REV (DRV-308) | Contradicts ("ground-guarded") |
| G-07 | PCB-I-11 | Q1 | Every connector carrying fast pairs (DF40 pair, pogo field, FH35C) gives each pair adjacent ground contacts (G-S-S-G or better). Input to E1.2 and E1.3 | — | IW-HS-01 (Johnson, *Advanced Black Magic*, chapter **UNVERIFIED**); module rule M3 | interface files (E4.6), REV (DRV-320) | Partial |

The research note's "power-plane copper pulled back by a multiple of H" (RK3566 layout rules §1, factor cut off in the source) is the 20-H idea; Hubing's measurements show 20-H increases power-bus radiation (IW-SR-05). Proposal: no general pull-back rule; decide per plane in the stack-up review.

### 1.2 Audio grounding and coexistence (constraints §7)

| Gap | Proposed ID | Level | Proposed constraint | Value | Source | Enforced by | Status |
|---|---|---|---|---|---|---|---|
| G-08 | PCB-A-13 | Q1 | Each OPA1622's rail decoupling capacitors return to the output stage's power ground point, not to the difference-amplifier reference resistors' ground (BOM line 37) and not to the CS43198 REF nets | — | IW-GA-04: Self, rail-decoupling distortion; ADR 0015 (rail current is a rectified sine, 433 mA peak) | REV (DRV-208) | Missing |
| G-09 | PCB-A-14 | Q1 | Amplifier rail traces and headphone load-current paths do not run parallel to, or under, the difference-amplifier input and feedback traces | Separation **UNVERIFIED** (set at the M-AUD layout, checked by V2 THD+N at full output) | IW-GA-05: Self, induction distortion | REV (DRV-208) | Missing |
| G-10 | PCB-A-15 | Q1 | One reference point per single-ended output through the whole chain: the reference resistors of the single-ended difference amplifiers return to the same 3.5 mm jack ground sense as REFA/REFB (PCB-A-03), or the schematic states why not | — | IW-GA-06; PCB-A-03; BOM lines 19, 37 | schematic, REV (DRV-114) | Partial (open question) |
| G-11 | PCB-A-16 | Q2 | Copper resistance of any return shared by both channels between the reference point and the 3.5 mm sleeve pin | ≤ 5 mΩ, **UNVERIFIED** target (arithmetic: 5 mΩ / 16 Ω → −70 dB crosstalk from the board alone); to align with a T1-048 crosstalk threshold | IW-GA-06 (Self, headphone chapter **UNVERIFIED**) | CHK (copper resistance), REV (DRV-313) | Missing |
| G-12 | PCB-A-17 | Q2 | The ground current between USB-C and the headphone jacks (USB DAC mode connected to a computer, T1-054) runs in a defined path along the bottom edge, outside the DAC and amplifier reference region; the USB-C shield termination is decided in the schematic | — | IW-GA-07: Putzeys, Ott; V4-06 | REV (DRV-214) | Partial |
| G-13 | PCB-A-18 | Q2 | RF filter footprints at each headphone output near the jack: a series element (ferrite or 0 Ω) and a shunt capacitor to the jack ground, DNP by default; the OPA1622 with its 1 Ω ballast checked stable with the shunt fitted | Values **UNVERIFIED**: set by simulation (stability) and by V4-01 with the radio transmitting | IW-GA-08: TI SBOA128 (EMIRR); IW-ES-04 (the headphone cable is an antenna) | REV (DRV-116), SIM | Missing |

### 1.3 Power, converters and battery (constraints §6)

| Gap | Proposed ID | Level | Proposed constraint | Value | Source | Enforced by | Status |
|---|---|---|---|---|---|---|---|
| G-14 | PCB-P-11 | Q1 | A board frequency plan: every converter's frequency range and light-load mode, the beats between any two, and the harmonics that fall in 2.4 and 5 GHz; no beat in the audio band during playback | Converters: BQ25798, TPS62136, TPS62903 × 2, LMR33630C, TPS65131, RK809-5, RK860-0, TPS62840, TPS61169 | IW-SW-03; BOM line 116 (one pair already ≥ 0.3 MHz) | REV (DRV-112) | Partial |
| G-15 | PCB-P-12 | Q1 | Light-load mode of every converter feeding audio. TPS65131: power-save disabled during playback if its power-save pin allows (pin behaviour **UNVERIFIED**, check SLVS493E). LMR33630C: no forced PWM (TI E2E), so its idle bursts are measured at the amplifier output (ADR 0015); if a burst falls in the audio band above the T1-048 warning, a minimum load (footprint reserved, DNP) or another part follows | Footprint for a switchable minimum load on AUDIO_N7V0, DNP, **UNVERIFIED** value | IW-SW-04, IW-SW-05 | REV (DRV-113), V2 bench | Partial |
| G-16 | PCB-P-13 | Q1 | The LMR33630C layout follows SNVA856B's inverting buck-boost layout, not the buck layout of its datasheet: the input capacitors from VIN to the −7 V IC ground form the hot loop and sit closest | — | IW-SW-01: AN-136; TI SNVA856B (BOM line 116) | REV (DRV-207) | Partial |
| G-17 | PCB-P-14 | Q0 | Insertion transients checked against the absolute maximum of every part on BAT, VSYS, VBUS and the HAT 5.1 V output, with ceramic input capacitors ringing up to twice the source voltage | Battery: 2 × 8.8 V = 17.6 V worst case (arithmetic), unless damped | IW-PI-04: LT AN-88 (**UNVERIFIED**, text not retrieved) | SIM, REV (DRV-109) | Partial (VBUS only, PCB-E-02) |
| G-18 | PCB-P-15 | Q0 | The 5 A board fuse's voltage rating and breaking capacity cover the 2S pack's short-circuit current, and the pack PCM's short-circuit trip acts first | Pack short-circuit current from the pack makers (E1.10) | IW-BA-04 (fuse makers' guides, **UNVERIFIED**); ADR 0014 | REV (DRV-110) | Missing |
| G-19 | PCB-P-16 | Q0 | The four Micro-Fit pins (P+, P−, mid tap, NTC) are safe in any mating order: series resistance or clamping on the mid-tap and NTC lines per the gauge and charger datasheets | Per BQ28Z610-R1 (with E1.4) and BQ25798 TS input; **UNVERIFIED** until read | IW-BA-03 | schematic, REV (DRV-108) | Missing |
| G-20 | PCB-P-17 | Q0 | Every rail enable, amplifier enable, external-source enable and boot strap has a resistor default that keeps it off (or in its safe state) while its driver is unpowered or in reset: `HPA_RAIL_EN`, `HPA_LDO_EN`, OPA1622 EN, `HAT5V_EN`, `USB_SRC_ON`, `HAT3V3_EN`, FP_3V3, the oscillator ST pins | — | IW-SC-02; BOM line 35 (MaskROM gate) as the existing example | schematic, REV (DRV-104) | Partial |
| G-21 | PCB-P-18 | Q0 | No back-powering: a table of every net crossing between separately powered domains (faceplate, HAT, DAC VL, coprocessor, radio) with the sequencing or isolation that keeps it inside the receiver's absolute maximum | — | IW-SC-03 | schematic, REV (DRV-105) | Missing |

### 1.4 RF and ESD (constraints §8)

| Gap | Proposed ID | Level | Proposed constraint | Value | Source | Enforced by | Status |
|---|---|---|---|---|---|---|---|
| G-22 | PCB-R-04 | Q2 | Antennas, U.FL feeds and RF traces kept away from the USB 3 and PCIe routes, the DF40 pair and the HAT FPC; the FPC's fast pairs have ground on both sides of the flex | Distance **UNVERIFIED**: from the M-RF and M-HAT modules (V3-05, V3-07 with the radio on) | IW-RF-02: Intel USB 3 white paper | DRC (keep-out), REV (DRV-216) | Missing |
| G-23 | PCB-R-05 | Q2 | Input to the case: antenna positions clear of the metal pocket floor of ADR 0016 and of the battery, by the antenna vendor's clearance | **UNVERIFIED** (Molex 146187 data, or the chosen antenna's) | IW-RF-04 | case interface (E4.6), V5-01 | Missing |
| G-24 | PCB-E-04 | Q2 | An ESD return region at the bottom edge: each TVS at USB-C and the jacks grounds into a locally stitched ground at the connector; no analog reference sense (REFA/REFB, gain-network references) and no clock in that region | Region size **UNVERIFIED** (set at placement, checked by V4-05) | IW-ES-02: Ott, ESD chapter; IEC 61000-4-2 (about 30 A first peak at 8 kV contact, **UNVERIFIED** text) | DRC (keep-out area), REV (DRV-213) | Missing |
| G-25 | PCB-E-05 | Q1 | Each TVS ground pad has its own vias directly at the pad into the ground plane; no stub on the protected line | Two vias or more, **UNVERIFIED** count | IW-ES-01: TI SLVA680A | REV (DRV-316) | Partial (PCB-E-01 has placement only) |

### 1.5 Test, assembly and thermal (constraints §4, §8; a new thermal section)

| Gap | Proposed ID | Level | Proposed constraint | Value | Source | Enforced by | Status |
|---|---|---|---|---|---|---|---|
| G-26 | PCB-T-07 | Q1 | A rail isolation link at every converter and LDO output (0201 or 0402 0 Ω, or a solder jumper), fitted on prototypes, so each rail can be brought up alone | One per regulated rail in the power tree | IW-BU-01: Ganssle, "Debuggable designs" | CHK (one link per rail), REV (DRV-119) | Missing |
| G-27 | PCB-T-08 | Q1 | Test points on SoC reset, PMIC power-on, sleep and interrupt, the MaskROM window (`WINDOW_N`), boot-mode nets, the coprocessor's RUN and BOOTSEL (QSPI_SS); one spare SoC GPIO and one spare RP2354A GPIO on pads | — | IW-BU-02, IW-BU-04: Ganssle | CHK, REV (DRV-119) | Partial (BOM lines 86, 88) |
| G-28 | PCB-T-09 | Q1 | Scope ground points next to each converter cluster, the audio section and the clocks, sized for a probe ground spring | Pad size **UNVERIFIED** (probe maker's spring) | IW-BU-03: Ganssle; IW-PI-05: AN-47 | REV (DRV-220) | Missing |
| G-29 | PCB-T-10 | Q1 | Board revision in copper on an inner or outer layer, besides the EEPROM (BOM line 17) | — | IW-PD-05 | REV (DRV-403) | Missing |
| G-30 | PCB-T-11 | Q1 | Rework keep-out around the RK3566, LPDDR4X and eMMC; the decoupling under them on the opposite side (ADR 0016) recorded as an accepted rework cost | Keep-out **UNVERIFIED** (ask PCBWay with E3.6) | IW-DF-06: IPC-7095 (**UNVERIFIED** value) | DRC (courtyard area), REV (DRV-218) | Missing |
| G-31 | PCB-G-09 | Q1 | Balanced copper on both pads of every 0201 and 0402 part; where a decoupling capacitor needs a solid connection for inductance, both pads get it the same way | — | IW-DF-02 (IPC-7351B, EMS guides, *secondary*); IW-PI-01 for the inductance trade-off | REV (DRV-318) | Missing (PCB-G-07 covers connectors only) |
| G-32 | PCB-G-10 | Q1 | Via treatment: any via in a pad filled and capped (IPC-4761 type VII); exposed-pad thermal vias filled, plugged or tented per PCBWay's process | — | IW-DF-03, IW-TH-03 | fab notes, REV (DRV-319) | Partial (PCB-S-02 allows via-in-pad, no type) |
| G-33 | PCB-H-01 | Q2 | A device-level sustained power budget: the dissipation the body can shed at a surface-temperature target, against which E4.10's per-part data and V4-03 are checked | ≈ 0.19 W/K (est.; arithmetic: h ≈ 10 W/m²·K × 0.0189 m² body surface), so 3 W → ≈ 16 K mean rise; surface target from the IEC 62368-1 touch-temperature table (**UNVERIFIED** value) | IW-TH-01: Incropera (coefficient range **UNVERIFIED** table) | REV, V4-03 | Missing |

## 2. Proposed plan additions

Proposals for the plan owner, not edits.

| Proposal | Level | Task | Reason | Practice |
|---|---|---|---|---|
| P-01 | Q1 | Move E3.6's stack-up request (PCBWay HDI stack-up and impedance table) before E4.1 completes, or mark E4.1's net-class widths provisional until it lands | Every width and plane order depends on it | IW-SR-08 |
| P-02 | Q1 | E1.6 gains a criterion: slew rate at the CS43198 XTI threshold with the attenuator, against the unattenuated oscillator into the same load, and the resulting noise-to-jitter estimate | ADR 0010's "does not slow down materially" has no number; a slower edge converts more noise into jitter | IW-CK-02 |
| P-03 | Q1 | New E2.6: return-current map of the large currents (headphone loads, amplifier rails, charger and battery, HAT 5.1 V, USB to a computer, ESD at the bottom edge), drawn on the outline before placement | Feeds G-08 to G-12 and G-24; checklist DRV-206 | IW-GA-03 |
| P-04 | Q1 | New E2.7: board frequency plan (G-14, G-15) | One table instead of per-line notes | IW-SW-03 |
| P-05 | Q1 | E8.1: order X-ray of the BGA, LGA and QFN joints on prototype 1; write a first-article inspection record | Hidden joints cannot be seen otherwise | IW-DF-04, IW-PD-04 |
| P-06 | Q0 | E8.2: the bring-up method: current-limited supply, rails one by one through G-26's links, expected value before each measurement, short-ground probing, ψJT for junction temperatures | Already partly in ADR 0014 item 4; the rest is not written | IW-BU-01, IW-BU-05, IW-PI-05, IW-TH-02 |
| P-07 | Q2 | New: antenna inventory (headphone cable, USB-C cable, HAT FPC, faceplate flex) and near-field scans at L2 and L4, before the L6 pre-scan | Fixes are cheapest at the module stage | IW-ES-04, IW-ES-05 |
| P-08 | Q2 | New: production test strategy before the DIY kit (Q2 is the kit's level in RFC 0010): what the fixture tests, through which pads | "The product behind the product" | IW-DF-07 |
| P-09 | Q3 | New: single-fault analysis of the charge path for the Commercial edition | IEC 62368-1 Annex M checks charge limits under single faults | IW-BA-01 |
| P-10 | Q3 | New: board-level drop test (JEDEC JESD22-B111) and a decision on BGA underfill | Fine-pitch BGAs in a handheld | IW-DF-08 |
| P-11 | Q2 / Q3 | parts-lib: a provenance field (authorised or not) at Q2; a lifecycle watch for single-source and critical parts at Q3 | Several lines are stocked only at LCSC (e.g. BOM line 117) | IW-SP-01, IW-SP-03 |

## 3. Inputs to other components

- **Case (t1 interface files, E4.6):** antenna positions against the metal pocket floor (G-23); pocket clearance for cell swelling and no pressure on the cell corners (IW-BA-02: the Note 7 findings, *secondary*). Swelling allowance **UNVERIFIED** until the pack makers state it.
- **hat-standard (E1.3):** G-S-S-G contacts for every fast pair in the DF40 and pogo numbering (G-07); a 2.4 GHz desense row in the coupon criteria of hat-standard ADR 0004 with USB 3 traffic (G-22).
- **faceplate-touch (E1.2, E1.9):** the same contact rule for the DSI pairs in the FH35C assignment (G-07).

## 4. What the T1 documents already do well

Checked and covered, so not repeated as gaps: one ground with partition by placement (PCB-A-01, MT-031); the DAC's ground pad, filters and references (PCB-A-02 to A-05); hot loop and switch node per datasheet (PCB-P-07, P-08); the spur budget through the LDO PSRR (BOM §7.31, line 26); DAC as clock master with the oscillator next to it and J-test verification (ADR 0010); 0201 AC capacitors (PCB-I-02, I-03); TDR coupons (M-SI); the radio module per Murata (PCB-R-01 to R-03); shield-can frames DNP first (PCB-T-06); double-sided reflow order (ADR 0016); bench supply for bring-up (ADR 0014 item 4); expected values before measuring (verification matrices); board revision in EEPROM (BOM line 17); second sources and dated availability (PLIB-003); the habit of marking every assumption **UNVERIFIED** with its closing action (Bogatin rule 13).

## 5. IDs as integrated (2026-10-24)

The [PCB design constraints](../specs/pcb-design-constraints.md) v0.6 took in §1 of this note. The compliance pass (v0.5) and the DFM rules had already used some of the proposed IDs, so these gaps carry new ones there. The plan proposals of §2 are not affected. The same version renamed the impedance-controlled net classes to the craft convention: `MCLK` → `MCLK_50SE`, `I2S_DSD` → `I2S_50SE`, `EMMC_SD_50` → `EMMC_SD_50SE`, `RF_50` → `RF_50SE`, `DDR` → `DDR_50SE` (DQ, DM, CA) and `DDR_100D` (DQS, CK), and `PCIE_REFCLK_100D` split from `PCIE_85D`; the notes written before it keep the old names.

| Gap | Proposed here | In the constraints (v0.6) |
|---|---|---|
| G-01 to G-04 | PCB-S-09 to S-12 | PCB-S-10 to S-13 (S-09 is laminate flammability) |
| G-05 | PCB-I-10 | PCB-I-10 |
| G-06 | PCB-I-09 rewording | PCB-I-09, reworded, with the MCLK branch limit (≤ 20 mm per branch, `sim/mclk-attenuator`) |
| G-07 | PCB-I-11 | PCB-I-11 |
| G-08 to G-13 | PCB-A-13 to A-18 | PCB-A-14 to A-19 (A-13 is the power-up default of amplifier enables) |
| G-14 to G-21 | PCB-P-11 to P-18 | PCB-P-12 to P-19 (P-11 is the second limiter on HAT and USB-C outputs) |
| G-22 | PCB-R-04 | PCB-R-06 (R-04 is the certified antenna list; different content) |
| G-23 | PCB-R-05 | PCB-R-07 (R-05 places antennas for SAR; this one is the case input on the pocket floor and battery) |
| G-24 | PCB-E-04 | PCB-E-05 |
| G-25 | PCB-E-05 | Merged into PCB-E-04 (the same vias-at-the-pad rule; E-04 gains "no stub on the protected line" and TI SLVA680A) |
| G-26 to G-30 | PCB-T-07 to T-11 | PCB-T-08 to T-12 (T-07 is the RoHS and REACH BOM field); T-12's distance is PCB-D-01 |
| G-31, G-32 | PCB-G-09, G-10 | PCB-G-09, G-10 |
| G-33 | PCB-H-01 | PCB-L-03 (PCB-H is mounting holes) |
