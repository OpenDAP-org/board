# HAT flat cable

- **Status:** Draft v0 (2026-10-24). Task E1.8 of the [electronics plan](https://github.com/opendap-project/t1/blob/main/docs/plans/2026-10-electronics-plan.md). Written by Claude under the maintainers' delegation. Nothing here is built or measured; every impedance, loss and temperature figure is computed and is confirmed only by the test coupon (§14).
- **Requirements:** BRD-013 (this repository owns the flat cable), BRD-042 (nothing in the high-speed paths limits the link), BRD-049 (margin below every rating), BRD-060 (constraints with limits); hat-standard HCS-004, HCS-015, HCS-023, HCS-026.
- **Inputs:** hat-standard [interface v1.1](https://github.com/opendap-project/hat-standard/blob/main/docs/specs/interface-v1.md) §5 and §7.2, [ADR 0004](https://github.com/opendap-project/hat-standard/blob/main/docs/adr/0004-pogo-part-and-field-geometry.md) (coupon), [ADR 0005](https://github.com/opendap-project/hat-standard/blob/main/docs/adr/0005-interface-v1-1-shared-extension-and-contact-reduction.md) (one DF40C-100 pair per end, 87 used, 9 spare, fault ceilings 3.0 / 1.5 / 4.5 A); [ADR 0002](../adr/0002-hat-signals-leave-the-board-over-a-flat-cable.md); [BOM v1](bom-v1.md) lines 65, 66, 102; [PCB design constraints](pcb-design-constraints.md) PCB-I-01 to PCB-I-03, PCB-I-12, PCB-R-06, PCB-P-05, PCB-P-20; kicad-lib [PCBWay capabilities](https://github.com/opendap-project/kicad-lib/blob/main/docs/research/2026-10-pcbway-capabilities.md) §1.3 and [`pcbway-flex`](https://github.com/opendap-project/kicad-lib/tree/main/design-rules/pcbway-flex); parts-lib `Hirose/DF40C-100DS-DP-0.4V.md`; the Hirose DF40 catalog (May 1, 2020) and drawing EDC3-311351-00; PCBWay's *Stack-up for FPC* page (fetched 2026-10-24).
- **Computation:** [`sim/flex-impedance`](../../sim/flex-impedance/README.md), a 2D finite-difference field solver (validated within 1 % against closed forms). `odapkit stackup` (toolkit-hardware) did not exist yet; the geometries are to be rerun there.
- **Conventions:** **UNVERIFIED** = no primary source checked. *Input from the case* = a value the case repository sets; this spec assumes a range and says so. Rule IDs `HFC-nn` carry their RFC 0010 quality level; an untagged item is Q1. Positions are DF40 contact numbers as in interface v1.1 §7.2.

## Summary

The flat cable carries the whole HAT interface, signals and power, from the board to the HAT device-side piece. It is a fabricated 4-layer polyimide circuit:

- **Stack-up:** PCBWay's standard 4-layer FPC, 0.268 mm, adhesive-based cores, 12 µm inner and 18 µm (24 µm finished) outer copper (§4).
- **Connectors:** one Hirose DF40C-100 at each end. Hirose recommends mounting the **header** on the FPC (catalog p. 19), so the cable carries two DF40C-100DP-0.4V(51) headers and the board and device-side piece carry the DF40C-100DS-0.4V(51) receptacles. This swaps the genders of BOM line 66 (§2, §17).
- **Pairs:** every pair runs on L2 as a stripline, ground on L1 above (51 µm) and L4 below (114 µm, L3 voided under the pairs): `EXT0`–`EXT4` 60 / 150 µm for 100.3 Ω, USB 3 and USB 2 70 / 100 µm for 89.9 Ω, I2S 65 µm for 49.7 Ω single-ended. Pairs sit at least 0.35 mm apart (backward coupling −61 dB at 0.3 mm and −77 dB at 0.4 mm, computed). No guard traces between pairs; the ground is the two planes and the via fences (§6, §8).
- **Power:** `HAT_5V` ≥ 10.5 mm and `HAT_3V3` ≥ 4.0 mm on L3, return on the L1 and L4 planes, sized by IPC-2221B for a 10 °C rise at the fault ceilings (3.0 / 1.5 / 4.5 A) and about 4 °C at the continuous ratings. Drop for a 100 mm cable with both DF40 pairs at their maximum contact resistance: 106 mV (2.1 %) on `HAT_5V` and 114 mV (3.5 %) on `HAT_3V3` at the continuous ratings (§9).
- **Shielding:** none added. With ground planes on both outer layers an EMI film changes nothing the pairs see; on a microstrip cable it would drop the impedance by about 34 % (§10).
- **Stiffeners:** 0.2 mm stainless steel under each DF40, bonded with a reflow-capable adhesive (§11).
- **Bend:** static (bend-to-install) only, inside radius ≥ 4.0 mm (15 × thickness), never below 2.7 mm (10 ×) (§12).
- **Length and width:** input from the case. This spec assumes 40–100 mm and a 25.0 mm body; the cross-section needs 24.7 mm (§5, §12).
- **Coupon:** six cable members join the hat-standard ADR 0004 coupon (§14).

## 1. Scope and topology

```text
board DF40C-100DS ── FPC DF40C-100DP ══ flat cable (4-layer FPC) ══ FPC DF40C-100DP ── device-side piece DF40C-100DS ── pogo field
                     └ steel stiffener                                └ steel stiffener
```

This spec covers the cable: conductors, stack-up, geometry, stiffeners, bend, fab notes and its coupon members. It does not cover the board-side routing (PCB design constraints), the device-side piece or the pogo field (hat-standard), or the case (case repository); §15 lists what the cable needs from the case.

## 2. Connectors

| Item | Value | Source |
|---|---|---|
| Part on the cable, both ends | Hirose **DF40C-100DP-0.4V(51)** header, 100 positions, 0.4 mm pitch | Catalog p. 19: "We recommended to mount the header side to the FPC"; the receptacle "may peel away" from an FPC without enough rigidity, and Hirose gives its FPC-rigidity evaluation on request |
| Mating part on the board and on the device-side piece | DF40C-100DS-0.4V(51) receptacle | BOM line 66 (gender swapped, §17) |
| Stack height | 1.5 mm (DS + DP, no height code) | Catalog p. 3 |
| Usable positions | 96: the four corner contacts are metal hold-downs | Catalog p. 10 note 3; drawing EDC3-311351-00 note 2 |
| Rating | 0.3 A per contact, 30 V; contact resistance ≤ 90 mΩ; 30 mating cycles | Catalog p. 2 |
| Lock | None on the 60- to 120-position parts | Drawing note 3; catalog p. 10 note 2 |
| Polarization | None; a 180° mating would put `HAT_5V` on signal contacts | Catalog p. 10 note 5; interface v1.1 §7.2 |
| Header land pattern (on the cable) | 0.23 ± 0.02 mm lands at 0.4 mm; outer edge to edge 3.37 mm, inner 2.05 mm; hold-down lands 0.35 mm | Drawing EDC3-311351-00, recommended pattern |
| Flatness under the connector | ≤ 0.02 mm at the connector's centre against its two ends | Catalog p. 16, item 4 |
| Data rate | Not published by Hirose for the standard type (**UNVERIFIED**; a distributor lists 10 Gb/s, hat-standard interconnect benchmark §5) | Parts-lib sheet |

**Contact numbering (UNVERIFIED).** Interface v1.1 §7.2 numbers contacts 1, 3, 5 … on row A and 2, 4, 6 … on row B, 1 and 2 at the same end. The drawing for reference (EDC3-311351-00, revision 7) shows a triangular mark at one end of the body and no contact numbers; which end is contact 1, and that receptacle contact *n* mates header contact *n*, are to be confirmed on Hirose's drawing for approval before the cable layout (interface v1.1 §10 item 6).

## 3. Conductor map, end to end

The cable joins position *n* at the board end to position *n* at the device-side end, for every *n*: the two FPC headers are placed with contact 1 on the same cable edge, so every conductor runs straight and none crosses another outside the stiffened areas. A fold in the case changes which face a connector is on, never the map.

Classes: **P5** `HAT_5V` pour, **P3** `HAT_3V3` pour, **G** ground (L1 and L4 planes), **D100** 100 Ω pair, **D90** 90 Ω pair, **S50** 50 Ω single-ended, **LS** low-speed, **R** reserved (routed end to end, unconnected or ≥ 100 kΩ to `GND` on the device side, interface v1.1 §8), **—** spare (pad only, no conductor), **MF** metal fitting (hold-down, no conductor).

| Row A | Net | Class, cable layer | Row B | Net | Class, cable layer |
|---|---|---|---|---|---|
| 1 | metal fitting | MF | 2 | metal fitting | MF |
| 3–21 (odd) | HAT_5V ×10 | P5, L3 | 4–22 (even) | GND ×10 | G |
| 23–31 (odd) | HAT_3V3 ×5 | P3, L3 | 24–32 (even) | GND ×5 | G |
| 33 | HAT_DET# | LS, L2 | 34 | spare | — |
| 35 | GND | G | 36 | HAT_INT# | LS, L2 |
| 37 | USB3_SSTX+ | D90, L2 | 38 | ID_SCL | LS, L2 |
| 39 | USB3_SSTX− | D90, L2 | 40 | ID_SDA | LS, L2 |
| 41 | GND | G | 42 | I2C_SCL | LS, L2 |
| 43 | USB3_SSRX+ | D90, L2 | 44 | I2C_SDA | LS, L2 |
| 45 | USB3_SSRX− | D90, L2 | 46 | RSVD_1A | R, L2 |
| 47 | GND | G | 48 | RSVD_1B | R, L2 |
| 49 | USB3_D+ | D90, L2 | 50 | RSVD_1C | R, L2 |
| 51 | USB3_D− | D90, L2 | 52 | spare | — |
| 53 | GND | G | 54 | EXT_SB0 | LS, L2 |
| 55 | EXT0+ | D100, L2 | 56 | EXT_SB1 | LS, L2 |
| 57 | EXT0− | D100, L2 | 58 | EXT_SB2 | LS, L2 |
| 59 | GND | G | 60 | RSVD_3A | R, L2 |
| 61 | EXT1+ | D100, L2 | 62 | RSVD_3B | R, L2 |
| 63 | EXT1− | D100, L2 | 64 | spare | — |
| 65 | GND | G | 66 | HAT_RST# | LS, L2 |
| 67 | EXT2+ | D100, L2 | 68 | RSVD_2C | R, L2 |
| 69 | EXT2− | D100, L2 | 70 | spare | — |
| 71 | GND | G | 72 | GPIO0 | LS, L2 |
| 73 | EXT3+ | D100, L2 | 74 | GPIO1 | LS, L2 |
| 75 | EXT3− | D100, L2 | 76 | GPIO2 | LS, L2 |
| 77 | GND | G | 78 | GPIO3 | LS, L2 |
| 79 | EXT4+ | D100, L2 | 80 | RSVD_2A | R, L2 |
| 81 | EXT4− | D100, L2 | 82 | RSVD_2B | R, L2 |
| 83 | GND | G | 84 | spare | — |
| 85 | I2S_MCLK | S50, L2 | 86 | I2S_DIN0 | S50, L2 |
| 87 | GND | G | 88 | I2S_DIN1 | S50, L2 |
| 89 | I2S_BCLK | S50, L2 | 90 | I2S_DIN2 | S50, L2 |
| 91 | GND | G | 92 | I2S_DIN3 | S50, L2 |
| 93 | I2S_FS | S50, L2 | 94 | spare | — |
| 95 | I2S_DOUT | S50, L2 | 96 | spare | — |
| 97 | spare | — | 98 | spare | — |
| 99 | metal fitting | MF | 100 | metal fitting | MF |

Count, as interface v1.1 §7.2: 87 conductors (power 15, `GND` 26, pairs 16, `HAT_DET#` 1, low-speed 21 of which I2S 8, reserved 8), 9 spare positions, 4 metal fittings. Spare positions get pads and no conductor: a later interface revision that uses them comes with a new cable revision (interface v1.1 §8: spares let the interface grow "without a new flat-cable connector", not without a new cable).

## 4. Stack-up

PCBWay standard 4-layer FPC, 0.268 mm (nominal, base copper; about 0.28 mm with the outer plating). Every layer thickness is PCBWay's published figure.

| Layer | Material | Thickness | Use |
|---|---|---|---|
| Coverlay | PI 12.5 µm + adhesive 15 µm (yellow or black) | 27.5 µm | — |
| **L1** | Copper 18 µm base, 24 µm finished | 18 (24) µm | `GND` plane; DF40 lands at both ends |
| Dielectric | Adhesive 13 / PI 25 / bonding sheet 13 | 51 µm | — |
| **L2** | Copper 12 µm | 12 µm | Pairs, I2S, low-speed, reserved |
| Dielectric | Adhesive 13 / PI 25 / adhesive 13 | 51 µm | — |
| **L3** | Copper 12 µm | 12 µm | `HAT_5V`, `HAT_3V3` pours; **void under the pair band** |
| Dielectric | Bonding sheet 13 / PI 25 / adhesive 13 | 51 µm | — |
| **L4** | Copper 18 µm base, 24 µm finished | 18 (24) µm | `GND` plane |
| Coverlay | Adhesive 15 µm + PI 12.5 µm | 27.5 µm | — |

- Dielectric constant: PI 3.3 adhesiveless, 3.5 with adhesive (PCBWay); the adhesive and bonding sheet DK is not published, so 3.5 is assumed and 3.3–3.6 is the computed sensitivity. Loss tangent not published (**UNVERIFIED**).
- Why this stack: its dielectrics are 51 µm, the thickest of PCBWay's standard 4-layer stacks; the 0.204 mm stack (38 µm between L1 and L2, 25 µm between L2 and L3) needs pair traces of about 35–45 µm, below PCBWay's 0.06 mm floor. A custom stack with 75 µm cores lowers the conductor loss from 1.35 to about 1.19 dB per 100 mm at 2.5 GHz (computed) for a 0.35 mm, stiffer cable: not worth it on the figures, kept as the option if the coupon asks for it.
- Thickness tolerance: ±1.2 mil (±0.03 mm) for a multilayer flex up to 12 mil; 0.268 mm is 10.6 mil (PCBWay [P5]).

## 5. Layer use and cross-section

Across the cable body, from the edge on the contact-1 side (layout estimate; the KiCad layout checks it):

| Band | Width | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| Edge, via fence | 0.6 mm | GND | — | — | GND |
| Power, 3.3 V | 4.0 mm | GND | Low-speed and reserved lines (22, 0.10 mm wide, 0.15 mm apart: 5.5 mm, spread over both power bands) | `HAT_3V3` | GND |
| Gap | 0.3 mm | GND | | — | GND |
| Power, 5 V | 10.5 mm | GND | | `HAT_5V` | GND |
| Pair band | 8.7 mm | GND | 3 × D90, 5 × D100, 8 × S50 | **void** | GND |
| Edge, via fence | 0.6 mm | GND | — | — | GND |
| **Total** | **24.7 mm** | | | | |

Pair band detail (L2): 0.65 mm margin to the `HAT_5V` pour edge (room for the band's via fence), SSTX, SSRX, USB 2 (0.24 mm each), EXT0–EXT4 (0.27 mm each), 0.35 mm between pairs, 0.4 mm to the I2S group, the I2S group (about 2.5 mm), 0.65 mm to the band edge. The L3 pour edge stays ≥ 0.65 mm from the nearest pair or I2S trace so it does not change their impedance.

**Fan-out zone.** At the connector, row A's pairs sit at positions 37–83, across from row B's low-speed positions 36–82, and the power positions 3–32 are at one end. Between the connector and the cable body, inside the stiffened area, the layers are used freely: the pairs shift on L2 to the pair band, row B's low-speed lines cross the pair escapes on L3 at right angles (L3 is not yet a pour there) and settle on L2 over the power bands once clear of the power vias, and the power pours widen from the connector's 6 mm to their body widths. No line crosses a pair outside the stiffened areas.

## 6. Impedance geometry

Computed with the field solver of `sim/flex-impedance` (method in its README). Pairs are edge-coupled striplines on L2: L1 51 µm above the trace, L4 114 µm below it (L3 voided). DK 3.3 (PI) and 3.5 (adhesive, assumed).

| ID | Class (net class on the cable) | Signals | Target | Trace / gap | Computed | DK 3.3 / 3.6 | Width −10 / +10 µm |
|---|---|---|---|---|---|---|---|
| HFC-01 [Q1] | D100 `HAT_EXT_100D` | `EXT0±`–`EXT4±` | 100 Ω ± 10 % differential (interface v1.1 §4.1, ADR 0005, PCB-I-12) | 60 / 150 µm | 100.3 Ω diff, 26.4 Ω common | 102.2 / 97.8 Ω | 108.8 / 93.1 Ω |
| HFC-02 [Q1] | D90 `USB_90D` | `USB3_SSTX±`, `USB3_SSRX±`, `USB3_D±` | 90 Ω ± 10 % differential (interface v1.1 §4.1, PCB-I-01, PCB-I-02) | 70 / 100 µm | 89.9 Ω diff, 25.4 Ω common | 91.6 / 87.7 Ω | 97.4 / 83.3 Ω |
| HFC-03 [Q1] | S50 `I2S_50SE` | `I2S_*` (8) | 50 Ω ± 10 % single-ended (as the board's PCB-I-08) | 65 µm | 49.7 Ω | — | 51.5 Ω (60 µm) / 48.0 Ω (70 µm) |
| HFC-04 [Q1] | LS | Low-speed, reserved | Not controlled | ≥ 0.10 mm / ≥ 0.15 mm | — | — | — |

- PCBWay controls flex impedance to ±7 % above 50 Ω [P5] by compensating the width; the ±10 µm columns show why the width is theirs to adjust. The order names L2 as the signal layer and L1 and L4 as its references, with L3 void under the pair band (a custom impedance request, **UNVERIFIED** as a standard PCBWay case).
- 60 µm sits at PCBWay's 0.06 mm order-form floor and below the `pcbway-flex` 3 mil default: the cable's product rules allow it in the D100 class only (§13).
- Propagation: effective DK 3.42, 6.17 ps/mm.
- Matching on the cable: within each pair ≤ 0.1 mm (HFC-05 [Q1]); `EXT0`, `EXT2`–`EXT4` against `EXT1` (the CSI-2 clock) ≤ 0.1 mm (HFC-06 [Q1]). The pairs run straight and parallel, so both are met by construction; the board owner decides whether the cable's 0.1 mm counts inside PCB-I-12's 0.91 mm CSI-2 budget (§17).
- Both members of a pair take the same number of vias, side by side, at each end (HFC-07 [Q1], as PCB-I-10).

## 7. Loss and length

Estimates for the assumed maximum length, 100 mm; the coupon measures the real channel (§14).

| Item at 2.5 GHz (the Nyquist frequency of 5 Gb/s) | D100 | D90 | Method |
|---|---|---|---|
| Conductor loss, smooth copper | 1.35 dB | 1.34 dB | Wheeler incremental inductance, field solver |
| Dielectric loss, loss tangent 0.005–0.02 (**UNVERIFIED**, assumed range) | 0.21–0.84 dB | 0.21–0.84 dB | 42.1 × tan δ dB per 100 mm at effective DK 3.42 |
| Cable total | 1.6–2.2 dB | 1.6–2.2 dB | Sum; roughness and the DF40 transitions not included |
| At 1.25 GHz, conductor | 0.96 dB | 0.95 dB | Same |

- Loss scales with length: a 40 mm cable has 0.6–0.9 dB at 2.5 GHz.
- The channel budget of each link (board traces, extension switch, two DF40 pairs, cable, pogo field, HAT pads) against the USB 3, PCIe Gen 2 and D-PHY budgets is not set here: the DF40 has no published loss figure and the pogo field none at all. The hat-standard benchmark's proposed coupon criteria (§14) and the measured channel decide. Until then the cable is held at ≤ 100 mm (HFC-08 [Q1]); a longer route from the case needs this section redone.

## 8. Grounds around the pairs

- **No guard traces between pairs** on L2 (HFC-09 [Q1]). An unstitched guard across a bend would be a resonant stub, and the board's own rule allows a guard only when it is stitched along its length (PCB-I-09). Isolation comes from spacing between two planes: two 60 µm lines 0.3 mm apart couple at about −61 dB backward, 0.4 mm apart at −77 dB (computed). Pairs keep ≥ 0.35 mm from each other and ≥ 0.4 mm from the I2S group and any other line.
- **Planes:** L1 and L4 are solid ground over the whole body (HFC-10 [Q1]). PCB-R-06's "ground on both sides of the flex" is met by them.
- **Via fences:** through vias tie L1 to L4 along both cable edges and along the pair band's edge on the power side, at ≤ 2.0 mm pitch (about λ/10 at 7.5 GHz, the third harmonic of 2.5 GHz, in effective DK 3.42), everywhere except in bend zones (HFC-11 [Q1]).
- **At each connector:** every `GND` position (the 15 power returns, the 9 pair grounds between the G-S-S-G pairs of row A, and 87, 91 next to the audio clocks) has its own via to L1 and L4 inside the stiffened area (HFC-12 [Q1]). The I2S clocks `I2S_MCLK` and `I2S_BCLK` keep ≥ 0.4 mm from every other line along the cable.

## 9. Power conductors

Sizing rule (BRD-049, as the interface's contacts): each conductor is rated at a 10 °C rise, the rating is at least the fault ceiling (100 %), and the continuous rating is at most 70 % of it. Method: IPC-2221B design equation, I = k · ΔT^0.44 · A^0.725 (A in mil², k = 0.024 for an inner layer), conservative for a thin polyimide circuit; the coupon measures the real rise.

| ID | Rail | Continuous (interface) | Fault ceiling | Conductor | Minimum width | Rise at continuous |
|---|---|---|---|---|---|---|
| HFC-13 [Q0] | `HAT_5V`, both directions | 2.0 A | 3.0 A | L3 pour, 12 µm | **10.4 mm** (10.5 mm used) | ≈ 4 °C |
| HFC-14 [Q0] | `HAT_3V3` | 1.0 A | 1.5 A | L3 pour, 12 µm | **4.0 mm** | ≈ 4 °C |
| HFC-15 [Q0] | `GND` return | 3.0 A | 4.5 A | L1 + L4 planes, 18 µm base | 4.65 mm on one outer layer; the planes give about 46 mm | < 1 °C |

- **At the connectors:** each power pad carries ≤ 0.3 A (the DF40 rating, interface v1.1 §5) and has at least one via to its pour, two where they fit (HFC-16 [Q0]). A 0.15 mm via with 15 µm plating (plating **UNVERIFIED** for PCBWay flex) rates about 0.75 A at 10 °C by the same equation.
- **Neck-downs:** none along the body; a narrower route from the case changes the widths (the 18 µm inner-copper option of PCBWay [P13] takes `HAT_5V` to 6.9 mm and `HAT_3V3` to 2.7 mm).

**Voltage drop** (round trip, cable plus both DF40 pairs at the catalog's 90 mΩ maximum per contact; copper at 20 °C):

| Length | Case | `HAT_5V` | `HAT_3V3` | Of which DF40 contacts |
|---|---|---|---|---|
| 40 mm | Continuous (2.0 / 1.0 A) | 85 mV (1.7 %) | 89 mV (2.7 %) | 36 mV per rail and 36 mV on `GND` |
| 40 mm | Fault ceiling (3.0 / 1.5 A) | 128 mV (2.6 %) | 133 mV (4.0 %) | 54 mV each |
| 100 mm | Continuous | 106 mV (2.1 %) | 114 mV (3.5 %) | as above |
| 100 mm | Fault ceiling | 158 mV (3.2 %) | 171 mV (5.2 %) | as above |

The `GND` return carries both rails' current, so it appears in both loops. The DF40 maximum contact resistance dominates. The `HAT_5V` voltage window is still open (interface v1.1 §10 item 1, **UNVERIFIED**); these figures are an input to it.

## 10. Shielding

- **No EMI shielding film in the baseline** (HFC-17 [Q2]). The pairs are striplines between the L1 and L4 planes: a film on either coverlay sits outside a solid plane and does not change their impedance.
- **Why not microstrip with a film:** on the 0.204 mm stack, a 60 / 150 µm microstrip pair on L1 is 93.7 Ω bare and 62.0 Ω with a film on its coverlay (−34 %); 70 / 150 µm goes from 87.7 to 56.8 Ω (computed). A film over microstrip has to be designed in from the start, and its conductive-adhesive thickness is not published (**UNVERIFIED**).
- **If pre-compliance (Q2) asks for more:** PCBWay offers HCF-6000G or PC800 film on either side [P13]; over the L1 and L4 planes it adds thickness (recheck the bend radius) and nothing else. The coupon includes a film variant (§14, member C6).

## 11. Stiffeners

| ID | Item | Value | Source or reason |
|---|---|---|---|
| HFC-18 [Q0] | Material and thickness | Stainless steel 0.2 mm, under each DF40 header, on the opposite face | PCBWay offers 0.1–0.5 mm steel [P13]. Steel gives the most stiffness per thickness of PCBWay's options; FR-4 0.4 mm is the alternative where the case gives more height |
| HFC-19 [Q0] | Extent | The header's land pattern and the whole fan-out zone (§5), plus ≥ 1.0 mm on every side (about 25 × 8 mm; the layout sets it) | Hirose: flatness ≤ 0.02 mm under the connector (p. 16) and enough FPC rigidity (p. 19) |
| HFC-20 [Q0] | Bond | Heat-cured adhesive rated for the DF40 reflow (peak 250 °C, two cycles, catalog p. 16); not the 3M tapes PCBWay marks "not for reflow" | PCBWay [P13]; which adhesive PCBWay uses is **UNVERIFIED** (DFM) |
| HFC-21 [Q1] | Edges | Stiffener edges ≥ 1.0 mm from any bend zone; coverlay overlaps the stiffener edge | Strain relief |
| HFC-22 [Q1] | Mating surface | The stiffener is the surface the case presses to keep the unlocked DF40 mated (§15) | Catalog p. 16: hold the connector with the case if impact or the FPC's counterforce can unmate it |

Hirose's FPC-rigidity evaluation data (catalog p. 19) is to be requested; it can change the thickness. The stiffener can be grounded to L4 through PCBWay's conductive tape [P13] if the case wants it as a ground contact (input from the case).

## 12. Bend, length and routing

| ID | Item | Value | Source |
|---|---|---|---|
| HFC-23 [Q0] | Bend type | Static: folded once at assembly, held in place; never flexed in use | Design choice; a 4-layer circuit with solid planes is not a dynamic flex |
| HFC-24 [Q0] | Minimum inside bend radius | **2.7 mm absolute** (10 × 0.268 mm) | PCBWay multilayer 10–15 × thickness [P5] |
| HFC-25 [Q1] | Design inside bend radius | **≥ 4.0 mm** (15 ×) | Same, upper end |
| HFC-26 [Q1] | Bend zones | No vias, pads, stiffener edges, plane or pour edges, or changes of trace width within a bend zone and 1.0 mm either side; traces cross the bend axis at right angles; both members of a pair bend together | kicad-lib `pcbway-flex` README (bend keep-outs) |
| HFC-27 [Q1] | Length | Assumed 40–100 mm (input from the case); ≤ 100 mm unless §7 is redone | §7 |
| HFC-28 [Q1] | Width | 25.0 mm body assumed (input from the case); the cross-section needs 24.7 mm (§5) | §5 |
| HFC-29 [Q2] | Placement in the case | Away from the antennas and their feeds; distance **UNVERIFIED** (PCB-R-06) | PCB-R-06 |

Assumed range, stated: the board sits behind the display and the device-side piece on the back of the body, with the battery layer between them (board ADR 0016: back components 1.5 mm, pocket floor 0.4 mm, battery 12.3 mm, back cover 1.5 mm). The cable rises about 16 mm past the battery's edge plus the lateral run to the pogo field, which gives the 40–100 mm range. The real route is the case's.

## 13. Fab notes

- **Rules:** kicad-lib `pcbway-flex` (3 mil track and gap, 0.15 / 0.35 mm vias, 0.20 mm copper to outline **UNVERIFIED** for flex), with cable product rules on top: 60 µm minimum track in the D100 class only (PCBWay's 0.06 mm order-form floor); the widths of §6 and §9 per net class; HFC-26 keep-outs as rule areas.
- **Coverlay at the DF40:** the header lands are 0.23 mm at 0.4 mm pitch, a 0.17 mm gap, below the 8 mil coverlay bridge [P5]: one coverlay opening per land row, or LPI solder mask in that area.
- **Finish:** ENIG (soldered lands only).
- **Outline:** laser routed, ±2 mil [P5]; keying features (§15) in the outline if the case uses them.
- **Assembly:** DF40 headers placed on the steel-stiffened areas; flex assembly is "contact us" at PCBWay [P8] (**UNVERIFIED**, DFM). No other part on the cable.
- **Impedance coupon** on the production panel for each class (§14 member C1).

## 14. Test coupon

Hat-standard ADR 0004 requires a coupon (pogo field, DF40 flat cable, HAT pads: TDR, S-parameters to 10 GHz, crosstalk, real USB 3, PCIe Gen 2 and CSI-2 links, mating cycles and contact resistance) before the pad map freezes; ADR 0005 adds the row fence, the extension switch with D-PHY low-power signalling and the ground-backed fallback field. The cable contributes these members (RFC 0010 level at which each becomes mandatory):

| Member | What | Measured | Proposed pass | Level |
|---|---|---|---|---|
| C1 | PCBWay impedance coupons on the cable panel, one per class (D100, D90, S50) | TDR | Within HFC-01 to HFC-03 (± 10 %) | Q1 |
| C2 | The production cable at 100 mm (the assumed maximum) with both DF40 headers, mated to fixture boards carrying DF40C-100DS receptacles and coaxial launches, plus a 2×-thru fixture for de-embedding (IEEE P370 style, hat-standard benchmark §6 step 1) | TDR mated; SDD21, SDD11, NEXT and FEXT to 10 GHz for the nearest aggressor pairs | TDR within ± 15 % across the connector region and ± 10 % on the cable (benchmark §6 step 2 for the contact region); SDD21 against §7; crosstalk recorded (criteria from the USB 3, PCIe and D-PHY budgets, **UNVERIFIED** until derived) | Q1 |
| C3 | The same at 40 mm | As C2 | As C2 | Q1 |
| C4 | C2 folded at the 4.0 mm and 2.7 mm radii, held as in the case | TDR across the fold; SDD21 | Change within the ± 10 % band | Q1 |
| C5 | C2 under current: `HAT_5V` 3.0 A, `HAT_3V3` 1.5 A, `GND` 4.5 A, then the continuous ratings, in still air at 25 °C | Temperature rise of the cable body and at each DF40 (thermocouple or IR), four-wire voltage drop per rail | ≤ 10 °C at the fault ceilings on the body; drop ≤ §9 figures | Q0 |
| C6 | C2 with EMI film on both coverlays (only if Q2 pre-compliance asks for it) | As C2 | Impedance unchanged within ± 3 % | Q2 |
| C7 | DF40 mating cycles on C2: 30 cycles (the catalog rating) with contact resistance every 5 cycles | Four-wire per power position | ≤ 90 mΩ per contact (catalog p. 2) | Q1 |

C2 and C3 also go into the end-to-end channel of hat-standard ADR 0004 (pogo field, HAT pads, extension switch), where the real USB 3, PCIe Gen 2 and CSI-2 links run.

## 15. Inputs needed from the case

The cable cannot be laid out until the case gives:

1. **Route:** the path from the board DF40 to the device-side piece's DF40, the folds (count, position, axis) and the inside radius each fold has room for (≥ 4.0 mm wanted, 2.7 mm absolute).
2. **Length** of that route (assumed 40–100 mm).
3. **Width** available along the route (assumed 25.0 mm; 24.7 mm needed).
4. **Position and orientation** of the device-side piece's DF40 relative to the board's, which sets the face each cable end mates on.
5. **Height above each mated DF40:** stack 1.5 mm + cable 0.27 mm + steel 0.2 mm + adhesive, about 2.0 mm, plus the retention part.
6. **Retention:** a pad or bracket pressing each stiffener so the unlocked 100-position DF40 stays mated under drop and the cable's counterforce (catalog p. 16); the force is to be set with Hirose's data (**UNVERIFIED**).
7. **Keying** at both ends against a 180° mating (interface v1.1 §7.2).
8. **Fixing** of the cable body so the folds stay static (adhesive or clips), clear of sharp edges, the battery and its contacts.
9. **Keep-out** from the antennas and their feeds (PCB-R-06).
10. **Assembly and service sequence:** when the cable is mated and how it is reached.
11. **Grounding** of the stiffeners or the cable's planes to the frame, if the case wants that path for ESD or EMC.

## 16. Open items

1. DF40 contact numbering, and receptacle *n* mating header *n*: Hirose's drawing for approval (interface v1.1 §10 item 6).
2. Hirose's FPC-rigidity data for the header on an FPC (catalog p. 19); stiffener thickness and the retention force follow it.
3. PCBWay DFM review: the L2 impedance with L3 voided as a custom request; DK and post-lamination thickness of the bonding sheet; loss tangent of the stack; reflow-capable stiffener adhesive; flex assembly of a 0.4 mm DF40 on a steel stiffener; coverlay openings; plating thickness in flex vias (kicad-lib research §5 questions 4 and 5 already cover some).
4. Channel budgets of USB 3, PCIe Gen 2 and D-PHY through the full path, with the DF40 and pogo field measured (coupon C2, C3).
5. The `HAT_5V` voltage window (HCS-015), against the drops of §9.
6. Route, length and width from the case (§15).
7. Rerun the geometries in `odapkit stackup` when it exists.

## 17. Changes the board needs (for the board owner)

This spec does not edit the BOM, the pinout, the PCB design constraints or the rules.

| # | Where | Change | Why |
|---|---|---|---|
| B1 | BOM line 66 | Genders swapped: **DF40C-100DP-0.4V(51) header on the cable** (2 per cable), **DF40C-100DS-0.4V(51) receptacle on the board** (and on the device-side piece). Stock as recorded on line 66: DF40C-100DP Mouser 10,937, Digi-Key 0 (5,000 due 2027-01-05); DF40C-100DS Digi-Key 169,419 | Hirose catalog p. 19 (header on the FPC; the receptacle may peel from an FPC) |
| B2 | BOM line 102 | "FPC, impedance-controlled (90 Ω diff)" becomes: PCBWay standard 4-layer FPC 0.268 mm, pairs 100 Ω (`EXT`) and 90 Ω (USB) differential and 50 Ω I2S, power conductors per this spec, 0.2 mm steel stiffeners under both headers, length from the case; this spec as the reference | §4–§11 |
| B3 | PCB-Z-05 | The board's DF40 becomes the receptacle: 1.45 ± 0.15 mm high (was the header, 1.14 mm) | Catalog p. 4 |
| B4 | Board footprint (kicad-lib) | DF40C-100DS land pattern: 0.2 ± 0.02 mm lands at 0.4 mm, outer edge to edge 3.78 mm, inner 2.38 mm, ≤ 1.5 mm resist area between the rows (catalog p. 4 note 3) | B1 |
| B5 | PCB-I-12 (and PCB-I-01 to PCB-I-03 for their HAT segments) | Name the cable segment: geometry per HFC-01 and HFC-02, ≤ 100 mm, intra-pair ≤ 0.1 mm, `EXT` lanes to `EXT1` ≤ 0.1 mm; decide whether the cable's 0.1 mm counts inside the 0.91 mm CSI-2 data-to-clock budget (board share 0.81 mm) or on top of it | §6 |
| B6 | PCB-R-06 | Record that the cable's pairs have ground on both sides (L1 and L4 planes); the distance stays **UNVERIFIED** | §8 |
| B7 | Net classes and rules | The cable is its own KiCad project with `pcbway-flex` plus its product rules (§13): classes `HAT_EXT_100D` 60 / 150 µm on L2, `USB_90D` 70 / 100 µm on L2, `I2S_50SE` 65 µm on L2, `PWR_HAT5V` ≥ 10.4 mm and `PWR_HAT3V3` ≥ 4.0 mm on L3; the main-board rules gain nothing from it except the DF40 receptacle land | §6, §9 |
| B8 | Feature blocks, `blk.hat-signals`, `blk.hat-5v`, `blk.hat-3v3` | Connector: DF40C-100DS on the board; cable per this spec | B1 |
| — | Pinout v1 | No change: positions are interface v1.1 §7.2 | — |

For hat-standard (not edited here): interface v1.1 §7.2 and ADR 0005's BOM note name the receptacle on the cable; with B1 the device-side piece carries the DF40C-100DS receptacle and the cable the header. §5's "Flat cable (T1)" bullet can point to this spec.

## 18. Next step: the KiCad project

Not added in this change: a 4-layer flex project with its stack-up, composed rules (`kicad-dru-composed`) and the ERC and DRC hooks is more than a skeleton, and the board's rules are being edited in parallel. Next: `hardware/hat-flat-cable/` with the stack-up of §4, the net classes of B7, the DF40C-100DP footprint at both ends, the conductor map of §3 as the netlist, the stiffener and bend-zone areas on user layers, and the coupon members C1–C4 as separate boards on the same panel.

## 19. Sources

- Hirose Electric, DF40 Series catalog, May 1, 2020: pp. 2–4, 10, 16, 19; drawing EDC3-311351-00 rev. 7; parts-lib `Hirose/DF40C-100DS-DP-0.4V.md` (hashes there).
- PCBWay, *Stack-up for FPC*, <https://www.pcbway.com/pcb_prototype/Stack_up_for_FPC.html>, fetched 2026-10-24; [P5], [P8], [P13] as in the kicad-lib PCBWay capabilities research (fetched 2026-10-22).
- IPC-2221B, *Generic Standard on Printed Board Design*, conductor current-carrying design equation.
- Hat-standard interface v1.1, ADR 0004, ADR 0005, HAT interconnect benchmark §6.
- `sim/flex-impedance` (this repository), results of 2026-10-24.
