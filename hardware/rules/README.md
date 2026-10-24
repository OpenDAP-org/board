# Main board rules

The T1 main board's own design rules, from the [PCB design constraints](../../docs/specs/pcb-design-constraints.md) (BRD-060).

- `t1-main-board.kicad_dru`: the product rules. Each rule is named after the constraint it enforces (`T1 PCB-…`). A value still **UNVERIFIED** in the specification is a warning; a value with a source is an error.
- `netclasses.toml`: the net classes the rules and the schematic share, with their constraint IDs, design currents and impedance targets.
- `test/`: a test board with one failing and one passing object per rule, built by `make_test_board.py` on kicad-lib's test-board tools (submodule `../lib/opendap`).

The KiCad project's `<project>.kicad_dru` is the composition of the PCBWay HDI fab rules (kicad-lib `design-rules/pcbway-hdi`) and these product rules, made and checked with `odapkit dru` (E3.5).

## Check

```sh
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
$PY hardware/rules/test/make_test_board.py
python3 hardware/lib/opendap/design-rules/tools/check_drc.py hardware/rules/test/t1-main-board-rules-test.kicad_pcb
```

Every rule fires exactly once in the FAIL column and nothing fires in the PASS column.

## Not checked by DRC

Impedance, length matching and skew (PCB-I), height zones (PCB-Z), copper area per net and via counts (PCB-P-01 to PCB-P-03, PCB-P-09), ESD distance (PCB-E-01) and test-pad coverage (PCB-T-02) are layout checks (E4.5). Review items are listed in the specification.
