# Main board rules

The T1 main board's own design rules, from the [PCB design constraints](../../docs/specs/pcb-design-constraints.md) (BRD-060) and the [DFM and reliability rules research](../../docs/research/2026-10-pcb-dfm-reliability-rules.md).

- `t1-main-board.kicad_dru`: the product rules. Each rule is named after the constraint it enforces and the lowest quality level at which it is mandatory ([RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md)): `T1 PCB-H-01 [Q1]: …`.
- `netclasses.toml`: the net classes the rules and the schematic share, with their constraint IDs, design currents and impedance targets.
- `test/`: a test board with one failing and one passing object per rule, built by `make_test_board.py` on kicad-lib's test-board tools (submodule `../lib/opendap`).

The KiCad project's rules, [`../t1-main-board/t1-main-board.kicad_dru`](../t1-main-board/), are the composition of the PCBWay HDI fab rules (kicad-lib `design-rules/pcbway-hdi`), the OpenDAP craft rules (kicad-lib `design-rules/opendap-craft`) and these product rules, in that order, made and checked with `odapkit dru` (E3.5) from `t1-main-board.dru.toml`.

Impedance-controlled net classes are named `<name>_<ohms>D` (differential) or `<name>_<ohms>SE` (single-ended), so the craft rules exempt them from their general width rules (CRAFT-40, CRAFT-43; the composition was checked with every impedance class: no craft or fab report on their tracks). The product rules find the same classes with the same wildcards (PCB-S-14, PCB-W-01).

## Layers

The board is the 10-layer [stackup v1](../../docs/specs/stackup-v1.md). The rules name KiCad's layers:

| Stackup | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 | L9 | L10 |
|---|---|---|---|---|---|---|---|---|---|---|
| KiCad | `F.Cu` | `In1.Cu` | `In2.Cu` | `In3.Cu` | `In4.Cu` | `In5.Cu` | `In6.Cu` | `In7.Cu` | `In8.Cu` | `B.Cu` |
| Role | signal | ground | signal | ground | power | power | ground | signal | ground | signal |

Per-class widths are rules on `(layer outer)` (L1, L10) and `(layer inner)` (L3, L8); PCB-S-14 keeps impedance classes off every other inner layer, so "inner" means L3 and L8 for them. Each width rule is min / opt / max = the stackup width −5 % / exact / +5 %: a 5 % width error moves the impedance by 2–3 % (stackup v1 §5.1), a third of PCBWay's ±10 % window, so the rule catches a wrong width while the fab's own corners keep the rest. The minimum never goes below 0.075 mm, PCBWay's published HDI 3/3 mil option; for those classes the rules replace the fab set's 3 mil (0.0762 mm) track rule, which the inner 100 Ω width (75.0 µm) would otherwise break. Pair gaps are a clearance between the two nets of a pair at the gap −5 %, never below 0.1 mm. Every width and gap is **UNVERIFIED** (a warning) until PCBWay's DFM review confirms the stackup.

## Severity

- A rule at Q0 or Q1 whose value has a source is an **error**.
- A rule at Q2 to Q4 is a **warning**, whatever its source (RFC 0010: items above the build's target level are debt, not blockers).
- A rule whose value is still **UNVERIFIED** is a **warning** at any level, and becomes an error when the value is sourced and the level is Q0 or Q1.

Each rule's comment in the `.kicad_dru` names its source; the research note lists primary and secondary sources per rule.

## Conventions the rules rely on

The rules find objects by reference prefix, footprint field, pad fabrication property and rule-area name. The schematic symbols and footprints carry them; a footprint that does not follow them escapes its rules.

| Object | Convention | Rules |
|---|---|---|
| Mounting hole | Footprint reference `H*` (`H1`…`H4`); one pad, NPTH or plated | PCB-H-01 to H-06 |
| Ceramic capacitor (MLCC) | Reference `C*`. A capacitor that is not an MLCC still gets the MLCC rules, which only cost distance | PCB-H-05, PCB-B-03 |
| Edge-mounted part | Reference `J*` (connectors) or `SW*` (side buttons): exempt from the part-to-edge rule, may overhang the edge | PCB-B-01 |
| BGA needing rework access | Footprint field `Rework` = `BGA` (RK3566, LPDDR4X, eMMC) | PCB-D-01 |
| BGA ball pads | Pad fabrication property "BGA pad" (also used by the fab rules) | PCB-H-06 |
| Fiducial | Reference `FID*`; pad fabrication property "Fiducial, global to board" or "Fiducial, local to footprint" | PCB-D-02 to D-04 |
| Test point | Reference `TP*`; pad fabrication property "Test point pad" | PCB-D-06 to D-09 |
| Via in a pad | Via property Filling = Filled and Capping = Capped (IPC-4761 type VII) | PCB-D-10 |
| Heat source | Footprint field `Thermal` = `hot` (converters, eFuses, charger, SoC, PMIC) | PCB-L-01 |
| Battery pocket | Rule area `BATTERY_POCKET`: the pocket's footprint on the board, grown by a 3 mm margin (**UNVERIFIED**) | PCB-L-01 |
| Battery contacts | Rule area `BATTERY_CONNECTOR`: the pocket-floor contact window plus 1 mm, around the six battery contacts and their unfused copper (ADR 0020) | PCB-L-02, L-05 |
| Battery nets | Net classes `PWR_BAT` (P+, P−) and `BAT_SENSE` (mid-cell tap, NTC) in `netclasses.toml` | PCB-L-02, L-05 |
| Empty contact position | Rule area `BATTERY_CONTACT_EMPTY`: the 7.00 × 2.70 mm pad position left empty between P+ and the mid-cell tap | PCB-L-04 |
| Battery contact ESD | Footprint field `ESD` = `battery` on the TPD1E10B06 of the mid-cell tap and NTC; rule area `BATTERY_ESD`: the contact pads grown by 3 mm (**UNVERIFIED**) | PCB-L-08 |
| Panel break tab | Rule area `BREAK_TAB` around each tab or mouse-bite position on the outline, reaching at least 5.08 mm (PCB-B-03) into the board | PCB-B-02, B-03 |
| RK3566 escape | Rule area `BGA_ESCAPE` (existing) | PCB-G-02, W-01, V-01 |
| Analog audio | Rule area `AUDIO_ANALOG` (existing) | PCB-A-07 |
| Differential pair | Net names ending in `_P` / `_N` (or `+` / `-`), so KiCad couples the pair | PCB-I-01 to I-05, I-12 (pair gap) |
| RF ground cut-out | Rule area `RF_CUTOUT`: the L2 (L9) cut-out under the RF line, 1.6 mm wide and 0.6 mm past each end, on the cut layer and the pour layer of the line's side only (`In1.Cu` + `In2.Cu` for an L1 line, `In8.Cu` + `In7.Cu` for L10), with "keep out copper fills" set so the plane's fill stays out | PCB-R-03 |

## Check

```sh
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
$PY hardware/rules/test/make_test_board.py
python3 hardware/lib/opendap/design-rules/tools/check_drc.py hardware/rules/test/t1-main-board-rules-test.kicad_pcb
```

Every rule fires exactly once in the FAIL column and nothing fires in the PASS column.

Rules that overlap the fab and craft rule sets are left to them: silkscreen to pads and vias, silk sizes, 45° routing, acute angles (CRAFT-41, 135° minimum), short segments and the via set live in kicad-lib `opendap-craft`. The composition `pcbway-hdi` + `opendap-craft` + these rules compiles under KiCad 10.0.7 with every T1 rule still firing on the test board. The test board has ten copper layers; its GND objects are joined by a bus on L7 (`In6.Cu`), which no rule constrains, so the board reports no unconnected items.

## Not checked by DRC

Impedance itself, the maximum pair gap, spacing to other nets (3–5 × W), length matching, skew and delay matching across layers (PCB-I, PCB-S-15), height zones (PCB-Z, including the battery-contact exception of PCB-L-05), copper area per net and via counts for current (PCB-P-01 to PCB-P-03, PCB-P-09), the battery contacts' pad size, pitch and order (PCB-L-04), via count per contact pad and pour symmetry (PCB-L-07), ESD distance (PCB-E-01) and test-pad coverage (PCB-T-02) are layout checks (E4.5). The contact working height and the liner distance (PCB-L-06) are 3D review and case items. Review items are listed in the specification.

KiCad 10.0.7 can express three more rules, thermal-relief spoke count (`min_resolved_spokes`), differential-pair uncoupled length (`diff_pair_uncoupled`) and differential-pair gap (`diff_pair_gap`, with its maximum and the router's gap), but its report does not name the rule for them ("zone min spoke count", "(<rule> maximum uncoupled length", "(<rule> maximum gap"), so `check_drc.py` cannot attribute them. The pair gap's minimum is checked as a clearance instead (see Layers). They wait for a kicad-lib `check_drc.py` that reads those messages; until then they are CHK items in the research note, with the other checks DRC cannot make.
