# Research: a contact battery interface for the T1

- **Date:** 2026-10-24
- **Status:** Desk research behind [ADR 0020](../adr/0020-battery-connected-through-contacts.md). Nothing here has been built or measured. Values are from datasheets (named with page or sheet), from the [generic method](https://github.com/opendap-project/toolkit-hardware/blob/main/docs/research/2026-10-contact-battery-interfaces.md), or are arithmetic or estimates, marked as such. **UNVERIFIED** marks what was not read in a primary source.
- **Question:** how the T1's quoted 2S pack ([ADR 0014](../adr/0014-two-cell-battery.md)) connects to the board through contacts instead of the Micro-Fit 3.0 lead, keeping every ADR 0014 acceptance criterion, the gauge wiring of [ADR 0017](../adr/0017-fuel-gauge-wiring-sense-resistor-and-configuration.md), and BRD-049 margins.
- **Aim (maintainers, 2026-10-24):** a battery that connects through contacts (spring, blade or pad), not through a cable connector, so listeners replace it easily: the right to repair, and because many commercial players in this range have had battery problems; replacing the pack should not mean replacing the device, unplugging a cable or desoldering.
- **Scope:** the electronics and what they need from the case and the pack. The case mechanics are out of scope beyond those needs.
- **Method and precedents:** the generic method is in toolkit-hardware (precedents, architectures, sizing, qualification). This note applies it to the T1.

## 0. Summary

1. **Arrangement: face compression.** Six spring-finger contacts on the board, in a window of the pocket floor at the pocket's bottom end, press on six recessed gold pads on the underside of the pack's terminal board. The pack drops in, the back cover's foam holds it down. No side-acting part was found that carries ≥ 4.6 A per pole inside the 2.5 mm length allowance at the pocket end (§3).
2. **Part: KYOCERA AVX 70-9258-001-120-006**, 6 A per contact, 1.6–2.8 mm working height, 0.4 µm gold over nickel, 2,500 cycles, ≈ $0.25 at 1,000, stocked at four distributors. Two per power pole: 3.2 A worst continuous is **33 %** of one contact's rating on the hotter contact (sharing factor 1.25, assumed), the 5 A protective limit **52 %**; pole rating counted at **9.6 A** against the ADR 0014 criterion of ≥ 4.6 A.
3. **Working height 2.1 mm** (component zone 1.5 + pocket floor 0.4 + pad recess 0.2), ± 0.3 mm assumed: 1.8–2.4 mm, inside 1.6–2.8 mm. No battery-layer thickness is lost. The 2.5 mm of pocket length budgeted for the lead exit is freed (§2.3).
4. **Gauge and charger stay accurate**: the coulomb counter is on the board sense resistor, outside the contacts; cell voltages read at most ≈ 40 mV low per cell at 3.2 A through the contacts (est., 12.5 mΩ per pole), zero at rest, where Impedance Track takes its voltage readings; contact resistance can only make charging stop short, never overcharge. No Kelvin contact (§4.1).
5. **Insertion is soft by construction**: with no adapter, the BQ25798 is unpowered when the pack goes in, so the ship FET is off; the charger powers up from BATP and turns the ship FET on through its 100 nA charge pump (SLUSDV2C §7.3.12): the system capacitance charges at ≈ 0.3 V/ms (est.). With an adapter present, the inrush into the 2 × 10 µF BAT node lasts microseconds (est. 0.004 A²s against the fuse's 5.566 A²s melting I²t) (§4.3).
6. **Removal under load is safe** below gold's 15 V minimum arc voltage; the NTC contact opening stops charging in hardware; a cover-detect input lets Blackbird OS power down before the pack can be reached (should, not a safety function) (§4.4).
7. **Pack specification additions** (§5) and **PCB constraint proposals** PCB-L-04 to PCB-L-10 (§6), BOM line changes in ADR 0020.

## 1. Inputs

| Input | Value | Source |
|---|---|---|
| Poles | P+, P−, mid-cell tap, NTC | ADR 0014 item 1 |
| Worst continuous battery current | ≈ 3.2 A at VSYS 6.6 V | ADR 0014 item 1; BOM v1 §7 item 17 |
| Protective limits | Pack PCM over-current trip 4.0–5.0 A; board fuse 5 A (Littelfuse 0451005.MRL, cold resistance 12.5 mΩ, melting I²t 5.566 A²s at 8 ms) | ADR 0014 item 2; BOM line 104 |
| Per-pole acceptance | ≥ 4.6 A (3.2 A at 70 %) | ADR 0014 item 2 |
| Pack voltage | 2S, 6.0–8.8 V (4.2 V or LiHV cells) | ADR 0014 items 1, 2; ADR 0008 |
| Pocket | 10.9 × 50.5 × 63.8 mm, behind the board | [battery selection](2026-10-battery-selection.md); ADR 0016 |
| Under the pocket | Components ≤ 1.5 mm (PCB-Z-01; RK3566, LPDDR4X, eMMC there); pocket floor 0.4 mm, a metal plate tied to the frame | ADR 0016 items 3, 4; battery selection §2.2 |
| Pocket-end length allowance | 2.5 mm for lead exit, bend radius and connector seating; connector on the board in a notch outside the pocket | Battery selection §2.3 |
| Gauge | BQ28Z610-R1; VC2 and PBI on the pack side of the ship FET after the fuse; VC1 to the mid-cell tap; 3 mΩ low-side sense resistor in the P− return; gauge VSS on the cell side | ADR 0017 item 2 |
| Charger | BQ25798; BAT and BATP absolute maximum 20 V; recommended BAT capacitance 2 × 10 µF; BATP through 100 Ω to the pack positive | SLUSDV2C §5 (pin table), §6.1 |
| Ship FET | CSD17575Q3, Qg 23 nC typ at 4.5 V, Crss 157 pF typ | SLPS489A, p. 2 |
| Ingress | T1-017: IP65 for the Commercial edition (should, Draft); screw-retained gasketed back cover | T1-017; battery selection §2.1 |
| Regulation | Art. 11 of Regulation (EU) 2023/1542 from 18 Feb 2027; T1-055, T1-079, T1-080 | Generic method §5.1 |

## 2. Arrangement

### 2.1 Options

| Option | Fit in the T1 | Verdict |
|---|---|---|
| A. Face compression through a window of the pocket floor | Working height 1.9–2.1 mm is available without touching the battery layer; a stocked 6 A contact covers it (§3) | **Chosen** |
| B. Side-acting contacts at the pocket end | The best documented side-acting part (AVX 9155-500, 3 A per way, 1.5 mm travel, 140 g at 1.5 mm, drawing 00-9155-01_500S Issue 3 note 10) needs about 6.5 mm of length; the allowance is 2.5 mm, and the bottom band is full (jacks at about 14.5 mm of its 17 mm) | Rejected: costs about 4 mm of pocket length, ≈ 6 % of pack energy (arithmetic: 4 / 63.8) |
| C. Pogo pins | Mill-Max 0990 (2 A, 1.50–2.49 mm) needs four per pole; Harwin P70-7000045 has 50 mΩ maximum | Kept as an alternative to qualify (§3) |
| D. Blades | Too large for a pocket device | Rejected |

### 2.2 Geometry

- **Where:** a row of contacts in a window of the pocket floor at the pocket's bottom end, the end toward the bottom band, away from the top band's antenna keep-out. On the pack, the terminal board sits at the PCM end, its pads facing the board.
- **Order (one row, pitch 3.5 mm):** P+, P+, empty position, mid-cell tap, NTC, P−, P−. A pack displaced sideways by up to one pitch can join P+ only to the empty position, the mid-cell tap only to the NTC (≤ 4.45 V into TS, below its 6 V absolute maximum, SLUSDV2C §6.1) and the NTC only to P−, to which the NTC is referenced. Keying in the pocket and on the pack limits the displacement to well under a pitch; the order makes even that case harmless.
- **Window:** about 24.5 × 9 mm (arithmetic: 7 × 3.5 mm by the 7.8 mm contact length plus clearance). It takes board area from the zone under the pocket, where the RK3566, LPDDR4X and eMMC sit (ADR 0016 item 3): an input to placement (§6, PCB-L-04).
- **Working height:** 2.1 mm nominal from the board top to the pad surface: 1.5 mm component zone + 0.4 mm floor + 0.2 mm recess of the pads into the pack's underside. The tolerance, ± 0.3 mm, is an assumption until the case tolerance stack exists; it gives 1.8–2.4 mm against the contact's 1.6–2.8 mm.
- **Lift margin:** free height 3.0–3.3 mm. If a drop lifts the pack 0.5 mm, the power contacts' working height rises from 2.1 to 2.6 mm (inside the rated range); at the + 0.3 mm tolerance limit it reaches 2.9 mm, 0.1 mm above the range and still below the minimum free height: contact is kept, at reduced force. The signal contacts (pads 0.2 mm deeper, §4.2) can open at that worst corner; a momentary NTC opening pauses charging, nothing more. The Fairphone 4 lost contact at about 0.13 mm (generic method §1.2): the cover's preload, not the springs, keeps the pack down.

### 2.3 What changes elsewhere

- The 2.5 mm lead-exit allowance of the pocket length (battery selection §2.3) is no longer needed. It returns to the pack (about +4 % of pack length, arithmetic 2.5 / 60.5, est.) or to the case: an input to the pack specification and the case.
- The pocket floor needs the window and an insulating liner on its edges (it is metal, tied to the frame).
- The back cover's foam must preload the pack above the six contact forces (unknown until measured, §3).

## 3. Board-side part

| Part | Per contact | Pole as used | Working height | Force | Plating, cycles | Stock (2026-10-24) | Verdict |
|---|---|---|---|---|---|---|---|
| **KYOCERA AVX 70-9258-001-120-006** | 6 A (TDS-BTB-0026 Rev 1) | 2 per pole | 1.6–2.8 mm (drawing sheet 2) | **UNVERIFIED** (spec 201-01-252) | 0.4 µm Au over Ni; 2,500 cycles | Digi-Key 1,384 @ $0.25 (1,000); Mouser 3,495; Newark 3,930; Future 4,000 | **Chosen** |
| KYOCERA AVX 00-9155-002-101-006 (2-way) | 3 A per way (catalog p. 8) | 2 ways per pole: 4.8 A | 1.30–1.95 mm | > 40 g at minimum deflection | 0.4 µm Au; 5,000 cycles | Digi-Key 388; Mouser 2,728; Newark 2,847 | Rejected: 3.2 A is 67 % at nominal sharing; the range sits below 2.1 mm |
| Mill-Max 0990-0-15-20-76-14-11-0 pogo | 2 A (3 A peak), 20 mΩ max (catalog p. 28.4) | 4 per pole | 1.50–2.49 mm | 60 g at mid stroke | 0.5 µm Au; 1,000,000 cycles | Not found | Alternative: needs its own land and four pins per pole; stock to check |
| Mill-Max 0965-0-15-20-80-14-11-0 pogo | 2 A (3 A peak), 20 mΩ max | 4 per pole | 1.93–2.54 mm | 115 g at mid stroke | 0.5 µm Au; 1,000,000 cycles | Digi-Key 41,785; Mouser 290,264 | Alternative: lower working limit at the bottom of the range |
| KYOCERA AVX 00-9155-002-401-006 | 5 A | 1 per pole | 4.8 ± 0.7 mm | 0.65–1.75 N | 0.4 µm Au; 5,000 cycles | Digi-Key 7,357 | Rejected: too tall |
| Harwin P70-7000045 | 2 A, 50 mΩ max | — | 1.95–2.10 mm | 69 gf (secondary) | 0.41 µm Au; 10,000 cycles | Digi-Key 10,437 | Rejected: resistance |

Sources: KYOCERA AVX catalog *Board to Board Connectors 090325* and sales drawings; Mill-Max metric catalog (2023-08-15); Harwin PD012. Stock from Digi-Key product pages and FindChips, 2026-10-24. Molex, Würth, Hirose, TE and JAE battery contacts were not researched against datasheets in this pass (search budget): a later pass may find a second source on the same land.

**Current per pole** (generic method §3.1): two contacts per pole, sharing factor k = 1.25 (assumption until measured):

| Case | Pole current | Hotter contact | % of 6 A |
|---|---|---|---|
| Worst continuous | 3.2 A | 2.0 A | **33 %** |
| PCM trip upper limit, fuse rating | 5.0 A | 3.1 A | 52 % |
| ADR 0014 criterion | ≥ 4.6 A per pole | Pole rating 0.8 × 2 × 6 A = 9.6 A | 3.2 A is 33 % of 9.6 A |

**Resistance budget** (generic method §3.2), with an assumed end-of-life resistance of ≤ 20 mΩ per contact (**UNVERIFIED** until 201-01-252 or CB-01) and the pole taken as 12.5 mΩ (two contacts with unequal sharing):

| | 3.2 A | 5.0 A |
|---|---|---|
| Drop per pole | 40 mV | 63 mV |
| Drop, both poles | 80 mV (1.1 % of 7.4 V) | 125 mV |
| Loss per pole | 0.13 W | 0.31 W |
| Hotter contact | 0.08 W | 0.19 W |

The contacts add about 25 mΩ to a battery path that already holds the fuse (12.5 mΩ), the ship FET (≤ 3.2 mΩ) and the sense resistor (3 mΩ) (BOM lines 104, 120, 43). For comparison, the Micro-Fit lead it replaces had two contacts per pole in series (header and receptacle) plus the lead.

## 4. Electrical consequences

### 4.1 Gauge and charger accuracy

- **Coulomb counting:** the 3 mΩ sense resistor is on the board; SRP and SRN sense it directly (ADR 0017). Contact resistance is outside the measurement: counting is unaffected.
- **Cell voltages:** VC2 and VC1 are read on the board side of the contacts; VSS is the board P− node. During a 3.2 A discharge both cells read low by the drop of one pole each, ≤ 40 mV (est., §3), and zero at rest. Impedance Track takes its open-circuit voltage readings at rest (relaxed), and learns the series resistance of the whole path (cells, PCM FETs, contacts) as part of its impedance tables, which already include the PCM FETs. What would corrupt it is resistance that changes (fretting, contamination): stability is the requirement, checked by CB-03 to CB-06 and CB-12 of the generic plan.
- **Kelvin sense contacts: not used.** A separate VC2 sense contact would remove the P+ drop only (VSS cannot be separated from the gauge ground), and adds a contact whose opening gives a worse reading than the drop it removes. Cell protection does not depend on these readings: the pack PCM measures each cell inside the pack, and the gauge's protections are disabled (ADR 0017).
- **Charging:** the BQ25798 regulates at its BAT pin, with BATP sensing the pack side of the ship FET on the board. A drop in the contacts during constant-current charging lowers the cell voltage reached, never raises it; it falls to zero as the current tapers to termination. Charging slows slightly; it cannot overcharge.

### 4.2 Sequencing and safe states

- **Make:** P− and P+ before the signals, by pad recess: the power pads are recessed 0.2 mm, the mid-cell tap and NTC pads 0.4 mm, so a pack lowered flat touches the signal contacts about 0.2 mm later (est.; tilt can reverse it). **Break:** the reverse.
- **Every order is safe anyway** (PCB-P-17, kept): series resistance and clamping on the mid-cell tap and NTC lines per the BQ28Z610-R1 and BQ25798 absolute maxima, because a tilted pack can make in any order.
- **Missing NTC first:** when the NTC contact opens, the BQ25798 sees a missing thermistor and stops charging; with an adapter present it holds BAT near 2.5 V and regulates SYS at SYSMIN, and reports the fault (SLUSDV2C §7.3.6, the "no battery" case 1).

### 4.3 Hot insertion and inrush

- **No adapter** (the usual case): the old pack is out, so the BQ25798 is unpowered and SDRV is low: the ship FET is off. The new pack sees only the pack-side network: BATP through 100 Ω, the gauge VC2, PBI and VC1 filters, the fuse. The charger powers up from BATP once it exceeds VBAT_UVLOZ (3.25–3.55 V with the ship FET installed, SLUSDV2C §6.5), runs its POR (I²C after about 20 ms, §7.3.3) and turns the ship FET on (SDRV_CTRL = 00 at POR, §7.3.12). SDRV is a 100 nA charge pump, at about 50 % duty in battery-only mode (§7.3.12). Through the CSD17575Q3's Miller plateau (Crss 157 pF), the source rises at about 100 nA × 0.5 / 157 pF ≈ 0.3 V/ms (est.); with ≈ 100 µF on BAT and SYS (est.), the inrush is ≈ 30 mA (est.). Full enhancement takes Qg / (0.5 × 100 nA) ≈ 0.5 s (est.). The ship FET is a soft start.
- **Adapter present** (pack swapped with the T1 on its charger): the ship FET is on and BAT sits near 2.5 V. At contact, the pack (≤ 8.8 V) charges the BAT node (2 × 10 µF) through the loop (pack cells and PCM, contacts, fuse, ship FET; ≈ 0.1 Ω, est.): peak ≈ 63 A (arithmetic, 6.3 V / 0.1 Ω, an upper bound that ignores inductance), time constant ≈ 2 µs, I²t ≈ 0.004 A²s, 0.07 % of the fuse's 5.566 A²s melting I²t; energy ½CV² ≈ 0.4 mJ. Whether the pack PCM's short-circuit detection ignores a 2 µs pulse depends on its delay, which the pack specification must state (§5) (**UNVERIFIED**: typical PCM short-circuit delays are hundreds of microseconds).
- **Ringing:** PCB-P-15 (insertion transients against every absolute maximum on BAT, ceramic capacitors ringing up to 2 × 8.8 = 17.6 V against BAT and BATP's 20 V) stays. TI recommends an RC on BATP for hot-plugging packs with long leads (SLUSDV2C Figure 8-2, note 2: 100 Ω series, 47 nF) and a snubber capacitor on the EVM for hot-plugged 4S packs with a ship FET (SLUUCB5E §1, note on CSNUB3). The contacts have far less inductance than a lead; the RC on BATP is fitted anyway (PCB-L-09), and CB-07 measures the node.

### 4.4 Removal while on

- **Can the OS be running?** Yes. The back cover comes off first (screws, gasket), and nothing in the hardware assumes the OS is off.
- **No adapter:** the system loses its supply when the power contacts part. At ≤ 8.8 V there is no sustained arc (minimum arc voltage of gold 15 V, TE; generic method §4.4); a break spark at up to 3.2 A erodes the gold slightly. With the NTC contact recessed deeper, it usually opens first, but nothing depends on it.
- **Adapter present:** the BQ25798 keeps SYS regulated from the adapter (NVDC power path) and reports the missing battery; the T1 keeps running.
- **Cover detect (should):** a board input that changes state when the back cover is lifted, before the pack can be reached, so Blackbird OS syncs storage and powers off (the storage sequence of ADR 0017 item 3 when no adapter is present), as cameras do. It protects data, not safety: T1-086 is met without it.

### 4.5 Keying, polarity, ESD, contamination

- **Keying:** the pack's terminal end and the pocket carry matching asymmetric features (case and pack input). Pads on the underside only: an inverted pack presents no pads to the contacts; a pack turned end for end puts its plain end over the window.
- **Reverse polarity:** cannot be presented by a pack built to the specification. The BQ25798 has no reverse-battery protection (BAT minimum −0.3 V, SLUSDV2C §6.1); keying is the protection, and the contact order of §2.2 keeps a misaligned pack harmless.
- **ESD:** the contacts are reachable only with the cover off, during a replacement. The mid-cell tap and NTC lines get one TPD1E10B06 each at the contacts (bidirectional, ±5.5 V working, as BOM lines 36 and 74), grounded at the pad (PCB-E-04). The power contacts sit on low-impedance nodes (BAT pack side, P− ground); a TVS position on the P+ contacts (standoff ≥ 9 V, clamp below 20 V, part to choose) is kept as a footprint until CB-07 and CB-10 show whether it is needed.
- **Contamination and fretting:** gold on both sides; no tin in the contact area (the contact's tin is on its solder base only, drawing note 2). The pocket keeps loose metal out (no screw drops into the bay: case input).

## 5. Pack specification additions

The quoted pack (ADR 0014 item 2, T1-038 exception) adds, in place of the lead and Micro-Fit plug:

| Item | Specification |
|---|---|
| Terminal board | A rigid board at the PCM end of the pack, part of or soldered to the PCM board, its pad face flush with the pack's underside except for the recesses |
| Pads | Seven positions at 3.5 mm pitch in one row: P+, P+, (no pad), mid-cell tap, NTC, P−, P−. Each pad at least 4.0 × 2.5 mm (the contact's mating pad, drawing 70-9258-001-1X0-00XS sheet 2), lengthened along the contact axis by the pack's position tolerance in the pocket; gaps between pads ≥ 1.0 mm |
| Plating | Electrolytic hard gold, ≥ 0.76 µm, over nickel (thickness of nickel per the maker's practice, **UNVERIFIED** value to set); no ENIG or immersion gold in the contact area |
| Recess | Power pads 0.2 mm, signal pads 0.4 mm below the pack's underside (§2.2, §4.2); walls of the end cap around each group, so a flat metal object lying on the pack cannot touch two pads |
| Keying | Asymmetric terminal end matching the pocket (case input); polarity marked next to the pads (IEC 62133-2 clause 5.5) |
| Current | Each power pad and its copper to the PCM carry ≥ 5 A continuous |
| PCM | As ADR 0014 item 2 (over-charge, over-discharge, over-current trip 4.0–5.0 A, short-circuit, balancing), plus its short-circuit detection delay and threshold stated, and a pulse of 63 A for 2 µs (§4.3) shown not to trip it, or the actual behaviour stated |
| Tests | UN 38.3 (T.5 external short at the pads) and IEC 62133-2 (7.3.2 external short with a single fault in the protection) on the pack as shipped, with exposed pads (T1-079) |
| Transport and spares | A terminal cover or separating packaging for spare packs |
| Label | Art. 13 and WEEE marks (T1-080), polarity at the pads, the specification identifier |
| Published | The full pack specification, so any maker can build a replacement (T1-079) |

## 6. PCB constraint proposals

For the owner of [PCB design constraints](../specs/pcb-design-constraints.md) to merge; this note does not edit it. Levels per RFC 0010.

| ID | Constraint | Source | Check |
|---|---|---|---|
| PCB-L-04 [Q0] | Battery contact window at the pocket's bottom end: seven positions at 3.5 mm pitch, order P+, P+, empty, mid-cell tap, NTC, P−, P−; six KYOCERA AVX 70-9258-001-120-006 on 7.00 × 2.70 mm pads; the empty position carries no copper | ADR 0020; drawing sheet 2 | REV, CHK |
| PCB-L-05 [Q0] | Rule area `BATTERY_CONNECTOR` (PCB-L-02) becomes the contact window plus 1 mm; inside it only the battery nets and GND; zone exception to PCB-Z-01 for the contacts (free height 3.3 mm) | PCB-L-02; ADR 0020 | DRC |
| PCB-L-06 [Q0] | Board top to pack pad 2.1 mm nominal, inside 1.6–2.8 mm over the tolerance stack (input to the case: floor standoff, floor thickness, pack recess); ≥ 1.0 mm from any contact and its travel to the metal floor's window edge, which carries an insulating liner | ADR 0020 item 3; ADR 0016 | REV (3D), case |
| PCB-L-07 [Q1] | Each pole's two contacts joined in a symmetric pour: equal copper length from each contact to the fuse (P+) or the sense resistor (P−), so the sharing factor stays near 1; ≥ 4 vias per contact pad to the pour (count **UNVERIFIED**, to replace by the IPC-2152 via calculation of PCB-P-09) | Generic method §3.1; PCB-P-01 | REV, CHK |
| PCB-L-08 [Q1] | One TPD1E10B06 on each of the mid-cell tap and NTC lines, within 3 mm of the contact, ground at the pad (PCB-E-04); a TVS position on P+ at the contacts (standoff ≥ 9 V, clamp < 20 V), DNP until CB-07 and CB-10 | ADR 0020 item 6 | schematic, REV |
| PCB-L-09 [Q0] | BATP: 100 Ω in series at the pin and 47 nF to GND (SLUSDV2C pin table, Figure 8-2 note 2); test points on the pack side of the fuse and on BAT for the insertion measurement (CB-07) | SLUSDV2C; PCB-P-15 | schematic, REV |
| PCB-L-10 [Q2] | Cover detect: one input with a pull-up and a TPD1E10B06, a contact pad at the board edge for the case's actuator; the GPIO is chosen in the pinout | ADR 0020 item 7 | schematic, REV |

Wording changes: PCB-P-01 "connector → fuse" becomes "battery contacts → fuse"; PCB-P-17 "the four Micro-Fit pins" becomes "the six battery contacts".

## 7. Qualification of the T1 interface

The generic plan (toolkit-hardware, CB-01 to CB-12) applies, with these T1 values:

| Row | T1 value |
|---|---|
| CB-01 | ≤ 20 mΩ per contact at end of life (budget assumed in §3; replace with 201-01-252) |
| CB-02 | 3.2 A per pole continuous, 5 A per pole for the PCM's trip time; contact and pad temperature below the pack's charge limit at the pocket |
| CB-04 | Drop tests of the T1 (t1 verification matrix) with event detection on BAT; no reset on battery |
| CB-07 | Insertion with and without an adapter: BAT, BATP and the pack side of the fuse ≤ 20 V × the BRD-049 margin; no PCM trip |
| CB-12 | Gauge state of charge within the T1 target after CB-03 to CB-06 |

Before the board freezes: obtain KYOCERA AVX product specification 201-01-252 (force, resistance, current-rating basis); build a bench terminal board (the pack's pad layout on a small board, wired to a bench supply or a protected 2S pack) so prototype 1 is brought up through the same contacts (ADR 0014 item 4).

## 8. Sources

- KYOCERA AVX: TDS-BTB-0026 Rev 1 (9258-100), 2025-09-10; drawing 70-9258-001-1X0-00XS Rev F; catalog *Board to Board Connectors 090325* (pp. 8, 12, 13, 36); drawing 00-9155-01_500S Issue 3. Manifest entries in [parts-lib](https://github.com/opendap-project/parts-lib/blob/main/manifest.toml) for the chosen part.
- Mill-Max metric catalog (2023-08-15), p. 28.4. Harwin PD012 (2025-09-29).
- TI SLUSDV2C (BQ25798, revised June 2026): §5 pin table (BAT, BATP, SDRV), §6.1, §6.5 (VBAT_UVLOZ), §7.3.3, §7.3.6, §7.3.12, Figure 8-2 notes. TI SLUUCB5E (BQ25798EVM, July 2022), §1 notes. TI SLPS489A (CSD17575Q3), p. 2.
- [Contact-based battery interfaces](https://github.com/opendap-project/toolkit-hardware/blob/main/docs/research/2026-10-contact-battery-interfaces.md) (toolkit-hardware), for precedents, standards and the method.
- Stock: Digi-Key product pages and FindChips, read 2026-10-24.
