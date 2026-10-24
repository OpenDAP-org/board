# RK3566 BGA escape study

A KiCad study of how the RK3566 (FCCSP565L, 0.4 mm ring and 0.65 mm core) escapes on the T1 main board, with the composed T1 rules. Method, assumptions and results: [`docs/research/2026-10-bga-escape-study.md`](../../../docs/research/2026-10-bga-escape-study.md).

| File | What it is |
|---|---|
| `escape.py` | Builds the study boards: places the escape vias and routes the escape of every used ball of `hardware/pinout/pinout-v1.csv`, then fills the ground planes. Run with KiCad's Python |
| `bga-escape-8l.result.json`, `bga-escape-10l.result.json` | The router's counts per layer, via counts, failures |
| `plots/` | Copper per layer of the 8-layer board, exported with `kicad-cli pcb export svg` and converted to PNG |

The boards (`bga-escape-<n>l.kicad_pcb`, `.kicad_pro`, and the rule copy `.kicad_dru`) are generated, not committed: their DRC with the composed rules has no error but reports unconnected power and ground items under the SoC (the plane result of the study), which the pre-commit DRC hook rejects, as it should for a board.

## Run

```sh
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
$PY hardware/studies/bga-escape/escape.py          # both stackups, about 30 s each
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$K pcb drc --format json --severity-all -o drc-8l.json hardware/studies/bga-escape/bga-escape-8l.kicad_pcb
$K pcb export svg --mode-single -l In2.Cu,Edge.Cuts --page-size-mode 2 --exclude-drawing-sheet \
   -o l3.svg hardware/studies/bga-escape/bga-escape-8l.kicad_pcb
```

The RK3566 footprint is read from kicad-lib through the workspace `repos.tsv` (or `ODAP_KICAD_LIB_DIR`) until the `hardware/lib/opendap` submodule is moved to a kicad-lib tag that carries it. A sensitivity run with another inner hole-to-copper value: `ESCAPE_HOLE_CU_IN_MIL=6 ESCAPE_OUT=<dir> $PY …/escape.py 8` (writes a modified rule copy to `<dir>`, never here).
