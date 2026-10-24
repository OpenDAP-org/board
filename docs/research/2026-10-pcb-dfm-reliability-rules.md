# PCB manufacturing, assembly and reliability rules for the T1 main board

- **Date:** 2026-10-24
- **Status:** Desk research and the DRC rules built from it. Nothing here is a decision of the maintainers. The rules are in [`hardware/rules/t1-main-board.kicad_dru`](../../hardware/rules/t1-main-board.kicad_dru) and tested on the rule test board; the [PCB design constraints](../specs/pcb-design-constraints.md) are not edited here.
- **Request:** the maintainers asked (2026-10-24) that the DRC cover what matters on a real board beyond the electrical design: screw holes, regulatory and manufacturing margins, routing rules, expert precautions.
- **Levels:** every rule carries the lowest quality level at which it is mandatory ([RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md)). Severity: Q0–Q1 with a source is an error; Q2–Q4, or any **UNVERIFIED** value, is a warning.
- **Method:** each value was taken from the page or document named in [Sources](#sources), fetched on 2026-10-24. *Primary* means the standard's text, a manufacturer's own document or a fab's capability page; *secondary* means a third party quoting one. Arithmetic on sourced figures is shown as such. Each KiCad constraint was tried on a scratch board with kicad-cli 10.0.7 before use, and every rule fires once in the FAIL column and never in the PASS column of the test board (§9).

## 0. Summary

1. **51 product rules now pass the test board**, 30 of them new: mounting holes (6), board edges and panelisation (3), assembly (10), voltage spacing (2), routing hygiene (7 rules under 3 IDs), battery and heat placement (2). Seven new ones are errors (PCB-V-01, V-02, B-03, D-02, D-03 and the two W-01); the other 23 are warnings, because their level is Q2 or their value is **UNVERIFIED**. The 21 existing rules are retagged with levels: P-01 to P-05 Q0 (sized for the protection rating, BRD-049), the others Q1.
2. **Uncoated pads need more than the general clearance.** IPC-2221B Table 6-1 gives 0.13 mm for uncoated component terminations (A6) at 0–15 V and 0.25 mm at 16–30 V; the T1's general clearance is 0.1 mm. Bare-board conductors (B1 0.05 mm internal, B2 0.1 mm external, B4 0.05 mm coated) are already met by PCB-G-01 and PCB-G-02. PCB-V-01 and PCB-V-02 close the gap; pin pairs inside one footprint are left to the part's maker.
3. **The screw is not chosen, so every hole rule is a warning.** The rings are sized for the larger case (M2 with an ISO 7089 washer, 5.0 mm). They become errors when the case fixes the screw.
4. **Several sources say "as far as possible" without a number** (Murata on MLCCs near screws, rework clearance around BGAs). Those values are **UNVERIFIED** placeholders, listed in §8 with what would close them.
5. **Two expert rules are expressible but not testable yet.** KiCad 10.0.7 checks thermal-relief spoke count and differential-pair uncoupled length, but does not name the rule in its report, so kicad-lib's `check_drc.py` cannot attribute them (§9). They are CHK items until that tool reads those messages.
6. **ID prefixes changed against the request.** The spec already uses `PCB-E` (ESD protection) and `PCB-T` (test and assembly), so edges are `PCB-B` and battery and heat placement is `PCB-L`. `PCB-H` is also proposed for a heat budget in the [industry-wisdom gaps](2026-10-industry-wisdom-t1-gaps.md) (G-33, `PCB-H-01`); one of the two needs another letter when the spec takes them in.
7. **The craft rule set owns the generic hygiene.** Acute angles (CRAFT-41, 135° minimum), 45° routing, short segments, silk sizes and silk to pads and vias are in kicad-lib `opendap-craft`; the T1 rules do not repeat them. A T1 rule matching every track would also override the craft rule, since KiCad applies the last matching rule.

## 1. Conventions the rules rely on

DRC finds objects by name. The conventions are in [`hardware/rules/README.md`](../../hardware/rules/README.md): mounting holes `H*`, MLCCs `C*`, edge parts `J*` and `SW*`, fiducials `FID*` with the pad property "Fiducial…", test points `TP*` with "Test point pad", BGA rework candidates with the footprint field `Rework` = `BGA`, heat sources with `Thermal` = `hot`, and rule areas `BREAK_TAB`, `BATTERY_POCKET`, `BATTERY_CONNECTOR`, `BGA_ESCAPE`, `AUDIO_ANALOG`. A footprint that does not follow them escapes its rules; CHK-D-08 (§8) checks that they are followed.

## 2. Mounting holes (PCB-H)

The case has four Ø 4 mm bosses (battery selection §2.3, **UNVERIFIED** until the case). The screw is M2 or M1.6 class, not chosen. Rings are computed for M2 with a washer, the larger case: ISO 7089 M2 washer d1 2.2 mm, d2 5.0 mm [F1]; hole 2.2 mm (the washer's inner diameter, used as the ISO 273 fine clearance hole, **UNVERIFIED**: ISO 273 not retrieved). Ring from the hole edge: (5.0 − 2.2) / 2 = 1.4 mm (arithmetic). Without a washer an ISO 7380 M2 head is smaller, so the washer case covers it (**UNVERIFIED**, head table not retrieved).

| ID | Level | Rule | Value | KiCad constraint | Source | Kind | Severity |
|---|---|---|---|---|---|---|---|
| PCB-H-01 | Q1 | No part under the screw head or washer | Courtyards ≥ 1.4 mm from the hole edge | `physical_hole_clearance`, B = footprint courtyard | [F1], arithmetic | Primary-equivalent table (vendor copy of ISO 7089) | Warning (screw **UNVERIFIED**) |
| PCB-H-02 | Q1 | No other-net copper under the head, outer layers | 1.4 mm | `hole_clearance`, `(layer outer)` | [F1]; Rockchip keeps traces away from mounting holes [RK, HSPCB p. 12] | As above; RK primary | Warning |
| PCB-H-03 | Q2 | A plated mounting hole is on GND | Net = GND | `assertion` | Proposal: plated holes give a chassis and ESD path (§8, CHK-H-02); not decided | — | Warning |
| PCB-H-04 | Q1 | Hole to board edge | ≥ 1.5 mm | `physical_hole_clearance`, B = Edge.Cuts | "minimum edge distance of 1.5–2 mm between the hole edge and the PCB edge to prevent board cracking" [AP]; fab minimum is lower, 0.4 mm drill to outline [JL] | Secondary (blog) | Warning (**UNVERIFIED**: no primary) |
| PCB-H-05 | Q1 | MLCC away from screw holes | Courtyard ≥ 3 mm from the hole edge | `physical_hole_clearance`, B = `C*` courtyard | Murata: "mounted in a position as far away from the screw holes as possible" [MU]; number **UNVERIFIED** | Primary (no number) | Warning |
| PCB-H-06 | Q2 | BGA balls away from screw holes | ≥ 5 mm | `physical_hole_clearance`, B = "BGA pad" | **UNVERIFIED** (IPC-7095 not retrieved) | — | Warning |

## 3. Board edges and panelisation (PCB-B)

PCBWay assembles the T1 panelised with rails; it requires rails when copper is closer than 3.5 mm to the edge [P20]. The outline is routed; the panel holds the board by tabs, marked on the board by `BREAK_TAB` rule areas.

| ID | Level | Rule | Value | KiCad constraint | Source | Kind | Severity |
|---|---|---|---|---|---|---|---|
| PCB-B-01 | Q1 | Courtyard to board edge, except `J*` and `SW*` (which may overhang) | ≥ 0.3 mm | `physical_clearance`, A = footprint, B = Edge.Cuts | PCB-G-05 applied to the body; **UNVERIFIED** | — | Warning |
| PCB-B-02 | Q1 | Copper to the edge at a break tab | ≥ 0.4 mm | `edge_clearance` in `BREAK_TAB` | JLCPCB: copper to a V-cut ≥ 0.4 mm [JL]; PCBWay publishes none for tabs | Primary (another fab, another edge type) | Warning (**UNVERIFIED** for tabs) |
| PCB-B-03 | Q1 | MLCC at a break tab | Courtyard ≥ 5.08 mm from the edge | `physical_clearance` in `BREAK_TAB` | KYOCERA AVX: "MLCCs be located at least .2" away from nearest edge of board"; when not possible, "the panel be routed along the cut line" [DK] | Secondary | Error |

Related figures, not used as rules: JLCPCB mouse bites 0.5–0.8 mm holes, 0.2–0.3 mm apart, tab width ≥ 5 mm with mouse bites [JL]; copper to a routed edge 0.2 mm [JL], 0.20 mm at PCBWay [P1] (the T1 uses 0.3 mm, PCB-G-05).

## 4. Assembly (PCB-D)

| ID | Level | Rule | Value | KiCad constraint | Source | Kind | Severity |
|---|---|---|---|---|---|---|---|
| PCB-D-01 | Q1 | Rework clearance around a BGA (`Rework` = `BGA`) | Courtyard to courtyard ≥ 2 mm | `courtyard_clearance` | **UNVERIFIED** (IPC-7095 and rework-station nozzle data not retrieved) | — | Warning |
| PCB-D-02 | Q1 | Fiducial size | Round, 1.0–3.0 mm | `assertion` on Size_X, Size_Y | "the recommended diameter is 1.0 mm for most production scenarios" [LC] | Secondary | Error |
| PCB-D-03 | Q1 | Fiducial clear area | Nothing within 1.0 mm of the dot (3 mm window on a 1 mm dot) | `physical_clearance` | "a window with a diameter of 3mm" [LC] | Secondary | Error |
| PCB-D-04 | Q2 | Fiducial to board edge | ≥ 3.85 mm | `edge_clearance` | "must be greater than 3.85 mm" [LC]; with rails the conveyor holds the rails, so not binding on panelised builds | Secondary | Warning |
| PCB-D-05 | Q2 | Silkscreen to board edge | ≥ 0.3 mm | `silk_clearance`, B = Edge.Cuts | **UNVERIFIED** (no fab publishes one; JLCPCB's page is silent [JL]) | — | Warning |
| PCB-D-06 | Q2 | Test pad size | ≥ 1.0 mm | `assertion` | "1.0 to 1.27 mm (40 to 50 mil)" for signal nets [JD] | Secondary (fab blog) | Warning |
| PCB-D-07 | Q2 | Test pad spacing | 2.54 mm pitch: ≥ 1.54 mm edge to edge for 1.0 mm pads (arithmetic) | `physical_clearance` | "2.54 mm (100 mil)" production standard [JD] | Secondary | Warning |
| PCB-D-08 | Q2 | Test pad to other parts | ≥ 1.0 mm to their pads | `physical_clearance` | "1.0 mm (40 mil)" from component bodies [JD]; measured to pads, bodies are CHK-D-05 | Secondary | Warning |
| PCB-D-09 | Q2 | Test pad to board edge | ≥ 3.8 mm | `edge_clearance` | "3.8 mm (150 mil)" [JD] | Secondary | Warning |
| PCB-D-10 | Q1 | Open via near an SMD pad; a via in a pad is filled and capped | Open via hole ≥ 0.2 mm from SMD pads; filled + capped may sit in the pad | `physical_hole_clearance`, condition on the via's Filling and Capping | Filled and capped is IPC-4761 type VII, offered by PCBWay [P11, P16]; distance **UNVERIFIED** | Primary (process); distance none | Warning |

Silkscreen to pads (0.15 mm, the same figure JLCPCB publishes [JL]) and to vias is CRAFT-07 in `opendap-craft`; it is not repeated.

## 5. Routing hygiene (PCB-W)

| ID | Level | Rule | Value | KiCad constraint | Source | Kind | Severity |
|---|---|---|---|---|---|---|---|
| PCB-W-01 | Q1 | No copper neck or sliver narrower than the narrowest track | 0.1 mm; 0.065 mm in `BGA_ESCAPE` | `connection_width` | PCB-G-01; PCBWay HDI 0.065 mm [P3] | Primary | Error |
| PCB-W-02 | Q2 | Teardrops enabled on every via | Enable_Teardrops | `assertion` | Margin for the 0.075 mm microvia ring [P2, P3]; as a requirement **UNVERIFIED** | — | Warning |
| PCB-W-03 | Q2 | Vias per line: USB 3 ≤ 2, PCIe ≤ 2, MIPI ≤ 4, USB 2 ≤ 6 | as listed | `via_count` per net class | Rockchip HSPCB Tables 1, 2, 5, 10, copied in [RK] | Primary (RK3568 edition, **UNVERIFIED** for the RK3566 package per [RK]) | Warning (Q2) |

Acute angles (acid traps), 45° routing and short segments are CRAFT-40, -41 and -47.

## 6. Voltage spacing (PCB-V)

IPC-2221B Table 6-1, "Voltage Between Conductors (DC or AC Peaks)" [IPC]:

| Voltage | B1 internal | B2 external, uncoated, ≤ 3050 m | B4 external, polymer coating | A5 conformal coat | A6 component termination, uncoated | A7 termination, coated |
|---|---|---|---|---|---|---|
| 0–15 V | 0.05 | 0.1 | 0.05 | 0.13 | 0.13 | 0.13 |
| 16–30 V | 0.05 | 0.1 | 0.05 | 0.13 | 0.25 | 0.13 |
| 31–50 V | 0.1 | 0.6 | 0.13 | 0.13 | 0.4 | 0.13 |

The T1's voltages: battery ≤ 8.8 V, VSYS ≤ 8.8 V, USB-C PD input up to 12 V, TVS2200 standoff 22 V and clamp 28.4 V on VBUS. So every net is in the 0–15 V row in steady state, and VBUS is in the 16–30 V row during a surge or with a faulty source.

- **Bare-board conductors are covered.** PCB-G-01 (0.1 mm) meets B2 and B1 up to 30 V. PCB-G-02 (0.065 mm, the RK3566 escape) meets B1 (0.05 mm) and B4 (0.05 mm, under solder mask); the escape carries only SoC signals, all ≤ 15 V.
- **Uncoated terminations are not.** A6 is 0.13 mm at 0–15 V and 0.25 mm at 16–30 V, above 0.1 mm.

| ID | Level | Rule | Value | KiCad constraint | Source | Kind | Severity |
|---|---|---|---|---|---|---|---|
| PCB-V-01 | Q1 | Pad on an outer layer to copper of another net, pads of one footprint excepted, outside `BGA_ESCAPE` | ≥ 0.13 mm | `clearance`, `(layer outer)`, `A.Parent != B.Parent` | IPC-2221B Table 6-1, A6, 0–15 V [IPC] | Secondary (standard quoted by Altair) | Error |
| PCB-V-02 | Q1 | VBUS pad to copper of another net | ≥ 0.25 mm | as above, `PWR_VBUS` | A6, 16–30 V [IPC]; voltages from the BOM (TVS2200) | Secondary | Error |

**Creepage.** KiCad 10 has a `creepage` constraint. Whether IEC 62368-1 sets any creepage for functional insulation inside an ES1 circuit (≤ 60 V DC) was not established here; no creepage rule is added. If the compliance work finds one, the battery path (`PWR_BAT`, `PWR_VSYS`) gets a `creepage` rule.

## 7. Battery and heat placement (PCB-L)

| ID | Level | Rule | Value | KiCad constraint | Source | Severity |
|---|---|---|---|---|---|---|
| PCB-L-01 | Q0 | No heat source (`Thermal` = `hot`) over the battery pocket | `BATTERY_POCKET` = pocket footprint + 3 mm | `disallow footprint` | Safety (BRD-049); margin **UNVERIFIED** (no cell-maker distance retrieved) | Warning |
| PCB-L-02 | Q0 | Only `PWR_BAT` and GND tracks and vias in the battery connector area (unfused copper) | `BATTERY_CONNECTOR` area | `disallow track via` | Safety (BRD-049); a partition rule, no external source | Warning |

The margin lives in the drawn area, not in the rule, because KiCad measures courtyard distances only between footprints on the same side and the pocket is not a part. CHK-L-01 checks the area against the case's pocket outline.

## 8. What DRC cannot check: review and script items

Proposed checklist wording; the level is the lowest at which the item is mandatory.

| ID | Level | Kind | Checklist wording |
|---|---|---|---|
| CHK-H-01 | Q1 | REV | The screw, washer and hole are chosen with the case; the PCB-H rules' 1.4 mm ring is recomputed from them, and H-01, H-02 become errors. |
| CHK-H-02 | Q2 | REV | Plated or non-plated mounting holes decided; if plated, on GND and stitched to the ground planes, and the case boss is insulating or its contact is part of the ESD path. |
| CHK-H-03 | Q1 | REV | No MLCC within the bending zone of a screw is oriented with its length towards the screw; parts near screws are placed with their long axis tangential to the hole. |
| CHK-B-01 | Q1 | REV | Tab and mouse-bite positions agreed with PCBWay's panel drawing; a `BREAK_TAB` area drawn at each, reaching 5.08 mm into the board. |
| CHK-B-02 | Q1 | REV | MLCCs within 5.08 mm of any broken edge lie parallel to the break line (KYOCERA AVX, Murata guidance; distance in PCB-B-03). |
| CHK-B-03 | Q1 | REV | Every part that overhangs the edge (J*, SW*) matches its case opening in the t1 interface files. |
| CHK-D-01 | Q1 | CHK | Three global fiducials per populated side, not symmetric, and two local fiducials at the RK3566 (PCB-M-09): count pads with the fiducial property per side. |
| CHK-D-02 | Q1 | REV | Polarity and pin-1 marks visible after assembly for every polarised part (diodes, tantalum or polymer capacitors, ICs, connectors). |
| CHK-D-03 | Q1 | REV | Paste on exposed thermal pads in a window pattern per each part's datasheet layout; coverage within the datasheet's range (**UNVERIFIED** generic figure, no IPC-7525 text retrieved). |
| CHK-D-04 | Q1 | CHK | Parts taller than the BGA within the rework clearance of a `Rework` = `BGA` part flagged from the 3D model heights. |
| CHK-D-05 | Q2 | CHK | Test pads 1.0 mm from component bodies (3D model outline), 5 mm from parts over 6.4 mm tall [JD]. |
| CHK-D-06 | Q1 | CHK | One test pad per net where required (PCB-T-02 rails, BRD-040 I2S, BRD-047 UART, BRD-015 SWD). |
| CHK-D-07 | Q1 | CHK | Via tenting set at board level (front and back tented), so only vias the layout opens on purpose are open; PCBWay order option matches. |
| CHK-D-08 | Q1 | CHK | Naming conventions followed: every mounting hole H*, fiducial pads carry the fiducial property, test pads the test-point property, BGA rework candidates and heat sources their fields. |
| CHK-W-01 | Q1 | CHK | Thermal relief on plane connections of connectors and test pads, at least 2 spokes resolved (PCB-G-07). KiCad `min_resolved_spokes` works but reports "zone min spoke count" without the rule name. |
| CHK-W-02 | Q2 | CHK | Differential-pair uncoupled length within the class limit. KiCad `diff_pair_uncoupled` works but reports "(<rule> maximum uncoupled length" without "rule '…'". The limit itself is **UNVERIFIED** (no source retrieved). |
| CHK-W-03 | Q2 | SIM | Via stubs over 0.30 mm on high-speed pairs simulated (Rockchip HSPCB p. 10 [RK]). |
| CHK-W-04 | Q2 | CHK | No test pad on a high-speed pair (Rockchip HSPCB p. 12 [RK]). Expressible in DRC as a later rule. |
| CHK-L-01 | Q0 | REV | `BATTERY_POCKET` drawn from the case's pocket outline plus the margin; the margin confirmed by the thermal analysis (V4-03). |
| CHK-V-01 | Q3 | REV | Creepage and clearance needs of IEC 62368-1 for the declared markets confirmed for ES1 circuits. |

## 9. KiCad 10.0.7 behaviour found while testing

- **Angles are bare numbers.** `track_angle (min 90deg)` makes KiCad drop the whole file silently; `(min 90)` works. Each acute corner is reported twice, once per segment order.
- **A rule with `min 0` loses its name.** A `courtyard_clearance (min 0mm)` overlap is reported as the built-in "Courtyards overlap" without "(rule …)", so it cannot be tested; any value above zero is named.
- **Courtyards are measured from the line's centre; Edge.Cuts lines from their outer edge** in physical rules, and from their centre in `edge_clearance`.
- **Courtyard distance is per side.** A front part and a back footprint are not compared; hence the area-based PCB-L-01.
- **`physical_clearance` against a courtyard needs `A.Type == 'Footprint'`.** Without it the courtyard graphic and the footprint are both reported (two violations for one fault). A pad and a courtyard are on different layers and are never compared.
- **Silk to edge:** a silk line within the distance is reported only when the edge clips it; text is reported, but its distance to an internal cutout does not follow the text's position, so the test uses a clipped line.
- **`connection_width` fires** (tested with zone necks), but only about 0.01 mm or more below the limit; the test board uses 0.02 mm.
- **`min_resolved_spokes` and `diff_pair_uncoupled` work but are not named** in the report (§8, CHK-W-01, CHK-W-02).
- **Unknown properties fail silently**: an assertion on a misspelt property fails on every object, which the PASS column catches. Via properties `Filling`, `Capping`, `Front_tenting`, `Back_tenting` and `Enable_Teardrops` exist with values `Filled`, `Capped`, `Tented`, `Not tented`.
- **`memberOfFootprint('H*')` is false for the footprint itself**; conditions on footprints use `Reference == 'H*'`.

## Sources

Fetched 2026-10-24 unless stated.

| Key | Source | Kind |
|---|---|---|
| IPC | IPC-2221B Table 6-1 as reproduced in Altair Pollex documentation, "IPC Material": <https://help.altair.com/pollex/topics/pollex/verification/dfe_ipc_material_r.htm> | Secondary |
| F1 | ISO 7089 flat washer dimensions, fasten.it norm table: <https://www.fasten.it/en/norms/norm/iso_7089> (M2: d1 2.2, d2 5, h 0.3; M1.6: 1.7, 4, 0.3) | Secondary (vendor copy of the standard) |
| MU | Murata FAQ on chip capacitor mounting near screw holes: <https://www.murata.com/en-global/support/faqs/capacitor/ceramiccapacitor/mnt/0030> and the GRM data-sheet caution ("as far away from the screw holes as possible") | Primary |
| DK | DigiKey TechForum, "Ceramic Capacitor Failure: Design Solutions & Mitigating Board Flex Cracking", quoting KYOCERA AVX: <https://forum.digikey.com/t/ceramic-capacitor-failure-design-solutions-mitigating-board-flex-cracking/26195> | Secondary |
| JL | JLCPCB PCB capabilities (Legend, Outline, panelisation): <https://jlcpcb.com/capabilities/pcb-capabilities> | Primary (another fab) |
| JD | JLCPCB blog, "PCB Test Points and Smart DFT": <https://jlcpcb.com/blog/pcb-test-points-and-smart-dft> | Secondary |
| LC | LCSC blog, "How to Properly Place Fiducial Marks on PCBs": <https://www.lcsc.com/blog/how-to-properly-place-fiducial-marks-on-pcbs-a-step-by-step-guide/> | Secondary |
| AP | ALLPCB, "Non-Plated Through Holes: Design Rules": <https://www.allpcb.com/allelectrohub/non-plated-through-holes-design-rules-for-optimal-performance-and-reliability> | Secondary |
| RK | [RK3566 layout rules from Rockchip's documents](2026-10-rk3566-layout-rules.md) (Rockchip RK3568 High Speed PCB Design Guide V1.0.0, cited by page) | Primary, via the board note |
| P1–P20 | PCBWay pages as keyed in kicad-lib's [PCBWay capabilities research](https://github.com/opendap-project/kicad-lib/blob/main/docs/research/2026-10-pcbway-capabilities.md) (fetched 2026-10-22): P1 capabilities, P2 advanced, P3 HDI, P11 via-in-pad, P16 order options, P20 assembly reminders | Primary |
| KiCad | KiCad 10.0.7 PCB Editor manual, custom rules (bundled `pcbnew.html`), and the experiments in §9 | Primary |

Not retrieved, so not used for any value: IPC-7351B courtyard excess table, IPC-7095 rework clearances, IPC-A-610, IPC-2152, IPC-7525 paste, SMEMA 3.1 text, TI and Intel high-speed layout guides for uncoupled length, PCBWay pages on fiducials, test points and tab clearance, and any Li-ion cell maker's heat-source distance.
