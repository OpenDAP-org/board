# RK3566 BGA escape study

- **Date:** 2026-10-24
- **Status:** Study, part of task E4.2 of the [electronics plan](https://github.com/opendap-project/t1/blob/main/docs/plans/2026-10-electronics-plan.md) (plan step 3 for the SoC). Nothing here is a decision. It answers, on a KiCad board checked with the composed T1 rules, the questions left open by the [RK3566 layout rules](2026-10-rk3566-layout-rules.md) §3 and PCB-S-02 of the [PCB design constraints](../specs/pcb-design-constraints.md): how many layers the escape needs and whether via-in-pad is required.
- **Study project:** [`hardware/studies/bga-escape/`](../../hardware/studies/bga-escape/) (`escape.py` builds the boards; results and plots are committed there).
- **Inputs:** the RK3566 footprint from kicad-lib (`Rockchip:Rockchip_FCCSP-565L_15.5x14.4mm_P0.4mm_P0.65mm_Ball0.25mm_Pad0.25mm_NSMD`, kicad-lib `878c769`, land pattern reasoning in kicad-lib `generator/bga/README.md`); the ball nets of [`hardware/pinout/pinout-v1.csv`](../../hardware/pinout/pinout-v1.csv); the composed rules [`hardware/t1-main-board/t1-main-board.kicad_dru`](../../hardware/t1-main-board/t1-main-board.kicad_dru), copied unchanged next to each study board. KiCad 10.0.7.

## Summary

1. **Every used ball escapes in three signal layers: L1 plus two inner layers.** Of the 260 used signal balls, 149 leave on L1, 105 on L3 and 6 on L4 (8-layer board). L6 and the bottom layer carry no escape. The 10-layer board gives the same split, so the layer count of the T1 is not set by the SoC escape.
2. **Via-in-pad is not required anywhere.** No ball, signal, power or ground, needs a via in its land. Laser microvias as dog-bones in the 0.825–0.875 mm channel between the ring and the core and through vias at the core interstitials are enough.
3. **DRC with the composed rules: 0 errors** on both boards. The warnings are expected study artefacts or Q2 items (§4).
4. **The open problem is the planes, not the escape.** The PCBWay hole-to-inner-copper value in the composed rules, 9 mil, clears 0.657 mm around each 0.2 mm drill on every inner layer, more than the 0.65 mm core pitch. Next to each other, mechanical vias leave no copper between them, so the planes under the core break up: 25 unconnected items remain (10 ground, 15 power) on each board. With 6 mil (PCBWay's high-difficulty value) 16 remain. Joining the ground and power under the SoC needs a plane plan of its own (§5).

## 1. Geometry

From the RK3566 Datasheet Rev 1.1 (DS), p. 21, Fig. 2-3 and p. 22, Fig. 2-5; arithmetic shown.

| Item | Value |
|---|---|
| Body | 15.5 × 14.4 mm |
| Ring | 222 balls, 0.4 mm, outer centres 14.8 × 13.6 mm, two rows per side |
| Core | 343 balls, 0.65 mm, 20 columns × 18 rows, first centre 1.575 mm (x) and 1.675 mm (y) from the edge |
| Channel, inner ring row to first core row | 0.825 mm (x sides), 0.875 mm (y sides) |
| Land | 0.25 mm NSMD, mask opening 0.3008 mm |
| Used balls (pinout v1) | 260 signal (153 ring, 107 core), 80 power (core), 188 ground, 37 not connected |

## 2. Rules and assumptions

**Rules:** the composed `t1-main-board.kicad_dru` (PCBWay HDI, OpenDAP craft, T1 product rules), unchanged. The router uses the values below, each at or above the rule; KiCad's DRC is the judge.

| Item | Study value | Rule |
|---|---|---|
| Escape track | 0.08 mm | PCB-G-02 ≥ 0.065 mm in `BGA_ESCAPE`; PCBWay 3 mil normal; CRAFT-43 series |
| Copper clearance | 0.0762 mm (3 mil) | PCB-G-02 ≥ 0.065 mm; PCBWay BGA pad to line 3 mil [P10] |
| Laser microvia | 0.10 mm drill, 0.25 mm land | PCB-G-03, CRAFT-45, PCBWay laser drill and 3 mil ring |
| Mechanical via (through, buried) | 0.20 mm drill, 0.46 mm pad | PCB-G-04 ≥ 0.45 mm, CRAFT-45 |
| Hole to copper | 6 mil outer, 9 mil inner | PCBWay HDI (8 layers, normal) |
| Hole to hole, mechanical | 11 mil | PCBWay HDI |
| Power and ground dog-bones | 0.15 mm | — |
| Mask web (Board Setup) | 3 mil | PCBWay advanced green [P2]; the NSMD ring lands give 3.9 mil |
| Rule area `BGA_ESCAPE` | body + 1.0 mm (the courtyard) | PCB-G-02 |

**Stackup (assumed; the board has no stackup specification yet):** HDI 1+N+1, L2 and L7 ground.

| Board | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 | L9 | L10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 8 layers | signal, SoC | GND | signal | signal | power | signal | GND | signal | | |
| 10 layers | signal, SoC | GND | signal | signal | power | signal | GND | signal | GND | signal |

**Via types:** microvia L1–L2 (ground balls: into the L2 plane); microvia L1–L2 stacked on a buried via L2–L(n−1) (signals whose via sits in the channel: in a 1+N+1 build the laser via alone stops on the L2 ground plane); through via (core signals and power at the interstitials, as the task asks: "through vias where they fit").

The SoC sits on the back of the real board (ADR 0016); the study places it on L1, which mirrors the layer roles and changes no count.

**Method:** a grid router (0.025 mm grid, eight directions, A* with a turn penalty) over obstacle maps inflated by the clearances above; every via site is checked exactly against the same clearances, including the hole-to-copper rules. Order: (1) ring signals on L1, outer row first; (2) ground microvias for the ring; (3) a via for every other signal, ring first, then core from the outside in (core balls take the interstitial site pointing away from the package centre, the outer core rows also the channel); (4) each signal via routed out on L3, then L4, L6, the bottom; a signal boxed in moves its via, or a neighbour's, and is routed again; (5) power through vias and core ground microvias around the routed signals; (6) each power net joined on L5 by tracks, standing in for the split plane; (7) ground zones on L2 and L7. A route has escaped once it is 0.3 mm outside the body.

## 3. Results

| | 8 layers | 10 layers |
|---|---|---|
| Signal balls escaped on L1 | 149 | 149 |
| on L3 | 105 | 105 |
| on L4 | 6 | 6 |
| on L6, L8 and below | 0 | 0 |
| Signal balls not escaped | 0 | 0 |
| Microvias L1–L2 to ground | 185 (+3 ground balls joined to a neighbour on L1) | same |
| Stacked microvia + buried via (signals, channel) | 35 (4 ring, 31 outer core rows) | same |
| Through vias (76 signal, 80 power) | 156 | same |
| Via in pad | 0 | 0 |
| DRC errors (composed rules) | 0 | 0 |
| Unconnected items | 25 (GND 10; power 15: vcca_1v8 6, vdd_npu 4, vcc3v3_sys 2, vdd_logic 2, vdda_0v9 1) | same |

Per-layer plots of the 8-layer board: [L1](../../hardware/studies/bga-escape/plots/8l-L1.png), [L2 ground](../../hardware/studies/bga-escape/plots/8l-L2-gnd.png), [L3](../../hardware/studies/bga-escape/plots/8l-L3.png), [L4](../../hardware/studies/bga-escape/plots/8l-L4.png), [L5 power](../../hardware/studies/bga-escape/plots/8l-L5-pwr.png).

What the numbers show:

- **The ring needs almost no vias.** 149 of the 153 used ring signals leave on L1: the outer row straight out, the inner row through the gaps of the outer row, either the gap in front of the ball or, diagonally, a gap next to it (0.316 mm of copper gap between an outer ball and the diagonal inner one, enough for a 0.08 mm track at 3 mil). The layout-rules note expected about 78 inner-ring balls to need a via; with pinout v1 and the diagonal escape, 4 do.
- **The channel carries the outer core rows.** 31 core signals of the outermost rows take a stacked microvia in the channel instead of an interstitial site; the core's interstitial through vias fit everywhere (0.46 mm from four lands: 0.105 mm of copper and 0.235 mm hole to land).
- **Two inner layers are enough because the core's signals are few and outside.** 107 core signals, mostly in the outer two or three rows; the centre is power and ground.
- **Through vias for the ring do not fit**, as the layout-rules note found: a 0.46 mm pad needs 0.42 mm from a land, more than half the 0.825 mm channel. Stacked microvias do.

## 4. DRC warnings (8 layers; the 10-layer board is the same plus 14 more isolated-fill warnings)

| Count | Check | Reading |
|---|---|---|
| 199 | `T1 PCB-W-02 [Q2]` teardrops on vias | Study boards have no teardrops; a Q2 item |
| 199 | track dangling | Escapes end 0.3 mm outside the body by design |
| 70 | `T1 PCB-D-10 [Q1]` open via within 0.2 mm of an SMD pad (warning, distance **UNVERIFIED**) | 62 microvias (channel and ground) and 8 through vias moved off their interstitial site by a rip-up. PCBWay's HDI microvias are copper-filled; the vias need the filled and capped property (IPC-4761 type VII) in the board, or the rule's distance revisited |
| 35 | holes co-located | Each stacked microvia on its buried via, by design |
| 19 | via dangling | Vias of power links that failed (§5) |
| 14 | isolated copper | Ground fill islands (§5) |
| 6 | `CRAFT-07 [Q2]` silk to via | The footprint's corner marks near channel vias |

## 5. Planes under the SoC

The escape leaves the planes broken under the core. A mechanical via (through or buried, 0.20 mm drill) keeps 9 mil from inner copper (PCBWay HDI, hole to inner conductor, 8 layers, normal [P1]), so it clears a 0.657 mm disc on every inner layer, more than the 0.65 mm pitch of the interstitial sites. Where power or signal vias sit next to each other, no plane copper passes between them. The result is 10 ground islands on L2 (ground balls whose microvia lands in a cut-off island) and 16 power links that could not be made on L5 (15 unconnected power items).

Sensitivity (study only, rule copy changed outside the repository): with **6 mil** inner hole to copper (PCBWay high difficulty [P1], or the advanced table [P2]), 16 items remain unconnected (9 ground, 7 power). The escape still needs L1, L3 and L4 (149 / 103 / 7) plus one signal on L6, and the greedy order put one via in a pad. Clearance alone does not close the planes.

What the planes need, for the layout: ground through vias (or buried L2–L7 vias) under the core so L2 islands reach L7 and each other; power balls of one rail kept adjacent with their vias in rows that leave plane necks; power joined on L1 or the bottom where the plane cannot reach; and a decision with PCBWay on the inner hole-to-copper value under the SoC. These are layout and stackup work, not escape.

## 6. Open items

1. **Stackup.** No `docs/specs/stackup-v1.md` exists; the roles above are this study's assumption. Rerun `escape.py` (its `STACKUPS` table) when the stackup is specified.
2. **PCBWay (with E3.6):** stacked microvia on a buried via in 1+N+1 (35 stacks); the 3 mil mask web between the 0.4 mm NSMD lands; the inner hole-to-copper value under the SoC (§5); copper-filled microvias within 0.2 mm of a land (PCB-D-10).
3. **Rule composition.** KiCad 10.0.7 applies the PCBWay hole-to-copper rule to a microvia's hole when the copper is a pad or a mechanical via, although the rule names the hole owner as A (observed in this study's DRC). Whether the later T1 rule PCB-G-02 (0.065 mm in `BGA_ESCAPE`) overrides PCBWay's 3 mil BGA pad to line was not tested: the study used 3 mil, **UNVERIFIED**.
4. **Escape only.** No length matching, differential pairs, DDR byte-lane grouping, reference-plane changes or stitching vias (PCB-S-10) are modelled; signal nets on two balls get one net per ball. The router is greedy: other orders give the same layer count with small changes in the split.
5. **Submodule.** The board's `hardware/lib/opendap` still pins kicad-lib `5491c92`; the study reads the footprint from the kicad-lib checkout until the submodule moves to a tag that carries it.

## Sources

- Rockchip *RK3566 Datasheet* Rev 1.1, 2021-03-05, pp. 21–23 (parts-lib `manifest.toml`).
- PCBWay capabilities as copied in kicad-lib [`docs/research/2026-10-pcbway-capabilities.md`](https://github.com/opendap-project/kicad-lib/blob/main/docs/research/2026-10-pcbway-capabilities.md): [P1] <https://www.pcbway.com/capabilities.html>, [P2] <https://www.pcbway.com/advanced-pcb-capabilities.html>, [P10] <https://www.pcbway.com/pcb_prototype/PCB_BGA.html>.
- The composed rules and the constraints they enforce: [`../specs/pcb-design-constraints.md`](../specs/pcb-design-constraints.md) (PCB-G-01 to G-04, PCB-D-10, PCB-W-02, PCB-S-02, PCB-S-10).
